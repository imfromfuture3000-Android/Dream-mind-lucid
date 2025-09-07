// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./LucidBlocks.sol";

/**
 * @title ConsensusCoordinator
 * @dev Simple coordinator for finalizing lucid blocks on-chain. In production,
 * threshold signature verification (BLS) should be performed on-chain or via a precompile.
 */
contract ConsensusCoordinator {
    LucidBlocks public immutable lucidBlocks;
    address public admin;
    BLSVerifier public verifier;

    event Finalized(uint64 indexed dreamSequenceId, bytes32 lucidHash);

    constructor(address lucidBlocksAddr, address blsVerifier) {
        lucidBlocks = LucidBlocks(lucidBlocksAddr);
        admin = msg.sender;
        verifier = BLSVerifier(blsVerifier);
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "not admin");
        _;
    }

    /// @notice Finalize a lucid block header on-chain.
    /// @dev Verifies lucidity proof via BLS verifier precompile (or forceVerify).
    function finalize(
        uint64 dreamSequenceId,
        uint32 dreamRecordCount,
        bytes32 previousLucidHash,
        bytes32 lucidHash,
        address envisioner,
        bytes calldata lucidityProof,
        bytes calldata aggregatedPubkey,
        bytes calldata aggregatedSignature
    ) external onlyAdmin {
        // message for signature verification: e.g., encode(dreamSequenceId, lucidHash)
        bytes memory message = abi.encodePacked(dreamSequenceId, lucidHash);
        bool ok = verifier.verify(aggregatedPubkey, message, aggregatedSignature);
        require(ok, "BLS verification failed");
        lucidBlocks.commitHeader(dreamSequenceId, dreamRecordCount, previousLucidHash, lucidHash, envisioner, lucidityProof);
        emit Finalized(dreamSequenceId, lucidHash);
    }

    function setAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }

    function setVerifier(address v) external onlyAdmin {
        verifier = BLSVerifier(v);
    }
}
