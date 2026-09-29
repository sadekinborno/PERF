from collections import defaultdict

def aggregate_votes(votes, gold_label=None, flag_threshold=0.60):
    """
    Takes a list of vote dicts: [{'label': 'A', 'confidence': 90}, ...]
    Returns {final_label, agreement_pct, flagged: bool}
    """
    if not votes:
        return {"final_label": None, "agreement_pct": 0, "flagged": False}
        
    score_by_label = defaultdict(float)
    total_confidence = 0.0
    
    for v in votes:
        if v.get("label"):
            conf = v.get("confidence", 50.0)
            score_by_label[v["label"]] += conf
            total_confidence += conf
            
    if total_confidence == 0:
        return {"final_label": None, "agreement_pct": 0, "flagged": False}
        
    # Find label with highest confidence sum
    best_label = max(score_by_label, key=score_by_label.get)
    best_score = score_by_label[best_label]
    
    agreement_pct = best_score / total_confidence
    
    # Flagging logic: PERF disagrees with gold AND consensus is strong (>= threshold)
    flagged = False
    if gold_label and best_label != gold_label and agreement_pct >= flag_threshold:
        flagged = True
        
    return {
        "final_label": best_label,
        "agreement_pct": agreement_pct,
        "flagged": flagged,
        "scores": dict(score_by_label)
    }
