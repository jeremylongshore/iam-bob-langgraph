"""Typed Cartographer state + illegal transition enforcement."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

StateName = Literal[
    "requested",
    "collecting",
    "validating",
    "awaiting_approval",
    "projecting",
    "verifying",
    "completed",
    "degraded",
    "refused",
    "failed",
]

ALLOWED: dict[str, frozenset[str]] = {
    "requested": frozenset({"collecting", "refused", "failed"}),
    "collecting": frozenset({"validating", "degraded", "failed", "refused"}),
    "validating": frozenset(
        {"awaiting_approval", "projecting", "degraded", "failed", "refused"}
    ),
    "awaiting_approval": frozenset({"projecting", "refused", "failed", "degraded"}),
    "projecting": frozenset({"verifying", "failed", "degraded"}),
    "verifying": frozenset({"completed", "failed", "degraded"}),
    "completed": frozenset(),
    "degraded": frozenset({"completed", "failed", "refused"}),
    "refused": frozenset(),
    "failed": frozenset(),
}


class IllegalTransition(ValueError):
    pass


def transition(cur: str, nxt: str) -> str:
    if nxt not in ALLOWED.get(cur, frozenset()):
        raise IllegalTransition(f"{cur!r} → {nxt!r}")
    return nxt


class CartographerState(TypedDict, total=False):
    run_id: str
    phase: StateName
    dry_run: bool
    intent_os_root: str
    events: list[dict[str, Any]]
    proposals: list[dict[str, Any]]
    disputes: list[dict[str, Any]]
    approvals: list[dict[str, Any]]
    projection_meta: dict[str, Any]
    verification: dict[str, Any]
    error: str
    previous_event_hash: str
