#! python3
import sys
import re
import os

def replace_uuid_in_file(file_path):
    # Define the pattern and replacement string
    pattern = r'@UUID\[[^\]]+\]\{([^}]+)\}'
    replacement = r'\1'

    try:
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace all occurrences of the pattern
        modified_content = re.sub(pattern, replacement, content)

        # Write the modified content back to the original file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        print(f"Replacements made in {file_path}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

# 删除从FVTT导出的随机表中的引用

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            replace_uuid_in_file(full_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python replace_uuid.py <filename1> [filename2 ... filenameN]")
    else:
        for path in sys.argv[1:]:
            if os.path.isdir(path):
                process_directory(path)
            elif os.path.isfile(path):
                replace_uuid_in_file(path)
            else:
                print(f"Path not found or invalid: {path}")