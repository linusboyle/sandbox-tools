import json
import csv
import os
import re
from dice_roller import roll_formula
from dice_util import guess_dice_formula

def flatten(xss):
    return [x for xs in xss for x in xs]

def replace_inline_rolls(pattern):
    try:
        def replacer(match):
            formula = match.group(1)
            result = roll_formula(formula)
            return str(result["result"])
        
        # Replace all occurrences of [[string]] with the result of roll_formula(string)
        return re.sub(r'\[\[(.*?)\]\]', replacer, pattern)
    except Exception as e:
        print(f"Error replacing inline rolls: {e}")
        return pattern

class RandomTable:
    """
    Represents a random table used to generate random results based on dice rolls,
    commonly utilized in tabletop games and simulations. This class provides a structured
    way of defining and rolling tables with various entry types, including text and links
    to other tables.

    Attributes:
        name (str): The name of the table.
        roll_formula (str): The dice roll formula used for generating random results (e.g., "1d100").
        entries (list): A list of Entry objects that define the possible outcomes.
        displayRoll (bool): Whether to display the roll result when drawing from the table. Defaults to True.
        replacement (bool): Whether to disable an entry when it is drawn. Defaults to True.

    Methods:
        roll(): Rolls the dice and returns the result.
        get_entry(roll_result): Finds the appropriate entry based on the roll result.
        resolve_target(entry, tables=None): Resolves the target of an entry, handling text and document types.
        draw(tables=None): Rolls on the table and resolves the target, returning a dictionary with results and rolls.
        formatted_draw(tables=None): Returns a formatted string of the roll and resolved target.
        save_to_json(file_path): Saves the random table to a JSON file.
        save_to_tsv(file_path): Saves the random table to a TSV file.
    """
    def __init__(self, name, roll_formula, entries, displayRoll=True, replacement=True):
        """
        Initializes a RandomTable object.

        Args:
            name (str): The name of the table.
            roll_formula (str): The dice roll formula (e.g., "1d100").
            entries (list): A list of Entry objects that define the possible outcomes.
        """
        self.name = name
        self.roll_formula = roll_formula
        self.entries = entries
        self.displayRoll = displayRoll
        self.replacement = replacement

        self.roll_results_stash = []

    def roll(self):
        """
        Rolls the dice and returns the result.

        Returns:
            int: The result of the dice roll.
        """
        return roll_formula(self.roll_formula)["result"]

    def get_entry(self, roll_result):
        """
        Finds the appropriate entry based on the roll result.

        Args:
            roll_result (int): The result of the dice roll.

        Returns:
            Entry: The matching Entry object, or None if no match is found.
        """
        return filter(lambda e: e.min_roll <= roll_result <= e.max_roll, self.entries)

    def resolve_target(self, entry, tables=None):
        """
        Resolves the target of an entry.  If the target is a string, it returns the string.
        If the target is a link to another table, it rolls that table and returns the result.

        Args:
            entry (Entry): The entry to resolve.
            tables (dict, optional): A dictionary of RandomTable objects, used for resolving table links. Defaults to None.

        Returns:
            str: The resolved target.
        """
        match entry.type:
            case "text":
                return [replace_inline_rolls(entry.target)]
            case "document":
                if tables and entry.target in tables:
                    #Recursively roll the linked table by name
                    linked_table = tables[entry.target]
                    linked_result = linked_table.draw(tables)
                    self.roll_results_stash += linked_result['roll']
                    return linked_result['result']
        print(f"Warning: Cann't resolve target for {entry}")
        return []

    def draw(self, tables=None):
        """
        Rolls on the table and resolves the target

        Args:
            tables (dict, optional): A dictionary of RandomTable objects, used for resolving table links. Defaults to None.

        Returns:
            str: The resolved target.
        """
        roll_result = self.roll()
        self.roll_results_stash = [roll_result]
        entries = self.get_entry(roll_result)
        return {
            'result': flatten([self.resolve_target(entry, tables) for entry in entries]),
            'roll': self.roll_results_stash
        }

    def formatted_draw(self, tables=None):
        result = self.draw(tables)
        return f"{result['roll']} : {' '.join(result['result'])}"

    def __repr__(self):
        return f"RandomTable(name='{self.name}', roll_formula='{self.roll_formula}', entries={self.entries})"

    def save_to_json(self, file_path):
        """
        Saves a random table to a JSON file.

        Args:
            file_path (str): The path to the JSON file.
        """
        def prepare_entry(e):
            res = {
                'type': e.type,
                'text': e.target,
                'range': [e.min_roll, e.max_roll]
            }
            if e.type == "document":
                res['documentCollection'] = "RollTable" # for FVTT
            return res

        data = {
            'name': self.name,
            'formula': self.roll_formula,
            'displayRoll' : self.displayRoll,
            'replacement' : self.replacement,
            'results': [
               prepare_entry(e) for e in self.entries
            ]
        }
        with open(file_path, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save_to_tsv(self, file_path):
        """
        Saves a random table to a TSV file. The TSV file has two columns: range and target.
        If the target is a link to another table, it is formatted as [[tablename]].

        Args:
            file_path (str): The path to the TSV file.
        """
        with open(file_path, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            # Write header
            writer.writerow([self.roll_formula, self.name])
            for entry in self.entries:
                range_str = f"{entry.min_roll}-{entry.max_roll}" if entry.min_roll != entry.max_roll else f"{entry.min_roll}"
                target_str = f"[[{entry.target}]]" if entry.type == "document" else entry.target
                writer.writerow([range_str, target_str])

class Entry:
    def __init__(self, type, min_roll, max_roll, target):
        """
        Initializes an Entry object.

        Args:
            type (str): The type of the entry (e.g., "text", "document").
            min_roll (int): The minimum roll for this entry (inclusive).
            max_roll (int): The maximum roll for this entry (inclusive).
            target (str or RandomTable): The target of this entry.  Can be a string or a link to another RandomTable.
        """
        if not isinstance(min_roll, int) or not isinstance(max_roll, int):
            raise TypeError("min_roll and max_roll must be integers")
        if min_roll > max_roll:
            raise ValueError("min_roll must be less than or equal to max_roll")
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.target = target
        self.type = type

    def __repr__(self):
         return f"Entry(type={self.type}, min_roll={self.min_roll}, max_roll={self.max_roll}, target='{self.target}')"

def load_random_table_from_json(data):
    name = data['name']
    entries = [Entry(e['type'] if e['type'] != 'pack' else 'text', e['range'][0], e['range'][1], e['text']) for e in data['results']]

    displayRoll = True
    if 'displayRoll' in data:
        displayRoll = data['displayRoll']
    replacement = True
    if 'replacement' in data:
        replacement = data['replacement']

    if data['formula']:
        roll_formula = data['formula']
    else:
        roll_formula = f"1d{len(entries)}"
    return RandomTable(name, roll_formula, entries, displayRoll=displayRoll, replacement=replacement)

def load_random_table_from_json_file(file_path):
    """
    Loads a random table from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        RandomTable: A RandomTable object.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        return load_random_table_from_json(data)

def load_random_table_from_tsv_file(file_path):
    with open(file_path, 'r') as f:
        return load_random_table_from_tsv(f)

def load_random_table_from_tsv(src):
    """
    Loads a random table from a TSV file of a string of text in TSV format. The TSV text has two columns: range and target.

    Args:
        file_path (str): The path to the TSV file.

    Returns:
        RandomTable: A RandomTable object.
    """
    data = src.split('\n') if isinstance(src, str) else src
    reader = csv.reader(data, delimiter='\t')
    header = next(reader)

    roll_formula, name = header
    max_roll_target = []
    min_roll_target = []

    entries = []
    for row in reader:
        try:
            range_str = row[0]
            if '-' in range_str:
                min_roll, max_roll = map(int, range_str.split('-'))
            else:
                min_roll = max_roll = int(range_str)
            max_roll_target.append(max_roll)
            min_roll_target.append(min_roll)

            target = row[1]
            entry_type = "document" if target.startswith("[[") and target.endswith("]]") else "text"
            if entry_type == "document":
                target = target.strip('[]')
            entry = Entry(entry_type, min_roll, max_roll, target)
            entries.append(entry)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid TSV data: {e}") from e

    if not entries:
        raise ValueError("TSV file is empty or contains no valid data.")

    if roll_formula.strip() == "":
        roll_formula = guess_dice_formula(min(min_roll_target), max(max_roll_target)) 
    if name.strip() == "":
        name = "Random Table" 
    return RandomTable(name, roll_formula, entries)

if __name__ == '__main__':
    loaded_table = load_random_table_from_tsv_file("tables/Wilderness Tags.tsv")
    print(f"{loaded_table.formatted_draw()}")