// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {EscrowTestBase} from "./EscrowTestBase.sol";
import {Experiment001Escrow as Escrow} from "../src/Experiment001Escrow.sol";

contract EscrowSignaturesTest is EscrowTestBase {
    function testFuzz_MutatedAgreement(uint8 field) public {
        field = uint8(bound(field, 0, 9));
        Escrow.Agreement memory t = terms(0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        if (field == 0) t.requester = stranger;
        if (field == 1) t.provider = stranger;
        if (field == 2) t.serviceId = keccak256("other-service");
        if (field == 3) t.x++;
        if (field == 4) t.y++;
        if (field == 5) t.price++;
        if (field == 6) t.fundingDeadline++;
        if (field == 7) t.settlementDeadline++;
        if (field == 8) t.salt = keccak256("new-salt");
        if (field == 9) t.runId = keccak256("other-run");
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        vm.expectRevert();
        escrow.fund{value: t.price}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function testFuzz_MutatedAuthorization(uint8 field) public {
        field = uint8(bound(field, 0, 6));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        if (field == 0) auth.requester = stranger;
        if (field == 1) auth.provider = stranger;
        if (field == 2) auth.agreementId = keccak256("wrong-id");
        if (field == 3) auth.nonce++;
        if (field == 4) auth.maxAmount--;
        if (field == 5) auth.validUntil--;
        if (field == 6) auth.runId = keccak256("other-run");
        vm.prank(a);
        vm.expectRevert();
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(escrow.hashAgreement(t), auth.nonce);
    }

    function testFuzz_MutatedResult(uint8 field) public {
        field = uint8(bound(field, 0, 2));
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        if (field == 0) r.agreementId = keccak256("other-agreement");
        if (field == 1) r.value++;
        if (field == 2) r.runId = keccak256("other-run");
        // Even if A signs the tampered claim, B's original signature is not transferable.
        c.resultDigest = escrow.hashResult(r);
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        vm.prank(b);
        vm.expectRevert();
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
    }

    function testFuzz_MutatedAcceptance(uint8 field) public {
        field = uint8(bound(field, 0, 3));
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(c));
        if (field == 0) c.agreementId = keccak256("other-agreement");
        if (field == 1) c.resultDigest = keccak256("other-result");
        if (field == 2) c.authorizationNonce++;
        if (field == 3) c.runId = keccak256("other-run");
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidBinding.selector);
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
    }

    function testFuzz_WrongFundingSigners(uint8 which) public {
        which = uint8(bound(which, 0, 2));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(which == 0 ? keyB : keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(which == 1 ? keyA : keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(which == 2 ? keyB : keyA, escrow.hashAuthorization(auth));
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function testFuzz_WrongEvidenceSigners(bool wrongProvider) public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes memory sr = sign(wrongProvider ? keyA : keyB, escrow.hashResult(r));
        bytes memory sc = sign(wrongProvider ? keyA : keyB, escrow.hashAcceptance(c));
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
    }

    function testFuzz_MalformedSignatures(uint8 choice) public {
        choice = uint8(bound(choice, 0, 5));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        if (choice == 0) sa = new bytes(0);
        if (choice == 1) sa = new bytes(64);
        if (choice == 2) sa = new bytes(66);
        if (choice == 3) sa = new bytes(65);
        if (choice == 4) sa[64] = bytes1(uint8(0));
        if (choice == 5) {
            (uint8 v, bytes32 r, bytes32 s) = vm.sign(keyA, escrow.hashAgreement(t));
            uint256 n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;
            sa = abi.encodePacked(r, bytes32(n - uint256(s)), uint8(v == 27 ? 28 : 27));
        }
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function domain(string memory name, string memory version, uint256 chain, address verifier)
        internal
        pure
        returns (bytes32)
    {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes(name)),
                keccak256(bytes(version)),
                chain,
                verifier
            )
        );
    }

    function typed(bytes32 d, bytes32 h) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(hex"1901", d, h));
    }

    function flatAgreement(Escrow.Agreement memory t) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256(
                    "Agreement(address requester,address provider,bytes32 serviceId,uint64 x,uint64 y,uint256 price,uint64 fundingDeadline,uint64 settlementDeadline,bytes32 salt,bytes32 runId)"
                ),
                t.requester,
                t.provider,
                t.serviceId,
                t.x,
                t.y,
                t.price,
                t.fundingDeadline,
                t.settlementDeadline,
                t.salt,
                t.runId
            )
        );
    }

    function testFuzz_WrongSigningDomain(uint8 field) public {
        field = uint8(bound(field, 0, 3));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes32 d = domain(
            field == 0 ? "wrong-name" : "GenesisExperiment001",
            field == 1 ? "2" : "1",
            field == 2 ? 1 : 31337,
            field == 3 ? stranger : address(escrow)
        );
        bytes memory sa = sign(keyA, typed(d, flatAgreement(t)));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_CrossContractReplay() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        Escrow other = new Escrow(escrow.runId());
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidBinding.selector);
        other.fund{value: PRICE}(t, sa, sb, auth, sx);
        assertEq(other.totalLocked(), 0);
    }

    function test_CrossChainReplayAndDynamicDomain() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        bytes32 before = escrow.hashAgreement(t);
        vm.chainId(1);
        assertNotEq(escrow.hashAgreement(t), before);
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidBinding.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(before, 0);
    }

    function test_PreviousRunAtSameAddressRejected() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        Escrow next = new Escrow(keccak256("fresh-run"));
        vm.etch(address(escrow), address(next).code);
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidBinding.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sx);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_SignaturePurposeCannotBeSubstituted() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        vm.prank(a);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.fund{value: PRICE}(t, sa, sb, auth, sa);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_IndependentFlatEncodingsForAllFiveTypes() public view {
        bytes32 d = domain("GenesisExperiment001", "1", 31337, address(escrow));
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory x = permission(t, 0);
        Escrow.Result memory r = Escrow.Result(x.agreementId, 18, escrow.runId());
        Escrow.Acceptance memory c = Escrow.Acceptance(x.agreementId, escrow.hashResult(r), 0, escrow.runId());
        Escrow.Advertisement memory ad = Escrow.Advertisement(b, escrow.SERVICE_ID(), PRICE, 1060, escrow.runId());
        assertEq(escrow.hashAgreement(t), typed(d, flatAgreement(t)));
        assertEq(
            escrow.hashAuthorization(x),
            typed(
                d,
                keccak256(
                    abi.encode(
                        keccak256(
                            "Authorization(address requester,address provider,bytes32 agreementId,uint256 nonce,uint256 maxAmount,uint64 validUntil,bytes32 runId)"
                        ),
                        x.requester,
                        x.provider,
                        x.agreementId,
                        x.nonce,
                        x.maxAmount,
                        x.validUntil,
                        x.runId
                    )
                )
            )
        );
        assertEq(
            escrow.hashResult(r),
            typed(
                d,
                keccak256(
                    abi.encode(
                        keccak256("Result(bytes32 agreementId,uint256 value,bytes32 runId)"),
                        r.agreementId,
                        r.value,
                        r.runId
                    )
                )
            )
        );
        assertEq(
            escrow.hashAcceptance(c),
            typed(
                d,
                keccak256(
                    abi.encode(
                        keccak256(
                            "Acceptance(bytes32 agreementId,bytes32 resultDigest,uint256 authorizationNonce,bytes32 runId)"
                        ),
                        c.agreementId,
                        c.resultDigest,
                        c.authorizationNonce,
                        c.runId
                    )
                )
            )
        );
        assertEq(
            escrow.hashAdvertisement(ad),
            typed(
                d,
                keccak256(
                    abi.encode(
                        keccak256(
                            "Advertisement(address provider,bytes32 serviceId,uint256 price,uint64 expiresAt,bytes32 runId)"
                        ),
                        ad.provider,
                        ad.serviceId,
                        ad.price,
                        ad.expiresAt,
                        ad.runId
                    )
                )
            )
        );
    }

    function test_OutOfRangeOperandABIRejected() public {
        Escrow.Agreement memory t = terms(0);
        Escrow.Authorization memory auth = permission(t, 0);
        bytes memory sa = sign(keyA, escrow.hashAgreement(t));
        bytes memory sb = sign(keyB, escrow.hashAgreement(t));
        bytes memory sx = sign(keyA, escrow.hashAuthorization(auth));
        bytes memory data = abi.encodeCall(escrow.fund, (t, sa, sb, auth, sx));
        assembly {
            mstore(add(data, 132), shl(64, 1))
        }
        vm.prank(a);
        (bool ok,) = address(escrow).call{value: PRICE}(data);
        assertFalse(ok);
        checkUnfunded(auth.agreementId, 0);
    }

    function test_CrossAgreementAcceptanceCannotReleaseSecondEscrow() public {
        bytes32 first = funded();
        Escrow.Agreement memory t = terms(1);
        bytes32 second = fund(t, permission(t, 1));
        (, Escrow.Acceptance memory firstReceipt) = evidence(first, 18);
        (Escrow.Result memory secondResult,) = evidence(second, 18);
        bytes memory sr = sign(keyB, escrow.hashResult(secondResult));
        bytes memory sc = sign(keyA, escrow.hashAcceptance(firstReceipt));
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidBinding.selector);
        escrow.settle(second, secondResult, sr, firstReceipt, sc);
        assertEq(escrow.totalLocked(), 2 * PRICE);
        assertEq(escrow.totalCredits(), 0);
        checkAccounting();
    }

    function test_CorrectResultWithWrongDomainAcceptance() public {
        bytes32 id = funded();
        (Escrow.Result memory r, Escrow.Acceptance memory c) = evidence(id, 18);
        bytes32 h = keccak256(
            abi.encode(
                keccak256(
                    "Acceptance(bytes32 agreementId,bytes32 resultDigest,uint256 authorizationNonce,bytes32 runId)"
                ),
                c.agreementId,
                c.resultDigest,
                c.authorizationNonce,
                c.runId
            )
        );
        bytes memory sr = sign(keyB, escrow.hashResult(r));
        bytes memory sc = sign(keyA, typed(domain("GenesisExperiment001", "1", 31337, stranger), h));
        vm.prank(b);
        vm.expectRevert(Escrow.InvalidSignature.selector);
        escrow.settle(id, r, sr, c, sc);
        checkFunded(id);
    }
}
