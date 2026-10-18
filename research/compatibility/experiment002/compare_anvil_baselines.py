"""Finite negative/positive controls, identical fee predicates and signed limits."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from anvil_candidate import ROOT, profile
from candidate_regressions import original_probe
from investigate_fee_receipts import collect


def compare():
    old = collect(2)
    corrected = collect(2, candidate=True)
    if Counter(r["classification"] for r in old["results"]) != {
        "reconciled":12, "BLOCKED: contradictory RPC fee evidence":8, "not included":2}:
        raise AssertionError("old negative-control behavior changed")
    if Counter(r["classification"] for r in corrected["results"]) != {"reconciled":20,"not included":2}:
        raise AssertionError("candidate strict compatibility gate failed")
    for original, fixed in zip(old["results"], corrected["results"]):
        for field in ("case","repeat","requestedBaseFee","requestedPriorityFee"):
            if original[field] != fixed[field]:
                raise AssertionError("fee matrix inputs differ")
    command = [sys.executable, str(Path(__file__).with_name("check_anvil_fee_receipt.py"))]
    control = subprocess.run(command, capture_output=True, text=True, timeout=20)
    if control.returncode != 2:
        raise AssertionError("original strict negative control did not block")
    original = json.loads(control.stdout)
    if not original["contradiction"] or not original["actualFeeWithinReservation"]:
        raise AssertionError("original blocker/fee-bound evidence changed")
    fixed = original_probe()
    return {"decision":"PASS: bounded local infrastructure compatibility only",
        "candidateCommit":profile()[0]["commit"], "hardfork":"cancun",
        "oldBaseline":old,"correctedCandidate":corrected,
        "originalReproducer":{"oldExitCode":control.returncode,"old":original,"candidate":fixed}}


if __name__ == "__main__":
    print(json.dumps(compare(),sort_keys=True,indent=2))
