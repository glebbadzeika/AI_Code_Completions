import os
import random
import json
import tokenize
import io

TOTAL_SPLITS = 20
CODEBASE = "codebase"
OUTPUT_FILE = "splits_v2.json"
MIN_MIDDLE_LENGTH = 10

def get_token_boundaries(code):
    """
    Uses the tokenize module to find all token boundaries in the code.
    Returns a sorted list of unique token start positions.
    """
    token_boundaries = set()
    try:
        tokens = tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline)
        for tok in tokens:
            if tok.type == tokenize.ENDMARKER:
                continue
            start_pos = tok.start[1]
            end_pos = tok.end[1]
            token_boundaries.add(start_pos)
            token_boundaries.add(end_pos)
        token_boundaries.add(len(code))
    except tokenize.TokenError as e:
        print(f"Tokenization error: {e}")
    return sorted(token_boundaries)

def split_code(code):
    """
    Splits code into prefix, middle, and suffix at token boundaries to ensure
    splits do not occur in the middle of words or tokens. Ensures that prefix,
    middle, and suffix are all non-empty.
    """
    if len(code) < 20:
        return None

    token_boundaries = get_token_boundaries(code)

    # Ensure we have enough room for non-empty prefix, middle, and suffix
    valid_start_positions = [pos for pos in token_boundaries if 1 <= pos <= len(code) - 2]
    if not valid_start_positions:
        return None

    for _ in range(10):  # Try up to 10 times to find a valid split
        start_pos = random.choice(valid_start_positions)

        # Decide on desired middle length
        min_middle_length = MIN_MIDDLE_LENGTH  # Middle must be at least 1 character
        max_middle_length = len(code) - start_pos - 1  # Ensure suffix is at least 1 character
        if max_middle_length < min_middle_length:
            continue

        # Decide on middle length with more probability towards shorter middles
        if random.random() < 0.7:
            desired_middle_length = random.randint(min_middle_length, min(max_middle_length, 30))
        else:
            desired_middle_length = random.randint(min(50, max_middle_length), min(150, max_middle_length))

        # Find possible end positions
        possible_end_positions = [pos for pos in token_boundaries
                                  if start_pos + 1 <= pos <= start_pos + desired_middle_length and pos <= len(code) - 1]
        if not possible_end_positions:
            continue

        end_pos = random.choice(possible_end_positions)
        prefix = code[:start_pos]
        middle = code[start_pos:end_pos]
        suffix = code[end_pos:]

        # Ensure none of the sections are empty
        if prefix and middle and suffix:
            return prefix, middle, suffix

    return None

def generate_splits(folder_path=CODEBASE, output_file=OUTPUT_FILE, total_splits=TOTAL_SPLITS):
    splits = []
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    if not files:
        print("No .txt files found in the codebase directory.")
        return
    splits_per_file = max(total_splits // len(files), 1)

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

            for _ in range(splits_per_file * 10):  # Increased attempts per file
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

            if len(splits) >= total_splits:
                break

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(splits, outfile, indent=4, ensure_ascii=False)

    print(f"Splits saved to {output_file}")

if __name__ == "__main__":
    generate_splits()
