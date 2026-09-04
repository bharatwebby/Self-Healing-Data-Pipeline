import os, json
from anthropic import Anthropic
from dotenv import load_dotenv
from core.usage_logger import log_usage

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CODER_SYSTEM_PROMPT = """You are a Python code generator for a self-healing data pipeline.

You will be given a field_mapping describing how to extract data from a new
raw shape, plus a summary of what changed.

STRICT RULES for the code you generate:
1. You must define EXACTLY ONE function: def extract(raw):
2. It must return a list of dicts, each with EXACTLY these keys:
   external_id (int), display_name (str), amount_cents (int)
3. You may ONLY use these imports if needed: json, re, datetime, xml.etree.ElementTree
4. NEVER import or use: os, sys, subprocess, socket, requests, urllib, shutil,
   ctypes, eval, exec, compile, open, __import__
5. Handle the shape described in field_mapping precisely.
6. If PREVIOUS_ATTEMPT_FEEDBACK is provided, it describes what went wrong last
   time — fix that specific issue, don't rewrite everything from scratch.

Respond with ONLY the raw Python code. No markdown fences, no explanation,
no comments about what you're doing outside the code itself.
"""

def generate_extractor_code(field_mapping: list, structural_change_summary: str,
                             previous_attempt_feedback: str = None) -> str:
    user_message = f"""STRUCTURAL_CHANGE_SUMMARY:
{structural_change_summary}

FIELD_MAPPING:
{json.dumps(field_mapping, indent=2)}
"""
    if previous_attempt_feedback:
        user_message += f"\nPREVIOUS_ATTEMPT_FEEDBACK:\n{previous_attempt_feedback}\n"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=CODER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    log_usage("coder", response.usage)

    text = response.content[0].text.strip()
    return strip_markdown_fences(text)

def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()