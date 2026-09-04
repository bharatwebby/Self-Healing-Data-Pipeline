import json
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")  # no display needed, just save straight to a file
import matplotlib.pyplot as plt

LOG_PATH = "logs/token_usage.jsonl"
OUTPUT_PATH = "logs/token_usage_graph.png"

def load_usage():
    entries = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

def main():
    entries = load_usage()
    if not entries:
        print("No usage data found in", LOG_PATH)
        return

    totals = defaultdict(lambda: {"input": 0, "output": 0})
    for e in entries:
        totals[e["agent"]]["input"] += e["input_tokens"]
        totals[e["agent"]]["output"] += e["output_tokens"]

    agents = list(totals.keys())
    input_vals = [totals[a]["input"] for a in agents]
    output_vals = [totals[a]["output"] for a in agents]

    x = range(len(agents))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([i - width / 2 for i in x], input_vals, width, label="Input tokens")
    ax.bar([i + width / 2 for i in x], output_vals, width, label="Output tokens")
    ax.set_xticks(list(x))
    ax.set_xticklabels(agents)
    ax.set_ylabel("Tokens")
    ax.set_title("Token Usage by Agent (cumulative, this project's runs)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH)
    print(f"Saved graph to {OUTPUT_PATH}")
    print("Totals:", dict(totals))

if __name__ == "__main__":
    main()