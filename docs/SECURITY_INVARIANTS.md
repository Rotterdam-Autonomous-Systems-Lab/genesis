# Experiment 001 Security Invariants

Status: **proposed, testable requirements; not verified findings**. Scope is the local [Experiment 001](experiments/EXPERIMENT_001.md) design in [the architecture specification](architecture/EXPERIMENT_001_ARCHITECTURE.md). Every positive and adversarial test below is required evidence for an eventual implementation; no such code or test result is supplied by this task.

## Guarantee boundary

Signature binding assumes secure Ethereum-standard hashing/signatures, uncompromised signers, exact encoding, correct library integration, and correct EVM execution. Contract enforcement is a proposed code property, not an existing cryptographic proof. Off-chain verifier execution and local-only deployment are environmental/process properties. The trusted local host can inspect memory, impersonate RPC accounts, alter time/state, or reset the chain; this experiment offers no security against that administrator. Keys identify control, not persons, intelligence, or independent ownership in the real world.

Principal means the signed synthetic escrow price; gas is excluded. First-use authorization expiry/revocation and funded-agreement settlement deadlines are distinct. Every rejected contract call must leave records, nonce status, credits, accounting totals, and contract principal unchanged (apart from caller gas outside escrow).

## SI-01 — No funding or payment without valid authorization

- **Threat:** forged consent, unauthorized lock or payout.
- **Enforcement:** fund requires A caller, A/B Agreement signatures and A Authorization; settle requires B caller, B Result signature and A Acceptance, correct stored bindings and computation. No alternative credit path or admin.
- **Positive test:** valid complete flow credits B exactly once and permits B withdrawal.
- **Adversarial test:** remove or forge each signature independently; substitute an unrelated signer; invoke settle without funding. All revert without credit.
- **Limitations:** signatures represent key control; stolen keys or a trusted-host compromise can create otherwise valid consent. They do not prove an agent ran a particular verification program.

## SI-02 — Principal never exceeds the authorization maximum

- **Threat:** overspending or amount substitution.
- **Enforcement:** fund checks exact msg.value=Agreement.price, 0 < price <= Authorization.maxAmount <= MAX_PRICE (10^15 synthetic wei). Settlement/refund only credit stored price once.
- **Positive test:** price=maxAmount=MAX_PRICE succeeds; smaller price consumes the nonce without granting reusable remainder.
- **Adversarial test:** price=maxAmount+1, maxAmount=MAX_PRICE+1, zero price, under/overpaid msg.value all revert. Check multiple accepted actions cannot reuse one cap.
- **Limitations:** per-authorization principal bound only; no wallet-wide aggregate budget or gas cap enforced by escrow. Compromised A can sign distinct authorizations.

## SI-03 — Consumed authorizations and terminal records cannot replay

- **Threat:** repeated funding, duplicate payouts, retry duplication.
- **Enforcement:** requester-scoped nonce Unused -> Consumed atomically with fund; agreementId uniqueness; Funded -> Settled/Refunded terminal states never reopen; nonce remains Consumed after refund/withdraw.
- **Positive test:** independent nonce/new agreement can fund after prior completion.
- **Adversarial test:** retry consumed authorization, substitute another agreement with same nonce, fund an existing ID with a fresh nonce, replay settle/refund after success or withdrawal. No duplicate credit or funding.
- **Limitations:** state persistence is assumed. Fresh runId and no signature reuse separate resets; identical deliberately cloned chain/state/domains are not cryptographically distinguished.

## SI-04 — Expired first-use authorizations are rejected

- **Threat:** stale spending permission or deadline off-by-one.
- **Enforcement:** fund requires block.timestamp < validUntil <= fundingDeadline and block.timestamp < fundingDeadline.
- **Positive test:** fund at validUntil-1 with valid terms.
- **Adversarial test:** fund at validUntil and validUntil+1; independently test fundingDeadline equality and +1. Reverts; nonce remains Unused.
- **Limitations:** timestamps are chain values controlled by the local operator. Expiry does not unwind already-consumed authorization; settlement has its own deadline (SI-10).

## SI-05 — Effective revocation blocks new use

- **Threat:** revoked spending permissions or revocation races.
- **Enforcement:** only requester can mark its Unused nonce Revoked. Revoked nonce cannot fund. Effectiveness is canonical transaction execution. Consumed nonces cannot be revoked or reset.
- **Positive test:** revoke then fund fails; an unrelated Unused nonce remains usable.
- **Adversarial test:** stranger attempts A nonce revocation; funding and revocation ordered both ways; repeated revocation; revocation after funding. Fund-first preserves the obligation and allows otherwise valid settlement.
- **Limitations:** pending revocation cannot retroactively stop earlier funding. No Acceptance revocation or funded-escrow cancellation exists; this is explicitly a first-use permission model.

## SI-06 — Signed agreement terms are immutable

- **Threat:** price, inputs, parties or deadlines changed after consent.
- **Enforcement:** both parties sign identical full Agreement digest; contract derives ID and stores immutable fields. Changed terms require new salt/digest and both signatures.
- **Positive test:** both valid signatures over identical terms fund successfully.
- **Adversarial test:** mutate each field individually while keeping signatures; alter stored-term payload for settlement. Reject; original record remains intact.
- **Limitations:** parties can knowingly sign new terms; signatures do not establish informed human consent. Discovery offers are not enforced as contract terms.

## SI-07 — Signatures bind chain, contract, type and run

- **Threat:** cross-chain, cross-contract, cross-purpose or reset replay.
- **Enforcement:** fixed EIP-712 name/version with active chainId and verifyingContract; distinct primary types; all payloads match immutable nonzero runId. No personal-sign fallback.
- **Positive test:** Python and Solidity derive identical digests under the intended domain for every type.
- **Adversarial test:** wrong chainId, another deployment address, changed name/version, wrong runId, Advertisement signature as Agreement signature, previous-run signature. Reject.
- **Limitations:** depends on exact encoding and domain configuration. Chain ID/address alone do not distinguish cloned networks; local freshness and trusted runner remain assumptions.

## SI-08 — Authorization binds intended parties and agreement

- **Threat:** redirection to another provider, requester, service, or economic action.
- **Enforcement:** authorization requester/provider equal stored signed parties; agreementId derives all terms; Acceptance binds ID, Result digest, consumed nonce and runId; fixed beneficiary.
- **Positive test:** intended A/B settle the intended agreement.
- **Adversarial test:** swap A/B, change provider, use authorization/Acceptance from a second agreement, replace serviceId, or redirect withdrawal recipient. Reject or interface disallows redirection.
- **Limitations:** addresses do not prove real-world distinct ownership. Fixture asserts A != B but cannot prevent collusion or common ownership elsewhere.

## SI-09 — Invalid service results never trigger payment

- **Threat:** fabricated computation, dishonest provider, erroneous requester verifier.
- **Enforcement:** contract recomputes stored uint64 x+y as uint256 and checks Result.value, provider signature, and Acceptance digest. No result-based credit until all predicates pass.
- **Positive test:** (7,11)->18; (0,0)->0; (uint64 max,uint64 max)->2^65-2.
- **Adversarial test:** wrong value, wrong inputs, overflow/out-of-range input encoding, tampered B signature; even a valid A Acceptance for a wrong B-signed result cannot settle.
- **Limitations:** establishes correctness of this public arithmetic only, not B's effort, sensor truth, general computation, confidentiality, or outsourcing benefit.

## SI-10 — Failed or timed-out work cannot authorize payment

- **Threat:** paying despite failure, late results, conflicting settlement/refund windows.
- **Enforcement:** no result/Acceptance means no settle; timestamp < settlementDeadline required; refund at >= settlementDeadline only; funding rejects settlementDeadline more than 3600 seconds ahead of chain time. Terminal state excludes the competing transition.
- **Positive test:** valid settlement at deadline-1 succeeds; unfunded/failed work produces no credit; timeout refund at equality credits A.
- **Adversarial test:** settle at equality/+1, funding with excessive lock horizon, refund before deadline, settle after refund, refund after settle, reordered terminal calls. Reject incompatible action.
- **Limitations:** no automatic scheduler or liveness guarantee; A must call refund and chain must progress. B may lose uncompensated effort if A withholds its receipt.

## SI-11 — Independent verification and consent gate settlement

- **Threat:** trust in provider claim or a bare off-chain “verified” flag.
- **Enforcement:** A's workflow validates B evidence and recomputes independently before signing; contract separately recomputes and requires A Acceptance. Harness evidence records comparison and public digests.
- **Positive test:** separately implemented A verifier matches B's result and produces correct Acceptance; contract check agrees.
- **Adversarial test:** bypass A workflow and submit correct result without Acceptance (reject); faulty A verifier signs wrong result (contract rejects); transport substitutes a verified=true flag (reject schema).
- **Limitations:** A's signature is not proof its verifier ran. Off-chain execution evidence depends on harness integrity; only arithmetic and signed consent are enforceable on-chain.

## SI-12 — Unauthorized callers cannot change escrow state

- **Threat:** third-party funding, cancellation, settlement, refund or withdrawal theft.
- **Enforcement:** A-only fund/refund; B-only settle; caller namespace for revokeUnused; withdraw pays only msg.sender's positive credit. No admin or upgrade bypass.
- **Positive test:** allowed actors exercise each operation under valid state/time.
- **Adversarial test:** third party and wrong counterparty invoke each operation; copy signed mempool payload from another address; attempt beneficiary change or direct ETH deposit. Reject.
- **Limitations:** an unrelated user may revoke its own unused nonce, not A's. Valid B may copy its own signed transaction; public data reveals terms. Host impersonation is trusted out of scope.

## SI-13 — Refunds are deterministic, exact and exclusive

- **Threat:** arbitrary dispute payout, partial confiscation or double refund.
- **Enforcement:** only Funded at/after deadline, caller A; fixed exact price credited solely to A; state Refunded before any withdrawal; no partial refund, early cancel, admin adjudication or fees.
- **Positive test:** absence, incorrect result, or disagreement reaches exact A refund credit at deadline; A withdraws its credit.
- **Adversarial test:** B/stranger requests refund, duplicate refund, refund after Settled, refund value mutation. Reject; B gets no timeout credit.
- **Limitations:** deliberately favors requester control; no fairness guarantee or compensation for B. Lost A key can leave credit/escrow unusable within the run.

## SI-14 — Accounting and withdrawals resist duplication and reentrancy

- **Threat:** stolen escrow, cross-agreement drains, callbacks, forced-ETH accounting confusion.
- **Enforcement:** atomic terminal credits, per-account credits, checks-effects-interactions, nonReentrant mutators; withdrawal failure reverts credit debit; liabilities equal deposits-withdrawals and are <= balance. Forced ETH creates no credit.
- **Positive test:** multiple distinct agreement settlement/refund sequences preserve totals; successful withdrawals decrease correct credit once.
- **Adversarial test:** a contract test receiver reenters any mutator, rejects transfer, or forces ETH; assert no duplicate payout, no unrelated record change, preserved failed-withdrawal credit, correct surplus treatment.
- **Limitations:** attack receivers are test harness actors, not supported agent contract wallets. Unaccounted forced surplus has no rescue path. Guard correctness/library integration needs review.

## SI-15 — AI output has no consensus or state-validity authority

- **Threat:** nondeterministic intelligence output decides validity or payment.
- **Enforcement:** no model/oracle call; supported fixed integer computation, standard signatures, explicit state/time predicates determine escrow transitions on the local EVM.
- **Positive test:** complete flow without any AI service or framework.
- **Adversarial test:** inject free-form natural language, alternate service, forged “AI approved” claim, nondeterministic result, or arbitrary code in message. Reject before signing or contract validation.
- **Limitations:** local Anvil consensus/finality is assumed; this experiment does not research or prove a Genesis consensus design.

## SI-16 — No production funds or public-network deployment

- **Threat:** operational misuse, real-value transactions, credential exposure.
- **Enforcement:** loopback-literal RPC only, no fork URLs/proxy/redirect; expected chainId/runId/code hash; fresh ephemeral keys and synthetic balances; refuse public endpoints; no key logging/files. This is a process boundary, not a cryptographic guarantee.
- **Positive test:** local preflight succeeds and all artifacts contain only public identifiers/digests.
- **Adversarial test:** remote/public/DNS endpoint, proxy configuration, wrong chainId/runId/code, known/default key use, or secret-bearing log attempt causes refusal/redaction; inspect artifacts for private-key exposure before release.
- **Limitations:** trusted host can spoof chain metadata or copy code to a public network; chain ID 31337 alone does not ensure locality. No implementation/deployment is authorized by this specification task.

## SI-17 — Retrying an ambiguous action does not duplicate economic intent

- **Threat:** RPC loss, retries with new authorizations, stale receipt success claims.
- **Enforcement:** serialize account transaction nonces; reconcile canonical receipt/hash and state; preserve semantic action on rebroadcast/replacement; new auth nonce never automatic; abort inconclusive on reset/reorg.
- **Positive test:** drop response after successful fund, reconnect, observe consumed nonce and Funded state without funding again or creating duplicate credit.
- **Adversarial test:** drop/reorder messages, replace block after receipt, retry settled/refunded calls, simulate withdrawal transfer failure and replay. No duplicate credit; stale success is withdrawn and run marked inconclusive.
- **Limitations:** local canonical-chain assumption, not public-chain reorg safety or guaranteed recovery from key loss. Reorgs can rewind nonce state as well as funding.

## SI-18 — Inputs and execution remain bounded

- **Threat:** resource exhaustion, parser ambiguity, arbitrary service execution, unsafe autonomy.
- **Enforcement:** uint64 operands, fixed service, canonical typed values, 16 KiB message bound, 16 offers, 3 transport retries, one-agreement standard fixture, 16 transaction-submission budget and finite wall-time runner limit. No user-supplied executable payload.
- **Positive test:** maximum uint64 input and maximum allowed message size parse or reject according to schema, without unbounded work; normal fixture finishes within budgets.
- **Adversarial test:** duplicate keys, unknown fields, leading zeros, negative/oversized integers, 16 KiB+1, oversized discovery, spam, repeated RPC failure. Stop before signing/submitting new actions; no bypass of chain refund rules.
- **Limitations:** process limits are environmental and do not prevent local administrator or RPC denial of service. A stopped process may leave synthetic principal locked until valid refund/reset.

## Evidence requirement

An implementation review must trace each SI identifier to named tests, report positive and negative outcomes, include boundary/fuzz/sequence cases where applicable, and identify shared test-oracle assumptions. Passing tests supports only the tested implementation and environment; it is not a cryptographic proof or production security review. See [THREAT_MODEL.md](THREAT_MODEL.md) for residual threats and severity.
