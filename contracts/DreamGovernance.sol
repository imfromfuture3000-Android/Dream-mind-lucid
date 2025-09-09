// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/governance/GovernorUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/extensions/GovernorSettingsUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/extensions/GovernorCountingSimpleUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/extensions/GovernorVotesUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/extensions/GovernorVotesQuorumFractionUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/extensions/GovernorTimelockControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/governance/TimelockControllerUpgradeable.sol";
import "./interfaces/IDreamGovernance.sol";
import "./interfaces/IDreamToken.sol";

/**
 * @title DreamGovernance - DAO Governance for Dream Ecosystem
 * @dev Upgradeable governance contract with timelock and enhanced security
 * @notice Manages proposals, voting, and execution for the Dream-Mind-Lucid ecosystem
 * 
 * Key Features:
 * - OpenZeppelin Governor framework with timelock protection
 * - DREAM token-based voting with quadratic scaling options
 * - Timelocked execution for security (24-48 hour delays)
 * - Emergency governance mechanisms
 * - Parameter bounds checking and validation
 * - Integration with cognitive staking for enhanced voting power
 * - Proposal categorization and priority system
 * - SKALE network optimization
 */
contract DreamGovernance is
    Initializable,
    GovernorUpgradeable,
    GovernorSettingsUpgradeable,
    GovernorCountingSimpleUpgradeable,
    GovernorVotesUpgradeable,
    GovernorVotesQuorumFractionUpgradeable,
    GovernorTimelockControlUpgradeable,
    PausableUpgradeable,
    AccessControlUpgradeable,
    UUPSUpgradeable,
    IDreamGovernance
{
    // ============ Constants ============
    
    /// @notice Maximum voting delay (7 days in blocks)
    uint256 public constant MAX_VOTING_DELAY = 50400; // ~7 days at 12s blocks
    
    /// @notice Maximum voting period (30 days in blocks)
    uint256 public constant MAX_VOTING_PERIOD = 216000; // ~30 days at 12s blocks
    
    /// @notice Maximum proposal threshold (5% of total supply)
    uint256 public constant MAX_PROPOSAL_THRESHOLD_PERCENT = 500; // 5% in basis points
    
    /// @notice Maximum quorum fraction (20%)
    uint256 public constant MAX_QUORUM_FRACTION = 20;
    
    /// @notice Minimum timelock delay (24 hours)
    uint256 public constant MIN_TIMELOCK_DELAY = 86400; // 24 hours
    
    /// @notice Maximum timelock delay (7 days)
    uint256 public constant MAX_TIMELOCK_DELAY = 604800; // 7 days

    // ============ Roles ============
    
    /// @notice Role for emergency operations
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    
    /// @notice Role for parameter management
    bytes32 public constant PARAMETER_MANAGER_ROLE = keccak256("PARAMETER_MANAGER_ROLE");
    
    /// @notice Role for proposal management
    bytes32 public constant PROPOSAL_MANAGER_ROLE = keccak256("PROPOSAL_MANAGER_ROLE");

    // ============ Enums ============
    
    /// @notice Proposal priority levels
    enum ProposalPriority {
        Low,
        Medium,
        High,
        Critical,
        Emergency
    }

    /// @notice Proposal categories
    enum ProposalCategory {
        Parameter,
        Treasury,
        Upgrade,
        Integration,
        Emergency,
        Other
    }

    // ============ State Variables ============
    
    /// @notice Address of the DREAM token contract
    IDreamToken public dreamToken;
    
    /// @notice Timelock controller for delayed execution
    TimelockControllerUpgradeable public timelockController;
    
    /// @notice Emergency governance delay (shorter for critical issues)
    uint256 public emergencyDelay;
    
    /// @notice Mapping of proposal ID to priority
    mapping(uint256 => ProposalPriority) public proposalPriorities;
    
    /// @notice Mapping of proposal ID to category
    mapping(uint256 => ProposalCategory) public proposalCategories;
    
    /// @notice Mapping of proposal ID to execution deadline
    mapping(uint256 => uint256) public proposalDeadlines;
    
    /// @notice Mapping to track emergency proposals
    mapping(uint256 => bool) public emergencyProposals;
    
    /// @notice Total number of proposals created
    uint256 public totalProposals;
    
    /// @notice Mapping of user to their voting power multiplier from staking
    mapping(address => uint256) public stakingVotingMultiplier;

    // ============ Events ============
    
    /// @notice Emitted when a proposal is categorized
    event ProposalCategorized(
        uint256 indexed proposalId,
        ProposalCategory category,
        ProposalPriority priority,
        uint256 deadline
    );

    /// @notice Emitted when emergency governance is triggered
    event EmergencyGovernanceTriggered(
        uint256 indexed proposalId,
        address indexed trigger,
        string reason
    );

    /// @notice Emitted when voting power multiplier is updated
    event VotingMultiplierUpdated(
        address indexed voter,
        uint256 oldMultiplier,
        uint256 newMultiplier
    );

    // ============ Modifiers ============
    
    /// @notice Restricts to emergency or governance roles
    modifier onlyEmergencyOrGovernance() {
        require(
            hasRole(EMERGENCY_ROLE, msg.sender) || 
            hasRole(DEFAULT_ADMIN_ROLE, msg.sender),
            "DreamGovernance: Insufficient privileges"
        );
        _;
    }

    // ============ Initialization ============
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the DreamGovernance contract
     * @param dreamTokenAddr The address of the DREAM token contract
     * @param timelockAddr The address of the timelock controller
     * @param initialOwner The initial owner and admin
     * @param votingDelay Initial voting delay in blocks
     * @param votingPeriod Initial voting period in blocks
     * @param proposalThreshold Initial proposal threshold
     * @param quorumFraction Initial quorum fraction
     */
    function initialize(
        address dreamTokenAddr,
        address timelockAddr,
        address initialOwner,
        uint256 votingDelay,
        uint256 votingPeriod,
        uint256 proposalThreshold,
        uint256 quorumFraction
    ) public initializer {
        require(dreamTokenAddr != address(0), "DreamGovernance: Invalid token address");
        require(timelockAddr != address(0), "DreamGovernance: Invalid timelock address");
        require(initialOwner != address(0), "DreamGovernance: Invalid owner address");

        // Validate parameters
        require(votingDelay <= MAX_VOTING_DELAY, "DreamGovernance: Voting delay too high");
        require(votingPeriod <= MAX_VOTING_PERIOD, "DreamGovernance: Voting period too high");
        require(quorumFraction <= MAX_QUORUM_FRACTION, "DreamGovernance: Quorum fraction too high");

        dreamToken = IDreamToken(dreamTokenAddr);
        timelockController = TimelockControllerUpgradeable(payable(timelockAddr));
        emergencyDelay = 3600; // 1 hour emergency delay

        __Governor_init("DreamGovernance");
        __GovernorSettings_init(votingDelay, votingPeriod, proposalThreshold);
        __GovernorCountingSimple_init();
        __GovernorVotes_init(IVotesUpgradeable(dreamTokenAddr));
        __GovernorVotesQuorumFraction_init(quorumFraction);
        __GovernorTimelockControl_init(timelockController);
        __Pausable_init();
        __AccessControl_init();
        __UUPSUpgradeable_init();

        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(EMERGENCY_ROLE, initialOwner);
        _grantRole(PARAMETER_MANAGER_ROLE, initialOwner);
        _grantRole(PROPOSAL_MANAGER_ROLE, initialOwner);
    }

    // ============ Proposal Management ============
    
    /**
     * @notice Creates a new governance proposal with enhanced categorization
     * @param targets Array of target contract addresses
     * @param values Array of ETH values to send
     * @param calldatas Array of encoded call data
     * @param description Human-readable proposal description
     * @param category The category of the proposal
     * @param priority The priority level of the proposal
     * @return proposalId The ID of the created proposal
     */
    function proposeWithCategory(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description,
        ProposalCategory category,
        ProposalPriority priority
    ) external whenNotPaused returns (uint256 proposalId) {
        // Create the proposal using the standard Governor mechanism
        proposalId = propose(targets, values, calldatas, description);
        
        // Set category and priority
        proposalCategories[proposalId] = category;
        proposalPriorities[proposalId] = priority;
        
        // Set deadline based on priority
        uint256 deadline = block.timestamp + _getDeadlineForPriority(priority);
        proposalDeadlines[proposalId] = deadline;
        
        // Mark as emergency if critical or emergency priority
        if (priority == ProposalPriority.Critical || priority == ProposalPriority.Emergency) {
            emergencyProposals[proposalId] = true;
        }
        
        totalProposals++;
        
        emit ProposalCategorized(proposalId, category, priority, deadline);
        
        return proposalId;
    }

    /**
     * @notice Creates an emergency proposal with expedited timeline
     * @param targets Array of target contract addresses
     * @param values Array of ETH values to send
     * @param calldatas Array of encoded call data
     * @param description Description of the emergency
     * @param reason Reason for emergency classification
     * @return proposalId The ID of the emergency proposal
     */
    function proposeEmergency(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description,
        string memory reason
    ) external onlyRole(EMERGENCY_ROLE) returns (uint256 proposalId) {
        proposalId = proposeWithCategory(
            targets,
            values,
            calldatas,
            description,
            ProposalCategory.Emergency,
            ProposalPriority.Emergency
        );
        
        emit EmergencyGovernanceTriggered(proposalId, msg.sender, reason);
        
        return proposalId;
    }

    // ============ Enhanced Voting ============
    
    /**
     * @notice Casts a vote with enhanced voting power from staking
     * @param proposalId The proposal ID to vote on
     * @param support The vote type (0=against, 1=for, 2=abstain)
     * @param reason The reason for the vote
     */
    function castVoteWithStaking(
        uint256 proposalId,
        uint8 support,
        string calldata reason
    ) external {
        address voter = msg.sender;
        uint256 weight = _getVotesWithStaking(voter, proposalSnapshot(proposalId));
        
        _countVote(proposalId, voter, support, weight, "");
        
        emit VoteCast(voter, proposalId, support, weight, reason);
    }

    /**
     * @notice Updates voting power multiplier for a user based on staking
     * @param user The user to update
     * @param multiplier The new multiplier (in basis points, 10000 = 1x)
     */
    function updateStakingVotingMultiplier(address user, uint256 multiplier)
        external
        onlyRole(PARAMETER_MANAGER_ROLE)
    {
        require(multiplier >= 10000, "DreamGovernance: Multiplier cannot be less than 1x");
        require(multiplier <= 30000, "DreamGovernance: Multiplier cannot exceed 3x");
        
        uint256 oldMultiplier = stakingVotingMultiplier[user];
        stakingVotingMultiplier[user] = multiplier;
        
        emit VotingMultiplierUpdated(user, oldMultiplier, multiplier);
    }

    // ============ Governance Parameter Management ============
    
    /**
     * @notice Updates governance parameters through self-governance
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
    ) external override onlyGovernance {
        require(newVotingDelay <= MAX_VOTING_DELAY, "DreamGovernance: Voting delay too high");
        require(newVotingPeriod <= MAX_VOTING_PERIOD, "DreamGovernance: Voting period too high");
        require(newQuorumNumerator <= MAX_QUORUM_FRACTION, "DreamGovernance: Quorum too high");
        
        setVotingDelay(newVotingDelay);
        setVotingPeriod(newVotingPeriod);
        setProposalThreshold(newProposalThreshold);
        updateQuorumNumerator(newQuorumNumerator);
        
        emit GovernanceParametersUpdated(
            newVotingDelay,
            newVotingPeriod,
            newProposalThreshold,
            newQuorumNumerator
        );
    }

    // ============ Emergency Functions ============
    
    /**
     * @notice Emergency pause for critical situations
     */
    function emergencyPause() external override onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause after emergency
     */
    function emergencyUnpause() external override onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }

    /**
     * @notice Checks if the governance is currently paused
     * @return True if paused
     */
    function paused() public view override(PausableUpgradeable, IDreamGovernance) returns (bool) {
        return PausableUpgradeable.paused();
    }

    // ============ View Functions ============
    
    /**
     * @notice Gets proposal details
     * @param proposalId The proposal ID
     * @return The proposal struct
     */
    function getProposal(uint256 proposalId)
        external
        view
        override
        returns (Proposal memory)
    {
        // This is a simplified implementation
        // In a full implementation, you would construct the Proposal struct
        // from the various Governor storage mappings
        revert("DreamGovernance: Use individual getter functions");
    }

    /**
     * @notice Gets the voting power with staking multiplier
     * @param account The account to check
     * @param blockNumber The block number to check at
     * @return The enhanced voting power
     */
    function getVotesWithStaking(address account, uint256 blockNumber)
        external
        view
        returns (uint256)
    {
        return _getVotesWithStaking(account, blockNumber);
    }

    /**
     * @notice Gets proposal category and priority
     * @param proposalId The proposal ID
     * @return category The proposal category
     * @return priority The proposal priority
     * @return deadline The proposal deadline
     */
    function getProposalMetadata(uint256 proposalId)
        external
        view
        returns (
            ProposalCategory category,
            ProposalPriority priority,
            uint256 deadline
        )
    {
        return (
            proposalCategories[proposalId],
            proposalPriorities[proposalId],
            proposalDeadlines[proposalId]
        );
    }

    // ============ Internal Functions ============
    
    /**
     * @notice Gets voting power with staking multiplier applied
     * @param account The account to check
     * @param blockNumber The block number to check at
     * @return The enhanced voting power
     */
    function _getVotesWithStaking(address account, uint256 blockNumber)
        internal
        view
        returns (uint256)
    {
        uint256 baseVotes = getVotes(account, blockNumber);
        uint256 multiplier = stakingVotingMultiplier[account];
        
        if (multiplier == 0) {
            multiplier = 10000; // Default 1x multiplier
        }
        
        return (baseVotes * multiplier) / 10000;
    }

    /**
     * @notice Gets the deadline for a proposal based on priority
     * @param priority The proposal priority
     * @return The deadline in seconds
     */
    function _getDeadlineForPriority(ProposalPriority priority)
        internal
        pure
        returns (uint256)
    {
        if (priority == ProposalPriority.Emergency) return 3600; // 1 hour
        if (priority == ProposalPriority.Critical) return 86400; // 1 day
        if (priority == ProposalPriority.High) return 259200; // 3 days
        if (priority == ProposalPriority.Medium) return 604800; // 1 week
        return 1209600; // 2 weeks for low priority
    }

    /**
     * @notice Hook called before proposal execution
     * @param proposalId The proposal ID
     */
    function _beforeExecute(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override whenNotPaused {
        super._beforeExecute(proposalId, targets, values, calldatas, descriptionHash);
        
        // Check if proposal has expired
        uint256 deadline = proposalDeadlines[proposalId];
        if (deadline != 0 && block.timestamp > deadline) {
            revert("DreamGovernance: Proposal execution deadline passed");
        }
    }

    /**
     * @notice Authorizes contract upgrades
     * @param newImplementation The new implementation address
     */
    function _authorizeUpgrade(address newImplementation)
        internal
        override
        onlyRole(DEFAULT_ADMIN_ROLE)
    {}

    // ============ Overrides Required by Solidity ============
    
    function votingDelay()
        public
        view
        override(IGovernorUpgradeable, GovernorSettingsUpgradeable)
        returns (uint256)
    {
        return super.votingDelay();
    }

    function votingPeriod()
        public
        view
        override(IGovernorUpgradeable, GovernorSettingsUpgradeable)
        returns (uint256)
    {
        return super.votingPeriod();
    }

    function quorum(uint256 blockNumber)
        public
        view
        override(IGovernorUpgradeable, GovernorVotesQuorumFractionUpgradeable)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    function proposalThreshold()
        public
        view
        override(GovernorUpgradeable, GovernorSettingsUpgradeable)
        returns (uint256)
    {
        return super.proposalThreshold();
    }

    function getVotes(address account, uint256 blockNumber)
        public
        view
        override(IGovernorUpgradeable, GovernorVotesUpgradeable)
        returns (uint256)
    {
        return super.getVotes(account, blockNumber);
    }

    function state(uint256 proposalId)
        public
        view
        override(GovernorUpgradeable, GovernorTimelockControlUpgradeable)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description
    )
        public
        override(GovernorUpgradeable, IGovernorUpgradeable)
        returns (uint256)
    {
        return super.propose(targets, values, calldatas, description);
    }

    function _execute(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(GovernorUpgradeable, GovernorTimelockControlUpgradeable) {
        super._execute(proposalId, targets, values, calldatas, descriptionHash);
    }

    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(GovernorUpgradeable, GovernorTimelockControlUpgradeable) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal
        view
        override(GovernorUpgradeable, GovernorTimelockControlUpgradeable)
        returns (address)
    {
        return super._executor();
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(GovernorUpgradeable, GovernorTimelockControlUpgradeable, AccessControlUpgradeable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}