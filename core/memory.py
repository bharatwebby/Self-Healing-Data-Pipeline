import ast, difflib

def ast_diff(old_code: str, new_code: str) -> str:
    """Compact structural diff between two code versions — used instead of
    resending full code on retries, keeping context usage small and focused."""
    try:
        old_dump = ast.dump(ast.parse(old_code), indent=2)
    except Exception:
        old_dump = "<unparseable>"
    try:
        new_dump = ast.dump(ast.parse(new_code), indent=2)
    except Exception:
        new_dump = "<unparseable>"

    diff_lines = difflib.unified_diff(old_dump.splitlines(), new_dump.splitlines(), lineterm="")
    return "\n".join(diff_lines)[:2000]