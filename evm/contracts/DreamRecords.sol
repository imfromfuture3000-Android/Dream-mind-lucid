// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title DreamRecords
 * @dev Minimal contract to accept and store dream records on-chain (EVM).
 * This is a lightweight storage and event-emitter used by the off-chain OneiroAgent.
 */
contract DreamRecords {
    event DreamSubmitted(address indexed dreamer, uint256 indexed dreamId, bytes dreamData);

    uint256 public nextDreamId;
    mapping(uint256 => bytes) public dreams;
    mapping(uint256 => address) public dreamerOf;

    /// @notice Submit a dream record to the chain
    /// @param dreamData Arbitrary dream bytes (could be a pointer or compressed payload)
    /// @return dreamId The assigned dream id
    function submitDream(bytes calldata dreamData) external returns (uint256 dreamId) {
        dreamId = nextDreamId++;
        dreams[dreamId] = dreamData;
        dreamerOf[dreamId] = msg.sender;
        emit DreamSubmitted(msg.sender, dreamId, dreamData);
    }
}
