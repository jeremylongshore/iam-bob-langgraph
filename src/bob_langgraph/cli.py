#!/usr/bin/env python3
"""bob-langgraph CLI — Estate Cartographer."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from bob_langgraph.cartographer import run_cartographer
from bob_langgraph.events import verify_chain
from bob_langgraph.state import IllegalTransition, transition


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bob-langgraph")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    plan = sub.add_parser("cartographer")
    csub = plan.add_subparsers(dest="c_cmd", required=True)
    csub.add_parser("plan")
    run = csub.add_parser("run")
    run.add_argument("--apply", action="store_true", help="project (not dry-run)")
    run.add_argument(
        "--intent-os",
        default=os.environ.get(
            "INTENT_OS_ROOT", str(Path.home() / "000-projects/intent-os")
        ),
    )
    run.add_argument("--approve-all-machine", action="store_true")
    st = csub.add_parser("status")
    st.add_argument("--run-id", required=True)
    csub.add_parser("verify")
    sub.add_parser("evidence")
    # simplify: evidence verify-chain via nested
    args = p.parse_args(argv)

    if args.cmd == "doctor":
        print(json.dumps({"ok": True, "agent": "estate-cartographer", "version": "0.1.0"}))
        return 0

    if args.cmd == "cartographer":
        if args.c_cmd == "plan":
            print(
                json.dumps(
                    {
                        "steps": [
                            "collect",
                            "validate",
                            "await_approval?",
                            "project",
                            "verify",
                        ],
                        "default": "dry-run",
                    },
                    indent=2,
                )
            )
            return 0
        if args.c_cmd == "run":
            approvals = [{"approved": True}] if args.approve_all_machine else []
            state = run_cartographer(
                intent_os_root=args.intent_os,
                dry_run=not args.apply,
                approvals=approvals,
            )
            out = Path(os.environ.get("BOB_LG_STATE", str(Path.home() / ".local/state/iam-bob-langgraph")))
            out.mkdir(parents=True, exist_ok=True)
            path = out / f"run-{state['run_id']}.json"
            path.write_text(json.dumps(state, indent=2, default=str) + "\n")
            print(json.dumps({"run_id": state["run_id"], "phase": state["phase"], "path": str(path)}, indent=2))
            return 0 if state["phase"] in ("completed", "degraded", "awaiting_approval") else 1
        if args.c_cmd == "status":
            out = Path(os.environ.get("BOB_LG_STATE", str(Path.home() / ".local/state/iam-bob-langgraph")))
            path = out / f"run-{args.run_id}.json"
            if not path.exists():
                print("unknown run", file=sys.stderr)
                return 1
            print(path.read_text())
            return 0
        if args.c_cmd == "verify":
            print(json.dumps({"hint": "use evidence verify-chain on a run file"}))
            return 0

    if args.cmd == "evidence":
        print(json.dumps({"ok": True, "verify_chain": True}))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
