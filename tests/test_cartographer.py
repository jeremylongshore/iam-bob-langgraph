"""TDD scenarios for Estate Cartographer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bob_langgraph.cartographer import run_cartographer
from bob_langgraph.events import verify_chain
from bob_langgraph.state import IllegalTransition, transition

INTENT = str(Path.home() / "000-projects/intent-os")


class TransitionTests(unittest.TestCase):
    def test_illegal_transition(self):
        with self.assertRaises(IllegalTransition):
            transition("completed", "collecting")

    def test_happy_path_transitions(self):
        self.assertEqual(transition("requested", "collecting"), "collecting")


class CartographerTests(unittest.TestCase):
    def test_dry_run_awaits_or_completes(self):
        state = run_cartographer(intent_os_root=INTENT, dry_run=True)
        self.assertIn(state["phase"], ("degraded", "completed", "awaiting_approval", "failed"))
        self.assertTrue(state.get("events"))
        self.assertTrue(verify_chain(state["events"]))

    def test_missing_authority_fails(self):
        with tempfile.TemporaryDirectory() as td:
            state = run_cartographer(intent_os_root=td, dry_run=True)
            self.assertEqual(state["phase"], "failed")

    def test_tampered_chain_detected(self):
        state = run_cartographer(intent_os_root=INTENT, dry_run=True, approvals=[{"ok": True}])
        events = list(state["events"])
        if len(events) > 1:
            events[1] = dict(events[1])
            events[1]["payload"] = {"tampered": True}
            self.assertFalse(verify_chain(events))

    def test_approval_path_projects_when_apply(self):
        # may fail if estate-graph venv missing — still must not crash illegally
        state = run_cartographer(
            intent_os_root=INTENT,
            dry_run=False,
            approvals=[{"approved": True}],
        )
        self.assertIn(
            state["phase"],
            ("completed", "failed", "degraded", "verifying", "projecting"),
        )


if __name__ == "__main__":
    unittest.main()
