# Experiment 002 Corrected-Anvil Validation — Task 011

**2026-10-18 — PASS for bounded local infrastructure compatibility; required Ubuntu publication CI is the cross-platform gate.** The fee blocker is resolved for the explicit profile in [ADR 0005](../adr/0005-experiment-002-corrected-anvil-baseline.md) when that CI passes. This is not Experiment 002 acceptance: incomplete agents remain paused and all integration/security gates remain. No authorization, fee cap, wallet budget, escrow rule or reconciliation predicate was weakened.

## Exact correction and candidate selection

[Task 010](EXPERIMENT_002_FEE_INVESTIGATION.md) established the old node's missing clamp in derived RPC fee fields. The exact receipt correction is [75151e9cae397d34034c1d03defc4f94b6363a3c](https://github.com/foundry-rs/foundry/commit/75151e9cae397d34034c1d03defc4f94b6363a3c). Inspection of that immutable source confirms helper-based fee calculation for both receipt and mined-transaction reporting; its parent still had the receipt defect. The exact nightly artifact lookup returned 404, so it was not treated as an obtainable release binary.

The reviewed v1.5.1 source still has the receipt defect. Select **v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628**, the smallest suitable packaged family reviewed after that release, rather than the larger v1.8.5 proposed in Task 010. Git ancestry confirms the candidate contains the correction (240 commits ahead). This is not a claim of a globally minimum possible/custom revision. Preserve the rc1 label; GitHub's release metadata nevertheless marks it non-prerelease. The [candidate source](https://github.com/foundry-rs/foundry/blob/b272ce3366987406406e9eb1b82596653a3ad628/crates/anvil/src/eth/backend/mem/mod.rs#L3109) uses the standard helper in both reporting paths, the second at line 3766.

Only **Anvil** changes for future Experiment 002. Forge/Cast remain v1.0.0 (`8692e926198056d0228c1e166b1b6c34a5bed66c`), Solidity stays 0.8.28/Cancun/viaIR/optimizer 200, and OpenZeppelin, forge-std, Python 3.12.1 and all hash-locked Python dependencies stay unchanged. Force **--hardfork cancun**, rather than accepting the newer node's default EVM revision. The candidate is installed beside the original node, never over it or through global PATH changes. Experiment 001 retains its original default and published evidence.

## Source identity, integrity and provenance limits

[Manifest](../../research/compatibility/experiment002/anvil-candidate.json) and [provenance](../../research/compatibility/experiment002/task011-provenance.json) record exact identities. Source SHA-256 is `2de852961ab58eb50afe5b9b87e8823078283095bdbbb40a5e30e8cf9be34c16`; its immutable commit URL is verified before installation. Archives are official Foundry release assets; their hashes match the upstream published digests, and extracted Anvil bytes have additional fixed hashes:

| Platform | Archive SHA-256 | Anvil binary SHA-256 |
| --- | --- | --- |
| macOS x86_64 | ce8d6ebbf5a8ab1be36c298c6167dd97798d04c96d1342b50253550c1e523eca | 73036c6402dcbf5d1b3e5d933f9a3b64df83dac828b309f5deef930003050e92 |
| Linux x86_64 | 2e4378e23e93c35d938bd6faeeff8bc48aa5faf081033a9235309172bfb76d5f | 8c0444f7196c0a345ffb67254d77524a745cd9a307fdd651b7e48d83947a4077 |

The installer checks source, archive and binary hashes before execution, extracts only a bounded regular `anvil` member, and publishes it atomically without overwriting other tools. The loader rechecks the binary hash before `--version`/node execution, then verifies the exact source commit/version. Wrong bytes, wrong reported commit and unsupported platforms fail closed; no generic version bypass or RPC shim is added.

Before local execution, Mach-O inspection established x86_64 and minimum macOS 10.12, compatible with the current macOS 12.7.6 host. Existing linked libraries, including libusb, load successfully; the local libusb hash is recorded. Linux archive/extracted bytes were independently hash-checked locally without executing an ELF on macOS; Ubuntu runtime/loading/regressions are verified by the required CI steps. No operating-system package, global tool, authentication setting or credential changed.

The release attestation URL file was downloaded/hash-checked, but `gh attestation verify` returned HTTP 404 for the archive lookup. **No successful cryptographic attestation or reproducible source-build claim.** Provenance relies on HTTPS/GitHub publisher trust, recorded source/asset hashes, source ancestry, self-reported build commit and behavioral evidence. Hashes do not prove a clean supply chain. A source build was considered but unnecessary after successful verified downloads; the pinned source requires Rust 1.89, while the installed local Rust is 1.83.0. No Rust installation/build or custom patch was performed. Cargo source/lock hashes are recorded for later review, not a complete consumed-dependency audit.

## Identical negative and positive controls

[Comparison evidence](../../research/compatibility/experiment002/task011-comparison.json) archives **44 fresh local fixtures**: the identical 11 fee cases repeated twice on each node. Same compiled FeeWitness, signing algorithm, gas limit, principal-free call, fee/priority caps, initial wallet allowances, timestamps/observations, strict oracle and integer arithmetic. The old node uses its existing Cancun default; the new node explicitly selects Cancun and checks the reported hardfork and absence of a fork URL.

| Gate | Original v1.0.0 | Corrected v1.6.0-rc1 |
| --- | --- | --- |
| Included witness/revert cases | 20 | 20 |
| Strictly reconciled cases | 12 | **20** |
| Contradictory fee reports | 8 | **0** |
| Above-cap non-inclusions | 2, no debit/consumed nonce | 2, no debit/consumed nonce |
| All children stopped | Yes | Yes |
| Original Task 009 strict reproducer | Exit 2; reporting contradiction | Identical checks reconcile; no contradiction |

Previously contradictory base fees 2,000,000,001; 2,625,000,000; and 3,000,000,000 wei/gas, plus the clamped revert case, now reconcile exactly. RPC transaction gasPrice, individual receipt effectiveGasPrice, block-receipt effectiveGasPrice, EVM GASPRICE/BASEFEE and isolated sender debit all agree with EIP-1559. No floating-point tolerance, computed-value substitution or altered caps. At baseFee=3,000,000,001 the transaction remains unincluded during bounded observation; no liveness promise follows.

The original escrow probe on the candidate reports gasUsed=48,076, inclusion baseFee=2,625,000,000, signed maxFee=3,000,000,000 and priority cap=1,000,000,000. Receipt effectiveGasPrice and observed charged rate are both **3,000,000,000**; actual debit and reported fee are both **144,228,000,000,000 synthetic wei**. Deployment is still **1,632,623 gas**, below 2,000,000. The unchanged old control still reports 3,625,000,000 and fails the same check. Thus the correction fixes infrastructure reporting, not the economic limits or authorization semantics.

Every diagnostic wallet is fresh with only the specified initial synthetic allowance (deployer 6*10^15, requester 48*10^15), no top-ups; one deployment and one requester attempt per matrix fixture. Limits remain gas<=2,000,000, maxFee<=3 gwei, maxPriority<=1 gwei, principal<=10^15 and approved cumulative/closing budgets unchanged. These diagnostics do not implement or prove the incomplete agent budget manager.

## Regression evidence and preserved setup failures

Local results, unchanged test assertions:

- **86 Solidity tests passed**, no failures/skips; 58 original plus 28 Experiment 002. Fuzz 256 and stateful 128 x 64 budgets remain unchanged. Compiler/source/library restrictions are retained.
- **54 original Python tests passed on the original node**, then **the same 54 passed on the verified candidate**. An explicit test-only harness selects the preverified node and Cancun; existing escrow/agents/tests are not edited. Successful service/settlement and requester-refusal/refund controls both run with separate processes and cleanup.
- **14 existing research fee/oracle tests passed**, retaining the old node's negative control; **nine new candidate integrity/fee tests passed**, including rejection of corrupted candidate evidence and unverified binaries. Together with both Python runs and Solidity, this is **217 unittest/Foundry test executions**, not 217 unique test definitions.
- Both nodes matched **25 EIP-712 digests and 34 public signatures**, using unchanged Cast/Python/frozen fixtures; **20 integer fee-model cases** also pass. These probe cases are separate from the 217 count.
- Source/vendored hashes, exact tool pins, pip consistency, Markdown links, workflow lint and formatting checks pass. CI installs only the isolated pinned node and repeats the same Linux checks with existing read-only permissions and immutable actions; it never uses public blockchain RPC or production credentials.

[Candidate regression evidence](../../research/compatibility/experiment002/task011-regressions.json) records actual node identity separately from Experiment 001's historical hardcoded Foundry metadata; that old label is not evidence the candidate run used v1.0.0. Original control prefunding is preserved and does not claim enforcement of Experiment 002's tighter future wallet policy.

Two harness mistakes are retained in provenance: first, missing child-process PYTHONPATH caused one FIFO test setup failure (53/54 passed); exporting the same path as the original invocation fixed it, then all 54 passed unchanged. Second, nodeInfo preflight initially assumed nullable forkConfig; the actual object contains forkUrl=None. Correcting the schema check retained explicit Cancun/no-fork requirements and the full matrix passed. No failed assertion was removed or weakened.

## Exact reproduction

Install the existing [baseline](../../DEPENDENCIES.md) first. All paths below are repository-relative; initial source/archive/package installation requires HTTPS. Tests thereafter use only local files and loopback.

```sh
export PATH="$PWD/internal/tools/foundry:$PATH"
scripts/check-toolchain.sh
scripts/check-dependencies.sh
forge fmt --check
forge build --offline
forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
internal/agent-venv/bin/python research/compatibility/experiment002/check_vectors.py
internal/agent-venv/bin/python research/compatibility/experiment002/check_fee_bounds.py
internal/agent-venv/bin/python -m unittest discover -s research/compatibility/experiment002 -p 'test_fee_*.py' -v
internal/agent-venv/bin/python research/compatibility/experiment002/install_anvil_candidate.py
internal/agent-venv/bin/python -m unittest discover -s research/compatibility/experiment002 -p 'test_candidate_*.py' -v
internal/agent-venv/bin/python research/compatibility/experiment002/check_vectors.py --candidate
internal/agent-venv/bin/python research/compatibility/experiment002/compare_anvil_baselines.py
internal/agent-venv/bin/python research/compatibility/experiment002/candidate_regressions.py
```

An already downloaded official archive can be supplied with `install_anvil_candidate.py --archive path/to/foundry.tar.gz`; the same integrity checks apply. The default old diagnostic and original reproducer remain blocking by design; the comparison command requires that negative control **and** corrected positive evidence to pass. `investigate_fee_receipts.py --candidate --repeats 2` returns 0 only when its identical strict gate finds no included contradiction. It never chooses a different binary from a peer or silently updates PATH.

Fresh CI copies the already version-pinned control Anvil/Cast into ignored local paths for the original signature probe, then installs the separate candidate. No global binary is replaced. Results and raw RPC/state evidence stay in ignored internal output or the deliberately public research JSON, never private keys/raw signed transactions.

## Decision, risks and next dependency

**PASS for this bounded compatibility profile**, conditional on the publication's Ubuntu CI gate. When CI passes, B-ANVIL-FEE-EVIDENCE and the node portion of B-DEP are resolved under ADR 0005; B-FEE limits remain unchanged. A subsequent authorized Task 009 continuation may use the corrected node. **Task 011 does not resume or accept Experiment 002 agents.** Their full T01–T20/P2/fee/resource controls and security assessment remain the next implementation/evidence dependency.

Host/RPC trust, same-host process isolation, leaked public results, censorship/deadlines/finality, missing callers/keys and supply-chain risks remain. Web3's existing CCIP mitigation and old compiler/runtime limitations are preserved; no comprehensive advisory-clean, independent-audit or production-security claim. The rc1 node adds dependencies/features despite Cancun selection; new platforms/features or integrity/CI failures reopen compatibility. Neither success nor the EVM substrate validates Genesis's future independent blockchain, consensus, native asset or adoption.
