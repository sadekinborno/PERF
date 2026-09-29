import csv
import json
import os

def load_dataset(filepath):
    """
    Loads a dataset from CSV or JSON.
    Returns a list of dicts: [{'text': str, 'gold_label': str, 'metadata': dict}, ...]
    """
    ext = os.path.splitext(filepath)[1].lower()
    data = []
    
    if ext == '.csv':
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle standard 'text'/'label' or iSarcasm 'tweet'/'sarcastic' columns
                text = row.pop('text', row.pop('tweet', None))
                raw_label = row.pop('label', row.pop('sarcastic', None))
                
                if text is not None and raw_label is not None:
                    # Map binary 1/0 to readable labels for better LLM prompting
                    if str(raw_label).strip() == '1':
                        gold_label = 'sarcastic'
                    elif str(raw_label).strip() == '0':
                        gold_label = 'non-sarcastic'
                    else:
                        gold_label = str(raw_label).strip()
                        
                    data.append({
                        'text': text,
                        'gold_label': gold_label,
                        'metadata': row
                    })
    elif ext == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            for item in raw_data:
                text = item.pop('text', None)
                gold_label = item.pop('label', None)
                if text and gold_label:
                    data.append({
                        'text': text,
                        'gold_label': str(gold_label),
                        'metadata': item
                    })
    else:
        raise ValueError("Unsupported file format. Use .csv or .json")
        
    return data
