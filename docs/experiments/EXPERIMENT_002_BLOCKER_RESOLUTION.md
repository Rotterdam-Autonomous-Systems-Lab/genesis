# Experiment 002 Blocker Resolution and Architecture Review — Task 008

**Task 009 current disposition: partial contract implementation; acceptance FAIL / implementation BLOCKED.** [Fee-evidence review](EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) supersedes earlier READY status without changing the frozen design or budgets. Pinned Anvil receipt effectiveGasPrice conflicts with the actual capped wallet debit; dependency/fee-evidence compatibility is reopened. ADR 0002 remains accepted design only.

**2026-10-18 — B-DEP RESOLVED (constrained baseline reuse); B-FEE RESOLVED (explicit local policy). Implementation readiness: READY for a separately authorized bounded implementation.** This is design readiness, not an implemented, audited, deployed or experimentally accepted Experiment 002.

## 1. Exact dependency selection

Select the existing tested tuple for this disposable local experiment, without changing Experiment 001's files, flags or pins:

| Component | Exact selected baseline |
| --- | --- |
| Forge, Anvil and Cast | Foundry v1.0.0, commit 8692e926198056d0228c1e166b1b6c34a5bed66c. |
| Solidity | 0.8.28+commit.7893614a, Cancun, optimizer 200 runs, viaIR=true; no custom optimizer sequence. |
| OpenZeppelin Contracts | 5.2.0, acd4ff74de833399287ed6b31b4debf6b2b35527; existing unmodified source closure only. |
| forge-std | 1.9.6, 3b20d60d14b343ee4f908cb8079495c07f5e8981, test helpers only. |
| CPython | 3.12.1; no runtime change. |
| Python libraries | Web3.py 7.14.0, eth-account 0.13.7, eth-abi 6.0.0, eth-utils 6.0.0 and all 39 exact packages/hashes in the existing requirements.lock. |
| CI | Existing immutable action SHAs and read-only workflow in [DEPENDENCIES.md](../../DEPENDENCIES.md); no new privileged runner, secret or installer. |

Lock SHA-256: `e2450075b5170c2e4f08d12f6ea1244b89445c0b68d70f1b7dbfca404168e380`. Dependency source/flags are anchored to [d05d690](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d05d69008229cbb10f437eb622d88b11cc09bfdd). This selects compatibility and explicitly accepts residual risks for synthetic local-only work; it does not declare the old versions safe for production or preferable for general use.

## 2. Reproducible compatibility evidence

Local host: macOS 12.7.6 x86_64, CPython 3.12.1. Foundry commit checks passed; compiler binary SHA-256 matches the recorded macOS checksum `81515b0e53deaa266d549545ccaac0a5a96e6d4e8201c77f673b2c710976d9ea`. All 39 installed package versions match the hash-locked manifest; `pip check` passed; all 35 vendored file checksums passed.

- Fresh offline build: 37 files compiled successfully in **55.91 seconds**, with existing warnings, including the intentional forced-transfer test helper. This is a local setup observation, not a performance benchmark.
- Original Solidity suite: **58 passed**, zero failed/skipped; unchanged fuzz 256 and stateful 128 x 64 budgets retained.
- Original Python suite, after build completed: **54 passed** in 76.680 seconds.
- Public Experiment 002 vectors: **25 typed digests** recomputed using Cast ABI/Keccak; **34 public signatures** recovered identically by Python and Anvil's EVM ecrecover precompile. No keys, transactions or contract deployment in this compatibility probe. This checks encoding/primitive interoperability, not escrow semantics or Solidity implementation of the future contract.
- Additional unchanged Experiment 001 controls: success settled/withdrew; requester refusal refunded/withdrew. Both stopped all children. Measured gas is in the [fee model](EXPERIMENT_002_BOUNDED_COST_MODEL.md); these are baseline controls, not Experiment 002 results.

**Preserved setup failure:** an initial Python run started while `forge build --force` had removed its required artifact, yielding one failure and 40 errors. The build dependency was corrected by running sequentially; all 54 then passed. No assertion or source was weakened. A local optional Black entry point also lacked its installed module; no dependency was installed to repair that unrelated formatter. Syntax checks and the compatibility scripts themselves pass. Current [Ubuntu regression CI](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39116760576) passed for the baseline; it does not yet execute the new compatibility scripts or any Experiment 002 implementation.

Use the [compatibility instructions and checks](../../research/compatibility/experiment002/README.md) to reproduce. Installation remains a separate HTTPS-dependent step; runtime uses only local files/loopback. No package upgrade, node implementation or Experiment 002 contract was introduced.

## 3. Constrained reuse and source restrictions

The [Task 007 dependency review](EXPERIMENT_002_DEPENDENCY_REVIEW.md) remains valid historical evidence. Its existing advisory matches are not erased:

- **Web3.py CCIP Read:** keep global CCIP disabled and reject lookup/proxy/redirect/public RPC fallbacks. The upstream [CCIP advisory](https://github.com/ApeWorX/web3.py/security/advisories/GHSA-5hr4-253g-cpx2) remains applicable in general. Existing rejection regression passes; feature disable is not a patched library.
- **Compiler:** use no mutual recursion, transient storage/guard, named-argument custom-error `require`, storage arrays with writable indices/manual slots, or byte-array element deletion. Use the existing fixed short EIP-712 name/version and unchanged non-transient OpenZeppelin guard. Known-bug triage below is a constraint on future source, not a claim to have inspected code that does not exist.
- **Python/installer provenance:** old runtime patches, upstream binary trust, platform wheel availability and unknown advisories remain accepted residual risks only inside a trusted disposable local environment with no production keys or public inputs/services. No general advisory-clean claim.

| Inventory item | Scoped disposition |
| --- | --- |
| SOL-2026-1 transient storage helpers | Exclude transient storage/guards; use existing storage-based guard. |
| SOL-2026-2 / SOL-2026-4 recursive spill behavior | Exclude mutual recursion and unreviewed assembly changes. |
| SOL-2026-6 named custom-error arguments | Use explicit revert checks; exclude that named-argument require form. |
| SOL-2026-5 legacy pipeline | viaIR=true differs from its listed viaIR=false condition. |
| SOL-2025-1 storage-array slot overflow | No user-written storage arrays/manual indexing/slot arithmetic; existing short domain strings do not enter long-string fallback paths. |
| SOL-2026-7 postdated inventory entry | Preserve the [chronology caveat](EXPERIMENT_002_DEPENDENCY_REVIEW.md); no claim that a future publication/fix is established on this review date. Unknown optimizer risk is not eliminated. |

Before accepting any implemented component, verify its complete consumed source against these restrictions, rerun vectors/regressions and measure gas. A new compiler feature, dependency closure or advisory applicability reopens B-DEP; do not silently waive it. The local decision accepts bounded residual risk rather than pretending a complete audit exists. It selects no future Genesis L1 cryptography/compiler/VM.

## 4. Fee resolution and decision

[The bounded-cost model](EXPERIMENT_002_BOUNDED_COST_MODEL.md) selects explicit per-role transaction/gas/fee/run budgets and loss assumptions. Inspection found that the original [Chain.transact](../../sdk/python/genesis_experiment/chain.py) already signs maxFeePerGas=3,000,000,000 and maxPriorityFeePerGas=1,000,000,000. **Task 007 missed those existing fields**: B-FEE needed an explicit independently authorized cumulative model, not a claim that the baseline had no per-gas cap.

B-DEP and B-FEE are resolved for this restricted design. ADR 0002 is **Accepted for bounded local experimental design only**. Acceptance follows tested baseline interoperability, regressions, explicit source restrictions, bounded budgets and honest residual-risk disclosure. It does not follow merely from roadmap pressure, prove general fairness, or authorize implementation under Task 008.

Remaining implementation acceptance gates are normal evidence obligations: exact source/ABI/vector compliance, enforced signer budgets/timeouts/cleanup, measured gas below ceilings, all T01–T20 and cost controls, independent-result/canonical-accounting evidence, unchanged Experiment 001 regressions, and reviewed CI. If these fail, report failure/reopen design; do not increase caps or weaken assertions automatically. Public-result leakage, censorship/deadlines, absent callers, key loss, cloned ledgers and trusted host/RPC remain limitations. Useful-work uniqueness, issuance eligibility, consensus/Sybil security and native demand remain separate research.
