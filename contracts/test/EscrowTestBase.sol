// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

abstract contract EscrowTestBase is Test {
    Escrow internal escrow;
    address internal a;
    address internal b;
    address internal stranger;
    uint256 internal keyA;
    uint256 internal keyB;
    uint256 internal constant PRICE = 1e12;

    function setUp() public virtual {
        vm.chainId(31337);
        vm.warp(1000);
        (a, keyA) = makeAddrAndKey("unit-test-requester");
        (b, keyB) = makeAddrAndKey("unit-test-provider");
        stranger = makeAddr("unit-test-stranger");
        vm.deal(a, 100 ether);
        vm.deal(b, 0);
        escrow = new Escrow(keccak256("synthetic-unit-test-run"));
    }

    function terms(uint256 nonce) internal view returns (Escrow.Agreement memory) {
        return Escrow.Agreement(
            a,
            b,
            escrow.SERVICE_ID(),
            7,
            11,
            PRICE,
            uint64(block.timestamp + 60),
            uint64(block.timestamp + 120),
            bytes32(nonce + 1),
            escrow.runId()
        );
    }

    function permission(Escrow.Agreement memory t, uint256 nonce) internal view returns (Escrow.Authorization memory) {
        return Escrow.Authorization(
            t.requester,
            t.provider,
            escrow.hashAgreement(t),
            nonce,
            escrow.MAX_PRICE(),
            t.fundingDeadline,
            escrow.runId()
        );
    }

    function sign(uint256 key, bytes32 digest) internal pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(key, digest);
        return abi.encodePacked(r, s, v);
    }

    function fund(Escrow.Agreement memory t, Escrow.Authorization memory auth) internal returns (bytes32 id) {
        return submitFund(t, auth, bytes4(0));
    }

    function rejectFund(Escrow.Agreement memory t, Escrow.Authorization memory auth, bytes4 error) internal {
        submitFund(t, auth, error);
    }

    function submitFund(Escrow.Agreement memory t, Escrow.Authorization memory auth, bytes4 error)
        internal
        returns (bytes32 id)
    {
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.prank(a);
        if (error != bytes4(0)) vm.expectRevert(error);
        id = escrow.fund{value: t.price}(t, sa, sb, auth, sx);
    }

    function funded() internal returns (bytes32 id) {
        Escrow.Agreement memory t = terms(0);
        return fund(t, permission(t, 0));
    }

    function evidence(bytes32 id, uint256 value)
        internal
        view
        returns (Escrow.Result memory r, Escrow.Acceptance memory c)
    {
        r = Escrow.Result(id, value, escrow.runId());
        c = Escrow.Acceptance(id, escrow.hashResult(r), escrow.getAgreement(id).authorizationNonce, escrow.runId());
    }

    function settle(bytes32 id) internal {
        submitSettle(id, bytes4(0));
    }

    function rejectSettle(bytes32 id, bytes4 error) internal {
        submitSettle(id, error);
    }

    function submitSettle(bytes32 id, bytes4 error) internal {
        Escrow.Agreement memory t = escrow.getAgreement(id).terms;
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, uint256(t.x) + uint256(t.y));
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        vm.prank(b);
        if (error != bytes4(0)) vm.expectRevert(error);
        escrow.settle(id, r, sr, c, sc);
    }

    function checkAccounting() internal view {
        assertEq(escrow.totalLocked() + escrow.totalCredits(), escrow.totalDeposited() - escrow.totalWithdrawn());
        assertLe(escrow.totalLocked() + escrow.totalCredits(), address(escrow).balance);
    }

    function checkUnfunded(bytes32 id, uint256 nonce) internal view {
        assertEq(uint256(escrow.getAgreement(id).state), uint256(Escrow.State.None));
        assertEq(uint256(escrow.nonceStatus(a, nonce)), uint256(Escrow.NonceStatus.Unused));
        assertEq(escrow.totalDeposited(), 0);
        assertEq(escrow.totalLocked(), 0);
        assertEq(escrow.totalCredits(), 0);
        assertEq(escrow.credits(a), 0);
        assertEq(escrow.credits(b), 0);
        assertEq(address(escrow).balance, 0);
    }

    function checkFunded(bytes32 id) internal view {
        uint256 price = escrow.getAgreement(id).terms.price;
        assertEq(uint256(escrow.getAgreement(id).state), uint256(Escrow.State.Funded));
        assertEq(escrow.totalLocked(), price);
        assertEq(escrow.totalCredits(), 0);
        assertEq(escrow.credits(a), 0);
        assertEq(escrow.credits(b), 0);
        assertEq(address(escrow).balance, price);
        checkAccounting();
    }
}
