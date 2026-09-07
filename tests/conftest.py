import os

# agents/analyzer.py and agents/coder.py construct an Anthropic client at
# import time. Unit tests mock out the actual .create() call, so no real
# key is ever used — but the client constructor still wants *something*
# present, and CI won't have a real key. This keeps imports working
# everywhere without requiring secrets for pure unit tests.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-unit-tests")
