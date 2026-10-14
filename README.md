# iam-bob-langgraph

<!-- intent-select-partner:start -->
<p><a href="https://intentsolutions.io/"><img src="https://raw.githubusercontent.com/intent-solutions-io/.github/b82af5d3e7951d85e39ea9e65cc24ee8278722a7/assets/brand/claude-select-partner.svg" alt="Intent Solutions: Claude Partner Network Select Services Partner" width="300" height="95" /></a></p>

Intent Solutions is a Claude Partner Network Select Services Partner.
<!-- intent-select-partner:end -->

**Intent Agent Model (IAM) V3** — LangGraph runtime.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

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
