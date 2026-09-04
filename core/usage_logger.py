import json
from datetime import datetime

USAGE_LOG_PATH = "logs/token_usage.jsonl"

def log_usage(agent_name: str, usage):
    """Appends one line of token usage data per LLM call.
    usage is the .usage object returned by the Anthropic SDK response."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    }
    with open(USAGE_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")