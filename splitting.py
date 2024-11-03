import os
import random
import json
import re

TOTAL_SPLITS = 40
CODEBASE = "codebase"
OUTPUT_FILE = "splits.json"
def find_nearest_split_position(code, cursor_position):
    """
    Adjusts the cursor position to the nearest space or common delimiter to ensure
    more meaningful splits at natural code boundaries.
    """
    delimiters = r"\s|\(|\)|\{|\}|\[|\]|,|;|:|\n"
    before = re.finditer(delimiters, code[:cursor_position][::-1])  # Reverse search
    after = re.finditer(delimiters, code[cursor_position:])

    nearest_before = cursor_position - next(before).start() if next(before, None) else cursor_position
    nearest_after = cursor_position + next(after).start() if next(after, None) else cursor_position

    return nearest_before if abs(cursor_position - nearest_before) < abs(
        cursor_position - nearest_after) else nearest_after


def split_code(code):
    """
    Split code into prefix, middle, and suffix with a balance of within-word and
    between-word splits.
    """
    if len(code) < 20:
        return None

    cursor_position = random.randint(10, len(code) - 10)

    # 95% of the time, adjust the cursor to the nearest boundary
    if random.random() < 0.95:
        cursor_position = find_nearest_split_position(code, cursor_position)


    if random.random() < 0.5:
        middle_length = random.randint(3, 30)  # Shorter completion suggestions
    else:
        middle_length = random.randint(50, min(150, len(code) - cursor_position))  # Occasional longer suggestions

    prefix = code[:cursor_position]
    middle = code[cursor_position:cursor_position + middle_length]
    suffix = code[cursor_position + middle_length:]

    return prefix, middle, suffix


def generate_splits(folder_path=CODEBASE, output_file=OUTPUT_FILE, total_splits=TOTAL_SPLITS):
    splits = []

    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    splits_per_file = max(total_splits // len(files), 1)

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

            for _ in range(splits_per_file):
                split_result = split_code(code)

                if split_result:
                    prefix, middle, suffix = split_result
                    splits.append({
                        "id": len(splits),
                        "filename": filename,
                        "prefix": prefix,
                        "middle": middle,
                        "suffix": suffix
                    })

                if len(splits) >= total_splits:
                    break

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(splits, outfile, indent=4, ensure_ascii=False)

    print(f"Splits saved to {output_file}")


if __name__ == "__main__":
    generate_splits()
