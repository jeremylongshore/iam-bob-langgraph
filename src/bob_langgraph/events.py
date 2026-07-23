"""Versioned Cartographer events with hash chain."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

EVENT_VERSION = "1.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(
    name: str,
    *,
    run_id: str,
    agent_id: str,
    correlation_id: str,
    causation_id: str,
    source_authority: str,
    disclosure_tier: str,
    payload: dict[str, Any],
    previous_hash: str,
) -> dict[str, Any]:
    body = {
        "event_id": str(uuid.uuid4()),
        "event_name": name,
        "event_version": EVENT_VERSION,
        "run_id": run_id,
        "agent_identity": agent_id,
        "correlation_id": correlation_id,
        "causation_id": causation_id,
        "timestamp": _now(),
        "source_authority": source_authority,
        "disclosure_tier": disclosure_tier,
        "payload": payload,
        "previous_event_hash": previous_hash,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["content_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    return body


def verify_chain(events: list[dict[str, Any]]) -> bool:
    prev = ""
    for e in events:
        if e.get("previous_event_hash", "") != prev:
            return False
        copy = {k: v for k, v in e.items() if k != "content_hash"}
        canonical = json.dumps(copy, sort_keys=True, separators=(",", ":"))
        if hashlib.sha256(canonical.encode()).hexdigest() != e.get("content_hash"):
            return False
        prev = e["content_hash"]
    return True
