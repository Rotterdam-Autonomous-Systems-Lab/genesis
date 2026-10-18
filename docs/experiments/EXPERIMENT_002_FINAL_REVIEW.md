# Experiment 002 final review — Task 015

**2026-10-18 — NOT READY TO CLOSE.** Reviewed baseline: `f5efc4b4a1a73ec651e7f1cbde4c4720d1c558e5`, matching local HEAD and the local `origin/main` tracking ref. Remote freshness could not be checked. No material contract defect was confirmed. Source inspection and executable isolated probes support the remediation direction, but required live revalidation and publication CI could not be completed or independently verified in this session. This is an acceptance-evidence blocker, not a finding that correct work cannot settle. Do not upgrade the historical conditional result to unconditional PASS.

## Method and evidence boundary

Reviewed the [frozen specification](EXPERIMENT_002_FINAL_SPEC.md), [test plan](EXPERIMENT_002_TEST_PLAN.md), [threat model](EXPERIMENT_002_THREAT_MODEL.md), [acceptance assessment](EXPERIMENT_002_AGENT_ACCEPTANCE.md), [original review](EXPERIMENT_002_INDEPENDENT_REVIEW.md), [remediation report](EXPERIMENT_002_REMEDIATION.md), corrected-node validation, contract, Python protocol/agents/signer/supervisor, inherited read-only evidence machinery and relevant regression tests. Compared Task 014 against `7511f08`. The four findings were treated as hypotheses to retest, rather than relying on the remediation report's disposition.

Read the charter/context/decision register. Task 014 did not change Solidity contracts, Experiment 001 implementation/tests or MASTER_PLAN. This review adds only documentation and three independent tests; it changes no implementation, dependency, security cap, assertion in existing tests or CI permissions.

The 18-record Task 012 archive remains historical derived evidence, not authenticated ledger proof. Its arithmetic/limits test passed here. The Task 014 timing archive records two controlled late-funding runs and an old-clock delayed failure. Its reported measurements are distinguished below from measurements newly executed in this review. Full signed terms, transaction/event preimages and base-fee evidence are not all retained in the historical scenario archive; offline reconstruction of every historical digest and fee calculation is therefore unavailable.

## Findings and attempted falsification

| Finding | Independent assessment | Counterexamples and limits |
| --- | --- | --- |
| R013-01: ownership/terminal consistency | `audit_ledger` now derives state/result, locked principal, each owner's credit and wallet from decoded included funding/claim/refund/withdrawal actions. Funding binds terms/digest, parties, signatures, nonce, price and deadlines; terminal actions bind caller, agreement, result and events. Two block-pinned snapshots must equal the reconstructed model and the final head must remain unchanged. This directly addresses the original aggregate-only checker. | Inspected swapped-owner, stale-terminal, wrong-party and conflicting-owner regressions: they require rejection, including settlement with B credit still unwithdrawn. They could not execute here because fixture startup requires a forbidden loopback bind. Source support is substantial; live remediation verification remains pending. Closed single-agreement fixture rules are not a general indexer. |
| R013-02: RPC rereads/latch | Supplied/current/block receipts compare 12 fields including gas/price, inclusion and logs. Transaction identity and own signed intent are checked; fee arithmetic and principal-adjusted wallet debit remain exact. Decorated evidence/submission paths retain `halted`; good diagnostic replies do not clear it. | Added an independent synthetic receipt model with valid control and 24 single-field conflicts (12 fields in each of current/block receipt sources). Every conflict rejects; restoring good replies still permits no signature/send or extra budget charge. Added a good-record-after-latch probe. These pass without a node. Existing real-chain identity/intent/stale-record/timeout/reorg regressions remain unexecuted in this session. Matching fabricated RPC observations remain outside assurance. |
| R013-03: execution deadlines | Shared monotonic deadline reaches agent barriers, typed signing, RPC middleware, transaction construction/signing/broadcast and audit. Ready-file paths check guards. Cleanup has a separate 15-second cap. | Existing exact-boundary/typed-signing unit probe passes. Added expiry *inside* transaction signing: hash and reservation remain, broadcast is prevented, and a recovered clock cannot permit another signature. Delayed live RPC/build/post-broadcast and cleanup tests require unrestricted local sockets. An operation already executing can overshoot until its next cooperative check; no preemptive containment is established. |
| R013-04: timing/inclusion | Late-funding fixture disables automining before release, waits for pending funding, mines at the unchanged `fundBefore-1`, then restores automining. Signed windows and fee/receipt/wall limits remain unchanged. Separate inclusion-at-expiry rejection is retained. | Inspected the delayed old-clock reproduction and two controlled repetitions. Archived controlled inclusions have two seconds claim slack, late-claim rejection and refund/withdrawal. Old-clock receipt is at funding expiry, status zero, no consumed authorization/principal, with gas charged. Could not repeat either live control here. This is credible mechanism evidence, not recovery of the original failed CI timestamp. |

No successful in-model unauthorized payout, invalid result payment, duplicate obligation/payment or conflicting terminal transition was confirmed. That statement is limited by the blocked live tests; absence of a newly observed exploit is not clearance of every mandatory acceptance check.

The added tests specifically combine R013-02 with R013-03: expiry after a signature must retain uncertainty/reservation without broadcast; later good evidence/time must not reactivate the signer. The receipt model uses mocks and synthetic bytes, never a real signed transaction or key. It tests actual checker/control flow but cannot validate Anvil behavior, transport, process separation or inclusion.

## Core claim and preserved constraints

The core claim remains supported at the contract layer and by historical process evidence: **correct deterministic work can settle without a second requester authorization**, provided B's valid claim is included before the signed deadline. The passing `test_NoPostFundingRequesterActionAndOwnWithdrawal` directly exercises that contract path. No Acceptance schema exists. Funding requires A's bounded Authorization and both Terms signatures; claim requires stored B caller, bound provider signature, correct sum, Funded state and strict inclusion deadline. A refusal/offline process controls remain in the suite and historical archive; they were not newly executed here.

Source and passing Solidity/signature/budget tests support these bounded rules:

- Principal is exact signed price, positive and no greater than signed max and `10^15`; funding consumes authority atomically. Refund never restores authority. Revocation cannot cancel a funded obligation.
- EIP-712 binds domain/chain/deployment/run and exact fields; supported low-s 65-byte signatures and intended actors remain required. Frozen vectors, mutation/domain/encoding negatives and wrong-result/caller controls pass at the tested layers.
- Claims/refunds are exclusive, with claim strictly before and refund at/after deadline. Withdrawal clears own credit before guarded transfer and failure rolls back. Forced surplus grants no entitlement.
- Honest signer policy keeps gas <=2,000,000, max fee <=3 gwei, priority <=1 gwei, attempt caps 1/8/8 and conservative reservation `6*10^15` per attempt. Combined fee allowance remains `102*10^15`; closing slots, one funding intent, no top-ups/replacement/escalation remain. Contract principal limits are not universal wallet gas limits.
- Experiment 001's separate requester-acceptance policy/code/tests are preserved. All 58 original Solidity tests passed within the 86 total. Its live Python compatibility could not be revalidated here.
- Candidate loader verified the installed exact Anvil v1.6.0-rc1 / `b272ce3366987406406e9eb1b82596653a3ad628` hash/version. Fixture still explicitly requests Cancun, chain 31337, loopback, zero unlocked accounts and no fork. Startup/RPC profile checks were not reached in blocked runs. Candidate integrity negatives pass; fee/opcode-witness and cross-node compatibility remain CI dependencies.

## Targeted and regression results

| Check attempted in this review | Result |
| --- | --- |
| Exact Foundry v1.0.0 `8692e926198056d0228c1e166b1b6c34a5bed66c`, format/build/Solidity | PASS: 86 tests, zero failures/skips; fuzz 256, stateful 128 x 64 retained. |
| New `test_final_review015.py` | PASS: three tests, including 24 receipt-field mutation subcases and latch/deadline interactions. |
| Existing socket-free codec/budget/archive/exact-signature-deadline selection | PASS: 15 tests. |
| Candidate integrity negative controls | PASS: three tests; installed candidate loader also verified identity. |
| Vendored dependency checksums | PASS. |
| Full Experiment 002 Python suite before additions | FAILED to validate: 70 attempted, 58 errors, 12 passed; live fixtures encounter `PermissionError: [Errno 1] Operation not permitted` at `socket.bind(("127.0.0.1", 0))`. No tests removed/skipped to hide this. |
| Full Experiment 001 Python suite | FAILED to validate: 54 attempted, 40 errors, one failure, 13 passed. Live setup hits the same sandbox restriction; startup/cleanup expectation also fails under unavailable fixture startup. Not interpreted as an escrow regression. |
| Standalone Experiment 002 | BLOCKED at loopback bind; no exchange executed. |
| GitHub CI/remote freshness | UNKNOWN: `gh run list` cannot connect to `api.github.com`; `git ls-remote` cannot resolve `github.com`. No new CI run was triggered/observed. |

Initial Solidity invocation used globally installed Foundry commit `e144b820`; it passed 86 tests but failed the exact toolchain check. This was corrected by selecting existing `internal/tools/foundry` binaries, checking the required commit and rerunning format/build/all 86 tests successfully. No tool pin was changed. Python is 3.12.1. An initial integrity-discovery filename matched no tests; the explicit three-test class was subsequently executed successfully. Local logs remain ignored under `internal/task015/` and are not portable public evidence.

## Historical CI timing evidence

The [original review](EXPERIMENT_002_INDEPENDENT_REVIEW.md) records initial CI run [39139135792](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39139135792): late-funding setup canonically reverted, 57/58 tests passed, standalone skipped. Later [39139675027](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39139675027) passed without a corresponding fixture fix. These are retained historical records; this session could not fetch their logs or the Task 014 run status independently.

The delayed old automining schedule demonstrates a plausible failure mechanism: an empty block at `fundBefore-1` does not reserve the subsequent transaction's inclusion timestamp. Controlled pending-first mining addresses that fixture race. **The historical failed receipt timestamp has not been recovered; its exact root cause remains unestablished.** Later green CI alone cannot establish it. This uncertainty need not itself invalidate a bounded result after current valid-late and expiry controls pass on the required profile, but those checks remain unverified here.

## Guarantees, results and remaining risks

**Confirmed within tested scope:** contract authorization, fixed arithmetic, exclusive transitions, principal accounting and no second A approval; isolated receipt contradiction/latch and signing-expiry controls. These are finite tests and source-based assessments, not formal proofs or production guarantees.

**Environment-specific results:** historical separate-process settlement/refusal/offline/late-funding and fee compatibility belong to the exact trusted Anvil/Cancun fixture. New local Solidity and socket-free tests do not substitute for those integrations. Explicit mining/time advance is test control, not network inclusion assurance.

**Residual trust:** honest host, supervisor/scheduling, keys, loopback RPC, fresh run/deployment, compiler/libraries, upstream publisher hashes and CI infrastructure. One transaction per block, serialized wallets, no top-ups and one agreement underpin this audit. Distinct processes/addresses do not prove independent owners. No successful reproducible-build/attestation assurance or new advisory sweep is claimed.

**Unresolved security/liveness limits:** public inputs/output disclosure, absent or censored callers, insufficient deadline slack, key loss, chain rollback/finality and fully dishonest RPC can prevent payment or authenticity. Correct work may go unpaid; no automatic refund/withdrawal, confidential delivery or strong fair exchange. Latch/journal are in memory, without durable crash recovery. Cooperative deadlines/RSS/cleanup cannot contain hostile host, SIGKILL or stalled OS operations. Valid repeated work proves no unique effort, useful demand, Sybil resistance, mining eligibility, consensus or native economy.

## Acceptance decision and next dependency

**NOT READY TO CLOSE:** no new material contract defect is established, and the narrow result remains supported, but this reviewer cannot certify that all required remediation checks and compatibility/CI gates hold. Do not promote unexecuted live checks or previous author-reported passes to fresh independent verification. No material defect was silently fixed.

Next dependency is completion of this same review's validation in an environment permitting disposable loopback Anvil and GitHub access: run all existing/new tests and CI on the exact profile, verify the publication commit/run, then record a separate evidence-based closure disposition. If they pass and no material defect emerges, the allowed positive outcome is **BOUNDED CONDITIONAL PASS — READY TO CLOSE**, with the above limitations retained. A failure requires a separate remediation task, not relaxed assertions or budgets.

Only after that gate, recommend a separately scoped research question distinguishing deterministic result validity from useful/unique contribution or examining delivery/inclusion assumptions. This review authorizes no native-chain, consensus, token mechanics, autonomous discovery or public deployment work.

## Reproduction

From the repository root, with existing checksum-verified compiler, exact Foundry tools, hash-locked Python environment and verified candidate installed:

```sh
export PATH="$PWD/internal/tools/foundry:$PATH"
scripts/check-toolchain.sh
scripts/check-dependencies.sh
forge fmt --check
forge build --offline
forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/experiment002 -v
scripts/run-experiment-002.sh
scripts/run-experiment-002.sh --scenario late_funding
```

Run the unchanged `.github/workflows/foundry.yml` to include original-node negative fee controls, corrected-node fee/signature probes, Experiment 001 on both profiles and standalone settlement. For the new socket-free probes alone:

```sh
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/experiment002 -p test_final_review015.py -v
```

Full reproduction requires socket/process permissions; failure before node startup supplies no settlement evidence. Preserve historical archives and failed-run diagnostics; never invent missing measurements.
