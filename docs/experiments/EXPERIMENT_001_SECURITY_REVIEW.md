# Experiment 001 — Task 003C security review

Review date: 2026-10-17. Baseline: [`59375be`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/59375bee20d93eb1593363081dc0d6dd432bfbaa). **Acceptance outcome: CONDITIONAL PASS — core local experimental behavior works, with the explicit conditions below.** This is a project-assisted adversarial review of a research prototype, not an independent audit, formal verification, production approval, or final research report.

## Scope and methodology

Read the charter, context, decision register, ADR 0001, experiment specification, threat model, all 18 invariants, implementation, tests, dependency references, and workflow. Trace discovery -> terms -> authorization -> funding -> computation -> verification -> Acceptance -> settlement/withdrawal and timeout/refund. Review cancellation and revocation separately: unused funding authorization can be revoked; funded agreements cannot be cancelled early.

Use bounded field/domain/signature mutation matrices, actual local EVM transactions, a temporary literal-loopback RPC fault proxy, and controlled faults in separate requester/provider processes. Verify failed contract calls preserve principal/state, and distinguish uncertain delivery from a canonical revert. Retain the original 55 Solidity and 30 Python tests; add focused regressions rather than reduce fuzzing, invariant depth, or assertions. New Solidity tests cover concurrent mixed outcomes, price extremes, and copied settlement calldata. All development keys remain ephemeral and synthetic-only.

The initial new transport suite against the baseline produced two assertion failures (FIFO blocking and overwrite race) and one directory-read classification error. Fixes were followed by regression and full-suite runs. Source-traced evidence-reporting and exception-lifecycle findings below are distinguished from payment exploits. No critical contract vulnerability or need to redesign protocol semantics was confirmed.

## Findings and fixes

Severity is experimental impact, consistent with the threat model. **All listed implementation fixes are included in this task.** No finding establishes an unauthorized escrow payout.

| ID | Severity | Finding / reproduction | Fix and regression evidence |
| --- | --- | --- | --- |
| C-01 | Medium: availability | Put a FIFO at the fixed result-message path with no writer. Baseline `read()` blocks opening it, defeating the agent's three-second service timeout until the outer harness terminates the run. | Open with `O_NOFOLLOW` and `O_NONBLOCK`, then check the opened descriptor is a regular bounded file. Reject directories/devices/FIFOs. `test_fifo_message_cannot_block_read` uses a bounded child process; truncation/size/nonregular tests also pass. |
| C-02 | Low: transport integrity/availability | Publish a competing file after `write()`'s existence check but before `replace()`. Baseline silently overwrites the first message. Signatures still protect approved terms, but write-once transport was false. | Atomic hard-link publication fails if the destination exists; remove only the writer's temporary file. `test_publication_race_preserves_first_message` injects the race and asserts the original remains intact. |
| C-03 | Low: misleading component evidence | After valid settlement but without withdrawal, supply a provider report with `outcome=settled` and an empty receipt list. The baseline requester checks terminal state and iterates zero receipts, permitting its own success report. The outer harness independently rejects remaining credits, so this was not a complete-experiment false success or theft. | Require exactly two receipts, expected provider/agreement/settlement hash, canonical status/block membership, exact Settled and Withdrawn events, and zero remaining provider credit. `test_missing_and_forged_provider_report_rejected` rejects empty/one-receipt and altered reports, then accepts real settlement plus withdrawal. |
| C-04 | Low: ambiguous-action lifecycle | After an unresolved send, the baseline Chain object remains available for another submission. Agents did not automatically retry, and contract replay guards prevent duplicate funding, but the client did not enforce the specified stop-after-uncertainty boundary. | Latch the locally computed pending hash before broadcast. An unresolved/malformed outcome prohibits another submission; a canonical revert clears the latch. Before-send fault test calls twice and asserts only one RPC submission. After-send loss reconciles the exact hash; a deliberate subsequent replay reverts without duplicate principal. |
| C-05 | Medium upstream advisory; constrained exposure here | Pinned Web3.py 7.14.0 is in the affected range for [GHSA-5hr4-253g-cpx2](https://github.com/ethereum/web3.py/security/advisories/GHSA-5hr4-253g-cpx2): default CCIP Read may issue contract/RPC-directed HTTP requests. The fixed escrow does not emit OffchainLookup; exploitation would require an unexpected lookup response, outside its normal flow. | Disable `global_ccip_read_enabled` on every local provider before calls. `test_ccip_lookup_cannot_make_hidden_http_request` injects OffchainLookup and verifies zero secondary HTTP requests; deliberately restoring the old default in the test contacts only a controlled loopback target, demonstrating the dependency behavior. No public endpoint is contacted. The pinned package remains affected in general; this is a feature-disable mitigation, not an upgrade or vulnerability-free claim. |
| C-06 | Low: resource cleanup | Interrupt fixture startup with KeyboardInterrupt after Anvil starts but before `__enter__` returns. Baseline's Exception handler misses it; context cleanup has not yet been installed. | Cleanup on BaseException during startup, then re-raise; bound the Anvil version query. `test_interrupted_fixture_startup_terminates_node` injects the interruption and verifies the real child is stopped. SIGKILL/host failure remains outside Python cleanup guarantees. |
| C-07 | Low: failure classification | Baseline requester catches chain-preflight Inconclusive together with service timeout, potentially publishing a refund-wait request after a reorg. Later preflight prevents payment, but the workflow should abort on chain uncertainty immediately. | Catch only file-wait timeout as missing service; propagate chain uncertainty. `test_process_reorg_aborts_without_refund_or_acceptance` reverts the chain after result verification in real agent processes and checks no Acceptance/refund-wait publication and complete cleanup. |

Receipt handling also now validates returned transaction identity, status, block membership, and consistent canonical receipt fields. Proxy mutations of transaction hashes, receipt hashes/status, event price, and emitter all cause inconclusive failure, even when a transaction actually executed. These are defensive consistency checks against tested faults, not proof against a coherently dishonest privileged RPC.

### Reproduce

Follow [fresh-checkout instructions](../../sdk/python/README.md), then from the repository root:

```sh
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
scripts/run-experiment-001.sh
```

A focused new regression run is:

```sh
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -p test_adversarial.py -v
```

The RPC proxy and test observers exist only in trusted test code. The file-race injection is deterministic; it does not require a probabilistic stress loop. FIFO testing kills its helper on failure. Crash scenarios intentionally return inconclusive/nonzero, and their tests assert no observed credits/withdrawal plus child cleanup; they are not misrepresented as successful refunds.

## Tested attack scenarios

- Every ordered signed field in all five EIP-712 types; name/version/chain/contract domain changes; actual signatures from alternate domains; wrong signers/purposes; malformed lengths, v values, and high-s malleation; extra/missing fields and noncanonical integer ranges.
- Reused nonces/IDs, price/cap extremes, exact expiry -1/equality/+1, unused revocation followed by fund and funding followed by rejected revocation. Terminal replay, refund after settlement, settlement after refund, unauthorized funding/refund/withdrawal, copied settlement calldata.
- False results, malformed/oversized/truncated/unexpected evidence, valid-work requester refusal, requester mutation after signing, duplicate publication, nonregular transport files, and unsigned/incorrect local-client attempts.
- Provider termination before computation (retained test), provider crash after computation, requester crash before Acceptance, deadline expiry during computation, snapshot/revert before Acceptance, and interrupted startup cleanup.
- Real HTTP connection loss before broadcast and after accepted broadcast, exact-hash reconciliation, retry refusal after unresolved delivery, canonical reorg detection, and transaction/receipt/event mutations.
- Contract balance conservation, unexpected forced surplus, reentrancy into all mutators, failed withdrawal with preserved credit, and concurrent agreement mixed outcomes. These include retained Solidity attack receivers and stateful invariants; Python tests do not replace them.

There are no HTTP agent endpoints. Local transport is fixed files; signatures and escrow caller checks deny economic authority to unauthorized clients. The private temporary directory limits other OS users, but same-user peers/admins can sabotage files or privileged Anvil RPC. No adversarial OS isolation is claimed.

## Assessment of all 18 invariants

“Supported” means tested implementation evidence under documented assumptions, not universal proof. See [coverage](EXPERIMENT_001_ESCROW_COVERAGE.md) for retained test names and limitations.

| Invariant | Assessment and evidence | Boundary / remaining gap |
| --- | --- | --- |
| SI-01 authorization | Supported: both term signatures, requester funding authorization, provider result and requester Acceptance; live success and signature mutation tests. | Stolen keys/host compromise can create valid consent. |
| SI-02 cap | Supported: exact principal bound, one-wei/MAX_PRICE successes and invalid cap/value rejections. | No aggregate wallet/gas cap in the contract. |
| SI-03 replay | Supported: consumed nonce/new-ID replay, terminal retries, immutable stateful model. | Deliberately cloned/reset state is not distinguished without run freshness and trusted environment. |
| SI-04 expiry | Supported: actual execution timestamp -1/equality/+1, retained funding/settlement boundary tests. | Chain time is controlled by Anvil/operator. |
| SI-05 revocation | Supported: requester namespace and both canonical ordering outcomes tested. | No retroactive cancellation, Acceptance revocation, or real mempool censorship guarantee. |
| SI-06 immutable terms | Supported: every signed-field mutation plus requester-after-signing process rejection. | Parties may deliberately sign new terms; no informed human-consent proof. |
| SI-07 domain/type/run | Supported: five Python/Solidity digest matches, public vectors, all-type domain/field/encoding mutation matrix. | Vectors share standard primitives; no independently authored cryptographic audit. |
| SI-08 participants/agreement | Supported: ID/party/nonce/result binding checks and malicious local caller tests. | Addresses identify key control, not legal ownership. |
| SI-09 valid result | Supported: invalid-result/no-Acceptance refunds and retained wrong-result-with-both-signatures contract rejection. | Only fixed public addition, not provider effort/general computation. |
| SI-10 failure/timeout | Supported for tested cases: invalid/missing evidence and late computation refund; incompatible terminal calls reject. | Crashes after work or key loss may end inconclusive with synthetic principal still locked until reset. |
| SI-11 independent verification | Supported: separate Python computation paths, requester verifies before signing, on-chain sum independently checked. | Consent signature does not prove verifier execution; harness/host evidence is trusted. |
| SI-12 caller authority | Supported: A/B-only operations, copied calldata denial and own-credit withdrawals. | Privileged RPC/host impersonation is outside the model. |
| SI-13 refunds | Supported: exact, exclusive requester credits at deadline, then withdrawal. | Requester veto remains unfair to B; no automatic refund/key recovery. |
| SI-14 accounting/reentrancy | Supported: all original stateful/callback tests, mixed concurrent outcomes and forced-surplus checks. | No formal EVM/compiler proof or independent audit. |
| SI-15 no AI validity authority | Supported: fixed arithmetic/signatures and strict schema, no model calls. | No future Genesis consensus implementation or result. |
| SI-16 local-only operation | Supported process controls: endpoint/proxy/redirect guards, fresh owned keys, disabled CCIP, synthetic Anvil. | Not an OS egress sandbox or proof against malicious dependency/host. |
| SI-17 ambiguous actions | Supported tested faults: real loss before/after send, exact-hash reconciliation, pending latch, reorg abort, receipt consistency. | No automatic restart/recovery, transaction replacement/rebroadcast implementation, exhaustive fault schedule, or distributed finality. |
| SI-18 bounded execution | Supported tested paths: size/schema/range/discovery/transaction limits, FIFO denial, deadlines, crash/startup cleanup. | No OS CPU/memory quotas, exhaustive spam/interleaving proof, or SIGKILL cleanup guarantee. |

## Dependency and CI security review

- **Solidity:** exact 0.8.28 pragma and checksum-verified compiler; optimizer 200, viaIR, Cancun. Reviewed the upstream [known-bug inventory](https://github.com/ethereum/solidity/blob/develop/docs/bugs.json) against flags/source. The selected source has no transient-storage guard, mutual recursion, named custom-error require syntax, or dynamic escrow storage arrays; several published bug preconditions concern those features. This is source triage, not proof of immunity to optimizer bugs. The old compiler pin remains a maintenance risk; no compiler upgrade was silently introduced.
- **Foundry:** official v1.0.0 commit checked; fuzz 256, stateful 128 x 64, fail-on-revert retained. Checksums protect vendored dependencies and solc. The pinned toolchain action downloads a commit-pinned foundryup initializer and runs distribution tooling before our self-reported version check; this is still upstream supply-chain trust, not a project-pinned binary attestation. Reviewed its action metadata and installer entry source, not every bundled JavaScript dependency.
- **OpenZeppelin:** 5.2.0 immutable source closure and hashes retained. Reviewed consumed ECDSA/EIP712/ReentrancyGuard paths and upstream advisory inventory. [GHSA-9rcw-c2f9-2j55](https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-9rcw-c2f9-2j55) lists the package version but concerns Bytes.lastIndexOf; Bytes.sol is absent from the vendored closure. The old [ECDSA advisory](https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4h98-2769-gh6h) covers versions before 4.7.3, not this pin. No claim that all possible advisories or composition risks were excluded.
- **Python:** queried OSV for all 39 exact locked package versions on the review date. It returned Web3.py's CCIP advisory (GHSA and PYSEC aliases); mitigated by disabling the unused feature and tested locally. Absence of further matches is not absence of vulnerabilities. CPython 3.12.1 is an old patch pin, outside that PyPI package scan; runtime maintenance/advisory review remains a condition before broader use. No unrelated version upgrade occurred. CI/local instructions now require hash-locked wheels only, refusing unreviewed source-build fallback. Wheels still execute code on import and require publisher trust.
- **Actions/workflow:** all three actions use immutable full SHAs, `contents: read`, credential persistence false, no cache, secret inputs, OIDC, deployment environment, or artifact upload. Triggers remain push/main and pull_request, with no privileged PR-target/workflow-run combination. Repository defaults were observed read-only with PR approval disabled. Allowed actions remain unrestricted at repository level; no organization/repository security settings were changed. This workflow's selected actions remain pinned.
- **Untrusted PRs/network/logs:** a PR can execute modified code on a disposable GitHub-hosted runner with internet access. Loopback application guards cannot constrain a malicious PR or dependency. Do not add production secrets, writable tokens, shared privileged runners, or privileged downstream consumers. Standard evidence excludes keys/raw transactions; source and logs were checked for accidental secret material, not certified against all covert exfiltration. Follow GitHub's [secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).

## Acceptance gate and remaining conditions

Core experiment criteria are met in the tested local fixture: separate signer/process ownership, signed discovery and immutable agreements, bounded real escrow funding, independent fixed-service verification, requester consent, actual on-chain settlement and provider withdrawal, negative rejection/refund paths, canonical evidence, and clean normal/error shutdown. Existing contract tests are retained, and no critical protocol-semantic violation was confirmed.

**CONDITIONAL PASS** applies only to this experimental evidence. Conditions before treating the review gate as fully closed or expanding use:

1. Founder/security reviewer accepts the documented requester-veto and key-loss/inconclusive-run limitations. This task neither resolves fairness nor authorizes a redesign.
2. Independently review the implementation, compiler/runtime maintenance, binary provenance, and advisory applicability. This project-assisted review is not that independent audit.
3. Track remaining coverage gaps explicitly: broader reordered/dropped-message schedules, pending transaction replacement/rebroadcast, lifecycle-wide reorg/outage sequences, hard host termination/restart, systematic key-leak instrumentation, and OS resource limits. Current tests are bounded samples, not exhaustive adversarial assurance.

Successful local EVM experimentation does not validate a Genesis consensus mechanism, native blockchain, permissionless identity/discovery, fair exchange, production readiness, or the ultimate independent-network ambition. No Experiment 002 or final research report is authorized by this assessment.
