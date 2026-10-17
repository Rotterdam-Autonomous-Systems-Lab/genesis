// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EscrowTestBase} from "./EscrowTestBase.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

contract WithdrawalReceiver {
    Escrow private immutable escrow;
    bool private immutable reject;

    constructor(Escrow target, bool reject_) {
        escrow = target;
        reject = reject_;
    }

    receive() external payable {
        require(!reject, "synthetic receiver rejects transfer");
        Escrow.Agreement memory t;
        Escrow.Authorization memory x;
        Escrow.Result memory r;
        Escrow.Acceptance memory c;
        bytes[] memory payloads = new bytes[](5);
        payloads[0] = abi.encodeCall(escrow.withdraw, ());
        payloads[1] = abi.encodeCall(escrow.fund, (t, bytes(""), bytes(""), x, bytes("")));
        payloads[2] = abi.encodeCall(escrow.revokeUnused, (123));
        payloads[3] = abi.encodeCall(escrow.settle, (bytes32(0), r, bytes(""), c, bytes("")));
        payloads[4] = abi.encodeCall(escrow.refund, (bytes32(0)));
        for (uint256 i = 0; i < payloads.length; i++) {
            (bool ok, bytes memory ret) = address(escrow).call(payloads[i]);
            require(!ok && bytes4(ret) == bytes4(keccak256("ReentrancyGuardReentrantCall()")), "unguarded callback");
        }
    }
}

contract ForcedEther {
    constructor(address payable target) payable {
        selfdestruct(target);
    }
}

contract EscrowWithdrawalsTest is EscrowTestBase {
    function test_FailedWithdrawalPreservesCreditAndCanRetry() public {
        bytes32 id = funded();
        settle(id);
        WithdrawalReceiver rejector = new WithdrawalReceiver(escrow, true);
        vm.etch(b, address(rejector).code);
        vm.prank(b);
        vm.expectRevert(Escrow.TransferFailed.selector);
        escrow.withdraw();
        assertEq(escrow.credits(b), PRICE);
        assertEq(escrow.totalWithdrawn(), 0);
        assertEq(escrow.totalCredits(), PRICE);
        checkAccounting();
        vm.etch(b, hex"");
        vm.prank(b);
        escrow.withdraw();
        assertEq(b.balance, PRICE);
        checkAccounting();
    }

    function test_CrossFunctionReentrancyBlockedForEveryMutator() public {
        bytes32 id = funded();
        settle(id);
        WithdrawalReceiver attacker = new WithdrawalReceiver(escrow, false);
        vm.etch(b, address(attacker).code);
        vm.prank(b);
        escrow.withdraw();
        assertEq(b.balance, PRICE);
        assertEq(escrow.credits(b), 0);
        assertEq(escrow.totalWithdrawn(), PRICE);
        assertEq(uint256(escrow.nonceStatus(b, 123)), uint256(Escrow.NonceStatus.Unused));
        assertEq(uint256(escrow.getAgreement(id).state), uint256(Escrow.State.Settled));
        checkAccounting();
    }

    function test_ForcedSurplusDoesNotCreateCreditOrPermitRescue() public {
        bytes32 id = funded();
        vm.deal(address(this), 1 ether);
        new ForcedEther{value: 123}(payable(address(escrow)));
        assertEq(address(escrow).balance, PRICE + 123);
        assertEq(escrow.totalDeposited(), PRICE);
        checkAccounting();
        settle(id);
        vm.prank(b);
        escrow.withdraw();
        assertEq(address(escrow).balance, 123);
        vm.prank(a);
        vm.expectRevert(Escrow.NoCredit.selector);
        escrow.withdraw();
        checkAccounting();
    }
}
