// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EscrowTestBase} from "./EscrowTestBase.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

contract Experiment001EscrowTest is EscrowTestBase {
    function test_SuccessSettlementAndWithdrawal() public {
        bytes32 id = funded();
        checkFunded(id);
        settle(id);
        assertEq(uint256(escrow.getAgreement(id).state), uint256(Escrow.State.Settled));
        assertEq(escrow.credits(b), PRICE);
        assertEq(escrow.totalLocked(), 0);
        vm.prank(b);
        escrow.withdraw();
        assertEq(b.balance, PRICE);
        assertEq(escrow.credits(b), 0);
        checkAccounting();
        vm.prank(b);
        vm.expectRevert(Escrow.NoCredit.selector);
        escrow.withdraw();
    }

    function test_RefundAndWithdrawal() public {
        bytes32 id = funded();
        vm.warp(1120);
        vm.prank(a);
        escrow.refund(id);
        assertEq(escrow.credits(a), PRICE);
        assertEq(escrow.credits(b), 0);
        uint256 before = a.balance;
        vm.prank(a);
        escrow.withdraw();
        assertEq(a.balance, before + PRICE);
        assertEq(uint256(escrow.getAgreement(id).state), uint256(Escrow.State.Refunded));
        checkAccounting();
    }

    function testFuzz_FixedServiceAndCaps(uint64 x, uint64 y, uint256 price) public {
        price = bound(price, 1, escrow.MAX_PRICE());
        Escrow.Agreement memory t = terms(0);
        t.x = x;
        t.y = y;
        t.price = price;
        Escrow.Authorization memory auth = permission(t, 0);
        auth.maxAmount = price;
        bytes32 id = fund(t, auth);
        settle(id);
        assertEq(escrow.credits(b), price);
        checkAccounting();
    }

    function test_MaximumOperands() public {
        Escrow.Agreement memory t = terms(0);
        t.x = type(uint64).max;
        t.y = type(uint64).max;
        bytes32 id = fund(t, permission(t, 0));
        settle(id);
        assertEq(escrow.credits(b), PRICE);
    }

    function test_ZeroOperands() public {
        Escrow.Agreement memory t = terms(0);
        t.x = 0;
        t.y = 0;
        bytes32 id = fund(t, permission(t, 0));
        settle(id);
        assertEq(escrow.credits(b), PRICE);
    }

    function testFuzz_FundingValueAndCapRejections(uint8 choice) public {
        choice = uint8(bound(choice, 0, 5));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        uint256 value = t.price;
        if (choice == 0) auth.maxAmount = t.price - 1;
        if (choice == 1) auth.maxAmount = escrow.MAX_PRICE() + 1;
        if (choice == 2) value--;
        if (choice == 3) value++;
        if (choice == 4) t.price = 0;
        if (choice == 5) t.price = escrow.MAX_PRICE() + 1;
        auth.agreementId = escrow.hashAgreement(t);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.prank(a);
        vm.expectRevert();
        escrow.fund{value: value}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function testFuzz_InvalidTerms(uint8 choice) public {
        choice = uint8(bound(choice, 0, 7));
        Escrow.Agreement memory t = terms(0);
        if (choice == 0) t.requester = address(0);
        if (choice == 1) t.provider = address(0);
        if (choice == 2) t.provider = t.requester;
        if (choice == 3) t.serviceId = bytes32(uint256(1));
        if (choice == 4) t.salt = bytes32(0);
        if (choice == 5) t.settlementDeadline = t.fundingDeadline;
        if (choice == 6) t.settlementDeadline = t.fundingDeadline + 3601;
        if (choice == 7) {
            t.fundingDeadline = 4600;
            t.settlementDeadline = 4601;
        }
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.deal(t.requester, 100 ether);
        vm.prank(t.requester);
        vm.expectRevert(Escrow.InvalidTerms.selector);
        escrow.fund{value: t.price}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_ExcessiveValidityWindow() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        auth.validUntil++;
        rejectFund(t, auth, Escrow.InvalidTerms.selector);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_LockHorizonExactlyOneHour() public {
        Escrow.Agreement memory t = terms(0);
        t.settlementDeadline = 4600;
        bytes32 id = fund(t, permission(t, 0));
        checkFunded(id);
    }

    function testFuzz_FundingExpiryBoundary(uint8 delta) public {
        delta = uint8(bound(delta, 0, 2));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        auth.validUntil = 1030;
        vm.warp(1029 + delta);
        if (delta != 0) rejectFund(t, auth, Escrow.Expired.selector);
        else fund(t, auth);
        if (delta == 0) checkFunded(auth.agreementId);
        else checkUnfunded(auth.agreementId, 0);
    }

    function testFuzz_FundingDeadlineBoundary(uint8 delta) public {
        delta = uint8(bound(delta, 0, 2));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        vm.warp(1059 + delta);
        if (delta != 0) rejectFund(t, auth, Escrow.Expired.selector);
        else fund(t, auth);
        if (delta == 0) checkFunded(auth.agreementId);
        else checkUnfunded(auth.agreementId, 0);
    }

    function testFuzz_SettlementBoundary(uint8 delta) public {
        delta = uint8(bound(delta, 0, 2));
        bytes32 id = funded();
        vm.warp(1119 + delta);
        if (delta != 0) rejectSettle(id, Escrow.Expired.selector);
        else settle(id);
        if (delta != 0) checkFunded(id);
        else assertEq(escrow.credits(b), PRICE);
    }

    function testFuzz_RefundBoundary(uint8 delta) public {
        delta = uint8(bound(delta, 0, 2));
        bytes32 id = funded();
        vm.warp(1119 + delta);
        vm.prank(a);
        if (delta == 0) vm.expectRevert(Escrow.TooEarly.selector);
        escrow.refund(id);
        if (delta == 0) checkFunded(id);
        else assertEq(escrow.credits(a), PRICE);
    }

    function test_RevokeBeforeFunding() public {
        vm.prank(a);
        escrow.revokeUnused(0);
        Escrow.Agreement memory t = terms(0);
        rejectFund(t, permission(t, 0), Escrow.AuthorizationUnavailable.selector);
        assertEq(uint256(escrow.nonceStatus(a, 0)), uint256(Escrow.NonceStatus.Revoked));
        assertEq(escrow.totalDeposited(), 0);
        vm.prank(a);
        vm.expectRevert(Escrow.AuthorizationUnavailable.selector);
        escrow.revokeUnused(0);
        t = terms(1);
        fund(t, permission(t, 1));
        checkAccounting();
    }

    function test_FundBeforeRevocationObligationSurvivesExpiry() public {
        bytes32 id = funded();
        vm.prank(a);
        vm.expectRevert(Escrow.AuthorizationUnavailable.selector);
        escrow.revokeUnused(0);
        vm.warp(1061);
        settle(id);
        assertEq(escrow.credits(b), PRICE);
    }

    function test_StrangerRevokesOnlyOwnNamespace() public {
        vm.prank(stranger);
        escrow.revokeUnused(0);
        assertEq(uint256(escrow.nonceStatus(a, 0)), uint256(Escrow.NonceStatus.Unused));
        funded();
    }

    function test_ReplayFundWhileFunded() public {
        funded();
        Escrow.Agreement memory t = terms(0);
        rejectFund(t, permission(t, 0), Escrow.AgreementExists.selector);
        checkAccounting();
    }

    function test_ConsumedNonceCannotFundDifferentAgreement() public {
        funded();
        Escrow.Agreement memory t = terms(1);
        rejectFund(t, permission(t, 0), Escrow.AuthorizationUnavailable.selector);
        checkAccounting();
    }

    function test_ExistingAgreementCannotUseFreshNonce() public {
        funded();
        Escrow.Agreement memory t = terms(0);
        rejectFund(t, permission(t, 1), Escrow.AgreementExists.selector);
        assertEq(uint256(escrow.nonceStatus(a, 1)), uint256(Escrow.NonceStatus.Unused));
    }

    function test_TerminalSettlementNeverReopens() public {
        bytes32 id = funded();
        settle(id);
        vm.prank(b);
        escrow.withdraw();
        rejectSettle(id, Escrow.WrongState.selector);
        vm.prank(a);
        vm.expectRevert(Escrow.WrongState.selector);
        escrow.refund(id);
        Escrow.Agreement memory t = terms(0);
        rejectFund(t, permission(t, 1), Escrow.AgreementExists.selector);
        checkAccounting();
    }

    function test_TerminalRefundNeverReopens() public {
        Escrow.Agreement memory t = terms(0);
        bytes32 id = fund(t, permission(t, 0));
        vm.warp(1120);
        vm.prank(a);
        escrow.refund(id);
        vm.prank(a);
        escrow.withdraw();
        vm.prank(a);
        vm.expectRevert(Escrow.WrongState.selector);
        escrow.refund(id);
        rejectSettle(id, Escrow.WrongState.selector);
        assertEq(uint256(escrow.nonceStatus(a, 0)), uint256(Escrow.NonceStatus.Consumed));
        checkAccounting();
    }

    function test_WrongResultEvenWithBothValidSignatures() public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 19);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidResult.selector);
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
    }

    function test_CorrectResultWithoutAcceptanceRefunds() public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.settle(id, r, sr, c, "");
        checkFunded(id);
        vm.warp(1120);
        vm.prank(a);
        escrow.refund(id);
        assertEq(escrow.credits(a), PRICE);
        assertEq(escrow.credits(b), 0);
    }

    function test_UnauthorizedFunding() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.deal(stranger, PRICE);
        vm.prank(stranger);
        vm.expectRevert(Escrow.WrongCaller.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_UnauthorizedSettlementRefundWithdrawal() public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        vm.prank(stranger);
        vm.expectRevert(Escrow.WrongCaller.selector);
        escrow.settle(id, r, sr, c, sc);
        vm.warp(1120);
        vm.prank(b);
        vm.expectRevert(Escrow.WrongCaller.selector);
        escrow.refund(id);
        vm.prank(stranger);
        vm.expectRevert(Escrow.WrongCaller.selector);
        escrow.refund(id);
        checkFunded(id);
        vm.prank(a);
        escrow.refund(id);
        vm.prank(stranger);
        vm.expectRevert(Escrow.NoCredit.selector);
        escrow.withdraw();
        assertEq(escrow.credits(a), PRICE);
    }

    function test_UnfundedActionsRejected() public {
        bytes32 id = keccak256("unknown");
        vm.prank(a);
        vm.expectRevert(Escrow.WrongState.selector);
        escrow.refund(id);
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        vm.prank(b);
        vm.expectRevert(Escrow.WrongState.selector);
        escrow.settle(id, r, "", c, "");
    }

    function test_MultipleAgreementsIndependentAccounting() public {
        Escrow.Agreement memory t = terms(0);
        bytes32 id1 = fund(t, permission(t, 0));
        t = terms(1);
        bytes32 id2 = fund(t, permission(t, 1));
        settle(id1);
        vm.warp(1120);
        vm.prank(a);
        escrow.refund(id2);
        assertEq(escrow.credits(a), PRICE);
        assertEq(escrow.credits(b), PRICE);
        vm.prank(b);
        escrow.withdraw();
        vm.prank(a);
        escrow.withdraw();
        checkAccounting();
    }

    function test_DirectEtherAndFallbackRejected() public {
        vm.deal(address(this), 1 ether);
        (bool ok,) = address(escrow).call{value: 1}("");
        assertFalse(ok);
        (ok,) = address(escrow).call(hex"12345678");
        assertFalse(ok);
        assertEq(address(escrow).balance, 0);
    }

    function test_ConstructorLocalChainAndRunGuards() public {
        vm.chainId(1);
        vm.expectRevert(Escrow.UnsupportedChain.selector);
        new Escrow(keccak256("run"));
        vm.chainId(31337);
        vm.expectRevert(Escrow.InvalidRun.selector);
        new Escrow(bytes32(0));
    }

    function test_ConsumedNonceCannotBeReusedAfterRefund() public {
        bytes32 id = funded();
        vm.warp(1120);
        vm.prank(a);
        escrow.refund(id);
        Escrow.Agreement memory t = terms(1);
        rejectFund(t, permission(t, 0), Escrow.AuthorizationUnavailable.selector);
        assertEq(escrow.credits(a), PRICE);
        assertEq(escrow.totalDeposited(), PRICE);
        checkAccounting();
    }

    function test_RetryAfterRejectedFundingKeepsNonceReusable() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        auth.maxAmount = PRICE - 1;
        rejectFund(t, auth, Escrow.InvalidValue.selector);
        checkUnfunded(auth.agreementId, 0);
        auth.maxAmount = PRICE;
        bytes32 id = fund(t, auth);
        checkFunded(id);
    }

    function test_CapEqualityAtMaximum() public {
        Escrow.Agreement memory t = terms(0);
        t.price = escrow.MAX_PRICE();
        Escrow.Authorization memory auth = permission(t, 0);
        auth.maxAmount = t.price;
        bytes32 id = fund(t, auth);
        settle(id);
        assertEq(escrow.credits(b), escrow.MAX_PRICE());
        checkAccounting();
    }
}
