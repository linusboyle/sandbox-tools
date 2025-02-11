#! python3
import os
import argparse
from random_table_manager import RandomTableManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert json files to random tables.')
    parser.add_argument('in_dir', type=str, nargs='?', default='tables', help='the directory containing table files (default: tables)')
    parser.add_argument('out_dir', type=str, nargs='?', default='output', help='the directory to export (default: output)')
    args = parser.parse_args()

    manager = RandomTableManager(args.in_dir)
    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)
    manager.export_to_json(args.out_dir)