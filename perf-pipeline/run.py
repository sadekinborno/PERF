import argparse
import yaml
import sys
import os
from data.loader import load_dataset
from strategies.prompts import zero_shot, few_shot, chain_of_thought, rationale_critique
from models.clients import get_model_label
from voting.aggregator import aggregate_votes

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def estimate_cost(config, num_examples):
    print("--- Cost Estimation ---")
    worst_case_pct = config.get("worst_case_escalation_pct", 0.3)
    stage1_runs = num_examples
    stage2_runs = int(num_examples * worst_case_pct)
    
    total_cost = 0
    print(f"Assuming {num_examples} Stage 1 instances, {stage2_runs} Stage 2 instances.")
    
    # Rough token approximations for estimation
    avg_in_stage1, avg_out_stage1 = 100, 20
    avg_in_stage2, avg_out_stage2 = 250, 150 # CoT/critique uses more tokens
    
    for model, details in config["models"].items():
        c_in = details["cost_per_m_in"] / 1000000
        c_out = details["cost_per_m_out"] / 1000000
        
        cost1 = stage1_runs * (avg_in_stage1 * c_in + avg_out_stage1 * c_out)
        cost2 = stage2_runs * 3 * (avg_in_stage2 * c_in + avg_out_stage2 * c_out) # 3 expensive strategies
        
        model_total = cost1 + cost2
        total_cost += model_total
        print(f"Model: {model} -> Estimated Cost: ${model_total:.4f}")
        
    print(f"Total Projected Cost: ${total_cost:.4f}")
    if total_cost > config.get("max_spend_usd", 5.0):
        print(f"WARNING: Projected cost exceeds max budget of ${config.get('max_spend_usd')}")
    print("-----------------------")
    return total_cost

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to CSV/JSON dataset")
    parser.add_argument("--labels", required=True, help="Comma separated list of valid labels")
    parser.add_argument("--issue", default="", help="Known issue description for rationale-critique")
    parser.add_argument("--estimate-cost", action="store_true", help="Print cost estimation and exit")
    parser.add_argument("--confirm", action="store_true", help="Confirm execution and spend money")
    args = parser.parse_args()

    config = load_config()
    data = load_dataset(args.dataset)
    labels_list = [l.strip() for l in args.labels.split(",")]
    
    if args.estimate_cost and not args.confirm:
        estimate_cost(config, len(data))
        print("Run with --confirm to proceed with actual API calls.")
        sys.exit(0)

    if not args.confirm:
        print("Must run with --estimate-cost or --confirm to execute.")
        sys.exit(1)

    max_spend = config.get("max_spend_usd", 5.0)
    current_spend = 0.0
    results = []
    
    stage2_count = 0

    print(f"Starting pipeline on {len(data)} examples...")
    
    for idx, item in enumerate(data):
        text = item["text"]
        gold = item["gold_label"]
        
        votes = []
        
        # Stage 1: Zero-shot across all models
        stage1_votes = []
        for model_name, m_config in config["models"].items():
            prompt = zero_shot(text, labels_list)
            res = get_model_label(m_config["provider"], model_name, prompt)
            
            # Cost tracking
            c_in = m_config["cost_per_m_in"] / 1000000
            c_out = m_config["cost_per_m_out"] / 1000000
            current_spend += (res["tokens_in"] * c_in) + (res["tokens_out"] * c_out)
            
            if not res["error"]:
                stage1_votes.append({"label": res["label"], "confidence": res["confidence"]})
                votes.append(res)
                
        # Check agreement after Stage 1
        s1_agg = aggregate_votes(stage1_votes, gold)
        
        # Stage 2: Escalate if Stage 1 is uncertain or disagrees with gold
        # We define "needs escalation" if agreement < 0.8 or if best label != gold
        if s1_agg["agreement_pct"] < 0.8 or s1_agg["final_label"] != gold:
            stage2_count += 1
            for model_name, m_config in config["models"].items():
                if current_spend >= max_spend:
                    print(f"HARD LIMIT REACHED (${current_spend:.2f}). Stopping gracefully.")
                    break
                
                # Run the 3 advanced strategies (mocking few-shot exemplars for simplicity here)
                prompts = [
                    chain_of_thought(text, labels_list),
                    rationale_critique(text, labels_list, args.issue)
                ]
                
                for p in prompts:
                    res = get_model_label(m_config["provider"], model_name, p)
                    c_in = m_config["cost_per_m_in"] / 1000000
                    c_out = m_config["cost_per_m_out"] / 1000000
                    current_spend += (res["tokens_in"] * c_in) + (res["tokens_out"] * c_out)
                    
                    if not res["error"]:
                        votes.append(res)
                        
        if current_spend >= max_spend:
            break
            
        final_agg = aggregate_votes(votes, gold)
        results.append({
            "text": text,
            "gold": gold,
            "perf_label": final_agg["final_label"],
            "flagged": final_agg["flagged"],
            "votes_count": len(votes)
        })
        
        print(f"Processed {idx+1}/{len(data)} - Spend: ${current_spend:.4f}")

    print(f"\nPipeline finished. Total Spend: ${current_spend:.4f}")
    print(f"Escalated to Stage 2: {stage2_count} / {len(data)}")
    
    # Simple reporting
    flagged = [r for r in results if r["flagged"]]
    print(f"Total Flagged (Disputed labels): {len(flagged)}")

if __name__ == "__main__":
    main()
