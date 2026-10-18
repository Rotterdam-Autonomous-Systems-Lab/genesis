// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @notice Disposable local experiment: upfront consent to a fixed public predicate.
/// @dev Timely canonical inclusion is required; this does not guarantee strong fair exchange.
contract Experiment002Escrow is EIP712, ReentrancyGuard {
    uint256 public constant MAX_AMOUNT = 1e15;
    bytes32 public constant SERVICE_ID = keccak256("genesis.sum-u64.v1");
    bytes32 public constant POLICY_ID = keccak256("genesis.exp002.direct-sum-u64.v1");
    bytes32 public constant TERMS_TYPEHASH = keccak256(
        "Terms(address requester,address provider,bytes32 serviceId,bytes32 policyId,uint64 x,uint64 y,uint256 price,uint64 fundBefore,uint64 claimBefore,bytes32 salt,bytes32 runId)"
    );
    bytes32 public constant AUTHORIZATION_TYPEHASH = keccak256(
        "Authorization(address requester,address provider,bytes32 agreementId,uint256 nonce,uint256 maxAmount,uint64 expiresAt,bytes32 runId)"
    );
    bytes32 public constant CLAIM_TYPEHASH = keccak256(
        "Claim(address requester,address provider,bytes32 agreementId,uint256 authorizationNonce,uint256 value,bytes32 runId)"
    );

    enum State {
        None,
        Funded,
        Settled,
        Refunded
    }
    enum NonceStatus {
        Unused,
        Consumed,
        Revoked
    }

    struct Terms {
        address requester;
        address provider;
        bytes32 serviceId;
        bytes32 policyId;
        uint64 x;
        uint64 y;
        uint256 price;
        uint64 fundBefore;
        uint64 claimBefore;
        bytes32 salt;
        bytes32 runId;
    }

    struct Authorization {
        address requester;
        address provider;
        bytes32 agreementId;
        uint256 nonce;
        uint256 maxAmount;
        uint64 expiresAt;
        bytes32 runId;
    }

    struct Claim {
        address requester;
        address provider;
        bytes32 agreementId;
        uint256 authorizationNonce;
        uint256 value;
        bytes32 runId;
    }

    struct Record {
        Terms terms;
        uint256 authorizationNonce;
        State state;
        uint256 result;
    }

    bytes32 public immutable runId;
    mapping(bytes32 => Record) private _records;
    mapping(address => mapping(uint256 => NonceStatus)) public nonceStatus;
    mapping(address => uint256) public credits;
    uint256 public lockedPrincipal;
    uint256 public totalCredits;

    error Rejected();

    event Funded(
        bytes32 indexed agreementId,
        address indexed requester,
        address indexed provider,
        uint256 authorizationNonce,
        uint256 price
    );
    event Claimed(
        bytes32 indexed agreementId, address indexed provider, uint256 authorizationNonce, uint256 value, uint256 price
    );
    event Refunded(bytes32 indexed agreementId, address indexed requester, uint256 authorizationNonce, uint256 price);
    event Withdrawn(address indexed owner, uint256 amount);
    event AuthorizationRevoked(address indexed requester, uint256 nonce);

    constructor(bytes32 runId_) EIP712("GenesisExperiment002", "1") {
        if (runId_ == bytes32(0)) revert Rejected();
        runId = runId_;
    }

    function getRecord(bytes32 id) external view returns (Terms memory, uint256, State, uint256) {
        Record storage r = _records[id];
        return (r.terms, r.authorizationNonce, r.state, r.result);
    }

    function hashTerms(Terms memory t) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(TERMS_TYPEHASH, t)));
    }

    function hashAuthorization(Authorization memory a) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(AUTHORIZATION_TYPEHASH, a)));
    }

    function hashClaim(Claim memory c) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(CLAIM_TYPEHASH, c)));
    }

    function verifyResult(uint64 x, uint64 y, uint256 value) public pure returns (bool) {
        return uint256(x) + uint256(y) == value;
    }

    function fund(
        Terms calldata t,
        Authorization calldata a,
        bytes calldata sigA,
        bytes calldata sigB,
        bytes calldata sigAuth
    ) external payable nonReentrant {
        bytes32 id = hashTerms(t);
        if (
            msg.sender != t.requester || t.requester == address(0) || t.provider == address(0)
                || t.requester == t.provider || t.runId != runId || a.runId != runId || t.serviceId != SERVICE_ID
                || t.policyId != POLICY_ID || a.requester != t.requester || a.provider != t.provider || a.agreementId != id
                || t.price == 0 || t.price > a.maxAmount || a.maxAmount > MAX_AMOUNT || msg.value != t.price
                || block.timestamp >= a.expiresAt || a.expiresAt > t.fundBefore || t.fundBefore >= t.claimBefore
                || _records[id].state != State.None || nonceStatus[t.requester][a.nonce] != NonceStatus.Unused
        ) revert Rejected();
        _verify(id, sigA, t.requester);
        _verify(id, sigB, t.provider);
        _verify(hashAuthorization(a), sigAuth, t.requester);
        nonceStatus[t.requester][a.nonce] = NonceStatus.Consumed;
        _records[id] = Record(t, a.nonce, State.Funded, 0);
        lockedPrincipal += t.price;
        emit Funded(id, t.requester, t.provider, a.nonce, t.price);
    }

    function revokeUnused(uint256 nonce) external nonReentrant {
        if (nonceStatus[msg.sender][nonce] != NonceStatus.Unused) revert Rejected();
        nonceStatus[msg.sender][nonce] = NonceStatus.Revoked;
        emit AuthorizationRevoked(msg.sender, nonce);
    }

    function claim(Claim calldata c, bytes calldata signature) external nonReentrant {
        Record storage r = _records[c.agreementId];
        Terms storage t = r.terms;
        if (
            r.state != State.Funded || msg.sender != t.provider || block.timestamp >= t.claimBefore
                || c.requester != t.requester || c.provider != t.provider || c.authorizationNonce != r.authorizationNonce
                || c.runId != runId || !verifyResult(t.x, t.y, c.value)
        ) revert Rejected();
        _verify(hashClaim(c), signature, t.provider);
        r.state = State.Settled;
        r.result = c.value;
        lockedPrincipal -= t.price;
        credits[t.provider] += t.price;
        totalCredits += t.price;
        emit Claimed(c.agreementId, t.provider, c.authorizationNonce, c.value, t.price);
    }

    function refund(bytes32 id) external nonReentrant {
        Record storage r = _records[id];
        Terms storage t = r.terms;
        if (r.state != State.Funded || msg.sender != t.requester || block.timestamp < t.claimBefore) revert Rejected();
        r.state = State.Refunded;
        lockedPrincipal -= t.price;
        credits[t.requester] += t.price;
        totalCredits += t.price;
        emit Refunded(id, t.requester, r.authorizationNonce, t.price);
    }

    function withdraw() external nonReentrant {
        uint256 amount = credits[msg.sender];
        if (amount == 0) revert Rejected();
        credits[msg.sender] = 0;
        totalCredits -= amount;
        (bool ok,) = msg.sender.call{value: amount}("");
        if (!ok) revert Rejected();
        emit Withdrawn(msg.sender, amount);
    }

    function _verify(bytes32 digest, bytes memory signature, address expected) private pure {
        if (signature.length != 65) revert Rejected();
        (address signer, ECDSA.RecoverError err,) = ECDSA.tryRecover(digest, signature);
        if (err != ECDSA.RecoverError.NoError || signer != expected) revert Rejected();
    }

    receive() external payable {
        revert Rejected();
    }

    fallback() external payable {
        revert Rejected();
    }
}
