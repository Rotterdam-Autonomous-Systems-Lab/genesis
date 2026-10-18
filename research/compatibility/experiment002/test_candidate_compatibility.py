"""Same fee oracle/cases on a separately verified candidate; no agent implementation."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import anvil_candidate
from anvil_candidate import ROOT, candidate_path, profile
from candidate_regressions import original_probe
from fee_evidence import EvidenceContradiction, require_reconciled
from investigate_fee_receipts import CASES, collect


class CandidateIntegrityTests(unittest.TestCase):
    def test_wrong_binary_hash_rejected_before_execution(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "internal") as directory:
            file = Path(directory) / "anvil"
            file.write_bytes(b"unverified bytes")
            data, target = profile()
            data = {**data, "installDirectory": str(Path(directory).relative_to(ROOT))}
            with patch.object(anvil_candidate, "profile", return_value=(data, target)), patch.object(anvil_candidate.subprocess, "check_output") as execute:
                with self.assertRaises(RuntimeError):
                    candidate_path()
                execute.assert_not_called()

    def test_wrong_reported_commit_rejected(self):
        with patch.object(anvil_candidate.subprocess, "check_output", return_value="anvil wrong source"):
            with self.assertRaises(RuntimeError):
                candidate_path()

    def test_unknown_platform_fails_closed(self):
        with patch.object(anvil_candidate.platform, "system", return_value="Unsupported"):
            with self.assertRaises(RuntimeError):
                profile()


class CandidateFeeCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = collect(2, candidate=True)
        cls.results = cls.evidence["results"]

    def test_identical_cases_all_included_fees_reconcile(self):
        self.assertEqual(len(self.results), 2 * len(CASES))
        self.assertEqual(sum(r["classification"] == "reconciled" for r in self.results), 20)
        self.assertEqual(sum(r["classification"] == "not included" for r in self.results), 2)
        for result in self.results:
            if result["receipt"] is not None:
                require_reconciled(result)  # Identical strict oracle, not a candidate-specific substitute.

    def test_formerly_bad_cases_pass_without_fee_changes(self):
        cases = {"above-tip-clamp", "original-inclusion-base", "at-fee-cap", "revert-clamped"}
        for r in self.results:
            if r["case"] not in cases:
                continue
            self.assertEqual(r["classification"], "reconciled")
            self.assertEqual(int(r["transaction"]["maxFeePerGas"], 16), 3_000_000_000)
            self.assertEqual(int(r["transaction"]["maxPriorityFeePerGas"], 16), 1_000_000_000)
            self.assertEqual(int(r["transaction"]["gas"], 16), 2_000_000)
            self.assertEqual(r["measurements"]["receiptOverstatement"], 0)

    def test_mutated_candidate_receipts_still_reject(self):
        good = next(r for r in self.results if r["case"] == "original-inclusion-base")
        bad = copy.deepcopy(good)
        bad["receipt"]["effectiveGasPrice"] = hex(3_625_000_000)
        with self.assertRaises(EvidenceContradiction):
            require_reconciled(bad)
        bad = copy.deepcopy(good)
        bad["balanceAfter"] = bad["balanceBefore"]
        with self.assertRaises(EvidenceContradiction):
            require_reconciled(bad)

    def test_repeats_have_independent_identities_and_same_accounting(self):
        for case in CASES:
            first, second = [r for r in self.results if r["case"] == case[0]]
            if first["receipt"] is not None:
                self.assertNotEqual(first["transaction"]["from"], second["transaction"]["from"])
                self.assertEqual(first["measurements"], second["measurements"])

    def test_above_cap_is_not_included_and_all_children_stop(self):
        for r in self.results:
            self.assertTrue(r["childrenStopped"])
            if r["case"] == "above-fee-cap":
                self.assertEqual(r["balanceBefore"], r["balanceAfter"])
                self.assertEqual(r["nonceAfter"], "0x0")
                self.assertIsNone(r["receipt"])

    def test_original_reproducer_passes_unchanged_checks(self):
        result = original_probe()
        self.assertFalse(result["contradiction"])
        self.assertTrue(result["actualFeeWithinReservation"])
        self.assertEqual(result["receiptEffectiveGasPrice"], 3_000_000_000)
        self.assertEqual(result["actualBalanceDebit"], result["reportedFee"])
        self.assertLessEqual(result["deploymentGasUsed"], 2_000_000)


if __name__ == "__main__":
    unittest.main()
