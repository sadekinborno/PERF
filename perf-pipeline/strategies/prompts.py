def _base_instruction(labels):
    return f"Classify the text into one of these labels: {labels}. Respond ONLY with a JSON object in the format: {{\"label\": \"<chosen_label>\", \"confidence\": <0-100 integer>}}"

def zero_shot(text, labels):
    return f"{_base_instruction(labels)}\n\nText: {text}"

def few_shot(text, labels, exemplars):
    prompt = f"{_base_instruction(labels)}\n\nExamples:\n"
    for ex in exemplars:
        prompt += f"Text: {ex['text']}\nLabel: {ex['label']}\n\n"
    prompt += f"Text: {text}"
    return prompt

def chain_of_thought(text, labels):
    instruction = f"Classify the text into one of these labels: {labels}. First, provide step-by-step reasoning. Then, provide the final answer and confidence (0-100). Respond ONLY with a JSON object in the format: {{\"reasoning\": \"<steps>\", \"label\": \"<chosen_label>\", \"confidence\": <0-100>}}"
    return f"{instruction}\n\nText: {text}"

def rationale_critique(text, labels, known_issue_description):
    instruction = f"Classify the text into one of these labels: {labels}. Note this known issue with the dataset: {known_issue_description}. Critique whether this text falls into that trap. Then provide your final answer. Respond ONLY with a JSON object in the format: {{\"critique\": \"<your critique>\", \"label\": \"<chosen_label>\", \"confidence\": <0-100>}}"
    return f"{instruction}\n\nText: {text}"
