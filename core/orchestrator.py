import time, sys
from core.monitor import run_once
from core.deployer import deploy, get_active_version
from agents.analyzer import analyze_incident
from agents.coder import generate_extractor_code
from core.static_scan import static_scan
from core.sandbox import run_in_sandbox
from core.memory import ast_diff

MAX_RETRIES = 5
POLL_INTERVAL_SECONDS = 5

def load_code_for_version(version: int) -> str:
    with open(f"extractors/extractor_v{version}.py") as f:
        return f.read()

def heal(raw, previous_code: str, error_message: str) -> bool:
    attempt_log = []
    current_code = previous_code
    current_error = error_message

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- Healing attempt {attempt}/{MAX_RETRIES} ---")

        feedback = None
        if attempt_log:
            last = attempt_log[-1]
            feedback = (
                f"Your previous attempt failed. AST diff vs the attempt before it:\n"
                f"{last['diff']}\nError it produced:\n{last['error']}"
            )

        print("  Semantic Analyzer Agent thinking...")
        analysis = analyze_incident(raw, current_code, current_error)
        print("   ->", analysis["structural_change_summary"])

        print("  Coder Agent writing new extractor...")
        new_code = generate_extractor_code(
            analysis["field_mapping"], analysis["structural_change_summary"],
            previous_attempt_feedback=feedback,
        )

        print("  Running static security scan...")
        violations = static_scan(new_code)
        if violations:
            print("   REJECTED:", violations)
            diff = ast_diff(current_code, new_code)
            attempt_log.append({"diff": diff, "error": f"static_scan_violations: {violations}"})
            current_code, current_error = new_code, f"static_scan_violations: {violations}"
            continue

        print("  Running in isolated Docker sandbox...")
        verdict = run_in_sandbox(new_code, raw)

        if verdict["passed"]:
            version = deploy(new_code)
            print(f"   PASSED. Deployed as extractor_v{version}.")
            return True

        print("   FAILED sandbox check:", verdict["reason"])
        if verdict.get("stack_trace"):
            print("   Full stack trace:")
            print(verdict["stack_trace"])

        diff = ast_diff(current_code, new_code)
        attempt_log.append({"diff": diff, "error": verdict["reason"]})
        current_code, current_error = new_code, verdict["reason"]

    print(f"\n!!! ESCALATION: exhausted {MAX_RETRIES} attempts. Human needed. !!!")
    return False

def run_forever():
    print(f"Orchestrator running. Polling every {POLL_INTERVAL_SECONDS}s. Ctrl+C to stop.\n")
    while True:
        version_before = get_active_version()
        previous_code = load_code_for_version(version_before)

        success, error, raw = run_once()
        if not success:
            print("\n=== INCIDENT DETECTED — starting healing workflow ===")
            healing_start = time.time()
            healed = heal(raw, previous_code, error)
            healing_duration = time.time() - healing_start
            if healed:
                print(f"=== HEALED in {healing_duration:.2f} seconds — resuming normal polling ===\n")
            else:
                print(f"=== ESCALATED after {healing_duration:.2f} seconds — human needed ===\n")

        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_forever()
    except KeyboardInterrupt:
        print("\nOrchestrator stopped.")
        sys.exit(0)