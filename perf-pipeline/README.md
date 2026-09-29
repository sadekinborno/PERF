# PERF Pipeline

This is the Prompt Ensemble Re-annotation Framework (PERF) pipeline, built for NLP benchmark auditing.

## Features
- **Two-Stage Cascade**: Runs cheap zero-shot evaluation first. Only escalates to expensive Chain-of-Thought and Rationale-Critique strategies if the initial ensemble disagrees or conflicts with the gold label.
- **Cost Controls**: Built-in `--estimate-cost` flag and hard caps via `config.yaml` to ensure API usage stays within student budgets.
- **Confidence Voting**: Aggregates output from multiple LLMs across multiple strategies to flag disputed dataset labels.

## Setup
1. `pip install -r requirements.txt`
2. Export your API keys:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   export GEMINI_API_KEY="AIzaSy..."
   ```
3. Prepare a CSV/JSON dataset with `text` and `label` columns/keys.

## Usage
To estimate cost:
`python run.py --dataset data/isarcasm.csv --labels "sarcastic,non-sarcastic" --estimate-cost`

To run:
`python run.py --dataset data/isarcasm.csv --labels "sarcastic,non-sarcastic" --confirm`
