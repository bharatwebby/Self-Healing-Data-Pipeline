import ast

BANNED_IMPORTS = {"os", "sys", "subprocess", "socket", "requests", "urllib",
                   "shutil", "ctypes", "pathlib"}
BANNED_CALLS = {"eval", "exec", "compile", "open", "__import__"}

def static_scan(code: str) -> list[str]:
    """Returns a list of violations found. Empty list = safe to proceed."""
    violations = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"syntax_error: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BANNED_IMPORTS:
                    violations.append(f"banned import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in BANNED_IMPORTS:
                violations.append(f"banned import: {node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BANNED_CALLS:
                violations.append(f"banned call: {node.func.id}")
    return violations