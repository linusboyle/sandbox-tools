#! python3
import sys
import re

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
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python replace_uuid.py <filename1> [filename2 ... filenameN]")
    else:
        for file_path in sys.argv[1:]:
            replace_uuid_in_file(file_path)