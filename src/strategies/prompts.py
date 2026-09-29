"""
PERF Prompting Strategies Module
Defines the 4 key re-annotation strategies used across LLM ensemble queries.
"""

def _base_instruction(labels):
    return (
        f"Classify the input text into exactly one of these labels: {labels}.\n"
        f"Respond ONLY with a valid JSON object in the following format:\n"
        f'{{"label": "<chosen_label>", "confidence": <0-100 integer>}}'
    )

def zero_shot(text, labels):
    """Strategy 1: Direct Zero-Shot Classification"""
    return f"{_base_instruction(labels)}\n\nText: {text}"

def few_shot(text, labels, exemplars):
    """Strategy 2: Exemplar-Guided Few-Shot Classification"""
    prompt = f"{_base_instruction(labels)}\n\nReference Examples:\n"
    for ex in exemplars:
        prompt += f"Text: {ex['text']}\nLabel: {ex['label']}\n\n"
    prompt += f"Target Text: {text}"
    return prompt

def chain_of_thought(text, labels):
    """Strategy 3: Step-by-Step Chain-of-Thought (CoT) Reasoning"""
    instruction = (
        f"Classify the input text into exactly one of these labels: {labels}.\n"
        f"First, provide step-by-step reasoning explaining the semantics and nuances.\n"
        f"Then, provide the final chosen label and your confidence score (0-100).\n"
        f"Respond ONLY with a valid JSON object in the following format:\n"
        f'{{"reasoning": "<step_by_step_analysis>", "label": "<chosen_label>", "confidence": <0-100>}}'
    )
    return f"{instruction}\n\nText: {text}"

def rationale_critique(text, labels, known_issue_description=""):
    """Strategy 4: Domain-Aware Rationale Critique"""
    issue_context = (
        f"Note this known annotation vulnerability in this benchmark: {known_issue_description}.\n"
        if known_issue_description else ""
    )
    instruction = (
        f"Classify the input text into exactly one of these labels: {labels}.\n"
        f"{issue_context}"
        f"Critique whether this example might suffer from annotation ambiguity or label errors.\n"
        f"Respond ONLY with a valid JSON object in the following format:\n"
        f'{{"critique": "<analysis>", "label": "<chosen_label>", "confidence": <0-100>}}'
    )
    return f"{instruction}\n\nText: {text}"
