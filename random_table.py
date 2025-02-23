import json
import csv
import os
import re
from dice_roller import *
from dice_util import guess_dice_formula

def flatten(xss):
    return [x for xs in xss for x in xs]

def replace_links_for_markdown(pattern):
    try:
        def replacer(match):
            link = match.group(1)
            if is_dice_formula(link):
                return f"`dice: {link}`"
            else:
                return f"`dice: [[{link}^table]]`"
        
        # Replace all occurrences of [[string]] with the result of roll_formula(string)
        result = re.sub(r'\[\[(.*?)\]\]', replacer, pattern)
        # Escape reserved char of Markdown: |
        result = re.sub(r'\|', r"\|", result)
        return result
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
    def __init__(self, name, roll_formula, entries, displayRoll=True, replacement=True, file_path=None, mtime=None):
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

        # For Manager Only
        self.file_path = file_path
        self.mtime = mtime

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

    def replace_links_with_draw_results(self, pattern, tables=None):
        def replacer(match):
            rep_string = match.group(1)
            tree = try_parse(rep_string)
            if tree:
                # dice formula
                result = transform_formula(tree)
                return str(result["result"])
            else:
                # Not a dice formula, regarded as a table
                if tables and rep_string in tables:
                    #Recursively roll the linked table by name
                    linked_table = tables[rep_string]
                    linked_result = linked_table.draw(tables)
                    self.roll_results_stash += linked_result['roll']
                    return ' '.join(linked_result['result'])
                else:
                    print(f"Warning: No table named {rep_string} found, regarded as plain text")
                    return rep_string
        
        # Replace all occurrences of [[string]] with the result of roll_formula(string)
        return re.sub(r'\[\[(.*?)\]\]', replacer, pattern)

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
        return self.replace_links_with_draw_results(entry.target, tables)
        # match entry.type:
        #     case "text":
        #         return [replace_inline_rolls(entry.target)]
        #     case "document":
        #         if tables and entry.target in tables:
        #             #Recursively roll the linked table by name
        #             linked_table = tables[entry.target]
        #             linked_result = linked_table.draw(tables)
        #             self.roll_results_stash += linked_result['roll']
        #             return linked_result['result']
        # print(f"Warning: Cann't resolve target for {entry}")
        # return []

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
            'result': [self.resolve_target(entry, tables) for entry in entries],
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
            entry_type = "text"
            target = e.target
            if e.target.startswith("[[") and e.target.endswith("]]"):
                link = e.target.strip('[]')
                if not is_dice_formula(link):
                    entry_type = "document"
            res = {
                'type': entry_type,
                'text': target,
                'range': [e.min_roll, e.max_roll]
            }
            if entry_type == "document":
                res['documentCollection'] = "RollTable" # for FVTT
            return res
            # TODO: 根据[[]]将target分割，然后产生多个object。在下面results中flatten

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
                target_str = entry.target
                writer.writerow([range_str, target_str])

    def save_to_markdown(self, file_path):
        """
        Exports a RandomTable object to a Markdown formatted string.
    
        Args:
            random_table (RandomTable): The RandomTable object to export.
    
        Returns:
            str: A Markdown formatted string representing the table.
        """
        from datetime import datetime
    
        # Add YAML frontmatter
        markdown = f"""---
date: {datetime.now().strftime('%Y-%m-%d')}
tags: 
    - table
---
"""
    
        markdown += f"# {self.name}\n\n"
        markdown += f"`dice: [[{self.name}^table]]`\n\n"
        markdown += f"| dice: {self.roll_formula}  | {self.name} |\n"
        markdown += "| ---------- | ------- |\n"
    
        for entry in self.entries:
            dice_range = f"{entry.min_roll}-{entry.max_roll}" if entry.min_roll != entry.max_roll else str(entry.min_roll)
            target = replace_links_for_markdown(entry.target)
            markdown += f"| {dice_range} | {target} |\n"
    
        markdown += "^table\n"
    
        with open(file_path, 'w') as file:
            file.write(markdown)
        return markdown

class Entry:
    def __init__(self, min_roll, max_roll, target):
        """
        Initializes an Entry object.

        Args:
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
        # self.type = type

    def __repr__(self):
         return f"Entry: {self.min_roll}-{self.max_roll} '{self.target}'"

def load_random_table_from_json(data):
    name = data['name']
    entries = [Entry(e['range'][0], e['range'][1], e['text']) for e in data['results']]

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
            # entry_type = "document" if target.startswith("[[") and target.endswith("]]") else "text"
            # if entry_type == "document":
                # target = target.strip('[]')
            entry = Entry(min_roll, max_roll, target)
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
    loaded_table = load_random_table_from_tsv_file("tables/WWN/WWN Wilderness Tags.tsv")
    print(f"{loaded_table.formatted_draw()}")