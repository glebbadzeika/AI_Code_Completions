import os
import random
import json
import re

TOTAL_SPLITS = 40
CODEBASE = "codebase"
OUTPUT_FILE = "splits_v3.json"

def adjust_to_word_boundary(position, code, direction='both'):
    """
    Adjusts the position to the nearest word boundary.
    direction can be 'both', 'before', or 'after'.
    """
    code_len = len(code)

    if direction in ('both', 'before'):
        # Move position backward to the previous word boundary
        pos = position
        while pos > 0 and (code[pos-1].isalnum() or code[pos-1] == '_'):
            pos -= 1
        position_before = pos
    else:
        position_before = position

    if direction in ('both', 'after'):
        # Move position forward to the next word boundary
        pos = position
        while pos < code_len and (code[pos].isalnum() or code[pos] == '_'):
            pos += 1
        position_after = pos
    else:
        position_after = position

    if direction == 'both':
        # Choose the position closest to the original position
        if abs(position - position_before) <= abs(position_after - position):
            return position_before
        else:
            return position_after
    elif direction == 'before':
        return position_before
    elif direction == 'after':
        return position_after
    else:
        return position

def split_code(code):
    """
    Splits code into non-empty prefix, middle, and suffix without splitting words.
    """
    min_code_length = 3  # Minimal code length to split
    if len(code) < min_code_length:
        return None

    code_len = len(code)

    # Ensure that we have room for non-empty prefix, middle, and suffix
    min_prefix_length = 1
    min_middle_length = 1
    min_suffix_length = 1

    if code_len < (min_prefix_length + min_middle_length + min_suffix_length):
        return None

    # Choose cursor_position ensuring non-empty prefix and suffix
    min_cursor = min_prefix_length
    max_cursor = code_len - min_middle_length - min_suffix_length

    if min_cursor >= max_cursor:
        return None

    cursor_position = random.randint(min_cursor, max_cursor)

    # Adjust cursor_position to word boundary
    cursor_position = adjust_to_word_boundary(cursor_position, code, direction='both')

    # Now choose middle_length ensuring non-empty middle and suffix
    max_middle_length = code_len - cursor_position - min_suffix_length

    if max_middle_length < min_middle_length:
        return None

    # Decide on middle_length
    if random.random() < 0.5:
        middle_length = random.randint(min_middle_length, min(30, max_middle_length))  # Shorter suggestions
    else:
        middle_length = random.randint(50, min(150, max_middle_length))  # Occasional longer suggestions

    # Adjust middle_end to word boundary
    middle_end = cursor_position + middle_length
    middle_end = adjust_to_word_boundary(middle_end, code, direction='both')

    # Ensure middle_end is after cursor_position and within bounds
    if middle_end <= cursor_position:
        middle_end = cursor_position + min_middle_length
        middle_end = adjust_to_word_boundary(middle_end, code, direction='after')

    if middle_end > code_len - min_suffix_length:
        middle_end = code_len - min_suffix_length

    # Now extract prefix, middle, and suffix
    prefix = code[:cursor_position]
    middle = code[cursor_position:middle_end]
    suffix = code[middle_end:]

    # Ensure none are empty
    if not prefix.strip() or not middle.strip() or not suffix.strip():
        return None

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
