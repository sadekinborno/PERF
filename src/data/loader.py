import csv
import json
import os

def load_dataset(filepath):
    """
    Loads a dataset from CSV or JSON file.
    Returns a list of dictionaries in standardized PERF format:
    [{'text': str, 'gold_label': str, 'metadata': dict}, ...]
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    data = []

    if ext == '.csv':
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle common column variants ('text', 'tweet', 'sentence', 'statement')
                text = row.pop('text', row.pop('tweet', row.pop('sentence', row.pop('statement', None))))
                raw_label = row.pop('label', row.pop('gold_label', row.pop('sarcastic', None)))

                if text is not None and raw_label is not None:
                    # Normalize binary 1/0 flags into text labels if needed
                    str_label = str(raw_label).strip()
                    if str_label == '1':
                        gold_label = 'sarcastic'
                    elif str_label == '0':
                        gold_label = 'non-sarcastic'
                    else:
                        gold_label = str_label

                    data.append({
                        'text': text.strip(),
                        'gold_label': gold_label,
                        'metadata': row
                    })
    elif ext == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            for item in raw_data:
                text = item.pop('text', item.pop('sentence', None))
                gold_label = item.pop('label', item.pop('gold_label', None))
                if text and gold_label is not None:
                    data.append({
                        'text': str(text).strip(),
                        'gold_label': str(gold_label).strip(),
                        'metadata': item
                    })
    else:
        raise ValueError("Unsupported file format. Please use .csv or .json")

    return data
