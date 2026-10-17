// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EscrowTestBase} from "./EscrowTestBase.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

contract EscrowAdversarialTest is EscrowTestBase {
    function test_ConcurrentAgreementsMixedOutcomesKeepCreditsSeparate() public {
        Escrow.Agreement memory first = terms(0);
        Escrow.Agreement memory second = terms(1);
        second.x = 99;
        bytes32 id1 = fund(first, permission(first, 0));
        bytes32 id2 = fund(second, permission(second, 1));
        assertEq(escrow.totalLocked(), 2 * PRICE);
        settle(id1);
        assertEq(uint256(escrow.getAgreement(id2).state), uint256(Escrow.State.Funded));
        vm.warp(second.settlementDeadline);
        vm.prank(a);
        escrow.refund(id2);
        assertEq(escrow.credits(a), PRICE);
        assertEq(escrow.credits(b), PRICE);
        vm.prank(b);
        escrow.withdraw();
        assertEq(escrow.credits(a), PRICE);
        assertEq(address(escrow).balance, PRICE);
        vm.prank(a);
        escrow.withdraw();
        assertEq(escrow.totalWithdrawn(), 2 * PRICE);
        assertEq(address(escrow).balance, 0);
        assertEq(uint256(escrow.nonceStatus(a, 0)), uint256(Escrow.NonceStatus.Consumed));
        assertEq(uint256(escrow.nonceStatus(a, 1)), uint256(Escrow.NonceStatus.Consumed));
        rejectSettle(id1, Escrow.WrongState.selector);
        rejectSettle(id2, Escrow.WrongState.selector);
        checkAccounting();
    }

    function test_StrictPriceOneAndMaximumBoundsAcrossConcurrentRecords() public {
        Escrow.Agreement memory smallest = terms(0);
        smallest.price = 1;
        Escrow.Authorization memory auth1 = permission(smallest, 0);
        auth1.maxAmount = 1;
        bytes32 id1 = fund(smallest, auth1);
        Escrow.Agreement memory largest = terms(1);
        largest.price = escrow.MAX_PRICE();
        Escrow.Authorization memory auth2 = permission(largest, 1);
        auth2.maxAmount = largest.price;
        bytes32 id2 = fund(largest, auth2);
        settle(id1);
        settle(id2);
        assertEq(escrow.credits(b), 1 + escrow.MAX_PRICE());
        assertEq(escrow.totalLocked(), 0);
        checkAccounting();
    }

    function test_CopiedSettlementPayloadFromStrangerCannotReleaseCredit() public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        vm.prank(stranger);
        vm.expectRevert(Escrow.WrongCaller.selector);
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
        settle(id);
        vm.prank(stranger);
        vm.expectRevert(Escrow.NoCredit.selector);
        escrow.withdraw();
        assertEq(escrow.credits(b), PRICE);
        assertEq(escrow.credits(stranger), 0);
        checkAccounting();
    }
}
