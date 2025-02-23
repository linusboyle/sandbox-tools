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

def load_metadata(out_dir):
    metadata_path = os.path.join(out_dir, 'metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(out_dir, metadata):
    metadata_path = os.path.join(out_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

class RandomTableManager:

    def __init__(self, directory):
        self.tables = {}
        self.directory = directory
        # self.original_path = {}

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
        path = os.path.join(self.directory, table.name+".tsv")
        table.save_to_tsv(path)
   
    def load(self, directory):
        data_files = find_data_files(directory)
        for data_file in data_files:
            # print(f"Processing {data_file}...")
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
                if random_table.name in self.tables:
                    print(f"Warning: Duplicate Table Names {random_table.name}, Overwritten")
                random_table.data_file = data_file
                random_table.mtime = os.path.getmtime(data_file)
                self.tables[random_table.name] = random_table
                # self.original_path[random_table.name] = data_file

    def export_to_json(self, directory):
        metadata = load_metadata(directory)
        new_metadata = {}
        for table_name, table in self.tables.items():
            original_path = table.data_file
            last_modified = table.mtime
            if table_name not in metadata or metadata[table_name] < last_modified:
                relative_dir = os.path.relpath(os.path.dirname(original_path), start=self.directory)
                path = os.path.join(directory, relative_dir, f"{table_name}.json")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                table.save_to_json(path)
                new_metadata[table_name] = last_modified
            else:
                new_metadata[table_name] = metadata[table_name]
        
        save_metadata(directory, new_metadata)
    
    def export_to_tsv(self, directory):
        metadata = load_metadata(directory)
        new_metadata = {}
        for table_name, table in self.tables.items():
            original_path = table.data_file
            last_modified = table.mtime
            if table_name not in metadata or metadata[table_name] < last_modified:
                relative_dir = os.path.relpath(os.path.dirname(original_path), start=self.directory)
                path = os.path.join(directory, relative_dir, f"{table_name}.tsv")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                table.save_to_tsv(path)
                new_metadata[table_name] = last_modified
            else:
                new_metadata[table_name] = metadata[table_name]
        
        save_metadata(directory, new_metadata)
 
    def export_to_markdown(self, directory):
        metadata = load_metadata(directory)
        new_metadata = {}
        for table_name, table in self.tables.items():
            original_path = table.data_file
            last_modified = table.mtime
            if table_name not in metadata or metadata[table_name] < last_modified:
                relative_dir = os.path.relpath(os.path.dirname(original_path), start=self.directory)
                path = os.path.join(directory, relative_dir, f"{table_name}.md")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                table.save_to_markdown(path)
                new_metadata[table_name] = last_modified
            else:
                new_metadata[table_name] = metadata[table_name]
        
        save_metadata(directory, new_metadata)

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

    print(manager.formatted_draw("WWN Wilderness Tags"))
    print(manager.formatted_draw("WWN Wilderness Tags"))
    print(manager.formatted_draw("人类姓名"))