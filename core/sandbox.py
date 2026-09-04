import docker, base64, json
from schema.target import TargetRecord
from pydantic import ValidationError

client = docker.from_env()
SANDBOX_TIMEOUT_SECONDS = 10

def run_in_sandbox(generated_code: str, raw_sample: dict) -> dict:
    harness = (
        "import json, sys, traceback\n\n"
        + generated_code
        + "\n\n"
        + "raw = json.loads('''" + json.dumps(raw_sample) + "''')\n"
        + "try:\n"
        + "    result = extract(raw)\n"
        + "    print(json.dumps(result))\n"
        + "except Exception as e:\n"
        + "    print(json.dumps({\"__sandbox_error__\": str(e), \"__stack_trace__\": traceback.format_exc()}))\n"
        + "    sys.exit(1)\n"
    )

    encoded = base64.b64encode(harness.encode("utf-8")).decode("ascii")
    bootstrap = f"import base64; exec(base64.b64decode('{encoded}').decode('utf-8'))"

    container = None
    try:
        container = client.containers.run(
            "python:3.11-slim",
            command=["python", "-c", bootstrap],
            network_disabled=True,
            mem_limit="256m",
            nano_cpus=int(0.5 * 1e9),
            pids_limit=64,
            read_only=True,
            user="nobody",
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            detach=True,
        )
        exit_code = container.wait(timeout=SANDBOX_TIMEOUT_SECONDS)["StatusCode"]
        logs = container.logs().decode("utf-8", errors="replace")
    except Exception as e:
        return {"passed": False, "reason": f"sandbox_execution_error: {e}", "stack_trace": None}
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass

    if exit_code != 0:
        try:
            error_data = json.loads(logs.strip())
            return {
                "passed": False,
                "reason": error_data.get("__sandbox_error__", "unknown error"),
                "stack_trace": error_data.get("__stack_trace__", logs.strip()),
            }
        except json.JSONDecodeError:
            return {"passed": False, "reason": logs.strip(), "stack_trace": logs.strip()}

    try:
        records = json.loads(logs.strip())
    except json.JSONDecodeError:
        return {"passed": False, "reason": f"non_json_output: {logs}", "stack_trace": None}

    try:
        for r in records:
            TargetRecord.model_validate(r)
    except ValidationError as e:
        return {"passed": False, "reason": f"schema_validation_failed: {e}", "stack_trace": None}

    return {"passed": True, "records": records}