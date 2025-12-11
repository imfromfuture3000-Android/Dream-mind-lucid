// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IDreamOracle
 * @dev Interface for the Dream Oracle system
 */
interface IDreamOracle {
    function getDreamPrice() external view returns (uint256);
    function getSMindPrice() external view returns (uint256);
    function getLucidPrice() external view returns (uint256);
    function getNetworkStats() external view returns (
        uint256 activeAgents,
        uint256 dreamVolume24h,
        uint256 avgGasPrice,
        uint256 tvl,
        uint256 liquidityDepth
    );
}
