# Experiment 002 Dependency and Reproducibility Review

**Task 009 current status: partial escrow published; acceptance FAIL / implementation BLOCKED.** See [implementation review](EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) for the pinned-Anvil fee-evidence contradiction and pending integration gates. Earlier design/readiness statements below are historical; design semantics remain unchanged.

**Historical Task 007 review, 2026-10-18 — B-DEP was BLOCKING at that milestone.** [Task 008 resolution](EXPERIMENT_002_BLOCKER_RESOLUTION.md) now selects constrained baseline reuse with compatibility evidence and explicit residual risks. The historical findings below remain intact; resolution is not a claim they disappeared. No packages/toolchains, locks, source, credentials or CI settings were changed. Exact baseline is commit [ded3fff](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/ded3fff203145cd8ec50fb3d91cca916a95cb331); [DEPENDENCIES.md](../../DEPENDENCIES.md) remains Experiment 001's evidence, not an approved Experiment 002 manifest.

## Baseline assessment

| Component / exact baseline | Assessment and required disposition |
| --- | --- |
| Solidity 0.8.28+commit.7893614a; Cancun, optimizer 200, viaIR | Old pin has known-bug version-range matches. Review selected source/library constructs and flags or validate a maintained replacement. No future Experiment 002 source exists to establish applicability/exclusion. |
| Foundry Forge/Anvil v1.0.0, commit 8692e926198056d0228c1e166b1b6c34a5bed66c | Paired versions and self-reported commit are reproducible identifiers, not binary trust. Review artifact checksums/provenance, supported host architectures and installer dependencies; do not silently install latest or reuse a global cache. |
| OpenZeppelin 5.2.0, acd4ff74de833399287ed6b31b4debf6b2b35527 | Candidate EIP712/ECDSA/non-transient ReentrancyGuard are established libraries, not new primitives. Existing vendored closure/hash checks pass. Recheck exact consumed paths and advisories for any changed closure/version; do not assume package audit covers composition. |
| forge-std 1.9.6, 3b20d60d14b343ee4f908cb8079495c07f5e8981 | Test dependency only; exact source closure/pin required. Cheatcodes and fixtures are privileged test tools, not evidence of hostile-chain resistance. |
| CPython 3.12.1 | Old patch requires runtime/advisory maintenance review, separate from PyPI scanning. [Python lifecycle guidance](https://devguide.python.org/versions/) distinguishes branch support from using a current security patch. No replacement runtime is installed/selected here. |
| Web3.py 7.14.0 | Fresh exact-version OSV query still reports GHSA-5hr4-253g-cpx2 and PYSEC-2026-3414. [Upstream advisory](https://github.com/ApeWorX/web3.py/security/advisories/GHSA-5hr4-253g-cpx2) lists 7.15.0 as a patched version, but that is not an adoption decision or full compatibility assessment. Existing unused-CCIP feature-disable mitigation must remain; retain loopback/proxy/redirect guards even after any upgrade. |
| eth-account 0.13.7; eth-abi 6.0.0; eth-utils 6.0.0; transitive lock | Existing [typed-data API](https://eth-account.readthedocs.io/en/v0.13.7/eth_account.html) produced public vectors with matching ABI hashes/recovered signers. OSV found no other package matches, not a vulnerability-free guarantee. Recheck EIP-712 encoding, 65-byte policy and vectors under any replacement tuple. |
| Immutable checkout/setup-python/toolchain action SHAs | Current read-only CI uses no production secrets or public blockchain. Latest baseline CI warns that Node 20 actions are forced to Node 24. Review runtime compatibility separately; a pinned action can still download mutable/unverified tool artifacts. No workflow edit here. |

## Observed checks and limits

Queried **39 exact locked PyPI package versions** once via the public OSV batch API. One package, web3 7.14.0, returned the two IDs above; the previous security review records their related CCIP finding. A package database can miss advisories, native/runtime issues, malicious maintainers or newly discovered vulnerabilities. No claim of a complete dependency audit. Local `pip check` reports no broken installed requirements; vendored checksum verification passed. These checks are not new contract/agent execution evidence.

Inspected upstream [Solidity bug inventory snapshot](https://github.com/ethereum/solidity/blob/bbfadd4df957aede94abf02c44d2a416e4f1315a/docs/bugs.json), SHA-256 `7766acac0c69aa152c98bc4fefa97679c19a56eac997e3043ea6738c764a23df`. Version ranges include SOL-2026-6 (named custom-error arguments, viaIR), SOL-2026-4 and SOL-2026-2 (mutual-recursion spill behavior, viaIR), SOL-2026-1 (transient-storage helper, viaIR/Cancun), SOL-2025-1 (storage array slot overflow), and SOL-2026-5 (legacy pipeline condition, viaIR=false). A range match is not evidence that the proposed escrow is exploitable; the legacy-only condition differs from current flags and non-transient guards avoid one known feature, but source-level triage is still required.

**Temporal source caveat:** the retrieved inventory also contains SOL-2026-7 with a linked publication dated 2026-10-22, later than this review. It is not treated as an established finding available on 2026-10-18, nor as proof that a listed future fix is released. Validate publication/release chronology before relying on that entry. [Upstream bug documentation](https://docs.solidity.org/en/latest/bugs.html) is mutable; the snapshot records exactly what was consulted. No recommendation to adopt an unverified future release follows.

## Reproducibility anchors

All baseline pins and hashes remain in the immutable source commit. Reviewed file SHA-256 values:

| File | SHA-256 |
| --- | --- |
| foundry.toml | 85fa0da36ec65d2b8cef04068a191d37958291560f1437467d307403bf02d422 |
| dependencies.sha256 | 22f2cc7daaf384a5837c47bb5cae84c13488209f579885a5060f0a85621c977c |
| sdk/python/requirements.lock | e2450075b5170c2e4f08d12f6ea1244b89445c0b68d70f1b7dbfca404168e380 |
| .github/workflows/foundry.yml | 7714d7effec04ddd32ebddb66d76331269025a516f7c36c93e3277618dfbfccd |

The existing fresh-checkout commands in [contracts](../../contracts/README.md), [Python](../../sdk/python/README.md) and [published report](../../research/reports/EXPERIMENT_001_REPORT.md) apply to Experiment 001. Initial HTTPS downloads, package availability, platform wheels and upstream installer trust remain dependencies. Do not invent an Experiment 002 runner command before one exists. Future setup must pin/check exact binaries, compiler, source closure and Python wheel hashes, refuse unreviewed source-build fallback, and validate on fresh Ubuntu plus the supported local platform. Runtime must remain loopback-only without a public fork; installation access is a distinct phase.

## Blocking disposition and exit evidence

**B-DEP:** final choice between validated maintained versions and documented constrained baseline reuse remains unresolved. A follow-up maintenance/specification task must produce an exact compatible tuple and hashes, advisory/compiler applicability rationale, cross-language vector results and baseline regressions, plus tested installation commands. Explicitly accept residual local-only risks if reusing affected/old versions; do not describe mitigations as general fixes. Keep Experiment 001's historical pins/evidence intact or handle any maintenance change in a separately reviewed scope. No unsupported dependencies were introduced in this task.

The [final specification](EXPERIMENT_002_FINAL_SPEC.md) also records **B-FEE**, a separate finite operator fee-policy decision. These are actionable release gates, not a requirement to solve general fairness or native-token economics before the local experiment.
