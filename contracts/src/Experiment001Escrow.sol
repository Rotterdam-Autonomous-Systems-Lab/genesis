// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @notice Local Experiment 001 only. No admin, upgrades, tokens, or arbitrary execution.
/// @dev Requester consent is required even for a correct result; provider fairness is not guaranteed.
contract Experiment001Escrow is EIP712, ReentrancyGuard {
    uint256 public constant MAX_PRICE = 1e15;
    bytes32 public constant SERVICE_ID = keccak256("genesis.sum-u64.v1");
    bytes32 public constant ADVERTISEMENT_TYPEHASH =
        keccak256("Advertisement(address provider,bytes32 serviceId,uint256 price,uint64 expiresAt,bytes32 runId)");
    bytes32 public constant AGREEMENT_TYPEHASH = keccak256(
        "Agreement(address requester,address provider,bytes32 serviceId,uint64 x,uint64 y,uint256 price,uint64 fundingDeadline,uint64 settlementDeadline,bytes32 salt,bytes32 runId)"
    );
    bytes32 public constant AUTHORIZATION_TYPEHASH = keccak256(
        "Authorization(address requester,address provider,bytes32 agreementId,uint256 nonce,uint256 maxAmount,uint64 validUntil,bytes32 runId)"
    );
    bytes32 public constant RESULT_TYPEHASH = keccak256("Result(bytes32 agreementId,uint256 value,bytes32 runId)");
    bytes32 public constant ACCEPTANCE_TYPEHASH =
        keccak256("Acceptance(bytes32 agreementId,bytes32 resultDigest,uint256 authorizationNonce,bytes32 runId)");

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

    struct Advertisement {
        address provider;
        bytes32 serviceId;
        uint256 price;
        uint64 expiresAt;
        bytes32 runId;
    }

    struct Agreement {
        address requester;
        address provider;
        bytes32 serviceId;
        uint64 x;
        uint64 y;
        uint256 price;
        uint64 fundingDeadline;
        uint64 settlementDeadline;
        bytes32 salt;
        bytes32 runId;
    }

    struct Authorization {
        address requester;
        address provider;
        bytes32 agreementId;
        uint256 nonce;
        uint256 maxAmount;
        uint64 validUntil;
        bytes32 runId;
    }

    struct Result {
        bytes32 agreementId;
        uint256 value;
        bytes32 runId;
    }

    struct Acceptance {
        bytes32 agreementId;
        bytes32 resultDigest;
        uint256 authorizationNonce;
        bytes32 runId;
    }

    struct Record {
        Agreement terms;
        uint256 authorizationNonce;
        State state;
    }

    bytes32 public immutable runId;
    mapping(bytes32 => Record) private _records;
    mapping(address => mapping(uint256 => NonceStatus)) public nonceStatus;
    mapping(address => uint256) public credits;
    uint256 public totalLocked;
    uint256 public totalCredits;
    uint256 public totalDeposited;
    uint256 public totalWithdrawn;

    error UnsupportedChain();
    error InvalidRun();
    error InvalidSignature();
    error InvalidBinding();
    error InvalidTerms();
    error AuthorizationUnavailable();
    error AgreementExists();
    error WrongCaller();
    error WrongState();
    error Expired();
    error TooEarly();
    error InvalidValue();
    error InvalidResult();
    error NoCredit();
    error TransferFailed();
    error DirectPaymentRejected();

    event Funded(
        bytes32 indexed agreementId, address indexed requester, address indexed provider, uint256 nonce, uint256 price
    );
    event NonceRevoked(address indexed requester, uint256 nonce);
    event Settled(bytes32 indexed agreementId, bytes32 resultDigest, uint256 price);
    event Refunded(bytes32 indexed agreementId, uint256 price);
    event Withdrawn(address indexed account, uint256 amount);

    constructor(bytes32 runId_) EIP712("GenesisExperiment001", "1") {
        if (block.chainid != 31337) revert UnsupportedChain();
        if (runId_ == bytes32(0)) revert InvalidRun();
        runId = runId_;
    }

    function getAgreement(bytes32 id) external view returns (Record memory) {
        return _records[id];
    }

    // Static tuples encode identically to the ordered static fields in the normative schemas.
    function hashAdvertisement(Advertisement memory a) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(ADVERTISEMENT_TYPEHASH, a)));
    }

    function hashAgreement(Agreement memory a) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(AGREEMENT_TYPEHASH, a)));
    }

    function hashAuthorization(Authorization memory a) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(AUTHORIZATION_TYPEHASH, a)));
    }

    function hashResult(Result memory r) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(RESULT_TYPEHASH, r)));
    }

    function hashAcceptance(Acceptance memory a) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(ACCEPTANCE_TYPEHASH, a)));
    }

    function fund(
        Agreement calldata a,
        bytes calldata sigA,
        bytes calldata sigB,
        Authorization calldata auth,
        bytes calldata sigAuth
    ) external payable nonReentrant returns (bytes32 id) {
        if (msg.sender != a.requester) revert WrongCaller();
        if (a.runId != runId || auth.runId != runId) revert InvalidBinding();
        if (
            a.requester == address(0) || a.provider == address(0) || a.requester == a.provider
                || a.serviceId != SERVICE_ID || a.salt == bytes32(0) || a.price == 0 || a.price > MAX_PRICE
                || a.fundingDeadline >= a.settlementDeadline || uint256(a.settlementDeadline) - a.fundingDeadline > 3600
                || uint256(a.settlementDeadline) > block.timestamp + 3600 || auth.validUntil > a.fundingDeadline
        ) revert InvalidTerms();
        if (block.timestamp >= a.fundingDeadline || block.timestamp >= auth.validUntil) revert Expired();
        if (a.price > auth.maxAmount || auth.maxAmount > MAX_PRICE || msg.value != a.price) revert InvalidValue();
        id = hashAgreement(a);
        if (auth.requester != a.requester || auth.provider != a.provider || auth.agreementId != id) {
            revert InvalidBinding();
        }
        if (_records[id].state != State.None) revert AgreementExists();
        if (nonceStatus[a.requester][auth.nonce] != NonceStatus.Unused) revert AuthorizationUnavailable();
        _verify(id, sigA, a.requester);
        _verify(id, sigB, a.provider);
        _verify(hashAuthorization(auth), sigAuth, a.requester);
        nonceStatus[a.requester][auth.nonce] = NonceStatus.Consumed;
        _records[id] = Record(a, auth.nonce, State.Funded);
        totalLocked += a.price;
        totalDeposited += a.price;
        emit Funded(id, a.requester, a.provider, auth.nonce, a.price);
    }

    function revokeUnused(uint256 nonce) external nonReentrant {
        if (nonceStatus[msg.sender][nonce] != NonceStatus.Unused) revert AuthorizationUnavailable();
        nonceStatus[msg.sender][nonce] = NonceStatus.Revoked;
        emit NonceRevoked(msg.sender, nonce);
    }

    function settle(
        bytes32 id,
        Result calldata result,
        bytes calldata sigResultB,
        Acceptance calldata acceptance,
        bytes calldata sigAcceptanceA
    ) external nonReentrant {
        Record storage record = _records[id];
        if (record.state != State.Funded) revert WrongState();
        Agreement storage a = record.terms;
        if (msg.sender != a.provider) revert WrongCaller();
        if (block.timestamp >= a.settlementDeadline) revert Expired();
        bytes32 digest = hashResult(result);
        if (
            result.agreementId != id || result.runId != runId || acceptance.agreementId != id
                || acceptance.resultDigest != digest || acceptance.authorizationNonce != record.authorizationNonce
                || acceptance.runId != runId
        ) revert InvalidBinding();
        _verify(digest, sigResultB, a.provider);
        _verify(hashAcceptance(acceptance), sigAcceptanceA, a.requester);
        if (result.value != uint256(a.x) + uint256(a.y)) revert InvalidResult();
        record.state = State.Settled;
        totalLocked -= a.price;
        credits[a.provider] += a.price;
        totalCredits += a.price;
        emit Settled(id, digest, a.price);
    }

    function refund(bytes32 id) external nonReentrant {
        Record storage record = _records[id];
        if (record.state != State.Funded) revert WrongState();
        Agreement storage a = record.terms;
        if (msg.sender != a.requester) revert WrongCaller();
        if (block.timestamp < a.settlementDeadline) revert TooEarly();
        record.state = State.Refunded;
        totalLocked -= a.price;
        credits[a.requester] += a.price;
        totalCredits += a.price;
        emit Refunded(id, a.price);
    }

    function withdraw() external nonReentrant {
        uint256 amount = credits[msg.sender];
        if (amount == 0) revert NoCredit();
        credits[msg.sender] = 0;
        totalCredits -= amount;
        totalWithdrawn += amount;
        (bool ok,) = msg.sender.call{value: amount}("");
        if (!ok) revert TransferFailed();
        emit Withdrawn(msg.sender, amount);
    }

    function _verify(bytes32 digest, bytes memory signature, address expected) private pure {
        if (signature.length != 65 || expected == address(0)) revert InvalidSignature();
        (address signer, ECDSA.RecoverError error,) = ECDSA.tryRecover(digest, signature);
        if (error != ECDSA.RecoverError.NoError || signer != expected) revert InvalidSignature();
    }

    receive() external payable {
        revert DirectPaymentRejected();
    }

    fallback() external payable {
        revert DirectPaymentRejected();
    }
}
