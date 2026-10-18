"""Run unchanged Experiment 001 assertions using only the verified candidate node.

Explicit test-only selection, not a default-tool/PATH/production guard change.
Original fixture's hardcoded Foundry metadata remains historical; this report
records the actual candidate identity separately. No Experiment 002 agents.
"""
import contextlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from anvil_candidate import ROOT, candidate_path, profile

sys.path.insert(0, str(ROOT / "sdk/python"))


@contextlib.contextmanager
def selected_candidate():
    binary = candidate_path()  # Pin/hash check before every execution override.
    original = subprocess.Popen

    def launch(command, *args, **kwargs):
        if isinstance(command, (list, tuple)) and command[0] == binary and "--version" not in command:
            command = list(command) + ["--hardfork", "cancun"]
        return original(command, *args, **kwargs)

    with patch.dict(os.environ, {"PYTHONPATH": str(ROOT / "sdk/python")}), patch("genesis_experiment.runner.anvil_path", return_value=binary), patch("subprocess.Popen", side_effect=launch):
        yield binary


def original_probe():
    import check_anvil_fee_receipt as original
    with selected_candidate() as binary, patch.object(original, "anvil_path", return_value=binary):
        evidence = original.probe()
    if evidence["contradiction"] or evidence["actualBalanceDebit"] != evidence["reportedFee"]:
        raise AssertionError("original strict fee gate failed on candidate")
    return evidence


def run():
    from genesis_experiment.runner import run as control
    with selected_candidate():
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests/python"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful() or result.testsRun != 54:
            raise AssertionError("unchanged Python regression gate failed")
        controls = [control("success"), control("requester_refusal")]
    if [c["outcome"] for c in controls] != ["settled", "refunded"] or not all(c["childrenStopped"] for c in controls):
        raise AssertionError("control settlement/refund/cleanup failed")
    return {
        "candidateCommit":profile()[0]["commit"], "hardfork":"cancun", "pythonTests":result.testsRun,
        "originalStrictProbe":original_probe(),
        "experiment001Controls":[{"scenario":c["scenario"], "outcome":c["outcome"],
            "childrenStopped":c["childrenStopped"], "fixtureDeclaredFoundryCommit":c["versions"]["foundryCommit"],
            "actualNodeCommit":profile()[0]["commit"]} for c in controls],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
