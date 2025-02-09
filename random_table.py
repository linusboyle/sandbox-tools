import json
from dice_roller import roll_formula

class RandomTable:
    def __init__(self, name, roll_formula, entries):
        """
        Initializes a RandomTable object.

        Args:
            name (str): The name of the table.
            roll_formula (str): The dice roll formula (e.g., "1d100").
            entries (list): A list of Entry objects.
        """
        self.name = name
        self.roll_formula = roll_formula
        self.entries = entries

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
                return entry.target
            case "document":
                if tables and entry.target in tables:
                    #Recursively roll the linked table by name
                    linked_table = tables[entry.target]
                    return linked_table.draw()
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
        entries = self.get_entry(roll_result)
        return {
            'result': '\n'.join([self.resolve_target(entry, tables) for entry in entries]),
            'roll': roll_result
        }

    def formatted_draw(self, tables=None):
        result = self.draw(tables)
        return f"{result['roll']} : {result['result']}"

    def __repr__(self):
        return f"RandomTable(name='{self.name}', roll_formula='{self.roll_formula}', entries={self.entries})"


class Entry:
    def __init__(self, type, min_roll, max_roll, target):
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
        self.type = type

    def __repr__(self):
         return f"Entry(type={self.type}, min_roll={self.min_roll}, max_roll={self.max_roll}, target='{self.target}')"


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

    name = data['name']
    roll_formula = data['formula']
    entries = [Entry(e['type'], e['range'][0], e['range'][1], e['text']) for e in data['results']]
    return RandomTable(name, roll_formula, entries)


def save_random_table_to_json(table, file_path):
    """
    Saves a random table to a JSON file.

    Args:
        table (RandomTable): The RandomTable object to save.
        file_path (str): The path to the JSON file.
    """
    data = {
        'name': table.name,
        'formula': table.roll_formula,
        'results': [
            {
                'type': e.type,
                'text': e.target,
                'range': [e.min_roll, e.max_roll]
            } for e in table.entries
        ]
    }
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    loaded_table = load_random_table_from_json("wilderness_tags.json")
    print(f"{loaded_table.formatted_draw()}")