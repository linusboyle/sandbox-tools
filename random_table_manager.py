import os
import json
import argparse
from random_table import *

def find_data_files(directory):
    data_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] in ('.json', '.tsv', '.txt'):
                data_files.append(os.path.join(root, file))
    return data_files

class RandomTableManager:

    def __init__(self, directory):
        self.tables = {}
        self.directory = directory

        self.load(directory)

    def add_table_json(self, data):
        table = load_random_table_from_json(data)
        self.tables[table.name] = table
        # persist
        path = os.path.join(self.directory, table.name+".json")
        table.save_to_json(path)

    def add_table_tsv(self, data):
        table = load_random_table_from_tsv(data)
        self.tables[table.name] = table
        # persist
        path = os.path.join(self.directory, table.name+".json")
        table.save_to_json(path)
   
    def load(self, directory):
        data_files = find_data_files(directory)
        for data_file in data_files:
            print(f"Processing {data_file}...")
            try:
                (root ,ext) = os.path.splitext(data_file)
                if ext == '.json':
                    random_table = load_random_table_from_json_file(data_file)
                elif ext in ('.tsv', '.txt'):
                    random_table = load_random_table_from_tsv_file(data_file)
                else:
                    print(f"Unsupported file type: {data_file}, Skipping")
                    continue
            except Exception as e:
                print(f"Error loading {data_file}, Skipping: {e}")
            else:
                self.tables[random_table.name] = random_table

    def export_to_json(self, directory):
        for table_name, table in self.tables.items():
            path = os.path.join(directory, f"{table_name}.json")
            table.save_to_json(path)

    def export_to_tsv(self, directory):
        for table_name, table in self.tables.items():
            path = os.path.join(directory, f"{table_name}.tsv")
            table.save_to_tsv(path)

    def draw(self, name):
        table = self.tables[name]
        return table.draw(self.tables)

    def formatted_draw(self, name):
        table = self.tables[name]
        return table.formatted_draw(self.tables)

    def get_tables(self):
        return list(self.tables.keys())
       
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert json files to random tables.')
    parser.add_argument('directory', type=str, nargs='?', default='tables', help='the directory containing json files (default: tables)')
    args = parser.parse_args()
    manager = RandomTableManager(args.directory)

    print(manager.formatted_draw("Wilderness Tags"))
    print(manager.formatted_draw("Wilderness Tags"))