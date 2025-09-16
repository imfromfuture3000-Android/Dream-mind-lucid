Contracts in this directory:

- DreamRecords.sol — stores dream payloads and emits submission events.
- LucidBlocks.sol — stores finalized lucid block headers.
- ConsensusCoordinator.sol — admin-coordinated finalization entrypoint (placeholder for on-chain verification).

Goal: Off-chain OneiroAgent runs Dream-Mind-Lucid phases, forms lucidity proofs and threshold signatures, then calls `ConsensusCoordinator.finalize` to record a committed lucid header on-chain.
