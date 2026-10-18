# Adversarial specification review and fixture freeze — Task 018

**READY FOR COMPARATIVE MODELS.** Baseline: `23be098502f7fa0920e02930d3130fa78926289d`. This is a bounded specification review, not candidate execution or native-network acceptance. No architecture is eliminated or selected.

## Evidence and findings

Reviewed MASTER_PLAN, all Task 016/017 architecture documents, Experiment 001 report/security evidence, Experiment 002 final specification/acceptance/final review, relevant ADRs 0001–0004, repository instructions and testing conventions. Experiments demonstrate bounded local escrow/verification and settlement without a second requester authorization; they do not demonstrate native delegation, permissionless security, authenticated remote recovery, physical delivery or adoption. Experiment 002's historical unexplained timestamp remains unexplained; this task supplies no new historical evidence.

| Finding | Concrete counterexample and impact | Disposition / frozen evidence |
| --- | --- | --- |
| R018-01: role before fee | X submits Claim on B's agreement. Checking role after admission charges X and consumes a sequence, while checking it first rejects without fee. Implementations would disagree. | Resolved: explicit stored-principal/owner and grant-scope checks precede fee admission. Authorized B's wrong result is a fee-paying semantic revert. V07/V13/V15. |
| R018-02: atomic fee solvency | H has 10 and sends 10 with ceiling 1; checking principal against the pre-fee balance can create negative funds. Concurrent delegates can also exhaust F while P remains. | Resolved: reserve the entire ceiling before semantic principal checks, charge 1 on admitted revert, release unused ceiling. Separate cumulative P/F caps remain atomic. V01/V02/V19/V20. |
| R018-03: structural fairness | Two delegates build against one grant version. An object/input wrapper may become stale while an account transaction reads the updated record. Calling both the same logical rejection forces artificial implementation behavior. | Resolved: canonical fresh-reference barriers compare semantics; native stale-reference attempts are separate measured traces. Same intent may be rebuilt only under the recovery contract. V09 is an injected fault control, not a measured intrinsic conflict advantage. |
| R018-04: absence is not fencing | RPC says not found, client rebuilds, old wrapper arrives later. Even a genuine snapshot of absence does not settle pending delivery. | Resolved for this experiment: retry requires oracle-confirmed non-admission of every recorded wrapper and closure/invalidation of its delivery epoch. Ordinary RPC absence halts with exposure retained. Production fencing/proof construction remains open. V08–V11/V16/V17. |
| R018-05: unspecified service | W05 mentions planning/checksum but the shared predicate defines only widened sum. Implementers could choose incomparable verification costs. | Resolved: coordination uses the same sum stub. No physical service/navigation claim. |
| R018-06: freeze gaps | Different terminal codes change credit IDs; forgetting returned counters can hide renewed caps. Testing refund only when G also expires masks accidental replenishment. | Resolved: adapter fixes terminal codes, admission precedence, retained replay and reserve-return accounting. V14 deliberately keeps G valid until 40 while refund occurs at 20, then attempts to reuse principal. V06/V18 cover return/rotation. |

The [adapter](NATIVE_L1_ADAPTER.md) is the normative clarification of these laboratory ambiguities. The [versioned corpus](../../research/fixtures/native_l1/README.md) contains **21 vectors and 32 signed intents**, full expected ledger/client snapshots and independent codec examples. Signed negative cases intentionally include wrong-domain/key/epoch/role inputs. Static signatures are public research data; no private key is included.

## Validation and limits

Nine fixture tests pass: strict schema/duplicate-key rejection, artifact hashes, canonical encoding, RFC public signature example, actual corpus signatures, ownership/budget/supply identities, event bindings, unchanged rejected states and recovery coverage. A malformed RFC golden signature was caught during fixture development and corrected before freeze; the rejecting test remains. These tests check fixture integrity, **not the correctness of future candidate transitions**. CI additionally retains existing Experiment 001/002 regressions and adds the fixture suite.

Golden snapshots were authored independently of candidate mutation code. Their finite scope is not a proof; Task 019 must implement independent invariant assertions and report counterexamples rather than edit expectations to fit a candidate. No new contract defect claim or cryptographic audit follows from this review.

## Gate and remaining risks

The shared semantics, adapter, corpus and measurement plan suffice to authorize **bounded Task 019 models**, with all three candidates retained. The frozen 21 core configurations plus nine stress configurations fit the existing 30-configuration limit. Broader Task 017 mutation/permutation ideas remain follow-up coverage, not secretly claimed complete by this minimal freeze; Task 019 must publish the exact coverage list and cannot claim the entire Task 017 envelope passed.

Unresolved native dependencies remain authenticated finality/non-execution evidence, permissionless admission/bootstrap and small-network security, replay-history retention/pruning, real fee/VM metering, key-loss recovery, device operational security and physical-service truth. None is supplied by an honest AI, machine identity, deterministic useful work or the fixture oracle. They prevent native-network acceptance, not this finite state-model comparison.

Recommended Task 019: implement three distinct bounded representations and an independent harness against this unchanged v1 baseline; freeze dependency/source identities, candidate wrapper formats and instrumentation before measurements; reproduce on two clean environments. Classify failures as implementation defects, budget HOLDs or unresolved family constraints. Select no final L1 from a single prototype.
