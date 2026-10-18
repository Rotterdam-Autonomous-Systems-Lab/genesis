"""Integer budget/specification checks only; no signer, transaction sender or agent policy."""
import json

GAS_LIMIT = 2_000_000
MAX_FEE = 3_000_000_000
PRIORITY_FEE = 1_000_000_000
PER_ATTEMPT = GAS_LIMIT * MAX_FEE
limits = {"deployer": 1, "requester": 8, "provider": 8}
budgets = {role: attempts * PER_ATTEMPT for role, attempts in limits.items()}
checks = 0
for base in (0, 1_000_000_000, 2_000_000_000, 3_000_000_000, 3_000_000_001):
    for gas_used in (0, 21_000, 100_000, GAS_LIMIT):
        if base > MAX_FEE:
            eligible = False
            assert not eligible  # No valid inclusion at the signed cap; never raise it.
        else:
            effective = base + min(PRIORITY_FEE, MAX_FEE - base)
            assert 0 <= gas_used * effective <= PER_ATTEMPT
        checks += 1
for role, attempts in limits.items():
    for count in range(attempts + 1):
        assert count * PER_ATTEMPT <= budgets[role]
    assert (attempts + 1) * PER_ATTEMPT > budgets[role]
assert sum(budgets.values()) == 102_000_000_000_000_000
assert budgets["requester"] + 10**15 == 49_000_000_000_000_000
print(json.dumps({"fee_cases": checks, "fee_budgets_wei": budgets,
                  "combined_fee_bound_wei": sum(budgets.values()),
                  "max_principal_wei": 10**15,
                  "combined_starting_balance_ceiling_wei": sum(budgets.values()) + 10**15,
                  "transactions_sent": 0}))
