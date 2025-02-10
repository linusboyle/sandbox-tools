import os
import json
import argparse
from random_table import load_random_table_from_json

def find_json_files(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

class RandomTableManager:

    def __init__(self, directory):
        self.tables = {}
        self.load(directory)

    def load(self, directory):
        json_files = find_json_files(directory)
        for json_file in json_files:
            print(f"Processing {json_file}...")
            try:
                random_table = load_random_table_from_json(json_file)
            except:
                print(f"Error loading {json_file}, Skipping")
            else:
                self.tables[random_table.name] = random_table

    def draw(self, name):
        table = self.tables[name]
        return table.draw(self.tables)

    def formatted_draw(self, name):
        table = self.tables[name]
        return table.formatted_draw(self.tables)
       

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert JSON files to random tables.')
    parser.add_argument('directory', type=str, nargs='?', default='tables', help='The directory containing JSON files (default: tables)')
    args = parser.parse_args()
    manager = RandomTableManager(args.directory)

    print(manager.formatted_draw("Wilderness Tags"))
    print(manager.formatted_draw("Wilderness Tags"))