// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {StdInvariant} from "forge-std/StdInvariant.sol";
import {Experiment002Escrow as E} from "../src/Experiment002Escrow.sol";

contract Experiment002Test is Test {
    E internal e;
    uint256 internal ka = 0xA002;
    uint256 internal kb = 0xB002;
    address internal a;
    address internal b;
    uint256 internal constant P = 1e12;
    bytes32 internal constant RUN = bytes32(uint256(2));

    function setUp() public virtual {
        vm.chainId(31337);
        vm.warp(1000);
        a = vm.addr(ka);
        b = vm.addr(kb);
        vm.deal(a, 1 ether);
        e = new E(RUN);
    }

    function sig(uint256 key, bytes32 digest) internal pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(key, digest);
        return abi.encodePacked(r, s, v);
    }

    function terms(uint256 n) internal view returns (E.Terms memory) {
        return E.Terms(a, b, e.SERVICE_ID(), e.POLICY_ID(), 7, 11, P, 1120, 1300, bytes32(n), RUN);
    }

    function auth(E.Terms memory t, uint256 n) internal view returns (E.Authorization memory) {
        return E.Authorization(a, b, e.hashTerms(t), n, 2 * P, 1120, RUN);
    }

    function fund(E.Terms memory t, E.Authorization memory q) internal returns (bytes32) {
        bytes memory sa = sig(ka, e.hashTerms(t));
        bytes memory sb = sig(kb, e.hashTerms(t));
        bytes memory sq = sig(ka, e.hashAuthorization(q));
        vm.prank(a);
        e.fund{value: t.price}(t, q, sa, sb, sq);
        return e.hashTerms(t);
    }

    function claimFor(bytes32 id) internal view returns (E.Claim memory c) {
        (E.Terms memory t, uint256 n,,) = e.getRecord(id);
        c = E.Claim(a, b, id, n, uint256(t.x) + t.y, RUN);
    }

    function settle(bytes32 id) internal {
        E.Claim memory c = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(c));
        vm.prank(b);
        e.claim(c, s);
    }

    function state(bytes32 id) internal view returns (E.State s) {
        (,, s,) = e.getRecord(id);
    }

    function accounting() internal view {
        assertGe(address(e).balance, e.lockedPrincipal() + e.totalCredits());
        assertEq(e.totalCredits(), e.credits(a) + e.credits(b));
    }

    function rejectedFund(
        E.Terms memory t,
        E.Authorization memory q,
        bytes memory sa,
        bytes memory sb,
        bytes memory sq,
        uint256 value,
        address caller
    ) internal {
        vm.prank(caller);
        vm.expectRevert();
        e.fund{value: value}(t, q, sa, sb, sq);
        assertEq(uint256(state(e.hashTerms(t))), 0);
        assertEq(e.lockedPrincipal(), 0);
        assertEq(e.totalCredits(), 0);
    }

    function test_NoPostFundingRequesterActionAndOwnWithdrawal() public {
        bytes32 id = fund(terms(0), auth(terms(0), 0));
        vm.warp(1299);
        settle(id);
        assertEq(uint256(state(id)), 2);
        (,,, uint256 result) = e.getRecord(id);
        assertEq(result, 18);
        uint256 before = b.balance;
        vm.prank(b);
        e.withdraw();
        assertEq(b.balance, before + P);
        accounting();
        vm.prank(b);
        vm.expectRevert();
        e.withdraw();
        vm.prank(a);
        vm.expectRevert();
        e.refund(id);
        E.Claim memory c = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(c));
        vm.prank(b);
        vm.expectRevert();
        e.claim(c, s);
    }

    function test_RefundEqualityNoAutomaticClosureAndExclusiveOutcome() public {
        bytes32 id = fund(terms(0), auth(terms(0), 0));
        vm.warp(1301);
        assertEq(uint256(state(id)), 1);
        vm.prank(a);
        e.refund(id);
        assertEq(uint256(state(id)), 3);
        assertEq(e.credits(a), P);
        vm.prank(a);
        e.withdraw();
        accounting();
        vm.prank(a);
        vm.expectRevert();
        e.refund(id);
        E.Claim memory c = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(c));
        vm.prank(b);
        vm.expectRevert();
        e.claim(c, s);
        assertEq(uint256(e.nonceStatus(a, 0)), 1);
    }

    function test_FundingDeadlineBoundaryMatrix() public {
        for (uint256 t = 1119; t <= 1121; t++) {
            uint256 snap = vm.snapshotState();
            vm.warp(t);
            E.Terms memory x = terms(0);
            E.Authorization memory q = auth(x, 0);
            if (t == 1119) {
                fund(x, q);
            } else {
                rejectedFund(
                    x, q, sig(ka, e.hashTerms(x)), sig(kb, e.hashTerms(x)), sig(ka, e.hashAuthorization(q)), P, a
                );
            }
            vm.revertToState(snap);
        }
    }

    function test_ClaimRefundBoundaryAndOrderingMatrix() public {
        bytes32 id = fund(terms(0), auth(terms(0), 0));
        E.Claim memory c = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(c));
        for (uint256 t = 1299; t <= 1301; t++) {
            uint256 snap = vm.snapshotState();
            vm.warp(t);
            if (t == 1299) {
                vm.prank(a);
                vm.expectRevert();
                e.refund(id);
                vm.prank(b);
                e.claim(c, s);
            } else {
                vm.prank(b);
                vm.expectRevert();
                e.claim(c, s);
                vm.prank(a);
                e.refund(id);
            }
            accounting();
            vm.revertToState(snap);
        }
    }

    function test_RevocationOrdersAndReplay() public {
        E.Terms memory t = terms(0);
        E.Authorization memory q = auth(t, 0);
        uint256 snap = vm.snapshotState();
        vm.prank(a);
        e.revokeUnused(0);
        rejectedFund(t, q, sig(ka, e.hashTerms(t)), sig(kb, e.hashTerms(t)), sig(ka, e.hashAuthorization(q)), P, a);
        vm.prank(a);
        vm.expectRevert();
        e.revokeUnused(0);
        vm.revertToState(snap);
        bytes32 id = fund(t, q);
        vm.prank(a);
        vm.expectRevert();
        e.revokeUnused(0);
        bytes memory sa = sig(ka, e.hashTerms(t));
        bytes memory sb = sig(kb, e.hashTerms(t));
        bytes memory sq = sig(ka, e.hashAuthorization(q));
        vm.prank(a);
        vm.expectRevert();
        e.fund{value: P}(t, q, sa, sb, sq);
        t.salt = bytes32(uint256(1));
        q = auth(t, 0);
        sa = sig(ka, e.hashTerms(t));
        sb = sig(kb, e.hashTerms(t));
        sq = sig(ka, e.hashAuthorization(q));
        vm.prank(a);
        vm.expectRevert();
        e.fund{value: P}(t, q, sa, sb, sq);
        settle(id);
        accounting();
    }

    function testFuzz_PriceCapAndValue(uint8 choice) public {
        choice = uint8(bound(choice, 0, 6));
        E.Terms memory t = terms(0);
        E.Authorization memory q = auth(t, 0);
        uint256 value = P;
        if (choice == 0) q.maxAmount = P - 1;
        if (choice == 1) q.maxAmount = e.MAX_AMOUNT() + 1;
        if (choice == 2) t.price = 0;
        if (choice == 3) value = P - 1;
        if (choice == 4) value = P + 1;
        if (choice == 5) {
            t.price = e.MAX_AMOUNT() + 1;
            value = t.price;
        }
        if (choice == 6) q.expiresAt = 1121;
        q.agreementId = e.hashTerms(t);
        rejectedFund(t, q, sig(ka, e.hashTerms(t)), sig(kb, e.hashTerms(t)), sig(ka, e.hashAuthorization(q)), value, a);
    }

    function testFuzz_BoundaryOperandsAndPrincipal(uint64 x, uint64 y, uint256 price) public {
        price = bound(price, 1, e.MAX_AMOUNT());
        E.Terms memory t = terms(0);
        t.x = x;
        t.y = y;
        t.price = price;
        E.Authorization memory q = auth(t, 0);
        q.maxAmount = price;
        bytes32 id = fund(t, q);
        settle(id);
        (,,, uint256 value) = e.getRecord(id);
        assertEq(value, uint256(x) + y);
        assertEq(e.credits(b), price);
        accounting();
    }

    function test_ZeroAndMaximumOperands() public {
        E.Terms memory t = terms(0);
        t.x = 0;
        t.y = 0;
        settle(fund(t, auth(t, 0)));
        t = terms(1);
        t.x = type(uint64).max;
        t.y = type(uint64).max;
        bytes32 id = fund(t, auth(t, 1));
        settle(id);
        (,,, uint256 value) = e.getRecord(id);
        assertEq(value, 2 ** 65 - 2);
        accounting();
    }

    function test_AllTermsMutationsWithoutResigning() public {
        E.Terms memory original = terms(0);
        E.Authorization memory q = auth(original, 0);
        bytes memory sa = sig(ka, e.hashTerms(original));
        bytes memory sb = sig(kb, e.hashTerms(original));
        bytes memory sq = sig(ka, e.hashAuthorization(q));
        for (uint256 i = 0; i < 11; i++) {
            E.Terms memory t = terms(0);
            if (i == 0) t.requester = b;
            if (i == 1) t.provider = a;
            if (i == 2) t.serviceId = bytes32(uint256(3));
            if (i == 3) t.policyId = bytes32(uint256(3));
            if (i == 4) t.x++;
            if (i == 5) t.y++;
            if (i == 6) t.price++;
            if (i == 7) t.fundBefore++;
            if (i == 8) t.claimBefore++;
            if (i == 9) t.salt = bytes32(uint256(3));
            if (i == 10) t.runId = bytes32(uint256(3));
            rejectedFund(t, q, sa, sb, sq, P, a);
        }
        fund(original, q);
    }

    function test_AllAuthorizationMutationsWithoutResigning() public {
        E.Terms memory t = terms(0);
        E.Authorization memory original = auth(t, 0);
        bytes memory sa = sig(ka, e.hashTerms(t));
        bytes memory sb = sig(kb, e.hashTerms(t));
        bytes memory sq = sig(ka, e.hashAuthorization(original));
        for (uint256 i = 0; i < 7; i++) {
            E.Authorization memory q = auth(t, 0);
            if (i == 0) q.requester = b;
            if (i == 1) q.provider = a;
            if (i == 2) q.agreementId = bytes32(uint256(3));
            if (i == 3) q.nonce++;
            if (i == 4) q.maxAmount++;
            if (i == 5) q.expiresAt--;
            if (i == 6) q.runId = bytes32(uint256(3));
            rejectedFund(t, q, sa, sb, sq, P, a);
        }
        fund(t, original);
    }

    function test_AllClaimMutationsWrongResultAndOutsider() public {
        bytes32 id = fund(terms(0), auth(terms(0), 0));
        E.Claim memory original = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(original));
        for (uint256 i = 0; i < 6; i++) {
            E.Claim memory c = claimFor(id);
            if (i == 0) c.requester = b;
            if (i == 1) c.provider = a;
            if (i == 2) c.agreementId = bytes32(uint256(3));
            if (i == 3) c.authorizationNonce++;
            if (i == 4) c.value++;
            if (i == 5) c.runId = bytes32(uint256(3));
            vm.prank(b);
            vm.expectRevert();
            e.claim(c, s);
            assertEq(uint256(state(id)), 1);
            accounting();
        }
        E.Claim memory bad = claimFor(id);
        bad.value = 19;
        bytes memory badSig = sig(kb, e.hashClaim(bad));
        vm.prank(b);
        vm.expectRevert();
        e.claim(bad, badSig);
        vm.prank(a);
        vm.expectRevert();
        e.claim(original, s);
        vm.prank(address(9));
        vm.expectRevert();
        e.claim(original, s);
        settle(id);
    }

    function test_SignatureEncodingsAndWrongKeys() public {
        E.Terms memory t = terms(0);
        E.Authorization memory q = auth(t, 0);
        bytes memory sb = sig(kb, e.hashTerms(t));
        bytes memory sq = sig(ka, e.hashAuthorization(q));
        rejectedFund(t, q, new bytes(65), sb, sq, P, a);
        rejectedFund(t, q, new bytes(64), sb, sq, P, a);
        rejectedFund(t, q, sig(kb, e.hashTerms(t)), sb, sq, P, a);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(ka, e.hashTerms(t));
        bytes memory high = abi.encodePacked(
            r,
            bytes32(0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141 - uint256(s)),
            uint8(v == 27 ? 28 : 27)
        );
        rejectedFund(t, q, high, sb, sq, P, a);
        rejectedFund(t, q, abi.encodePacked(r, s, uint8(0)), sb, sq, P, a);
    }

    function test_DomainChainContractAndCrossExperiment() public {
        E.Terms memory t = terms(0);
        E.Authorization memory q = auth(t, 0);
        bytes memory sa = sig(ka, e.hashTerms(t));
        bytes memory sb = sig(kb, e.hashTerms(t));
        bytes memory sq = sig(ka, e.hashAuthorization(q));
        vm.chainId(31338);
        rejectedFund(t, q, sa, sb, sq, P, a);
        vm.chainId(31337);
        E other = new E(RUN);
        bytes memory wrong = sig(ka, other.hashTerms(t));
        rejectedFund(t, q, wrong, sb, sq, P, a);
        bytes32 domain = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256("GenesisExperiment001"),
                keccak256("1"),
                uint256(31337),
                address(e)
            )
        );
        bytes32 digest = keccak256(abi.encodePacked(hex"1901", domain, keccak256(abi.encode(e.TERMS_TYPEHASH(), t))));
        rejectedFund(t, q, sig(ka, digest), sb, sq, P, a);
    }

    function test_UnauthorizedFundingRefundWithdrawalAndDirectPayment() public {
        E.Terms memory t = terms(0);
        E.Authorization memory q = auth(t, 0);
        vm.deal(b, P);
        rejectedFund(t, q, sig(ka, e.hashTerms(t)), sig(kb, e.hashTerms(t)), sig(ka, e.hashAuthorization(q)), P, b);
        bytes32 id = fund(t, q);
        vm.warp(1300);
        vm.prank(b);
        vm.expectRevert();
        e.refund(id);
        vm.prank(a);
        e.refund(id);
        vm.prank(b);
        vm.expectRevert();
        e.withdraw();
        assertEq(e.credits(a), P);
        (bool ok,) = address(e).call{value: 1}("");
        assertFalse(ok);
        (ok,) = address(e).call(hex"abcd");
        assertFalse(ok);
        accounting();
    }

    function test_RepeatedIdenticalWorkConcurrentCreditsAndForcedSurplus() public {
        bytes32 one = fund(terms(0), auth(terms(0), 0));
        bytes32 two = fund(terms(1), auth(terms(1), 1));
        assertEq(e.lockedPrincipal(), 2 * P);
        settle(one);
        vm.warp(1300);
        vm.prank(a);
        e.refund(two);
        accounting();
        vm.deal(address(this), 1);
        new Force002{value: 1}(payable(address(e)));
        assertEq(address(e).balance, 2 * P + 1);
        accounting();
        vm.prank(a);
        e.withdraw();
        vm.prank(b);
        e.withdraw();
        assertEq(address(e).balance, 1);
        accounting();
    }

    function test_LateFundingAndDisclosedWorkCanRemainUnpaid() public {
        E.Terms memory t = terms(0);
        t.fundBefore = 1299;
        E.Authorization memory q = auth(t, 0);
        q.expiresAt = 1299;
        vm.warp(1298);
        bytes32 id = fund(t, q);
        assertEq(uint256(t.x) + t.y, 18);
        vm.warp(1300);
        E.Claim memory c = claimFor(id);
        bytes memory s = sig(kb, e.hashClaim(c));
        vm.prank(b);
        vm.expectRevert();
        e.claim(c, s);
        vm.prank(a);
        e.refund(id);
        assertEq(e.credits(b), 0);
        assertEq(e.credits(a), P);
        accounting();
    }

    function test_ZeroRunRejected() public {
        vm.expectRevert();
        new E(bytes32(0));
    }

    function test_ExpiryOrderingAndUnsupportedSemantics() public {
        for (uint256 i = 0; i < 6; i++) {
            E.Terms memory t = terms(0);
            E.Authorization memory q = auth(t, 0);
            if (i == 0) t.provider = address(0);
            if (i == 1) t.provider = a;
            if (i == 2) t.serviceId = bytes32(0);
            if (i == 3) t.policyId = bytes32(0);
            if (i == 4) t.fundBefore = t.claimBefore;
            if (i == 5) q.expiresAt = 1000;
            q.agreementId = e.hashTerms(t);
            rejectedFund(t, q, sig(ka, e.hashTerms(t)), sig(kb, e.hashTerms(t)), sig(ka, e.hashAuthorization(q)), P, a);
        }
    }
}

contract Force002 {
    constructor(address payable target) payable {
        selfdestruct(target);
    }
}

/// @dev Test-only credit seeding reaches callback defenses excluded by EOA signing policy.
contract CreditHarness002 is E {
    constructor() E(bytes32(uint256(2))) {}

    function seed(address owner) external payable {
        credits[owner] += msg.value;
        totalCredits += msg.value;
    }
}

contract Receiver002 {
    CreditHarness002 public e;
    bool public reject;
    bool public reentered;

    constructor(CreditHarness002 escrow) {
        e = escrow;
    }

    function setReject(bool value) external {
        reject = value;
    }

    function withdraw() external {
        e.withdraw();
    }

    receive() external payable {
        if (reject) revert();
        (bool ok,) = address(e).call(abi.encodeCall(e.withdraw, ()));
        reentered = ok;
    }
}

contract Callback002Test is Test {
    function test_CallbackAndTransferFailurePreserveCredits() public {
        CreditHarness002 e = new CreditHarness002();
        Receiver002 r = new Receiver002(e);
        vm.deal(address(this), 2);
        e.seed{value: 1}(address(r));
        r.setReject(true);
        vm.expectRevert();
        r.withdraw();
        assertEq(e.credits(address(r)), 1);
        assertEq(e.totalCredits(), 1);
        r.setReject(false);
        r.withdraw();
        assertFalse(r.reentered());
        assertEq(e.credits(address(r)), 0);
        assertEq(e.totalCredits(), 0);
        assertEq(address(r).balance, 1);
    }
}

contract Handler002 is Test {
    E public e;
    address public a;
    address public b;
    uint256 public count;
    mapping(uint256 => bytes32) public ids;
    uint256 public modeledLocked;
    uint256 public modeledA;
    uint256 public modeledB;

    constructor(E escrow) {
        e = escrow;
        a = vm.addr(0xA002);
        b = vm.addr(0xB002);
        vm.deal(a, 1 ether);
    }

    function sign(uint256 key, bytes32 digest) internal pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(key, digest);
        return abi.encodePacked(r, s, v);
    }

    function step(uint256 action, uint64 x, uint64 y) external {
        action %= 5;
        if (action == 0 || count == 0) {
            uint256 n = count++;
            E.Terms memory t = E.Terms(
                a,
                b,
                e.SERVICE_ID(),
                e.POLICY_ID(),
                x,
                y,
                1,
                uint64(block.timestamp + 120),
                uint64(block.timestamp + 300),
                bytes32(n),
                e.runId()
            );
            bytes32 id = e.hashTerms(t);
            E.Authorization memory q = E.Authorization(a, b, id, n, 1, t.fundBefore, e.runId());
            bytes memory sa = sign(0xA002, id);
            bytes memory sb = sign(0xB002, id);
            bytes memory sq = sign(0xA002, e.hashAuthorization(q));
            vm.prank(a);
            e.fund{value: 1}(t, q, sa, sb, sq);
            ids[n] = id;
            modeledLocked++;
        } else if (action == 1 || action == 2) {
            bytes32 id = ids[uint256(x) % count];
            (E.Terms memory t, uint256 n, E.State state,) = e.getRecord(id);
            if (state != E.State.Funded) return;
            if (action == 1 && block.timestamp < t.claimBefore) {
                E.Claim memory c = E.Claim(a, b, id, n, uint256(t.x) + t.y, e.runId());
                bytes memory s = sign(0xB002, e.hashClaim(c));
                vm.prank(b);
                e.claim(c, s);
                modeledB++;
                modeledLocked--;
            } else {
                if (block.timestamp < t.claimBefore) vm.warp(t.claimBefore);
                vm.prank(a);
                e.refund(id);
                modeledA++;
                modeledLocked--;
            }
        } else if (action == 3 && modeledA > 0) {
            vm.prank(a);
            e.withdraw();
            modeledA = 0;
        } else if (action == 4 && modeledB > 0) {
            vm.prank(b);
            e.withdraw();
            modeledB = 0;
        }
    }
}

contract Experiment002InvariantTest is StdInvariant, Test {
    E e;
    Handler002 h;

    function setUp() public {
        e = new E(bytes32(uint256(2)));
        h = new Handler002(e);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = h.step.selector;
        targetSelector(FuzzSelector(address(h), selectors));
        targetContract(address(h));
    }

    function invariant_ConservedLiabilities() public view {
        assertEq(e.lockedPrincipal(), h.modeledLocked());
        assertEq(e.totalCredits(), h.modeledA() + h.modeledB());
        assertEq(address(e).balance, e.lockedPrincipal() + e.totalCredits());
    }

    function invariant_NoCrossOwnerCredit() public view {
        assertEq(e.credits(h.a()), h.modeledA());
        assertEq(e.credits(h.b()), h.modeledB());
    }
}
