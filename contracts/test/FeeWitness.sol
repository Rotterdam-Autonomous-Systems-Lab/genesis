// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

/// @notice Test-only RPC diagnostic. Not an escrow or supported agent service.
contract FeeWitness {
    event FeeObserved(uint256 gasPrice, uint256 baseFee);

    function observe() external {
        emit FeeObserved(tx.gasprice, block.basefee);
    }

    function fail() external pure {
        revert("diagnostic revert");
    }
}
