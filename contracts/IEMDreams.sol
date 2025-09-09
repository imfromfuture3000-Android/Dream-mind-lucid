// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "./interfaces/IDreamToken.sol";
import "./interfaces/IDreamGovernance.sol";
import "./interfaces/IDreamStaking.sol";

/**
 * @title IEMDreams - Enhanced DREAM Token Contract
 * @dev Upgradeable ERC20 token with dream recording, governance, and staking features
 * @notice The core DREAM token (777,777,777 supply) with advanced dream ecosystem functionality
 * 
 * Key Features:
 * - Full ERC20 compliance with OpenZeppelin security patterns
 * - Dream recording with tokenomics (burn + reward mechanism)
 * - Governance integration with timelock and voting power
 * - Cognitive staking for enhanced rewards
 * - Upgradeable architecture for future evolution
 * - SKALE network optimization (zero-gas transactions)
 * - Comprehensive access controls and emergency mechanisms
 */
contract IEMDreams is
    Initializable,
    ERC20Upgradeable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable,
    UUPSUpgradeable,
    IDreamToken
{
    // ============ Constants ============
    
    /// @notice Total supply cap of DREAM tokens (777,777,777)
    uint256 public constant TOTAL_SUPPLY_CAP = 777_777_777 * 10**18;
    
    /// @notice Maximum burn rate per dream (prevents excessive burning)
    uint256 public constant MAX_BURN_RATE = 100 * 10**18; // 100 DREAM
    
    /// @notice Maximum mining reward per dream (prevents inflation attacks)
    uint256 public constant MAX_MINING_REWARD = 1000 * 10**18; // 1000 DREAM
    
    /// @notice Minimum staking duration (1 day in blocks, ~6400 blocks)
    uint256 public constant MIN_STAKING_DURATION = 6400;
    
    /// @notice Maximum staking duration (1 year in blocks, ~2.3M blocks)
    uint256 public constant MAX_STAKING_DURATION = 2_336_000;

    // ============ Roles ============
    
    /// @notice Role for addresses authorized to record dreams
    bytes32 public constant DREAM_RECORDER_ROLE = keccak256("DREAM_RECORDER_ROLE");
    
    /// @notice Role for governance operations
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    /// @notice Role for emergency operations
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    
    /// @notice Role for parameter updates
    bytes32 public constant PARAMETER_MANAGER_ROLE = keccak256("PARAMETER_MANAGER_ROLE");

    // ============ State Variables ============
    
    /// @notice Current dream mining reward rate
    uint256 public currentMiningRate;
    
    /// @notice Current dream recording burn rate
    uint256 public currentBurnRate;
    
    /// @notice Minimum stake amount for cognitive staking
    uint256 public minStakeAmount;
    
    /// @notice Maximum stake amount for cognitive staking
    uint256 public maxStakeAmount;
    
    /// @notice Current staking reward rate (per block)
    uint256 public stakingRewardRate;
    
    /// @notice Next stake ID for unique identification
    uint256 public nextStakeId;
    
    /// @notice Address of the governance contract
    IDreamGovernance public governanceContract;
    
    /// @notice Address of the staking contract
    IDreamStaking public stakingContract;

    // ============ Mappings ============
    
    /// @notice Mapping of authorized dream recorder contracts
    mapping(address => bool) public authorizedRecorders;
    
    /// @notice Mapping of dream hash to recording timestamp
    mapping(bytes32 => uint256) public dreamRecordings;
    
    /// @notice Mapping of user to their total dreams recorded
    mapping(address => uint256) public userDreamCount;
    
    /// @notice Mapping of user to their total mining rewards earned
    mapping(address => uint256) public userMiningRewards;
    
    /// @notice Mapping for stake information
    mapping(uint256 => CognitiveStake) public stakes;
    
    /// @notice Mapping of user to their stake IDs
    mapping(address => uint256[]) public userStakes;
    
    /// @notice Mapping of user to their total staked amount
    mapping(address => uint256) public userTotalStaked;

    // ============ Structs ============
    
    /// @notice Structure for cognitive staking information
    struct CognitiveStake {
        address staker;
        uint256 amount;
        uint256 duration;
        uint256 startBlock;
        uint256 endBlock;
        uint256 rewardRate;
        uint256 lastRewardBlock;
        uint256 accumulatedRewards;
        uint256 multiplier;
        bool isActive;
    }

    // ============ Events ============
    
    /// @notice Emitted when a dream is recorded with rewards
    event DreamRecorded(
        address indexed dreamer,
        bytes32 indexed dreamHash,
        string dreamContent,
        uint256 rewardAmount,
        uint256 burnAmount
    );

    /// @notice Emitted when governance parameters are updated
    event ParametersUpdated(
        uint256 newMiningRate,
        uint256 newBurnRate,
        uint256 newMinStake,
        uint256 newMaxStake,
        uint256 newStakingRate
    );

    /// @notice Emitted when a dream recorder is authorized/deauthorized
    event RecorderStatusChanged(address indexed recorder, bool authorized);

    // ============ Modifiers ============
    
    /// @notice Restricts access to authorized dream recorders
    modifier onlyAuthorizedRecorder() {
        require(authorizedRecorders[msg.sender], "IEMDreams: Not authorized recorder");
        _;
    }

    /// @notice Restricts access to governance or emergency roles
    modifier onlyGovernanceOrEmergency() {
        require(
            hasRole(GOVERNANCE_ROLE, msg.sender) || hasRole(EMERGENCY_ROLE, msg.sender),
            "IEMDreams: Insufficient privileges"
        );
        _;
    }

    // ============ Initialization ============
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the IEMDreams contract
     * @param initialOwner The initial owner and admin
     * @param governanceAddr The address of the governance contract
     * @param stakingAddr The address of the staking contract
     */
    function initialize(
        address initialOwner,
        address governanceAddr,
        address stakingAddr
    ) public initializer {
        __ERC20_init("IEM Dreams", "DREAM");
        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();
        __UUPSUpgradeable_init();

        // Grant roles to initial owner
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(GOVERNANCE_ROLE, initialOwner);
        _grantRole(EMERGENCY_ROLE, initialOwner);
        _grantRole(PARAMETER_MANAGER_ROLE, initialOwner);

        // Set initial parameters
        currentMiningRate = 50 * 10**18; // 50 DREAM per dream
        currentBurnRate = 10 * 10**18;   // 10 DREAM burn per dream
        minStakeAmount = 1000 * 10**18;  // 1000 DREAM minimum stake
        maxStakeAmount = 100000 * 10**18; // 100k DREAM maximum stake
        stakingRewardRate = 1 * 10**15;  // 0.001 DREAM per block per staked token
        nextStakeId = 1;

        // Set contract addresses
        if (governanceAddr != address(0)) {
            governanceContract = IDreamGovernance(governanceAddr);
        }
        if (stakingAddr != address(0)) {
            stakingContract = IDreamStaking(stakingAddr);
        }

        // Mint initial supply to contract (for distribution)
        _mint(address(this), TOTAL_SUPPLY_CAP);
        
        // Transfer initial allocation to owner for ecosystem bootstrap
        uint256 initialAllocation = TOTAL_SUPPLY_CAP / 10; // 10% to owner
        _transfer(address(this), initialOwner, initialAllocation);
    }

    // ============ Dream Recording Functions ============
    
    /**
     * @notice Records a dream and handles token economics
     * @dev Called by authorized dream recording contracts
     * @param dreamer The address recording the dream
     * @param dreamHash The hash of the dream content
     * @return rewardAmount The amount of DREAM tokens rewarded
     */
    function recordDreamReward(address dreamer, bytes32 dreamHash)
        external
        override
        onlyAuthorizedRecorder
        whenNotPaused
        nonReentrant
        returns (uint256 rewardAmount)
    {
        require(dreamer != address(0), "IEMDreams: Invalid dreamer address");
        require(dreamHash != bytes32(0), "IEMDreams: Invalid dream hash");
        require(dreamRecordings[dreamHash] == 0, "IEMDreams: Dream already recorded");

        // Check if dreamer has enough tokens for burn
        require(balanceOf(dreamer) >= currentBurnRate, "IEMDreams: Insufficient balance for burn");

        // Record the dream
        dreamRecordings[dreamHash] = block.timestamp;
        userDreamCount[dreamer]++;

        // Handle token economics
        if (currentBurnRate > 0) {
            _burn(dreamer, currentBurnRate);
        }

        // Calculate reward (with staking bonus if applicable)
        rewardAmount = currentMiningRate;
        if (address(stakingContract) != address(0)) {
            uint256 stakingBonus = stakingContract.getDreamBonusMultiplier(dreamer);
            rewardAmount = (rewardAmount * stakingBonus) / 10000; // stakingBonus in basis points
        }

        // Distribute reward from contract reserves
        if (balanceOf(address(this)) >= rewardAmount) {
            _transfer(address(this), dreamer, rewardAmount);
            userMiningRewards[dreamer] += rewardAmount;
        } else {
            rewardAmount = 0; // No reward if contract doesn't have enough reserves
        }

        // Notify staking contract if connected
        if (address(stakingContract) != address(0)) {
            stakingContract.onDreamRecorded(dreamer, dreamHash);
        }

        emit DreamRewardDistributed(dreamer, dreamHash, rewardAmount, currentBurnRate);
        return rewardAmount;
    }

    // ============ Cognitive Staking Functions ============
    
    /**
     * @notice Stakes DREAM tokens for cognitive mining rewards
     * @param amount The amount of DREAM tokens to stake
     * @param duration The staking duration in blocks
     */
    function stakeDream(uint256 amount, uint256 duration) external override whenNotPaused nonReentrant {
        require(amount >= minStakeAmount, "IEMDreams: Amount below minimum stake");
        require(amount <= maxStakeAmount, "IEMDreams: Amount exceeds maximum stake");
        require(duration >= MIN_STAKING_DURATION, "IEMDreams: Duration too short");
        require(duration <= MAX_STAKING_DURATION, "IEMDreams: Duration too long");
        require(balanceOf(msg.sender) >= amount, "IEMDreams: Insufficient balance");

        // Calculate multiplier based on duration
        uint256 multiplier = _calculateStakingMultiplier(duration);

        // Create stake
        uint256 stakeId = nextStakeId++;
        stakes[stakeId] = CognitiveStake({
            staker: msg.sender,
            amount: amount,
            duration: duration,
            startBlock: block.number,
            endBlock: block.number + duration,
            rewardRate: stakingRewardRate,
            lastRewardBlock: block.number,
            accumulatedRewards: 0,
            multiplier: multiplier,
            isActive: true
        });

        userStakes[msg.sender].push(stakeId);
        userTotalStaked[msg.sender] += amount;

        // Transfer tokens to contract
        _transfer(msg.sender, address(this), amount);

        emit Transfer(msg.sender, address(this), amount); // Additional event for tracking
    }

    /**
     * @notice Unstakes DREAM tokens and claims rewards
     * @param stakeId The ID of the stake to unstake
     */
    function unstakeDream(uint256 stakeId) external override nonReentrant {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.staker == msg.sender, "IEMDreams: Not stake owner");
        require(stake.isActive, "IEMDreams: Stake not active");
        require(block.number >= stake.endBlock, "IEMDreams: Staking period not ended");

        // Calculate final rewards
        uint256 rewards = _calculateStakeRewards(stakeId);
        stake.accumulatedRewards += rewards;

        // Mark stake as inactive
        stake.isActive = false;
        userTotalStaked[msg.sender] -= stake.amount;

        // Transfer staked amount back
        _transfer(address(this), msg.sender, stake.amount);

        // Transfer rewards if available
        if (stake.accumulatedRewards > 0 && balanceOf(address(this)) >= stake.accumulatedRewards) {
            _transfer(address(this), msg.sender, stake.accumulatedRewards);
        }

        emit Transfer(address(this), msg.sender, stake.amount + stake.accumulatedRewards);
    }

    /**
     * @notice Claims staking rewards without unstaking
     * @param stakeId The ID of the stake to claim rewards for
     */
    function claimStakingRewards(uint256 stakeId) external override nonReentrant {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.staker == msg.sender, "IEMDreams: Not stake owner");
        require(stake.isActive, "IEMDreams: Stake not active");

        uint256 rewards = _calculateStakeRewards(stakeId);
        if (rewards > 0) {
            stake.accumulatedRewards += rewards;
            stake.lastRewardBlock = block.number;

            if (balanceOf(address(this)) >= rewards) {
                _transfer(address(this), msg.sender, rewards);
                emit Transfer(address(this), msg.sender, rewards);
            }
        }
    }

    // ============ View Functions ============
    
    /**
     * @notice Gets the current dream mining reward rate
     * @return The current reward rate in DREAM tokens per dream
     */
    function getCurrentMiningRate() external view override returns (uint256) {
        return currentMiningRate;
    }

    /**
     * @notice Gets the current dream recording burn rate
     * @return The current burn rate in DREAM tokens per dream recorded
     */
    function getCurrentBurnRate() external view override returns (uint256) {
        return currentBurnRate;
    }

    /**
     * @notice Gets staking information for a user
     * @param user The address to get staking info for
     * @return totalStaked The total amount staked by the user
     * @return activeStakes The number of active stakes
     * @return pendingRewards The total pending staking rewards
     */
    function getStakingInfo(address user)
        external
        view
        override
        returns (
            uint256 totalStaked,
            uint256 activeStakes,
            uint256 pendingRewards
        )
    {
        totalStaked = userTotalStaked[user];
        
        uint256[] memory userStakeIds = userStakes[user];
        for (uint256 i = 0; i < userStakeIds.length; i++) {
            CognitiveStake memory stake = stakes[userStakeIds[i]];
            if (stake.isActive) {
                activeStakes++;
                pendingRewards += _calculateStakeRewards(userStakeIds[i]);
            }
        }
    }

    /**
     * @notice Gets the total supply cap of DREAM tokens
     * @return The maximum total supply (777,777,777 tokens)
     */
    function totalSupplyCap() external pure override returns (uint256) {
        return TOTAL_SUPPLY_CAP;
    }

    /**
     * @notice Checks if an address is authorized for dream recording
     * @param recorder The address to check
     * @return True if authorized for dream recording
     */
    function isAuthorizedRecorder(address recorder) external view override returns (bool) {
        return authorizedRecorders[recorder];
    }

    // ============ Governance Functions ============
    
    /**
     * @notice Updates mining parameters (governance only)
     * @param newMiningRate The new mining reward rate
     * @param newBurnRate The new burn rate for dream recording
     */
    function updateMiningParameters(uint256 newMiningRate, uint256 newBurnRate)
        external
        override
        onlyRole(PARAMETER_MANAGER_ROLE)
    {
        require(newMiningRate <= MAX_MINING_REWARD, "IEMDreams: Mining rate too high");
        require(newBurnRate <= MAX_BURN_RATE, "IEMDreams: Burn rate too high");

        currentMiningRate = newMiningRate;
        currentBurnRate = newBurnRate;

        emit MiningParametersUpdated(newMiningRate, newBurnRate, block.number);
    }

    /**
     * @notice Updates staking parameters (governance only)
     * @param newMinStake The new minimum stake amount
     * @param newMaxStake The new maximum stake amount
     * @param newRewardRate The new staking reward rate
     */
    function updateStakingParameters(
        uint256 newMinStake,
        uint256 newMaxStake,
        uint256 newRewardRate
    ) external override onlyRole(PARAMETER_MANAGER_ROLE) {
        require(newMinStake <= newMaxStake, "IEMDreams: Invalid stake range");
        require(newMinStake > 0, "IEMDreams: Min stake cannot be zero");

        minStakeAmount = newMinStake;
        maxStakeAmount = newMaxStake;
        stakingRewardRate = newRewardRate;

        emit StakingParametersUpdated(newMinStake, newMaxStake, newRewardRate);
    }

    /**
     * @notice Authorizes or deauthorizes a dream recorder
     * @param recorder The address to authorize/deauthorize
     * @param authorized Whether to authorize or deauthorize
     */
    function setRecorderAuthorization(address recorder, bool authorized)
        external
        onlyRole(GOVERNANCE_ROLE)
    {
        require(recorder != address(0), "IEMDreams: Invalid recorder address");
        authorizedRecorders[recorder] = authorized;
        emit RecorderStatusChanged(recorder, authorized);
    }

    // ============ Extension Hook ============
    
    /**
     * @notice Hook for future adaptive logic extensions
     * @dev Reserved for future upgrades and extensions
     * @param functionId The ID of the function being called
     * @param data Encoded function parameters
     * @return result The result of the extension function
     */
    function extensionHook(bytes4 functionId, bytes calldata data)
        external
        override
        onlyRole(GOVERNANCE_ROLE)
        returns (bytes memory result)
    {
        // Reserved for future extensions
        // This function will be implemented in future upgrades
        revert("IEMDreams: Extension not implemented");
    }

    // ============ Emergency Functions ============
    
    /**
     * @notice Pauses the contract (emergency only)
     */
    function pause() external onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    /**
     * @notice Unpauses the contract (emergency only)
     */
    function unpause() external onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }

    /**
     * @notice Emergency token recovery (governance only)
     * @param token The token to recover
     * @param amount The amount to recover
     * @param to The address to send recovered tokens to
     */
    function emergencyTokenRecovery(
        address token,
        uint256 amount,
        address to
    ) external onlyRole(EMERGENCY_ROLE) {
        require(to != address(0), "IEMDreams: Invalid recovery address");
        if (token == address(0)) {
            // Recover ETH
            payable(to).transfer(amount);
        } else {
            // Recover ERC20 tokens
            IERC20Upgradeable(token).transfer(to, amount);
        }
    }

    // ============ Internal Functions ============
    
    /**
     * @notice Calculates staking multiplier based on duration
     * @param duration The staking duration in blocks
     * @return The multiplier in basis points (10000 = 1x)
     */
    function _calculateStakingMultiplier(uint256 duration) internal pure returns (uint256) {
        if (duration < MIN_STAKING_DURATION) return 10000; // 1x
        if (duration < 64000) return 12000; // 1.2x for < 10 days
        if (duration < 384000) return 15000; // 1.5x for < 60 days
        if (duration < 1152000) return 20000; // 2x for < 180 days
        return 25000; // 2.5x for >= 180 days
    }

    /**
     * @notice Calculates pending rewards for a stake
     * @param stakeId The ID of the stake
     * @return The pending rewards amount
     */
    function _calculateStakeRewards(uint256 stakeId) internal view returns (uint256) {
        CognitiveStake memory stake = stakes[stakeId];
        if (!stake.isActive) return 0;

        uint256 blocksSinceLastReward = block.number - stake.lastRewardBlock;
        uint256 baseReward = (stake.amount * stake.rewardRate * blocksSinceLastReward) / 10**18;
        return (baseReward * stake.multiplier) / 10000;
    }

    /**
     * @notice Authorizes contract upgrades
     * @param newImplementation The new implementation address
     */
    function _authorizeUpgrade(address newImplementation)
        internal
        override
        onlyRole(GOVERNANCE_ROLE)
    {}

    /**
     * @notice Hook called before token transfers
     * @param from The sender address
     * @param to The recipient address
     * @param amount The amount being transferred
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }

    // ============ Receive ETH ============
    
    receive() external payable {
        // Allow contract to receive ETH for gas optimization on SKALE
    }
}
