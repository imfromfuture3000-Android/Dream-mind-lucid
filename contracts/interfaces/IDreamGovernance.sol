// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IDreamGovernance
 * @dev Interface for DAO governance in the Dream ecosystem
 * @notice Provides timelock mechanisms, proposal management, and voting functionality
 */
interface IDreamGovernance {
    // ============ Structs ============
    
    /**
     * @notice Structure representing a governance proposal
     * @param id Unique proposal identifier
     * @param proposer Address that created the proposal
     * @param targets Array of target contract addresses
     * @param values Array of ETH values to send with calls
     * @param signatures Array of function signatures to call
     * @param calldatas Array of encoded function call data
     * @param startBlock Block number when voting starts
     * @param endBlock Block number when voting ends
     * @param forVotes Number of votes in favor
     * @param againstVotes Number of votes against
     * @param abstainVotes Number of abstain votes
     * @param canceled Whether the proposal has been canceled
     * @param executed Whether the proposal has been executed
     * @param eta Estimated time of execution (for timelock)
     */
    struct Proposal {
        uint256 id;
        address proposer;
        address[] targets;
        uint256[] values;
        string[] signatures;
        bytes[] calldatas;
        uint256 startBlock;
        uint256 endBlock;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool canceled;
        bool executed;
        uint256 eta;
    }

    /**
     * @notice Enumeration of proposal states
     */
    enum ProposalState {
        Pending,
        Active,
        Canceled,
        Defeated,
        Succeeded,
        Queued,
        Expired,
        Executed
    }

    /**
     * @notice Enumeration of vote types
     */
    enum VoteType {
        Against,
        For,
        Abstain
    }

    // ============ Events ============
    
    /**
     * @notice Emitted when a new proposal is created
     * @param proposalId The ID of the created proposal
     * @param proposer The address that created the proposal
     * @param targets The target addresses for the proposal
     * @param values The ETH values for the proposal calls
     * @param signatures The function signatures for the proposal
     * @param calldatas The call data for the proposal
     * @param startBlock The block when voting starts
     * @param endBlock The block when voting ends
     * @param description The proposal description
     */
    event ProposalCreated(
        uint256 proposalId,
        address proposer,
        address[] targets,
        uint256[] values,
        string[] signatures,
        bytes[] calldatas,
        uint256 startBlock,
        uint256 endBlock,
        string description
    );

    /**
     * @notice Emitted when a vote is cast
     * @param voter The address that voted
     * @param proposalId The proposal ID voted on
     * @param support The vote type (0=against, 1=for, 2=abstain)
     * @param weight The voting weight
     * @param reason The reason for the vote
     */
    event VoteCast(
        address indexed voter,
        uint256 proposalId,
        uint8 support,
        uint256 weight,
        string reason
    );

    /**
     * @notice Emitted when a proposal is queued in the timelock
     * @param proposalId The proposal ID
     * @param eta The estimated execution time
     */
    event ProposalQueued(uint256 proposalId, uint256 eta);

    /**
     * @notice Emitted when a proposal is executed
     * @param proposalId The proposal ID
     */
    event ProposalExecuted(uint256 proposalId);

    /**
     * @notice Emitted when a proposal is canceled
     * @param proposalId The proposal ID
     */
    event ProposalCanceled(uint256 proposalId);

    /**
     * @notice Emitted when governance parameters are updated
     * @param newVotingDelay The new voting delay
     * @param newVotingPeriod The new voting period
     * @param newProposalThreshold The new proposal threshold
     * @param newQuorumNumerator The new quorum numerator
     */
    event GovernanceParametersUpdated(
        uint256 newVotingDelay,
        uint256 newVotingPeriod,
        uint256 newProposalThreshold,
        uint256 newQuorumNumerator
    );

    // ============ Proposal Management ============
    
    /**
     * @notice Creates a new governance proposal
     * @param targets Array of target contract addresses
     * @param values Array of ETH values to send
     * @param signatures Array of function signatures
     * @param calldatas Array of encoded call data
     * @param description Human-readable proposal description
     * @return proposalId The ID of the created proposal
     */
    function propose(
        address[] memory targets,
        uint256[] memory values,
        string[] memory signatures,
        bytes[] memory calldatas,
        string memory description
    ) external returns (uint256 proposalId);

    /**
     * @notice Queues a successful proposal for execution
     * @param proposalId The proposal ID to queue
     */
    function queue(uint256 proposalId) external;

    /**
     * @notice Executes a queued proposal
     * @param proposalId The proposal ID to execute
     */
    function execute(uint256 proposalId) external;

    /**
     * @notice Cancels a proposal
     * @param proposalId The proposal ID to cancel
     */
    function cancel(uint256 proposalId) external;

    // ============ Voting Functions ============
    
    /**
     * @notice Casts a vote on a proposal
     * @param proposalId The proposal ID to vote on
     * @param support The vote type (0=against, 1=for, 2=abstain)
     */
    function castVote(uint256 proposalId, uint8 support) external;

    /**
     * @notice Casts a vote with a reason
     * @param proposalId The proposal ID to vote on
     * @param support The vote type
     * @param reason The reason for the vote
     */
    function castVoteWithReason(
        uint256 proposalId,
        uint8 support,
        string calldata reason
    ) external;

    /**
     * @notice Casts a vote by signature
     * @param proposalId The proposal ID
     * @param support The vote type
     * @param v The recovery ID
     * @param r The signature parameter
     * @param s The signature parameter
     */
    function castVoteBySig(
        uint256 proposalId,
        uint8 support,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    // ============ View Functions ============
    
    /**
     * @notice Gets the current state of a proposal
     * @param proposalId The proposal ID
     * @return The current state of the proposal
     */
    function state(uint256 proposalId) external view returns (ProposalState);

    /**
     * @notice Gets proposal details
     * @param proposalId The proposal ID
     * @return The proposal struct
     */
    function getProposal(uint256 proposalId) external view returns (Proposal memory);

    /**
     * @notice Gets the voting power of an address at a specific block
     * @param account The address to check
     * @param blockNumber The block number to check at
     * @return The voting power at the specified block
     */
    function getVotes(address account, uint256 blockNumber) external view returns (uint256);

    /**
     * @notice Checks if an account has voted on a proposal
     * @param proposalId The proposal ID
     * @param account The account to check
     * @return True if the account has voted
     */
    function hasVoted(uint256 proposalId, address account) external view returns (bool);

    /**
     * @notice Gets the minimum number of votes required for a proposal
     * @return The proposal threshold
     */
    function proposalThreshold() external view returns (uint256);

    /**
     * @notice Gets the quorum required for a proposal at a block
     * @param blockNumber The block number to check
     * @return The quorum required
     */
    function quorum(uint256 blockNumber) external view returns (uint256);

    /**
     * @notice Gets the voting delay in blocks
     * @return The voting delay
     */
    function votingDelay() external view returns (uint256);

    /**
     * @notice Gets the voting period in blocks
     * @return The voting period
     */
    function votingPeriod() external view returns (uint256);

    // ============ Timelock Functions ============
    
    /**
     * @notice Gets the minimum timelock delay
     * @return The minimum delay in seconds
     */
    function getMinDelay() external view returns (uint256);

    /**
     * @notice Checks if a transaction is ready for execution
     * @param id The transaction ID
     * @return True if ready for execution
     */
    function isOperationReady(bytes32 id) external view returns (bool);

    /**
     * @notice Checks if a transaction is pending
     * @param id The transaction ID
     * @return True if pending
     */
    function isOperationPending(bytes32 id) external view returns (bool);

    // ============ Parameter Management ============
    
    /**
     * @notice Updates governance parameters (self-governance)
     * @param newVotingDelay The new voting delay
     * @param newVotingPeriod The new voting period
     * @param newProposalThreshold The new proposal threshold
     * @param newQuorumNumerator The new quorum numerator
     */
    function updateGovernanceParameters(
        uint256 newVotingDelay,
        uint256 newVotingPeriod,
        uint256 newProposalThreshold,
        uint256 newQuorumNumerator
    ) external;

    // ============ Emergency Functions ============
    
    /**
     * @notice Emergency pause for critical situations
     * @dev Should be heavily restricted and time-limited
     */
    function emergencyPause() external;

    /**
     * @notice Unpause after emergency
     */
    function emergencyUnpause() external;

    /**
     * @notice Checks if the governance is currently paused
     * @return True if paused
     */
    function paused() external view returns (bool);
}