"""Independent phase-interaction probes; no socket or live-ledger claims."""
import time
import unittest
from unittest.mock import Mock, patch
from web3 import Web3
from genesis_experiment.protocol import Inconclusive
from genesis_experiment002.chain import Chain, Budget, RESERVATION, GAS, FEE, PRIORITY


class PhaseInteractions(unittest.TestCase):
    def client(self):
        chain = Chain.__new__(Chain)
        chain.deadline = time.monotonic() + 60
        chain.halted = False
        chain.pending_hash = None
        chain.funding_intent = None
        chain.budget = Budget("requester")
        chain.principal = 10**12
        chain.intents = []
        chain.receipts = []
        chain.observations = {}
        chain.account = Mock(address="0x" + "11" * 20)
        chain.account.sign_transaction.return_value.raw_transaction = b"synthetic-test-only"
        chain.contract = Mock(address="0x" + "22" * 20)
        chain.w3 = Mock()
        chain.w3.eth.get_block.return_value = {"baseFeePerGas": 1, "timestamp": 10}
        chain.w3.eth.get_balance.return_value = 8 * RESERVATION + chain.principal
        chain.w3.eth.get_transaction_count.return_value = 0
        function = Mock(fn_name="revokeUnused", address=chain.contract.address)
        function._encode_transaction_data.return_value = "0x1234"
        function.build_transaction.side_effect = lambda tx: {
            **tx, "data": "0x1234", "to": chain.contract.address
        }
        return chain, function

    def test_expiry_inside_signing_retains_hash_budget_and_blocks_broadcast(self):
        chain, function = self.client()
        clock = [time.monotonic()]
        signed = chain.account.sign_transaction.return_value

        def slow_sign(tx):
            self.assertEqual((tx["gas"], tx["maxFeePerGas"], tx["maxPriorityFeePerGas"]),
                             (GAS, FEE, PRIORITY))
            clock[0] = chain.deadline
            return signed

        chain.account.sign_transaction.side_effect = slow_sign
        with patch.object(chain, "preflight"), patch("time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaises(Inconclusive):
                chain.transact(function)
        self.assertTrue(chain.halted)
        self.assertEqual(chain.budget.reserved, RESERVATION)
        self.assertEqual(chain.pending_hash, Web3.keccak(signed.raw_transaction))
        chain.w3.eth.send_raw_transaction.assert_not_called()
        # A later clock recovery cannot restore authority or reserve another attempt.
        with patch.object(chain, "preflight"):
            with self.assertRaises(Inconclusive):
                chain.transact(function)
        self.assertEqual(chain.account.sign_transaction.call_count, 1)
        self.assertEqual(chain.budget.used, 1)

    def test_good_record_diagnosis_cannot_clear_existing_latch(self):
        chain, function = self.client()
        chain.halted = True
        chain.w3.eth.get_block.return_value = {"number": 1, "hash": b"anchor"}
        chain.contract.functions.getRecord.return_value.call.return_value = [[], 0, 1, 0]
        self.assertEqual(chain.record(b"agreement")[2], 1)
        self.assertTrue(chain.halted)
        with patch.object(chain, "preflight"):
            with self.assertRaises(Inconclusive):
                chain.transact(function)
        chain.account.sign_transaction.assert_not_called()
        chain.w3.eth.send_raw_transaction.assert_not_called()
        self.assertEqual(chain.budget.used, 0)


    def test_receipt_field_matrix_and_latch_after_good_reread(self):
        fields = {
            "transactionHash": b"h" * 32, "blockHash": b"b" * 32,
            "blockNumber": 1, "transactionIndex": 0, "status": 1,
            "logs": [], "gasUsed": 10, "effectiveGasPrice": 2,
            "from": "0x" + "11" * 20, "to": "0x" + "22" * 20,
            "contractAddress": None, "cumulativeGasUsed": 10,
        }
        for source in ("current", "block"):
            for field, value in fields.items():
                with self.subTest(source=source, field=field):
                    chain, function = self.client()
                    eth = chain.w3.eth
                    digest = fields["transactionHash"]
                    block = {"number": 1, "hash": fields["blockHash"],
                             "parentHash": b"parent", "transactions": [digest],
                             "baseFeePerGas": 1, "timestamp": 10}
                    eth.get_block.side_effect = lambda n: block if n == 1 else {"number": 0, "hash": b"parent"}
                    eth.get_transaction.return_value = {
                        "hash": digest, "blockHash": block["hash"], "blockNumber": 1,
                        "transactionIndex": 0, "from": fields["from"], "to": fields["to"],
                        "maxFeePerGas": 3, "maxPriorityFeePerGas": 1, "type": 2,
                        "chainId": 31337, "gas": 20, "gasPrice": 2, "value": 0,
                    }
                    eth.get_transaction_receipt.return_value = fields
                    eth.get_block_receipts.return_value = [fields]
                    eth.get_balance.side_effect = lambda address, n: 100 if n == 0 else 80
                    chain.canonical_receipt(fields, digest)  # valid independent model
                    bad = dict(fields)
                    bad[field] = (value + 1 if isinstance(value, int) else
                                  ["bad-log"] if isinstance(value, list) else
                                  b"wrong" if isinstance(value, bytes) else "wrong")
                    if source == "current":
                        eth.get_transaction_receipt.return_value = bad
                    else:
                        eth.get_block_receipts.return_value = [bad]
                    with self.assertRaises(Inconclusive):
                        chain.canonical_receipt(fields, digest)
                    self.assertTrue(chain.halted)
                    eth.get_transaction_receipt.return_value = fields
                    eth.get_block_receipts.return_value = [fields]
                    chain.canonical_receipt(fields, digest)  # diagnosis succeeds
                    with patch.object(chain, "preflight"):
                        with self.assertRaises(Inconclusive):
                            chain.transact(function)
                    chain.account.sign_transaction.assert_not_called()
                    eth.send_raw_transaction.assert_not_called()
                    self.assertEqual(chain.budget.used, 0)


if __name__ == "__main__":
    unittest.main()
