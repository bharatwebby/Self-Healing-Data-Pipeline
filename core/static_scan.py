import ast

BANNED_IMPORTS = {"os", "sys", "subprocess", "socket", "requests", "urllib",
                   "shutil", "ctypes", "pathlib", "importlib", "pickle",
                   "marshal", "code", "codeop", "pty", "platform", "resource",
                   "multiprocessing", "threading", "asyncio"}

# Anything that can execute arbitrary code, touch the filesystem/OS, or —
# critically — retrieve a banned name indirectly (getattr/setattr/vars/
# globals/locals are how `getattr(__builtins__, '__import__')('os')`-style
# bypasses smuggle a banned capability past a scanner that only checks
# literal `import os` / `__import__(...)` spelling).
BANNED_CALLS = {
    "eval", "exec", "compile", "open", "__import__",
    "getattr", "setattr", "delattr", "vars", "globals", "locals",
    "input", "breakpoint", "help", "memoryview",
}

# Dunder attributes are the standard gadget for climbing the Python object
# graph to reach dangerous machinery without ever writing "import os"
# (e.g. `().__class__.__bases__[0].__subclasses__()`). Rather than
# maintain a denylist of every dangerous dunder, we ban dunder attribute
# access entirely — generated `extract(raw)` functions restricted to
# json/re/datetime/xml.etree.ElementTree never legitimately need one.

def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")

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
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
                violations.append(f"banned call: {node.func.id}")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in BANNED_CALLS:
                violations.append(f"banned call via attribute: {node.func.attr}")
        elif isinstance(node, ast.Attribute) and _is_dunder(node.attr):
            violations.append(f"banned dunder attribute access: {node.attr}")
        elif isinstance(node, ast.Name) and _is_dunder(node.id):
            violations.append(f"banned dunder name reference: {node.id}")

    return violations