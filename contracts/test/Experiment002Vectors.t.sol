// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {Experiment002Escrow as E} from "../src/Experiment002Escrow.sol";
/// @dev Public constants copied from frozen JSON; real signatures, no fixture private keys.

contract Experiment002VectorsTest is Test {
    E e;

    function setUp() public {
        vm.chainId(31337);
        vm.warp(1000);
        E template = new E(bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222"));
        address fixedAddress = address(bytes20(hex"1111111111111111111111111111111111111111"));
        vm.etch(fixedAddress, address(template).code);
        e = E(payable(fixedAddress));
    }

    function test_V01_nominal() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            7,
            11,
            1000000000000,
            1120,
            1300,
            bytes32(hex"3333333333333333333333333333333333333333333333333333333333333333"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"3a6536fff5884f850a3ff7aa50efadd24f392e2e1a2e6175c420c1fcf8290817"),
            0,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"3a6536fff5884f850a3ff7aa50efadd24f392e2e1a2e6175c420c1fcf8290817"),
            0,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"3a6536fff5884f850a3ff7aa50efadd24f392e2e1a2e6175c420c1fcf8290817"));
        assertEq(e.hashAuthorization(q), bytes32(hex"047a36a9cf62a3b2cce4179c73bb4f7488e1cefbc6b09cf634127c41a9457437"));
        assertEq(e.hashClaim(c), bytes32(hex"4df1ff9da827c2a0e5311c4f5d924b093bf5ae6dc61946e4f0d25daa07fcf847"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        e.fund{value: t.price}(
            t,
            q,
            hex"f23ac06f086ab56c7d956f0e6d024cc1e28faf8754cd80e469c2dd2363ca94dc559d65530d0e18ac6512088e91379e67d092250af7b50ff40e62b6d0265757c01c",
            hex"99361835274db4a79fc119d166b50a8452ee83410113bb16c87beaa7928aecef133354f34652f59ea82e0fddfd9b07c5afc046f7695da3af179af373d1d7d7e91b",
            hex"1478a7ed0f21e1f72380d39daae5caaa6e1efb70c9b4f55c0b367eb992f00ee207875d4c413c1d9da972ac3bb5e4ad79ff1808beb5c3129382512525272049631c"
        );
        vm.prank(t.provider);
        e.claim(
            c,
            hex"e80c126e32a051192c70ba89b68e12d397147a95235cfb8c3258a018e7101de1156d6328baf83698e28716d13ae3e768eb22f003886cff48c71ca39092fe127a1c"
        );
        (,, E.State state, uint256 value) = e.getRecord(c.agreementId);
        assertEq(uint256(state), 2);
        assertEq(value, c.value);
        assertEq(e.credits(t.provider), t.price);
    }

    function test_V02_max_operands() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            18446744073709551615,
            18446744073709551615,
            1000000000000,
            1120,
            1300,
            bytes32(hex"4444444444444444444444444444444444444444444444444444444444444444"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"247f3b806fae7fe67413a9021dd00d7a25b3dbf67b7d1e5aa356fc7f92c0e178"),
            1,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"247f3b806fae7fe67413a9021dd00d7a25b3dbf67b7d1e5aa356fc7f92c0e178"),
            1,
            36893488147419103230,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"247f3b806fae7fe67413a9021dd00d7a25b3dbf67b7d1e5aa356fc7f92c0e178"));
        assertEq(e.hashAuthorization(q), bytes32(hex"40fa322a9b1a565dfed663bf3bd60aafa5e30793483e24e59c2a41d596c72fda"));
        assertEq(e.hashClaim(c), bytes32(hex"05c0c28dd92c6ce4e3a6be70d64fd3be0d811422b150ed39abb633ab8ee2a884"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        e.fund{value: t.price}(
            t,
            q,
            hex"b3a93a5018ca701b05f3a03ffaf0f829125be895bd9b652bf3300a3c3035b6fe1c9c97d873110cb2af15213d464405418f3057ffd5fefad2eb1c92c9d444ad7e1b",
            hex"e0d7dd32458709526edd5f6d21c25e7f2e079aac1ba213d71ef2c6ac47dd376b6895066a2e75ce0e2548521d98a0b6f7f382b5d195f7014f63e9a14527f780ae1b",
            hex"c3cb7be540989e3ca882da8343e0503801a87473b856141138b032218c386fce3a885f1c9c30db6ad8208d364f6401b9d04819752e54fc34b3108f42e7b6e4ef1b"
        );
        vm.prank(t.provider);
        e.claim(
            c,
            hex"ff787741b06a13a1f9a7305518ed9baf884c02c51e4c74c9d68af20d7304531945d4fbc29bfd59eb32bb7d0ee1cc51e2423534bfe6f131d96e11c538272c80d31c"
        );
        (,, E.State state, uint256 value) = e.getRecord(c.agreementId);
        assertEq(uint256(state), 2);
        assertEq(value, c.value);
        assertEq(e.credits(t.provider), t.price);
    }

    function test_V03_zero_price() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            7,
            11,
            0,
            1120,
            1300,
            bytes32(hex"5555555555555555555555555555555555555555555555555555555555555555"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"833b0804bc682a542f32d6a27751e48c964bc4cb60354e34176b1f6b5d4950e7"),
            2,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"833b0804bc682a542f32d6a27751e48c964bc4cb60354e34176b1f6b5d4950e7"),
            2,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"833b0804bc682a542f32d6a27751e48c964bc4cb60354e34176b1f6b5d4950e7"));
        assertEq(e.hashAuthorization(q), bytes32(hex"476c461a0b155427c9f2d4997f5f39c595fbe71c4cfee4ce960a25bc37e67c0b"));
        assertEq(e.hashClaim(c), bytes32(hex"5d37312597a0346cad4c7fd9b83b727d7370b13a7fdbba8ed8153e14e279a459"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        vm.expectRevert();
        e.fund{value: t.price}(
            t,
            q,
            hex"6a4d2b52c18da2a713717bcfea850f275f5f1f12d16b61c9461cc5cb2a495b302a997a146ab2d2f4d4837ea9aa3713f5b6787f74df7b7e3a026d3847a09bf3611b",
            hex"04cf09546125fda573777791c80bedd226c8292ec1bc97e99a6537ca6517c1071a4fadcc2a0118b7d13094f9e1bdb493ca2ef3e1b924152605f8ed93eeddd9461b",
            hex"bae47cce71deceeade165f01870203ffbf66e1964112ffcc3402195739d115d44240fc50bbb34bbf2431b4c4b41927760682faa87708f706b4fa22e6dc0c57241b"
        );
        (,, E.State state,) = e.getRecord(q.agreementId);
        assertEq(uint256(state), 0);
        assertEq(uint256(e.nonceStatus(t.requester, q.nonce)), 0);
    }

    function test_V04_price_over_cap() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            7,
            11,
            2000000000001,
            1120,
            1300,
            bytes32(hex"6666666666666666666666666666666666666666666666666666666666666666"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"67ee93d1f664f937d3d69cac5dbb7693259b89f6d84ae864fa98de1227aa86b3"),
            3,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"67ee93d1f664f937d3d69cac5dbb7693259b89f6d84ae864fa98de1227aa86b3"),
            3,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"67ee93d1f664f937d3d69cac5dbb7693259b89f6d84ae864fa98de1227aa86b3"));
        assertEq(e.hashAuthorization(q), bytes32(hex"3441b971be8a647bd43c202e49d15c7afd0f07fb143310ff02a2a2b4ef43d43b"));
        assertEq(e.hashClaim(c), bytes32(hex"9dd9f66a86bffd220e1e80cfa00727284b33bc61db19d229351baab7e16b9211"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        vm.expectRevert();
        e.fund{value: t.price}(
            t,
            q,
            hex"1c126c2ffacad0e4dce524efe9b8b922f5e43fffeff4ea40da235dcfa6dd70bb4bbc7a7b456e8f2441ae2020713637bb3774db12269cee1e69717f6e56e5afd71b",
            hex"0232f6690a53c9019e3b1c7d43f9a8927f44958d99fc525e7d3e009b6cb25def58fe83a1321be7d93c7ebce2fa076dbcd39189c8b98cb810addaddde14f617671b",
            hex"337eecbe9441de6496441432f7a3e5eb6d051b94ecec00691411c837c77327996e47eac8cc65a9fb38e09bbc081e47bffb0fe9c95133faabbb56225b86d324a61c"
        );
        (,, E.State state,) = e.getRecord(q.agreementId);
        assertEq(uint256(state), 0);
        assertEq(uint256(e.nonceStatus(t.requester, q.nonce)), 0);
    }

    function test_V05_wrong_policy() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"7777777777777777777777777777777777777777777777777777777777777777"),
            7,
            11,
            1000000000000,
            1120,
            1300,
            bytes32(hex"7777777777777777777777777777777777777777777777777777777777777777"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"3bc9a6706315c8f515e528cea52f95d37f730340182671ace7a6d0c9e3afecce"),
            4,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"3bc9a6706315c8f515e528cea52f95d37f730340182671ace7a6d0c9e3afecce"),
            4,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"3bc9a6706315c8f515e528cea52f95d37f730340182671ace7a6d0c9e3afecce"));
        assertEq(e.hashAuthorization(q), bytes32(hex"24edd39ee4c2286eb351a1181f777e7bd82ea2b99fc060b0a249deadef35a1dc"));
        assertEq(e.hashClaim(c), bytes32(hex"28ff02957944cd731603f5d57a46152cc4cd723e21585e674e6c6d59f4596410"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        vm.expectRevert();
        e.fund{value: t.price}(
            t,
            q,
            hex"e2de0d563e99a84f5db18840aa2a6285b2d264468e0f214cdb9644919d7c4a9130f02bdc20ad033fd6d93ed9255f0333473d233a7a2be377c45b67bc77c89a711c",
            hex"a3b0606d0c312f04690b86e790e536a8dc296f8f9e68113fce3dd02ba1540f3a49b9d0fcd2aefbe57d2728bbaaf95d2bec66ddaedd46917cafb6f4627c1bb0cb1c",
            hex"230c33834a5811676d033fbd821ce1147d4e8e844036dfc28702843631a11a0a5e6431c8ad5865e2c3251c7308a07ab962aabac3dc2f6b8195fef22e7a8248781b"
        );
        (,, E.State state,) = e.getRecord(q.agreementId);
        assertEq(uint256(state), 0);
        assertEq(uint256(e.nonceStatus(t.requester, q.nonce)), 0);
    }

    function test_V06_late_funding() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            7,
            11,
            1000000000000,
            1299,
            1300,
            bytes32(hex"8888888888888888888888888888888888888888888888888888888888888888"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"15ff935596317375a50c3159152649f627658bc025179dae79cae72754b47cfa"),
            5,
            2000000000000,
            1299,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"15ff935596317375a50c3159152649f627658bc025179dae79cae72754b47cfa"),
            5,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"15ff935596317375a50c3159152649f627658bc025179dae79cae72754b47cfa"));
        assertEq(e.hashAuthorization(q), bytes32(hex"914a782ed3782779bed9b83907e2b1fe863c93405d818ec58ff7cf5ab5286eb1"));
        assertEq(e.hashClaim(c), bytes32(hex"b16d8cabcbebd5191ad8b59959f010f902169a21c26d7e84450d7bd35d68cfc4"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        e.fund{value: t.price}(
            t,
            q,
            hex"1b45d4b3b42aa05773bdd57e7d6159865d999ddbda4daddb2c941f4f963a10c0352ef9d90fc472f5771db584aa1617066e8f9459c461942cbd8528a033ac279b1c",
            hex"b29c9f8d51c730229bba89c4b2f6326e99d87d7f169ee0936d1e7eeb2358863a279fa0f939b507ce8f961f02e221cd6b90008d756b42332f67c35e1469d56e341c",
            hex"e17365548cfb7827317dd4f72338300b8c707eec51e938dada5ca5a36f60b6961c8cf3462846cf171b44881021c2426139705532580e0dbed80839bdb4273dc31c"
        );
        vm.prank(t.provider);
        e.claim(
            c,
            hex"128dbe5f42a2c1212ed0908a47619778d669c819749b76196c62586db5b466fd3647ee861ae6b4c7737954d13c2c7fd0e8dbb7f74cd6200ebf7d2b3730efa5d51b"
        );
        (,, E.State state, uint256 value) = e.getRecord(c.agreementId);
        assertEq(uint256(state), 2);
        assertEq(value, c.value);
        assertEq(e.credits(t.provider), t.price);
    }

    function test_V07_repeated_work() public {
        E.Terms memory t = E.Terms(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"47834750b7b5efb398f945a6f35d9719e5c854a6ebadde233cb70339cfe643bc"),
            bytes32(hex"1d6ddd70729ad2873537066269d1c77abd5bc2b500404336bd8f564c298fb0e0"),
            7,
            11,
            1000000000000,
            1120,
            1300,
            bytes32(hex"9999999999999999999999999999999999999999999999999999999999999999"),
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Authorization memory q = E.Authorization(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"9cfef38df8330390663877fae0d85287bd878fa422cbf6e3ec2d76b6fd2f4cbb"),
            6,
            2000000000000,
            1120,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        E.Claim memory c = E.Claim(
            address(bytes20(hex"6a1d8d21818039ab4a180a29961ec4a299841290")),
            address(bytes20(hex"176ab2f68a14156794f05943e131aeaf273a9acc")),
            bytes32(hex"9cfef38df8330390663877fae0d85287bd878fa422cbf6e3ec2d76b6fd2f4cbb"),
            6,
            18,
            bytes32(hex"2222222222222222222222222222222222222222222222222222222222222222")
        );
        assertEq(e.hashTerms(t), bytes32(hex"9cfef38df8330390663877fae0d85287bd878fa422cbf6e3ec2d76b6fd2f4cbb"));
        assertEq(e.hashAuthorization(q), bytes32(hex"a1244a920caec315b5dc44b0cf861f214ecfe9a7d470302c464067cf3b666fa9"));
        assertEq(e.hashClaim(c), bytes32(hex"587f24f1e538bd4d0ba93bc97bc04ade9ad0d5983a2672c4a604755d53aaa337"));
        vm.deal(t.requester, 1 ether);
        vm.prank(t.requester);
        e.fund{value: t.price}(
            t,
            q,
            hex"a6bedb2e0d93529fdd53c9b2c65fa2ec2e670c1e54bb6f69c68767b7bba128a149115bb49869b7bbf40a9a3bb8d9be566768b925dd8003996098707de68840df1b",
            hex"f3c321c243c0ce382cef8a801b74b305364c3a17efb159c68734e0032868065e4ecbeb4843a8469e9937b6f57ccd3924e37adcffb86097b52fa88ee1443d4df11c",
            hex"dfcac5dcb343c4d51c52b507d5ceb3909c20dca5393adbb38b985adbdbdd545f5040ad74dd75eced90ea6633b812ff3e9d0da1183227fc025327fbda14c59a331c"
        );
        vm.prank(t.provider);
        e.claim(
            c,
            hex"74d44a714db3894c32955c943bf5ae52cbfbc87519022076e10069be1c98969b36b575ea4586f2824bc1fba05709a791027043bb57f75dfc31a9e8de9684a7b41b"
        );
        (,, E.State state, uint256 value) = e.getRecord(c.agreementId);
        assertEq(uint256(state), 2);
        assertEq(value, c.value);
        assertEq(e.credits(t.provider), t.price);
    }
}
