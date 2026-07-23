"""Estate Cartographer — LangGraph workflow (deterministic path, no model required)."""

from __future__ import annotations

import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

from bob_langgraph.events import emit, verify_chain
from bob_langgraph.state import CartographerState, IllegalTransition, transition


AGENT_ID = "iam-bob-langgraph/estate-cartographer"


def _append(state: CartographerState, name: str, payload: dict[str, Any]) -> CartographerState:
    events = list(state.get("events") or [])
    prev = state.get("previous_event_hash") or ""
    ev = emit(
        name,
        run_id=state["run_id"],
        agent_id=AGENT_ID,
        correlation_id=state["run_id"],
        causation_id=events[-1]["event_id"] if events else state["run_id"],
        source_authority="intent-os",
        disclosure_tier="internal",
        payload=payload,
        previous_hash=prev,
    )
    events.append(ev)
    return {**state, "events": events, "previous_event_hash": ev["content_hash"]}


def node_collect(state: CartographerState) -> CartographerState:
    phase = state["phase"]
    if phase != "collecting":
        phase = transition(phase, "collecting")
    s = {**state, "phase": phase}
    root = Path(state["intent_os_root"])
    inv = root / "ops/inventory/estate-inventory.json"
    if not inv.exists():
        s = {**s, "phase": transition("collecting", "failed"), "error": "missing inventory"}
        return _append(s, "CartographerRunFailed", {"error": s["error"]})
    s = _append(s, "SourceCollectionCompleted", {"sources": [str(inv)]})
    return s


def node_validate(state: CartographerState) -> CartographerState:
    if state.get("phase") == "failed":
        return state
    s = {**state, "phase": transition(state["phase"], "validating")}
    # Detect human-owned / disputed heuristics: missing owners → proposals
    proposals = []
    disputes = []
    root = Path(state["intent_os_root"])
    # Use estate-graph validate if present
    cli = root / "ops/estate-graph/cli.py"
    venv_py = root / "ops/estate-graph/.venv/bin/python"
    if cli.exists() and venv_py.exists():
        proc = subprocess.run(
            [str(venv_py), str(cli), "validate"],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        if proc.returncode != 0:
            s = {
                **s,
                "phase": transition("validating", "failed"),
                "error": proc.stderr or proc.stdout,
            }
            return _append(s, "CartographerRunFailed", {"error": s["error"][:500]})
    # Always emit a machine-observed proposal for repos without human confirmation flag
    proposals.append(
        {
            "kind": "relationship",
            "type": "OWNS",
            "note": "machine-observed ownership candidate — human approval required to declare",
            "requires_approval": True,
        }
    )
    s = {**s, "proposals": proposals, "disputes": disputes}
    s = _append(s, "RelationshipProposalCreated", {"count": len(proposals)})
    if any(p.get("requires_approval") for p in proposals) and not state.get("approvals"):
        s = {**s, "phase": transition("validating", "awaiting_approval")}
        s = _append(s, "RelationshipDisputeDetected", {"awaiting": True})
        return s
    s = {**s, "phase": transition("validating", "projecting")}
    return s


def node_project(state: CartographerState) -> CartographerState:
    if state.get("phase") in ("failed", "refused", "awaiting_approval"):
        return state
    if state["phase"] != "projecting":
        try:
            s = {**state, "phase": transition(state["phase"], "projecting")}
        except IllegalTransition:
            return state
    else:
        s = state
    s = _append(s, "GraphProjectionStarted", {"dry_run": s.get("dry_run", True)})
    if s.get("dry_run", True):
        s = {
            **s,
            "projection_meta": {"dry_run": True, "note": "no apply; pass dry_run=false to project"},
            "phase": transition("projecting", "verifying"),
        }
        s = _append(s, "GraphProjectionCompleted", s["projection_meta"])
        return s
    root = Path(s["intent_os_root"])
    venv_py = root / "ops/estate-graph/.venv/bin/python"
    cli = root / "ops/estate-graph/cli.py"
    if not (venv_py.exists() and cli.exists()):
        s = {
            **s,
            "phase": transition("projecting", "failed"),
            "error": "estate-graph CLI missing",
        }
        return _append(s, "CartographerRunFailed", {"error": s["error"]})
    proc = subprocess.run(
        [str(venv_py), str(cli), "rebuild"],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    if proc.returncode != 0:
        s = {
            **s,
            "phase": transition("projecting", "failed"),
            "error": proc.stderr or "rebuild failed",
        }
        return _append(s, "CartographerRunFailed", {"error": s["error"][:500]})
    try:
        meta = json.loads(proc.stdout)
    except json.JSONDecodeError:
        meta = {"raw": proc.stdout[:500]}
    s = {
        **s,
        "projection_meta": meta,
        "phase": transition("projecting", "verifying"),
    }
    return _append(s, "GraphProjectionCompleted", {"meta_keys": list(meta.keys())})


def node_verify(state: CartographerState) -> CartographerState:
    if state.get("phase") != "verifying":
        return state
    s = state
    ok_chain = verify_chain(s.get("events") or [])
    root = Path(s["intent_os_root"])
    venv_py = root / "ops/estate-graph/.venv/bin/python"
    cli = root / "ops/estate-graph/cli.py"
    q_ok = True
    q_out = {}
    if venv_py.exists() and cli.exists() and not s.get("dry_run", True):
        proc = subprocess.run(
            [str(venv_py), str(cli), "query", "agents-authorized-tool", "--tool", ""],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        q_ok = proc.returncode == 0
        try:
            q_out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            q_out = {"raw": proc.stdout[:300]}
    verification = {
        "event_chain_ok": ok_chain,
        "query_ok": q_ok,
        "query": q_out,
    }
    s = {**s, "verification": verification}
    if not ok_chain or not q_ok:
        s = {
            **s,
            "phase": transition("verifying", "failed"),
            "error": "verification failed",
        }
        s = _append(s, "GraphVerificationFailed", verification)
        return s
    s = {**s, "phase": transition("verifying", "completed")}
    s = _append(s, "GraphVerificationCompleted", verification)
    s = _append(s, "CartographerRunCompleted", {"run_id": s["run_id"]})
    return s


def run_cartographer(
    *,
    intent_os_root: str,
    dry_run: bool = True,
    approvals: list[dict] | None = None,
) -> CartographerState:
    run_id = str(uuid.uuid4())
    state: CartographerState = {
        "run_id": run_id,
        "phase": "requested",
        "dry_run": dry_run,
        "intent_os_root": intent_os_root,
        "events": [],
        "proposals": [],
        "disputes": [],
        "approvals": approvals or [],
        "previous_event_hash": "",
    }
    state = _append(state, "PortfolioGraphRefreshRequested", {"dry_run": dry_run})
    state = {**state, "phase": transition("requested", "collecting")}
    state = node_collect(state)
    if state["phase"] == "failed":
        return state
    state = node_validate(state)
    if state["phase"] == "awaiting_approval":
        if approvals:
            state = {
                **state,
                "phase": transition("awaiting_approval", "projecting"),
                "approvals": approvals,
            }
            state = _append(state, "RelationshipApprovalRecorded", {"count": len(approvals)})
        else:
            state = _append(
                state,
                "CartographerRunDegraded",
                {"reason": "awaiting human approval for proposals"},
            )
            state = {**state, "phase": "degraded"}
            return state
    if state["phase"] in ("projecting", "validating"):
        if state["phase"] == "validating":
            state = {**state, "phase": transition("validating", "projecting")}
        state = node_project(state)
    if state["phase"] == "verifying":
        state = node_verify(state)
    return state
