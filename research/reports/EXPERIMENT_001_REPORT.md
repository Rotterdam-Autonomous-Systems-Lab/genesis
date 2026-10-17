# Experiment 001: Bounded Autonomous Service Exchange on a Local EVM

## 1. Publication metadata

- **Institution:** Rotterdam Autonomous Systems Lab (RASL), Rotterdam, Netherlands.
- **Initiative:** Genesis, the temporary research codename.
- **Publication date and version:** 2026-10-17, version 1.0; version-controlled technical research report, prepared with AI assistance from repository evidence.
- **Experimental assessment:** **CONDITIONAL PASS** for the bounded local fixture.
- **Validated implementation:** [`f66cda91af5cb2f2da266fe11d90bc67c05cfc77`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77).
- **Final validation workflow:** [GitHub Actions run 39057757966](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966), successful for that exact commit.
- **Review status:** project-assisted adversarial review; no independent audit, peer-review outcome, formal verification, or production-security assurance is claimed.

This publication synthesizes the existing experiment and its final validation milestone. It introduces no protocol feature, architectural commitment, native asset, or Experiment 002 implementation. Relative links aid current repository navigation; the immutable references in Section 17 identify the evidence snapshot if later development changes those files.

## 2. Abstract

Experiment 001 investigates whether two separately executing software participants can complete a narrowly bounded service exchange using cryptographically signed authority and independently checked actions. A Python requester and a separate Python provider create distinct ephemeral signing identities, exchange signed service terms over local files, and use a Solidity escrow on temporary Anvil. The provider adds two unsigned 64-bit integers. The requester independently recomputes the result and signs Acceptance only after validating the evidence; the contract separately checks the arithmetic and signatures before crediting payment. The standard fixture verified 7 + 11 = 18 and settled and withdrew 10^12 synthetic wei.

At the final validation milestone, **112 tests passed: 58 Solidity and 54 Python**. All 18 documented security invariants were assessed through scoped implementation evidence, not formal proof. Adversarial review identified and addressed transport, payment-evidence, uncertain-transaction, and cleanup gaps, and mitigated an unused dependency feature's HTTP lookup risk. The outcome is **CONDITIONAL PASS**: requester-veto fairness remains unresolved, key-loss crashes can terminate a run with locked synthetic principal, and independent review and broader fault coverage remain open. These results do not validate a new consensus mechanism, native blockchain, native asset, production system, or the long-term Genesis network.

## 3. Research question and hypothesis

**Research question:** Under an explicitly trusted local execution environment, can two distinct signer processes agree to fixed service terms, authorize a bounded synthetic payment, independently verify a deterministic result, and complete on-chain settlement while rejecting the specified unauthorized and invalid actions?

**Research hypothesis:** For this fixed addition service, explicit signature/domain/nonce/amount/time checks, requester-side verification, and independent contract arithmetic can enforce the specified authorization and settlement predicates in the tested implementation, despite the modeled malformed messages, dishonest results, and selected failures.

Falsification cases include an invalid result producing a valid requester Acceptance, a contract payout without the required signatures or above the authorized principal, replay yielding duplicate funding/payment, incompatible terminal transitions succeeding, or a run claiming success without its required canonical evidence. A crash or irreconcilable RPC outcome is an inconclusive execution, not successful service delivery. Test success supports only the tested paths and environment; it cannot prove the hypothesis for all executions.

The experiment does not test the stronger hypothesis that correct provider work guarantees payment. Its requester-veto rule supplies a direct counterexample: a correct result without requester Acceptance cannot settle.

## 4. Motivation and relationship to the Genesis vision

Genesis researches foundational economic coordination among humans, autonomous software, AI agents, robots, industrial machines, vehicles, drones, satellites, sensors, distributed computational systems, and future autonomous participants. The long-term ambition includes a possible independent permissionless network across different operators, hardware, models, jurisdictions, objectives, and connectivity conditions. That ambition remains a research direction, not an implemented capability.

The [canonical charter](../../MASTER_PLAN.md) prioritizes bounded cryptographic authority and verification of actions over trust in a participant's intelligence. This experiment operationalizes a small part of that principle: a peer's claimed result is insufficient for payment. It primarily exercises Autonomous Economic Authority and Verifiable Coordination; it supplies no consensus, Sybil-resistance, or decentralized-network security result for the third research track.

An agent-payment application is not the whole Genesis initiative. EVM/Anvil tooling is an experimental substrate, not a commitment to Ethereum or any final Genesis architecture. Existing cryptographic standards and libraries are reused; no originality or completed comprehensive prior-art review is asserted.

## 5. Experimental scope and explicit non-goals

The scope is one standard agreement per run, a public deterministic addition service (`genesis.sum-u64.v1`), two ephemeral EOA signers in separate Python processes, signed local file transport, synthetic ETH escrow, bounded execution, and a trusted temporary single-node chain. The contract also supports multiple records; dedicated tests exercise mixed concurrent agreement outcomes. This does not make the Python fixture a general multi-agent marketplace.

Non-goals include real funds, public blockchain deployment, AI/model calls, probabilistic computation, provider-effort verification, useful outsourcing efficiency, generalized service verification, confidential inputs, global discovery, real-world identity, fair exchange, production key custody, native assets, novel consensus, and a native Genesis blockchain. Hardware heterogeneity, offline/space operation, interoperability across networks, and long-term governance are not tested here.

## 6. System architecture and trust assumptions

| Component | Actual responsibility | Trust boundary |
| --- | --- | --- |
| Requester process A | Creates its own key; discovers and checks an offer; signs exact terms and spending authority; funds; recomputes result; signs Acceptance; checks settlement evidence or requests a valid refund. | Untrusted peer data; A's signing policy and process execution are part of the evaluated implementation. |
| Provider process B | Creates a different key; signs an advertisement and matching agreement; reads funded inputs; computes and signs a result; checks Acceptance; settles and withdraws. | Cannot authorize A's spending or sign A's Acceptance. |
| Public JSON files | Carry offers, agreements, requests, results, Acceptance, and public execution evidence. | Untrusted messages; fixed paths, schema and size bounds, regular-file reads and atomic publication. No HTTP agent endpoints. |
| Solidity escrow | Enforces signatures, binding, caps, nonce state, arithmetic, deadlines, terminal states and own-account credits. | EVM/compiler/library correctness remains assumed. |
| Trusted runner and Anvil | Deploy the contract, assign synthetic balances, start/stop processes, advance time in controlled tests, and check receipts/state/accounting. | Shared host/operator and privileged RPC control are trusted. |

Each agent generates its key inside its own process; the runner has a separate deployment signer and receives only agent public addresses. Distinct PIDs and addresses are asserted. **Independent processes and signing identities do not establish independent legal owners, hostile-OS isolation, or protection against the same-user administrator.** The host or privileged Anvil RPC can inspect memory, impersonate accounts, rewrite state/time, or falsify evidence.

RPC destinations are restricted to literal `127.0.0.1`; proxy configuration and redirects are rejected, and chain ID, deployment code hash and run ID are checked. CCIP Read is disabled. These application controls are not an OS network sandbox against malicious code or dependencies. Keys, raw signed transactions and `.env` content are not publication artifacts.

## 7. Cryptographic authorization and settlement design

The implementation uses [EIP-712](https://eips.ethereum.org/EIPS/eip-712) typed-data hashing/signing with Ethereum ECDSA through established libraries. Its domain is name `GenesisExperiment001`, version `1`, chain ID `31337`, and the deployed verifying-contract address. Every payload includes the fresh immutable run ID. EIP-712 supplies typed encoding and domain separation; this experiment adds explicit nonce and agreement state for replay protection. Signing is local; agents do not ask unlocked RPC accounts to sign.

| Message type | Signer(s) | Bound purpose |
| --- | --- | --- |
| Advertisement | B | Provider, supported service, price, offer expiry and run. |
| Agreement | A and B | Requester/provider, service, operands, price, funding/settlement deadlines, unique salt and run. |
| Authorization | A | Intended parties, Agreement digest, single-use nonce, maximum principal, first-use expiry and run. |
| Result | B | Agreement digest, computed value and run. |
| Acceptance | A | Agreement digest, Result digest, consumed authorization nonce and run. |

The exact ordered fields and widths are defined by the [architecture](../../docs/architecture/EXPERIMENT_001_ARCHITECTURE.md) and [contract source](../../contracts/src/Experiment001Escrow.sol), with matching fixed Python schemas. Wire integers are canonical decimal strings; hashing uses typed values, not raw JSON. Supported signatures are exactly 65 bytes with the specified low-s and v encoding; contract-wallet signing and alternative signature formats are outside scope.

Only A may fund the exact agreed price. The contract requires `0 < price <= maxAmount <= 10^15` synthetic wei. The standard price is `10^12`, with authorization maximum `2 * 10^12`; unused allowance is not reusable spending credit. Nonce state moves Unused -> Consumed or Revoked. Revocation blocks unused authorizations when executed; it cannot unwind an already-funded agreement or revoke Acceptance.

Escrow state is None -> Funded -> Settled **or** Refunded. Only B can settle before the immutable settlement deadline, using its signed Result and A's matching Acceptance, and only if the stored operands sum to the claimed value. A's independent off-chain check is exercised by the workflow; the contract's separate arithmetic check does not trust that A actually ran a verifier. Conversely, correct arithmetic does not substitute for A's signing consent.

At the settlement deadline, settlement is rejected and A may request an exact refund. Funding/authorization and settlement limits use strict `<`; refund uses `>=`, all against chain timestamps. There is no early funded cancellation, partial payout, adjudicator, owner rescue, proxy, or upgrade path. Credits are withdrawn by their owners through guarded pull payments. Tests check:

```text
totalLocked + totalCredits = totalDeposited - totalWithdrawn
totalLocked + totalCredits <= contract balance
```

Forced surplus may make the second relation strict without creating credit. Principal limits exclude gas. Local transaction budgets do not constitute a contract-enforced aggregate wallet limit.

## 8. Experimental methodology

The frozen implementation combines the specification, exact tool/dependency references, unit tests, bounded fuzzing, stateful model checks, live Python/Solidity interoperability, separate-process tests, and controlled fault injection. Fresh keys, run IDs and deployment addresses vary by run. Reproducibility means equivalent checked transitions and outcomes, not identical signatures or transaction hashes.

The standard flow signs an offer and identical terms, funds escrow, requests computation by Agreement ID, verifies B's signed result, issues Acceptance on a match, settles, and withdraws. The runner checks canonical receipts, expected contract events, terminal record state, exact deposits/withdrawals, zero remaining liabilities and contract balance, distinct identities/processes, and child shutdown. The requester additionally requires both settlement and withdrawal evidence from B.

Negative fixtures include malformed signatures, every signed field across all five types, wrong domain/chain/contract/run/participants, replay, caps, revocation ordering and deadline boundaries. Service and process fixtures include incorrect/malformed/oversized/truncated evidence, changed terms after signing, refusal of valid work, provider termination, requester crash, and deadline expiry during work. A temporary loopback RPC proxy drops connections before/after broadcast and mutates hashes, receipt status and event data. Snapshot/revert tests detect stale canonical evidence. Solidity attack receivers exercise callback reentrancy, failed withdrawals and forced surplus.

Limits include 16 KiB messages, at most 16 advertisements, fixed uint64 operands, eight transaction submissions per signer and at most 16 in the standard run, a 45-second agent budget and a 60-second harness budget. No unbounded fuzzing or persistent infrastructure is used. An inconclusive result after key loss or ambiguous delivery may abandon synthetic principal when the fixture is reset; it is not mislabeled as a refund.

## 9. Reproduction procedure

### 9.1 Evidence version and prerequisites

Reproduce the implementation at commit `f66cda91af5cb2f2da266fe11d90bc67c05cfc77`, rather than assuming a future main branch is identical. A fresh clone can select that snapshot with:

```sh
git clone https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis.git genesis-e001
cd genesis-e001
git checkout --detach f66cda91af5cb2f2da266fe11d90bc67c05cfc77
```

These are reader setup instructions; publication verification used the existing clean repository at that same implementation commit. GitHub credentials are unnecessary for the public clone and local experiment.

Prerequisites: CPython **3.12.1**, official Foundry **v1.0.0** commit `8692e926198056d0228c1e166b1b6c34a5bed66c`, Bash, curl, tar, jq and a SHA-256 utility. Compiler bootstrap supports macOS x86_64 and Linux x86_64; other platforms are not validated by this procedure. Install Foundry using the official platform archives linked in [contract setup](../../contracts/README.md), extract into ignored `internal/tools/foundry`, and add it to the current shell's PATH. CI installs that exact release automatically through its pinned action. No repository script silently installs a different Foundry version. For an isolated local installation from the official release archives:

```sh
case "$(uname -s)-$(uname -m)" in
  Darwin-x86_64) genesis_foundry_platform=darwin ;;
  Linux-x86_64) genesis_foundry_platform=linux ;;
  *) echo 'This reproduction procedure supports x86_64 macOS/Linux only.' >&2; exit 1 ;;
esac
mkdir -p internal/tools/foundry
curl --proto '=https' --tlsv1.2 --location --fail --silent --show-error --max-time 240 "https://github.com/foundry-rs/foundry/releases/download/v1.0.0/foundry_v1.0.0_${genesis_foundry_platform}_amd64.tar.gz" -o internal/tools/foundry-v1.0.0.tar.gz
tar -xzf internal/tools/foundry-v1.0.0.tar.gz -C internal/tools/foundry forge anvil cast chisel
export PATH="$PWD/internal/tools/foundry:$PATH"
scripts/check-toolchain.sh
```

The archive procedure was verified on the local macOS x86_64 host; the cited CI run independently demonstrates installation through the pinned action on Ubuntu x86_64. Version/commit checks are not independent binary attestations.

| Dependency | Exact experimental reference |
| --- | --- |
| Foundry / Anvil | v1.0.0, commit `8692e926198056d0228c1e166b1b6c34a5bed66c` |
| Solidity | `0.8.28+commit.7893614a`; Cancun, optimizer 200, viaIR |
| OpenZeppelin Contracts | v5.2.0, commit `acd4ff74de833399287ed6b31b4debf6b2b35527` |
| forge-std | v1.9.6, commit `3b20d60d14b343ee4f908cb8079495c07f5e8981` |
| Python / direct packages | CPython 3.12.1; Web3.py 7.14.0; eth-account 0.13.7 |
| Transitive Python packages | All 39 package versions/distribution hashes in `sdk/python/requirements.lock` |

The [dependency record](../../DEPENDENCIES.md) provides compiler platform hashes, vendored-source integrity and supply-chain limitations. Tool/package installation uses HTTPS; execution uses local files and temporary loopback Anvil only. No `.env`, production key, public RPC, real asset, VPS, or AI API is needed.

### 9.2 Local dependency setup and complete test commands

From the repository root, with the exact Foundry tools on PATH:

```sh
export PATH="$PWD/internal/tools/foundry:$PATH"
scripts/check-toolchain.sh
scripts/check-dependencies.sh
scripts/bootstrap-solc.sh
forge fmt --check
forge build --offline
forge test --offline -v
scripts/check-anvil.sh
python3.12 -m venv internal/agent-venv
internal/agent-venv/bin/python -m pip install --only-binary=:all: --require-hashes -r sdk/python/requirements.lock
internal/agent-venv/bin/python -m pip check
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
```

These commands were executed against the publication's implementation snapshot. Compiler/source checks, build, all tests, and the smoke check succeeded. The existing pinned Foundry installation was reused; this publication does not claim a newly independent binary provenance audit. Forge runs contract tests in its in-memory VM. The smoke script starts a separate zero-account node for a chain-ID query only. Python integration tests deploy to their own temporary local Anvil instances; they do not merely simulate escrow in Python.

### 9.3 Start the local experiment and confirm settlement

```sh
scripts/run-experiment-001.sh > internal/task004-run.json
internal/agent-venv/bin/python - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('internal/task004-run.json').read_text())
assert r['outcome'] == 'settled' and r['state'] == '2'
assert r['expectedResult'] == '18' and r['principal'] == '1000000000000'
assert r['requester']['acceptanceSigned'] is True
assert r['agents']['requester']['address'] != r['agents']['provider']['address']
assert r['agents']['requester']['pid'] != r['agents']['provider']['pid']
assert len(r['requester']['receipts']) == 1
assert len(r['provider']['receipts']) == 2
assert all(x['status'] == '1' for x in r['requester']['receipts'] + r['provider']['receipts'])
assert r['childrenStopped'] is True
print('Verified local settlement and withdrawal:', r['provider']['settlementTx'])
PY
```

The runner starts Anvil, deploys the existing escrow, starts B and A, executes the exchange, checks on-chain evidence and accounting, and shuts down every child. **The assertions above inspect its public summary; the runner performs the live on-chain checks before shutdown.** Anvil is no longer available after the command, so a later `cast call` against its former port would not confirm this run. JSON/logs alone are not independent cryptographic proof of execution.

### 9.4 Complete GitHub Actions execution — CI-only operations

The actual [workflow](../../.github/workflows/foundry.yml) runs on pushes to main and pull requests, with the `escrow` job on Ubuntu 24.04 and a 15-minute timeout. It checks out source without persisted credentials, installs pinned Foundry/compiler and CPython, performs the Solidity checks above, installs hash-locked wheels, runs the entire Python suite, and executes the end-to-end runner. All three external actions use full commit SHAs and workflow permissions are `contents: read`.

There is **no workflow_dispatch trigger**; `gh workflow run foundry.yml` is not a supported command for this repository's current workflow. Ordinary authorized pushes to main trigger the full workflow automatically. A maintainer with suitable GitHub permissions can request another full attempt of the validated workflow using the supported CLI commands:

```sh
gh run rerun 39057757966 --repo Rotterdam-Autonomous-Systems-Lab/genesis
gh run watch 39057757966 --repo Rotterdam-Autonomous-Systems-Lab/genesis --exit-status
```

This is a remote CI operation, not local execution; it changes the run's attempt history. The rerun command was checked against the installed CLI help, not invoked to collect the cited historical evidence. Publication verification retrieved the existing successful run and repeated local checks. To inspect the recorded evidence without starting a new attempt:

```sh
gh run view 39057757966 --repo Rotterdam-Autonomous-Systems-Lab/genesis --json headSha,conclusion,status,url
gh run view 39057757966 --repo Rotterdam-Autonomous-Systems-Lab/genesis --log
```

## 10. Results and quantitative test evidence

The final validation milestone is the successful push-triggered run for commit `f66cda91af5cb2f2da266fe11d90bc67c05cfc77`. Its logs, not an extrapolated claim from earlier milestones, establish the following counts:

| Evidence | Recorded result | Interpretation |
| --- | --- | --- |
| Solidity suite | 58 passed, 0 failed, 0 skipped, across five suites | 39 ordinary tests, 15 bounded fuzz properties and four stateful invariants. |
| Python suite | 54 tests, final status OK | Original 30 plus 24 adversarial methods; some methods contain multiple controlled subcases. |
| Total test methods/properties | **112 passed** | Not 112 statistically independent trials or exhaustive execution paths. |
| Fuzz configuration | 256 runs, fixed seed `0x003a` | Bounded property testing, not exhaustive enumeration; a test may also include a dictionary case. |
| Each stateful invariant | 128 runs x depth 64 = 8,192 calls, 0 unexpected reverts | Four model/accounting properties; no formal proof follows. |
| Standard service | Inputs 7 and 11; result 18 | B computes, A recomputes independently, contract checks arithmetic. |
| Standard payment | `1000000000000` synthetic wei | Exact bounded escrow principal; gas is separate. |
| End-to-end outcome | Settled, provider withdrawal successful, `childrenStopped=true` | Live temporary local chain and separate agent processes; no public-chain transaction. |

The successful process test includes two fresh clean runs; boundary tests also cover zero and maximum operands in the appropriate suites. Rejection/refund and crash/inconclusive cases are distinct outcomes. No throughput, latency, outsourcing efficiency, general gas-cost benchmark, or statistical attack-success estimate was designed or inferred. CI durations and per-run diagnostic metrics are not network performance claims.

## 11. Adversarial testing and confirmed implementation findings

The [Task 003C security review](../../docs/experiments/EXPERIMENT_001_SECURITY_REVIEW.md) records reproduction methods, scope, fixes, and regression tests against baseline commit `59375bee20d93eb1593363081dc0d6dd432bfbaa`. Its initial transport tests exposed FIFO blocking and a publication overwrite race, plus directory-read error classification. Subsequent source-traced findings concern evidence and lifecycle boundaries; they are not all financial exploits.

| Finding | Severity in the review | Resulting correction |
| --- | --- | --- |
| FIFO bypass of service timeout | Medium, availability | Nonblocking no-follow descriptor open, regular-file/size validation. |
| Check-then-replace publication race | Low, transport integrity/availability | Atomic no-clobber hard-link publication preserves the first message. |
| Incomplete provider settlement/withdrawal report | Low, misleading component evidence | Requester requires both canonical transactions/events and matching state. The old outer harness already rejected residual credit; no complete-experiment false success was established. |
| Chain client reuse after unresolved delivery | Low, ambiguous-action lifecycle | Pending-hash latch prohibits another submission until a canonical outcome is known. No automatic agent retry or duplicate payment was demonstrated in the old flow. |
| Web3.py's unused CCIP Read feature | Medium upstream advisory, constrained fixture exposure | Disable secondary lookup behavior and test against a controlled loopback target. The package remains affected in general; this is an application mitigation. |
| Interrupted fixture startup cleanup | Low, resource cleanup | Cleanup on startup BaseException and re-raise; bounded tool version query. |
| Reorg uncertainty classified as service timeout | Low, failure classification | Abort on chain uncertainty before signing or publishing refund-wait. |

Further proxy tests reject mutated transaction hashes, receipt hashes/status, event amounts, and emitters. Original Solidity tests retain unauthorized-call, replay, deadline, invalid-result, reentrancy, failed-withdrawal, and forced-surplus coverage. No critical protocol-semantic flaw or unauthorized escrow payout was confirmed. This statement reports review findings; it is not an assertion that no undiscovered vulnerability exists.

## 12. Security-invariant assessment

All 18 [documented invariants](../../docs/SECURITY_INVARIANTS.md) were assessed. “Supported” below means scoped test evidence under the stated assumptions, not proof. The full [coverage map](../../docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) and security review retain named tests and residual limits.

| ID | Requirement and evidence assessment | Important boundary |
| --- | --- | --- |
| SI-01 | Required funding/payment signatures and caller authority supported by success and forged/missing-signature tests. | Key control is not proof of operator identity or verifier execution. |
| SI-02 | Per-authorization principal cap supported by valid extremes and overspend/value rejection. | No aggregate wallet cap; gas excluded. |
| SI-03 | Consumed nonce and terminal-record replay rejection supported. | Trusted persistent state and fresh-run policy remain necessary. |
| SI-04 | First-use expiry supported by exact timestamp boundary tests. | Funding expiry does not unwind an already-funded obligation. |
| SI-05 | Effective unused-nonce revocation and both execution orders supported. | Pending revocation is not retroactive; funded cancellation is absent. |
| SI-06 | Immutable signed terms supported by field mutation and after-signing tampering rejection. | Participants can deliberately sign new terms. |
| SI-07 | Domain/type/run binding supported by all-five-type digest and mutation tests. | Shared primitives/vectors are not independently audited cryptography. |
| SI-08 | Participant/agreement/result/nonce binding supported. | Addresses do not establish independent real-world ownership. |
| SI-09 | Wrong results cannot pay in tested contract paths, even with both evidence signatures. | Fixed public addition only; no provider effort or general computation proof. |
| SI-10 | Tested service failure/deadline paths deny payment and permit defined refunds. | Key-loss/post-work crashes can remain inconclusive. |
| SI-11 | Requester verification executes separately; contract also checks sum and consent. | Acceptance does not prove a particular program ran. |
| SI-12 | Unauthorized callers cannot invoke protected transitions or steal peer credit in tested paths. | Privileged host/RPC impersonation is outside the model. |
| SI-13 | Exact requester-only timeout refunds and exclusive terminal states supported. | Requester veto remains unfair to a correct provider. |
| SI-14 | Conservation, pull withdrawal, callback resistance and forced-surplus handling supported. | Compiler/EVM assumptions and independent audit remain open. |
| SI-15 | Fixed computation and strict messages use no AI validity oracle. | No Genesis consensus mechanism is implemented or evaluated. |
| SI-16 | Local endpoint/key/deployment controls and disabled CCIP exercised. | Application controls are not an OS egress or hostile-host sandbox. |
| SI-17 | Exact-hash reconciliation, uncertainty latch and canonical reorg/receipt checks supported for tested faults. | No automatic restart/replacement/rebroadcast or distributed finality claim. |
| SI-18 | Parser/message/range/runtime limits and tested cleanup paths supported. | No exhaustive spam schedule, OS quotas, or SIGKILL cleanup guarantee. |

The contract alone does not enforce all 18 requirements. Verification workflow, environment confinement, key ownership, receipt interpretation and process cleanup require Python/harness behavior and trusted infrastructure assumptions.

## 13. Limitations and threats to validity

**Requester-veto fairness:** A can receive correct work, refuse Acceptance, and later refund. B has no recourse or cost compensation. This is a documented design limitation, not a test failure concealed by conditional acceptance. Neither correct arithmetic nor escrow funding resolves fair exchange under these semantics.

**Internal validity:** The host, privileged RPC, EVM, compiler, cryptographic libraries, runner and evidence collection are trusted. Separate processes share an administrator; coherent fabricated RPC evidence is not excluded. Tests, golden vectors and implementation share some primitives and may share mistakes. Project-assisted code review is not an independent audit or formal verification.

**Construct/external validity:** Addition is intentionally trivial, publicly observable and cheap to repeat. It demonstrates no outsourcing advantage, provider effort, AI capability, physical truth, confidentiality, global permissionless discovery, Sybil resistance, heterogeneity across operators/hardware, or satellite/offline operation. A single operator-controlled Anvil chain supplies no decentralized finality or consensus-security evidence.

**Failure coverage:** Bounded fault samples do not cover every interleaving or lifecycle-wide outage. Automatic restart, pending-transaction replacement/rebroadcast, hard host failure, complete key-leak instrumentation and OS CPU/memory quotas remain gaps. Lost ephemeral keys can leave synthetic principal unusable until chain reset; no recovery from real-value loss is demonstrated.

**Supply chain and CI:** Pins/hashes do not prove publisher or binary trust. The reviewed Web3.py pin remains generally affected by its CCIP advisory despite feature-disable mitigation here. Old CPython/compiler references require maintenance review. Hosted CI executes untrusted PR code with network access; application loopback guards do not contain a malicious dependency/PR. Read-only permissions and absent production secrets limit authority but do not certify the runner.

**Quantitative interpretation:** Deterministic property checks and bounded fuzz/stateful samples are not statistical population estimates. No probabilistic confidence interval, comprehensive literature review, or measured superiority to another system is claimed.

## 14. Lessons learned

1. Signed requester consent and independently checkable computation validity are different predicates. Both can hold while provider fairness still fails.
2. Settlement credit and withdrawal must be verified separately; accepting a peer's status string is weaker than checking both canonical transactions/events and final accounting.
3. Small transport details matter: blocking special files and publication races can undermine otherwise explicit execution budgets without breaking cryptography.
4. Ambiguous RPC delivery must preserve the original transaction identity and stop new submissions when unresolved. A failed response is not evidence that nothing executed.
5. A local RPC URL policy does not automatically constrain secondary HTTP features of a dependency; unused CCIP Read required explicit disabling.
6. Negative and inconclusive outcomes, dependency trust and cleanup limits belong in the result, not only in implementation notes.

These lessons concern this prototype and its reviewed boundaries. They do not establish new cryptographic techniques or a general autonomous-economy protocol.

## 15. Open research questions

- Can provider payment liveness improve without silently removing bounded requester consent, and which additional trust, proof, timing or dispute assumptions would be required?
- Which nontrivial services have objectively checkable results at acceptable verification cost, and how should that cost be evaluated?
- What recovery model preserves economic intent across lost messages, ambiguous delivery, process failure and key loss?
- Which additional fault schedules and independently authored tests would most challenge the present evidence?
- How should authority and verification interact with future permissionless discovery, intermittent connectivity, contribution markets and independently operated infrastructure?
- Does a future independent network offer a justified advantage over integration with existing systems? What native-asset or consensus research, if any, would that require?

The **next proposed step is selecting the Experiment 002 research question through a separate design review**, including prior art, competing hypotheses, explicit trust boundaries and falsifiable acceptance criteria. This report selects no Experiment 002 design and authorizes no implementation. Existing Experiment 001 acceptance conditions remain visible during that review.

## 16. Conclusion

Experiment 001 achieved **CONDITIONAL PASS** for a deliberately narrow local research fixture. Two independent Python processes with distinct signing identities completed a signed agreement, independently verified a deterministic service result, and settled and withdrew a bounded synthetic payment on Anvil. The final validation milestone recorded 112 passing tests and assessment of all 18 invariants, with known findings and limitations disclosed.

The result supports reproducible investigation of cryptographically bounded autonomous economic coordination. It does not establish fair exchange, independent auditing, production-security assurance, a novel consensus mechanism, native blockchain, native asset, or the feasibility of the ultimate Genesis network. EVM/Anvil is a replaceable experimental substrate; the broader independent-network research direction remains open.

## 17. References and evidence index

The evidence snapshot is commit `f66cda91af5cb2f2da266fe11d90bc67c05cfc77`; all source links below are immutable at that revision.

| Evidence | Immutable reference |
| --- | --- |
| Final implementation/review milestone | [Commit f66cda9](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) |
| Final passing CI, counts and end-to-end output | [Run 39057757966](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966) |
| Experiment specification | [EXPERIMENT_001.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/experiments/EXPERIMENT_001.md) |
| Architecture and exact schemas | [EXPERIMENT_001_ARCHITECTURE.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/architecture/EXPERIMENT_001_ARCHITECTURE.md) |
| Security review and acceptance conditions | [EXPERIMENT_001_SECURITY_REVIEW.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/experiments/EXPERIMENT_001_SECURITY_REVIEW.md) |
| Coverage and historical failures | [EXPERIMENT_001_ESCROW_COVERAGE.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) |
| All 18 requirements | [SECURITY_INVARIANTS.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/SECURITY_INVARIANTS.md) |
| Escrow source | [Experiment001Escrow.sol](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/contracts/src/Experiment001Escrow.sol) |
| Agent/protocol/RPC/runner source | [genesis_experiment/](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/tree/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/sdk/python/genesis_experiment) |
| Solidity tests | [contracts/test/](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/tree/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/contracts/test) |
| Python tests, vectors and fault proxy | [tests/python/](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/tree/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/tests/python) |
| Compiler/property settings | [foundry.toml](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/foundry.toml) |
| Dependency pins/hashes | [DEPENDENCIES.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/DEPENDENCIES.md), [requirements.lock](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/sdk/python/requirements.lock) |
| Complete workflow | [foundry.yml](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/.github/workflows/foundry.yml) |
| Runner entry command | [run-experiment-001.sh](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/scripts/run-experiment-001.sh) |
| Architecture decision scope | [ADR 0001](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/docs/adr/0001-experiment-001-architecture.md) |
| Genesis charter | [MASTER_PLAN.md](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/blob/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/MASTER_PLAN.md) |

Relevant established standards are [EIP-712: Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712) and [ERC-3668: CCIP Read](https://eips.ethereum.org/EIPS/eip-3668), the latter a dependency feature deliberately disabled rather than a service used by this experiment. The specific dependency finding is [GHSA-5hr4-253g-cpx2](https://github.com/ethereum/web3.py/security/advisories/GHSA-5hr4-253g-cpx2). For the actual cryptographic library code, see the immutable [vendored OpenZeppelin source](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/tree/f66cda91af5cb2f2da266fe11d90bc67c05cfc77/lib/openzeppelin-contracts/contracts/utils/cryptography).

These references establish this report's technical/evidence scope. They are not a claim of a completed academic prior-art survey, protocol novelty, or endorsement by the referenced projects.

Focused external scrutiny is invited through [GitHub Discussions](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions), especially on requester-veto fairness, verification assumptions, failure recovery and security coverage. Please identify the evidence commit and distinguish observed counterexamples from proposed designs. Follow [SECURITY.md](../../SECURITY.md) for sensitive security reporting; do not post secrets or production credentials.
