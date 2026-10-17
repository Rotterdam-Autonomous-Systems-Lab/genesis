// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {EscrowTestBase} from "./EscrowTestBase.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

contract EscrowHandler is Test {
    Escrow public immutable escrow;
    address public immutable a;
    address public immutable b;
    uint256 private immutable keyA;
    uint256 private immutable keyB;
    uint256 private nextNonce;
    bytes32[] private ids;
    uint256[] private revoked;
    mapping(bytes32 => Escrow.State) public modelState;
    uint256 public modelLocked;
    uint256 public modelCreditA;
    uint256 public modelCreditB;
    uint256 public modelDeposited;
    uint256 public modelWithdrawn;

    constructor(Escrow e, address a_, address b_, uint256 ka, uint256 kb) {
        escrow = e;
        a = a_;
        b = b_;
        keyA = ka;
        keyB = kb;
    }

    function sig(uint256 k, bytes32 digest) private pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(k, digest);
        return abi.encodePacked(r, s, v);
    }

    function open(uint64 x, uint64 y, uint96 seed) external {
        uint256 n = nextNonce++;
        uint256 price = 1 + uint256(seed) % escrow.MAX_PRICE();
        Escrow.Agreement memory t = Escrow.Agreement(
            a,
            b,
            escrow.SERVICE_ID(),
            x,
            y,
            price,
            uint64(block.timestamp + 60),
            uint64(block.timestamp + 120),
            keccak256(abi.encode(n)),
            escrow.runId()
        );
        bytes32 id = escrow.hashAgreement(t);
        Escrow.Authorization memory auth = Escrow.Authorization(a, b, id, n, price, t.fundingDeadline, escrow.runId());
        bytes memory sa = sig(keyA, id);
        bytes memory sb = sig(keyB, id);
        bytes memory sx = sig(keyA, escrow.hashAuthorization(auth));
        vm.prank(a);
        escrow.fund{value: price}(t, sa, sb, auth, sx);
        ids.push(id);
        modelState[id] = Escrow.State.Funded;
        modelLocked += price;
        modelDeposited += price;
    }

    function complete(uint256 index) external {
        if (ids.length == 0) return;
        bytes32 id = ids[index % ids.length];
        Escrow.Record memory record = escrow.getAgreement(id);
        if (record.state != Escrow.State.Funded || block.timestamp >= record.terms.settlementDeadline) return;
        Escrow.Result memory r = Escrow.Result(id, uint256(record.terms.x) + record.terms.y, escrow.runId());
        Escrow.Acceptance memory c =
            Escrow.Acceptance(id, escrow.hashResult(r), record.authorizationNonce, escrow.runId());
        bytes memory sr = sig(keyB, escrow.hashResult(r));
        bytes memory sc = sig(keyA, escrow.hashAcceptance(c));
        vm.prank(b);
        escrow.settle(id, r, sr, c, sc);
        modelState[id] = Escrow.State.Settled;
        modelLocked -= record.terms.price;
        modelCreditB += record.terms.price;
    }

    function timeout(uint256 index) external {
        if (ids.length == 0) return;
        bytes32 id = ids[index % ids.length];
        Escrow.Record memory record = escrow.getAgreement(id);
        if (record.state != Escrow.State.Funded || block.timestamp < record.terms.settlementDeadline) return;
        vm.prank(a);
        escrow.refund(id);
        modelState[id] = Escrow.State.Refunded;
        modelLocked -= record.terms.price;
        modelCreditA += record.terms.price;
    }

    function elapse(uint64 delta) external {
        vm.warp(block.timestamp + uint256(delta) % 181);
    }

    function revoke() external {
        uint256 n = nextNonce++;
        vm.prank(a);
        escrow.revokeUnused(n);
        revoked.push(n);
    }

    function withdrawCredit(bool requester) external {
        uint256 amount = requester ? modelCreditA : modelCreditB;
        if (amount == 0) return;
        vm.prank(requester ? a : b);
        escrow.withdraw();
        if (requester) modelCreditA = 0;
        else modelCreditB = 0;
        modelWithdrawn += amount;
    }

    function checkRecordsAndNonces() external view {
        for (uint256 i = 0; i < ids.length; i++) {
            Escrow.Record memory r = escrow.getAgreement(ids[i]);
            assertEq(uint256(r.state), uint256(modelState[ids[i]]));
            assertEq(escrow.hashAgreement(r.terms), ids[i]);
            assertEq(uint256(escrow.nonceStatus(a, r.authorizationNonce)), uint256(Escrow.NonceStatus.Consumed));
        }
        for (uint256 i = 0; i < revoked.length; i++) {
            assertEq(uint256(escrow.nonceStatus(a, revoked[i])), uint256(Escrow.NonceStatus.Revoked));
        }
    }
}

contract EscrowInvariantTest is EscrowTestBase {
    EscrowHandler private handler;

    function setUp() public override {
        super.setUp();
        handler = new EscrowHandler(escrow, a, b, keyA, keyB);
        bytes4[] memory selectors = new bytes4[](6);
        selectors[0] = handler.open.selector;
        selectors[1] = handler.complete.selector;
        selectors[2] = handler.timeout.selector;
        selectors[3] = handler.elapse.selector;
        selectors[4] = handler.revoke.selector;
        selectors[5] = handler.withdrawCredit.selector;
        targetSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
        targetContract(address(handler));
    }

    function invariant_ConservationAndSolvency() public view {
        checkAccounting();
    }

    function invariant_TotalsMatchIndependentModel() public view {
        assertEq(escrow.totalLocked(), handler.modelLocked());
        assertEq(escrow.totalDeposited(), handler.modelDeposited());
        assertEq(escrow.totalWithdrawn(), handler.modelWithdrawn());
    }

    function invariant_OnlyIntendedBeneficiaryCredits() public view {
        assertEq(escrow.credits(a), handler.modelCreditA());
        assertEq(escrow.credits(b), handler.modelCreditB());
        assertEq(escrow.totalCredits(), handler.modelCreditA() + handler.modelCreditB());
        assertEq(escrow.credits(stranger), 0);
    }

    function invariant_ImmutableRecordsAndTerminalNonces() public view {
        handler.checkRecordsAndNonces();
    }
}
