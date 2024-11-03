import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import sacrebleu
import Levenshtein
from rouge_score import rouge_scorer

SPLITS = "splits_v3.json"
OUTPUT_FILE = "annotated_completions_v3.json"
AUTOMATED = False
# Load model and tokenizer
model_name = "bigcode/tiny_starcoder_py"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


def compute_metrics(actual, generated):
    # Exact Match
    exact_match = int(actual.strip() == generated.strip())

    # chrF Score
    chrf_score = sacrebleu.sentence_chrf(generated, [actual]).score

    # BLEU Score
    bleu_score = sacrebleu.sentence_bleu(generated, [actual]).score

    # ROUGE-L Score
    rougeL = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

    # Levenshtein Ratio
    levenshtein_distance = Levenshtein.distance(actual, generated)
    max_len = max(len(actual), len(generated))
    levenshtein_ratio = (1 - levenshtein_distance / max_len) * 100

    return {
        "exact_match": exact_match,
        "chrf_score": chrf_score,
        "bleu_score": bleu_score,
        "rougeL_score": rougeL.score(generated, actual)['rougeL'].fmeasure,
        "levenshtein_ratio": levenshtein_ratio
    }


def generate_completion(prefix, suffix):


    # Format input with FIM tokens
    input_text = f"<fim_prefix>{prefix}<fim_suffix>{suffix}<fim_middle>"

    # Tokenize the input
    inputs = tokenizer(input_text, return_tensors="pt")
    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    # Generate the middle part
    output = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=20, do_sample=True)

    # Decode the generated tokens and isolate the middle section
    completion = tokenizer.decode(output[0], skip_special_tokens=True)

    # Extract the middle part by removing prefix and suffix
    fim_result = completion.replace(prefix, "").replace(suffix, "").strip()
    return fim_result






def load_splits(file_path=SPLITS):
    """
    Load splits from the JSON file.

    Parameters:
    - file_path: Path to the JSON file containing prefix, middle, and suffix.

    Returns:
    - splits: A list of dictionaries with 'filename', 'prefix', 'middle', and 'suffix' keys.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        splits = json.load(file)
    return splits


def main():
    # Load the splits
    splits = load_splits(SPLITS)

    results = []
    for i, entry in enumerate(splits):
        filename = entry["filename"]
        prefix = entry["prefix"]
        actual_middle = entry["middle"]
        suffix = entry["suffix"]

        # Generate completion
        generated_middle = generate_completion(prefix, suffix)

        # Display for manual review
        print(f"File: {filename}")
        print(f"Prefix:\n{prefix}")
        print(f"Actual Middle:\n{actual_middle}")
        print(f"Generated Middle:\n{generated_middle}")
        print(f"Suffix:\n{suffix}")
        print("-" * 50)

        # Compute metrics
        metrics = compute_metrics(actual_middle, generated_middle)

        if not AUTOMATED:
            label = input(f"{i}) Label (correct(c)/partially_correct(pc)/incorrect(i)): ").strip()
            label = "correct" if label in ["c", "correct"] or metrics[
                "exact_match"] else "partially_correct" if label in [
                "pc", "partially_correct"] else "incorrect"
        else:
            label = "correct" if  metrics["exact_match"] else "incorrect"




        # Store results with metrics
        result = {
            "id": i,
            "filename": filename,
            "prefix": prefix,
            "actual_middle": actual_middle,
            "generated_middle": generated_middle,
            "suffix": suffix,
            "label": label,
            "metrics": metrics
        }

        results.append(result)

    # Save results to a new JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)
    print(f"Annotated completions saved to {OUTPUT_FILE}")


# Run the main function
if __name__ == "__main__":
    main()
