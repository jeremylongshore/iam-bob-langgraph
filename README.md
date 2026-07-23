# iam-bob-langgraph

**Intent Agent Model (IAM) V3** — LangGraph runtime.

## Status

Vertical slice implemented: **Estate Cartographer** (read Intent OS authorities → proposals → optional graph projection → evidence chain).

Not a general-purpose agent framework.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install -r requirements.txt  # if present
```

## Commands

```bash
bob-langgraph doctor
bob-langgraph cartographer plan
bob-langgraph cartographer run                  # dry-run default
bob-langgraph cartographer run --apply --approve-all-machine
bob-langgraph cartographer status --run-id …
```

## Governance

May: read authorities, propose relationships, rebuild disposable graph, verify, emit receipts.  
May **not** without approval: declare human owners, expand allowlists, write GitHub/Plane/Beads, promote to Big Brain.

## Dependency

```
bob-langgraph → intent-os estate-graph CLI → LadybugDB
```
