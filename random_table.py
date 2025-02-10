import json
from dice_roller import roll_formula

def flatten(xss):
    return [x for xs in xss for x in xs]

class RandomTable:
    """
    Represents a random table used to generate random results based on dice rolls.
    This class is commonly used in tabletop games and simulations to provide a structured way
    of generating random outcomes.

    Attributes:
        name (str): The name of the table.
        roll_formula (str): The dice roll formula (e.g., "1d100").
        entries (list): A list of Entry objects that define the possible outcomes.
    """
    def __init__(self, name, roll_formula, entries):
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
                return [entry.target]
            case "document":
                if tables and entry.target in tables:
                    #Recursively roll the linked table by name
                    linked_table = tables[entry.target]
                    linked_result = linked_table.draw()
                    self.roll_results_stash += linked_result['roll']
                    return linked_result['result']
        print(f"Warning: Cann't resolve target for {entry}")
        return ''

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

def load_random_table(data):
    name = data['name']
    roll_formula = data['formula']
    entries = [Entry(e['type'], e['range'][0], e['range'][1], e['text']) for e in data['results']]
    return RandomTable(name, roll_formula, entries)

def load_random_table_from_json(file_path):
    """
    Loads a random table from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        RandomTable: A RandomTable object.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        return load_random_table(data)


def save_random_table_to_json(table, file_path):
    """
    Saves a random table to a JSON file.

    Args:
        table (RandomTable): The RandomTable object to save.
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
        return e

    data = {
        'name': table.name,
        'formula': table.roll_formula,
        'results': [
           prepare_entry(e) for e in table.entries
        ]
    }
    with open(file_path, 'w', encoding="utf8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    loaded_table = load_random_table_from_json("tables/wilderness_tags.json")
    print(f"{loaded_table.formatted_draw()}")