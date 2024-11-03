import json
import pandas as pd
from scipy.stats import pearsonr, spearmanr

INPUT_FILE = "annotated_completions_v3.json"

def analyze_correlation(results):
    # Convert results to DataFrame
    df = pd.json_normalize(results)


    # Map labels to numerical values
    label_mapping = {'correct': 2, 'partially_correct': 1, 'incorrect': 0}
    df['label_num'] = df['label'].map(label_mapping)

    # Expand metrics into separate columns, handling missing metrics
    if 'metrics' in df.columns:
        metrics_df = pd.json_normalize(df['metrics'])
        df = pd.concat([df, metrics_df], axis=1)

    # List of metrics (some may be missing)
    metrics_list = ['exact_match', 'chrf_score', 'bleu_score', 'rougeL_score', 'levenshtein_ratio']

    # Compute correlations only for available metrics
    for m in metrics_list:
        metric='metrics.'+m
        if metric in df.columns:

            pearson_corr, _ = pearsonr(df['label_num'], df[metric].fillna(0))
            spearman_corr, _ = spearmanr(df['label_num'], df[metric].fillna(0))


            print(f"Metric: {m}")
            print(f"  Pearson Correlation: {pearson_corr:.4f}")
            print(f"  Spearman Correlation: {spearman_corr:.4f}")
            print("-" * 30)
        else:
            print(f"Metric: {m} is not available in the data.")
            print("-" * 30)


def main():
    # Load the JSON data from file
    with open(INPUT_FILE, 'r') as file:
        json_data = json.load(file)

    # Analyze correlations
    analyze_correlation(json_data)


if __name__ == "__main__":
    main()
