# Autonomous Self-Healing Data Pipeline

An agentic system that detects data-source schema changes, diagnoses them,
generates fixed extraction code, tests it in an isolated Docker sandbox, and
deploys it automatically — no human intervention.

## Architecture

```
Mock Source (flat / nested / paginated XML / malicious)
        │
        ▼
Fetcher (trusted code, resolves pagination before any AI involvement)
        │
        ▼
Active Extractor ──success──▶ SQLite DB (validated against fixed schema)
        │
      failure
        ▼
Orchestrator (state machine, retry budget 5, AST-diff memory)
        ├─▶ Semantic Analyzer Agent — diagnoses the structural change
        ├─▶ Coder Agent — writes a new extract() function
        ├─▶ Static AST Scanner — rejects banned imports/calls
        ├─▶ Docker Sandbox — no network, resource-capped, non-root,
        │      capabilities dropped, returns real stack traces
        └─▶ Deployer — versioned file + atomic pointer swap, hot-reload
```

## Key Design Decisions

- **Pagination lives in trusted code, not the sandbox.** A network-isolated
  sandbox can't follow `next_page` links itself — pagination is resolved by
  the Fetcher before data ever reaches AI-generated code.
- **AST-diff memory, not full code history**, on retries — keeps context
  usage low and retries focused on the specific prior failure.
- **Defense in depth against prompt injection**: untrusted data is
  explicitly labeled as inert in prompts, a static scanner blocks banned
  imports/calls before execution, and the sandbox itself has zero network
  access regardless of what the model does.
- **`.env.example`, not `.env`, is committed** — standard practice, keeps
  the real API key out of a public repo.

## Setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create `.env` from `.env.example` with your own key.

Terminal 1:
```powershell
uvicorn mock_source.main:app --reload --reload-dir mock_source --port 9000
```
Terminal 2:
```powershell
python -m core.orchestrator
```
Terminal 3 — trigger schema changes live:
```powershell
curl.exe -X POST "http://127.0.0.1:9000/admin/mutate?mode=nested"
curl.exe -X POST "http://127.0.0.1:9000/admin/mutate?mode=xml_paginated"
curl.exe -X POST "http://127.0.0.1:9000/admin/mutate?mode=malicious"
```

## Results (live verification run)

| Mutation | Healing time | Attempts | Deployed |
|---|---|---|---|
| Flat → Nested | 14.59s | 1 | v7 |
| Nested → Paginated XML | 8.71s | 1 | v8 |
| XML → Nested (malicious payload) | 18.25s | 2 | v9 |

- Attempt 1 on the third mutation failed the sandbox (`dict` passed where a
  JSON string was expected); attempt 2 diagnosed and fixed it from the AST
  diff alone — real retry recovery, not simulated.
- Prompt-injection payload confirmed neutralized in two independent runs
  (`extractor_v5.py`, `extractor_v9.py`) — no `os`, `subprocess`, or network
  code in either.
- Total cost across this run: ~$0.03 (6,251 input / 1,632 output tokens,
  Claude Sonnet 4.5).

## Proof of Execution

- `logs/live_verification_run.txt` — full raw terminal output
- `logs/stack_trace_proof.txt` — real Python traceback from a sandbox failure
- `logs/prompt_injection_proof.txt` — injection test + generated code
- `logs/token_usage.jsonl` + `logs/token_usage_graph.png` — real API usage
- `pipeline.db` — populated database from live runs
- `extractors/extractor_v1.py` through `v9.py` — full version history
  (rollback available at any point)

## Known Limitations

- Polling-based detection (5s interval), not push-based.
- Retry budget (5) escalates to a human-needed state; not wired to alerting.
- Assumes JSON/XML-like sources; binary protocols aren't covered.
