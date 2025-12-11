// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LucidBlocks
 * @dev Stores committed lucid block headers and minimal indexing for EVM integration.
 */
contract LucidBlocks {
    struct Header {
        uint64 dreamSequenceId;
        uint32 dreamRecordCount;
        bytes32 previousLucidHash;
        bytes32 lucidHash;
        address envisioner;
        bytes lucidityProof; // threshold signature bytes (off-chain formed)
    }

    mapping(uint64 => Header) public headers;
    uint64 public latestSequence;

    event LucidBlockCommitted(uint64 indexed dreamSequenceId, bytes32 lucidHash, address indexed envisioner);

    /// @notice Commit a finalized lucid block header to chain
    /// @dev Verification of lucidity proof is performed off-chain for now
    function commitHeader(
        uint64 dreamSequenceId,
        uint32 dreamRecordCount,
        bytes32 previousLucidHash,
        bytes32 lucidHash,
        address envisioner,
        bytes calldata lucidityProof
    ) external {
        require(headers[dreamSequenceId].lucidHash == bytes32(0), "header exists");
        headers[dreamSequenceId] = Header({
            dreamSequenceId: dreamSequenceId,
            dreamRecordCount: dreamRecordCount,
            previousLucidHash: previousLucidHash,
            lucidHash: lucidHash,
            envisioner: envisioner,
            lucidityProof: lucidityProof
        });
        if (dreamSequenceId > latestSequence) {
            latestSequence = dreamSequenceId;
        }
        emit LucidBlockCommitted(dreamSequenceId, lucidHash, envisioner);
    }

    function getHeader(uint64 dreamSequenceId) external view returns (Header memory) {
        return headers[dreamSequenceId];
    }
}
