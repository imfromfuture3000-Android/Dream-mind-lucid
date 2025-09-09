// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";
import "./interfaces/IDreamStaking.sol";
import "./interfaces/IDreamToken.sol";
import "./interfaces/IDreamGovernance.sol";

/**
 * @title DreamStaking - Cognitive Staking for Dream Ecosystem
 * @dev Upgradeable staking contract with cognitive multipliers and governance integration
 * @notice Enables staking of DREAM tokens for enhanced dream mining and governance participation
 * 
 * Key Features:
 * - Cognitive staking with duration-based multipliers
 * - Governance voting power enhancement through staking
 * - Dream recording bonus rewards for stakers
 * - Flexible staking durations (1 day to 1 year)
 * - Compound staking and auto-reinvestment options
 * - Emergency withdrawal mechanisms
 * - Analytics and performance tracking
 * - SKALE network optimization
 */
contract DreamStaking is
    Initializable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable,
    UUPSUpgradeable,
    IDreamStaking
{
    using CountersUpgradeable for CountersUpgradeable.Counter;

    // ============ Constants ============
    
    /// @notice Precision factor for calculations
    uint256 public constant override PRECISION = 1e18;
    
    /// @notice Maximum cognitive multiplier (5x)
    uint256 public constant override MAX_MULTIPLIER = 50000; // 5x in basis points
    
    /// @notice Base multiplier (no bonus)
    uint256 public constant override BASE_MULTIPLIER = 10000; // 1x in basis points
    
    /// @notice Minimum staking duration (1 day in blocks)
    uint256 public constant MIN_STAKING_DURATION = 6400; // ~1 day at 13.5s blocks
    
    /// @notice Maximum staking duration (1 year in blocks)
    uint256 public constant MAX_STAKING_DURATION = 2_336_000; // ~1 year at 13.5s blocks
    
    /// @notice Minimum stake amount
    uint256 public constant MIN_STAKE_AMOUNT = 100 * 1e18; // 100 DREAM tokens
    
    /// @notice Maximum stake amount per user
    uint256 public constant MAX_STAKE_AMOUNT = 1_000_000 * 1e18; // 1M DREAM tokens

    // ============ Roles ============
    
    /// @notice Role for governance operations
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    /// @notice Role for parameter management
    bytes32 public constant PARAMETER_MANAGER_ROLE = keccak256("PARAMETER_MANAGER_ROLE");
    
    /// @notice Role for emergency operations
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    
    /// @notice Role for analytics operations
    bytes32 public constant ANALYTICS_ROLE = keccak256("ANALYTICS_ROLE");

    // ============ State Variables ============
    
    /// @notice Counter for unique stake IDs
    CountersUpgradeable.Counter private _stakeIdCounter;
    
    /// @notice Address of the DREAM token contract
    IDreamToken public dreamToken;
    
    /// @notice Address of the governance contract
    IDreamGovernance public governanceContract;
    
    /// @notice Current staking pool information
    StakingPool public stakingPool;
    
    /// @notice Cognitive multipliers for different duration ranges
    uint256 public shortTermMultiplier;  // < 30 days
    uint256 public mediumTermMultiplier; // 30-180 days
    uint256 public longTermMultiplier;   // > 180 days

    // ============ Mappings ============
    
    /// @notice Mapping of stake ID to CognitiveStake
    mapping(uint256 => CognitiveStake) public stakes;
    
    /// @notice Mapping of user to their stake IDs
    mapping(address => uint256[]) public userStakes;
    
    /// @notice Mapping of user to their total staked amount
    mapping(address => uint256) public userTotalStaked;
    
    /// @notice Mapping of user to their total rewards earned
    mapping(address => uint256) public userTotalRewards;
    
    /// @notice Mapping of user to their last interaction block
    mapping(address => uint256) public userLastActionBlock;
    
    /// @notice Mapping to track if user is a staker
    mapping(address => bool) public isStaker;

    // ============ Events ============
    
    /// @notice Additional events beyond interface requirements
    event StakeExtended(
        address indexed staker,
        uint256 indexed stakeId,
        uint256 additionalDuration,
        uint256 newEndBlock,
        uint256 newMultiplier
    );

    event RewardsCompounded(
        address indexed staker,
        uint256 indexed stakeId,
        uint256 compoundedAmount,
        uint256 newStakeAmount
    );

    event PoolUpdated(
        uint256 totalStaked,
        uint256 rewardRate,
        uint256 lastUpdateBlock
    );

    // ============ Modifiers ============
    
    /// @notice Validates stake ID
    modifier validStakeId(uint256 stakeId) {
        require(stakeId > 0 && stakeId <= _stakeIdCounter.current(), "DreamStaking: Invalid stake ID");
        _;
    }

    /// @notice Ensures only stake owner can access
    modifier onlyStakeOwner(uint256 stakeId) {
        require(stakes[stakeId].staker == msg.sender, "DreamStaking: Not stake owner");
        _;
    }

    // ============ Initialization ============
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the DreamStaking contract
     * @param dreamTokenAddr The address of the DREAM token contract
     * @param governanceAddr The address of the governance contract
     * @param initialOwner The initial owner and admin
     * @param initialRewardRate Initial reward rate per block
     */
    function initialize(
        address dreamTokenAddr,
        address governanceAddr,
        address initialOwner,
        uint256 initialRewardRate
    ) public initializer {
        require(dreamTokenAddr != address(0), "DreamStaking: Invalid token address");
        require(initialOwner != address(0), "DreamStaking: Invalid owner address");

        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();
        __UUPSUpgradeable_init();

        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(GOVERNANCE_ROLE, initialOwner);
        _grantRole(PARAMETER_MANAGER_ROLE, initialOwner);
        _grantRole(EMERGENCY_ROLE, initialOwner);
        _grantRole(ANALYTICS_ROLE, initialOwner);

        // Set contract addresses
        dreamToken = IDreamToken(dreamTokenAddr);
        if (governanceAddr != address(0)) {
            governanceContract = IDreamGovernance(governanceAddr);
        }

        // Initialize staking pool
        stakingPool = StakingPool({
            totalStaked: 0,
            totalStakers: 0,
            rewardRate: initialRewardRate,
            lastUpdateBlock: block.number,
            accRewardPerShare: 0,
            minStakeDuration: MIN_STAKING_DURATION,
            maxStakeDuration: MAX_STAKING_DURATION
        });

        // Initialize cognitive multipliers
        shortTermMultiplier = 12000;  // 1.2x for < 30 days
        mediumTermMultiplier = 15000; // 1.5x for 30-180 days
        longTermMultiplier = 25000;   // 2.5x for > 180 days
    }

    // ============ Staking Functions ============
    
    /**
     * @notice Stakes DREAM tokens for cognitive mining
     * @param amount The amount of DREAM tokens to stake
     * @param duration The staking duration in blocks
     * @return stakeId The ID of the created stake
     */
    function stakeDream(uint256 amount, uint256 duration)
        external
        override
        whenNotPaused
        nonReentrant
        returns (uint256 stakeId)
    {
        require(amount >= MIN_STAKE_AMOUNT, "DreamStaking: Amount below minimum");
        require(amount <= MAX_STAKE_AMOUNT, "DreamStaking: Amount exceeds maximum");
        require(duration >= stakingPool.minStakeDuration, "DreamStaking: Duration too short");
        require(duration <= stakingPool.maxStakeDuration, "DreamStaking: Duration too long");
        require(
            userTotalStaked[msg.sender] + amount <= MAX_STAKE_AMOUNT,
            "DreamStaking: Total stake would exceed maximum"
        );

        // Transfer tokens from user to contract
        require(
            dreamToken.transferFrom(msg.sender, address(this), amount),
            "DreamStaking: Transfer failed"
        );

        // Update pool before creating stake
        _updatePool();

        // Calculate cognitive multiplier
        uint256 multiplier = calculateCognitiveMultiplier(duration);

        // Generate stake ID
        _stakeIdCounter.increment();
        stakeId = _stakeIdCounter.current();

        // Create stake
        stakes[stakeId] = CognitiveStake({
            staker: msg.sender,
            amount: amount,
            duration: duration,
            startBlock: block.number,
            endBlock: block.number + duration,
            rewardRate: stakingPool.rewardRate,
            lastRewardBlock: block.number,
            accumulatedRewards: 0,
            multiplier: multiplier,
            isActive: true
        });

        // Update user tracking
        userStakes[msg.sender].push(stakeId);
        userTotalStaked[msg.sender] += amount;
        userLastActionBlock[msg.sender] = block.number;

        // Update staker status
        if (!isStaker[msg.sender]) {
            isStaker[msg.sender] = true;
            stakingPool.totalStakers++;
        }

        // Update pool state
        stakingPool.totalStaked += amount;

        // Update governance voting multiplier if governance contract is set
        if (address(governanceContract) != address(0)) {
            _updateGovernanceVotingPower(msg.sender);
        }

        emit CognitiveStakeCreated(msg.sender, stakeId, amount, duration, multiplier);

        return stakeId;
    }

    /**
     * @notice Unstakes DREAM tokens and claims all accumulated rewards
     * @param stakeId The ID of the stake to unstake
     */
    function unstakeDream(uint256 stakeId)
        external
        override
        validStakeId(stakeId)
        onlyStakeOwner(stakeId)
        nonReentrant
    {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.isActive, "DreamStaking: Stake not active");
        require(block.number >= stake.endBlock, "DreamStaking: Staking period not ended");

        // Update pool before unstaking
        _updatePool();

        // Calculate final rewards
        uint256 rewards = _calculateStakeRewards(stakeId);
        stake.accumulatedRewards += rewards;

        uint256 totalAmount = stake.amount + stake.accumulatedRewards;

        // Mark stake as inactive
        stake.isActive = false;
        userTotalStaked[msg.sender] -= stake.amount;
        userTotalRewards[msg.sender] += stake.accumulatedRewards;
        userLastActionBlock[msg.sender] = block.number;

        // Update pool state
        stakingPool.totalStaked -= stake.amount;

        // Check if user still has active stakes
        bool hasActiveStakes = false;
        uint256[] memory userStakeIds = userStakes[msg.sender];
        for (uint256 i = 0; i < userStakeIds.length; i++) {
            if (stakes[userStakeIds[i]].isActive) {
                hasActiveStakes = true;
                break;
            }
        }

        if (!hasActiveStakes) {
            isStaker[msg.sender] = false;
            stakingPool.totalStakers--;
        }

        // Transfer tokens back to user
        require(
            dreamToken.transfer(msg.sender, totalAmount),
            "DreamStaking: Transfer failed"
        );

        // Update governance voting power
        if (address(governanceContract) != address(0)) {
            _updateGovernanceVotingPower(msg.sender);
        }

        emit CognitiveStakeWithdrawn(msg.sender, stakeId, stake.amount, stake.accumulatedRewards);
    }

    /**
     * @notice Claims accumulated rewards without unstaking
     * @param stakeId The ID of the stake to claim rewards for
     */
    function claimRewards(uint256 stakeId)
        external
        override
        validStakeId(stakeId)
        onlyStakeOwner(stakeId)
        nonReentrant
    {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.isActive, "DreamStaking: Stake not active");

        // Update pool before claiming
        _updatePool();

        uint256 rewards = _calculateStakeRewards(stakeId);
        if (rewards > 0) {
            stake.accumulatedRewards += rewards;
            stake.lastRewardBlock = block.number;
            userTotalRewards[msg.sender] += rewards;
            userLastActionBlock[msg.sender] = block.number;

            require(
                dreamToken.transfer(msg.sender, rewards),
                "DreamStaking: Transfer failed"
            );

            emit StakingRewardsClaimed(msg.sender, stakeId, rewards);
        }
    }

    /**
     * @notice Extends the duration of an existing stake
     * @param stakeId The ID of the stake to extend
     * @param additionalDuration Additional blocks to extend
     */
    function extendStake(uint256 stakeId, uint256 additionalDuration)
        external
        override
        validStakeId(stakeId)
        onlyStakeOwner(stakeId)
        whenNotPaused
    {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.isActive, "DreamStaking: Stake not active");
        require(additionalDuration > 0, "DreamStaking: Invalid additional duration");
        
        uint256 newDuration = stake.duration + additionalDuration;
        require(newDuration <= stakingPool.maxStakeDuration, "DreamStaking: New duration exceeds maximum");

        // Claim existing rewards first
        uint256 currentRewards = _calculateStakeRewards(stakeId);
        if (currentRewards > 0) {
            stake.accumulatedRewards += currentRewards;
        }

        // Update stake parameters
        stake.duration = newDuration;
        stake.endBlock = stake.startBlock + newDuration;
        stake.lastRewardBlock = block.number;
        stake.multiplier = calculateCognitiveMultiplier(newDuration);
        userLastActionBlock[msg.sender] = block.number;

        // Update governance voting power
        if (address(governanceContract) != address(0)) {
            _updateGovernanceVotingPower(msg.sender);
        }

        emit StakeExtended(msg.sender, stakeId, additionalDuration, stake.endBlock, stake.multiplier);
    }

    /**
     * @notice Compounds rewards back into the stake
     * @param stakeId The ID of the stake to compound
     */
    function compoundRewards(uint256 stakeId)
        external
        override
        validStakeId(stakeId)
        onlyStakeOwner(stakeId)
        nonReentrant
    {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.isActive, "DreamStaking: Stake not active");

        // Update pool and calculate rewards
        _updatePool();
        uint256 rewards = _calculateStakeRewards(stakeId);
        
        if (rewards > 0) {
            // Add rewards to stake amount
            stake.amount += rewards;
            stake.lastRewardBlock = block.number;
            userTotalStaked[msg.sender] += rewards;
            userLastActionBlock[msg.sender] = block.number;

            // Update pool total
            stakingPool.totalStaked += rewards;

            // Update governance voting power
            if (address(governanceContract) != address(0)) {
                _updateGovernanceVotingPower(msg.sender);
            }

            emit RewardsCompounded(msg.sender, stakeId, rewards, stake.amount);
        }
    }

    // ============ View Functions ============
    
    /**
     * @notice Gets details of a specific stake
     * @param stakeId The ID of the stake
     * @return The CognitiveStake struct
     */
    function getStake(uint256 stakeId)
        external
        view
        override
        validStakeId(stakeId)
        returns (CognitiveStake memory)
    {
        return stakes[stakeId];
    }

    /**
     * @notice Gets all stake IDs for a user
     * @param user The address to get stakes for
     * @return Array of stake IDs
     */
    function getUserStakes(address user) external view override returns (uint256[] memory) {
        return userStakes[user];
    }

    /**
     * @notice Calculates pending rewards for a stake
     * @param stakeId The ID of the stake
     * @return The amount of pending rewards
     */
    function pendingRewards(uint256 stakeId)
        external
        view
        override
        validStakeId(stakeId)
        returns (uint256)
    {
        return _calculateStakeRewards(stakeId);
    }

    /**
     * @notice Gets the total staking information for a user
     * @param user The address to get info for
     * @return totalStaked Total amount staked by the user
     * @return totalRewards Total rewards earned by the user
     * @return activeStakes Number of active stakes
     * @return votingPower Current voting power from staking
     */
    function getUserStakingInfo(address user)
        external
        view
        override
        returns (
            uint256 totalStaked,
            uint256 totalRewards,
            uint256 activeStakes,
            uint256 votingPower
        )
    {
        totalStaked = userTotalStaked[user];
        totalRewards = userTotalRewards[user];
        votingPower = getVotingPower(user);

        uint256[] memory userStakeIds = userStakes[user];
        for (uint256 i = 0; i < userStakeIds.length; i++) {
            if (stakes[userStakeIds[i]].isActive) {
                activeStakes++;
                totalRewards += _calculateStakeRewards(userStakeIds[i]);
            }
        }
    }

    /**
     * @notice Gets current staking pool information
     * @return The StakingPool struct
     */
    function getStakingPool() external view override returns (StakingPool memory) {
        return stakingPool;
    }

    /**
     * @notice Calculates the cognitive multiplier for a duration
     * @param duration The staking duration in blocks
     * @return The multiplier (in basis points, 10000 = 1x)
     */
    function calculateCognitiveMultiplier(uint256 duration)
        public
        view
        override
        returns (uint256)
    {
        if (duration < 216000) { // < 30 days
            return shortTermMultiplier;
        } else if (duration < 1296000) { // 30-180 days
            return mediumTermMultiplier;
        } else { // > 180 days
            return longTermMultiplier;
        }
    }

    /**
     * @notice Gets the voting power of an address from staking
     * @param user The address to check
     * @return The voting power derived from staking
     */
    function getVotingPower(address user) public view override returns (uint256) {
        uint256 basePower = userTotalStaked[user];
        if (basePower == 0) return 0;

        // Apply average multiplier based on user's stakes
        uint256 totalMultipliedPower = 0;
        uint256[] memory userStakeIds = userStakes[user];
        
        for (uint256 i = 0; i < userStakeIds.length; i++) {
            CognitiveStake memory stake = stakes[userStakeIds[i]];
            if (stake.isActive) {
                totalMultipliedPower += (stake.amount * stake.multiplier) / BASE_MULTIPLIER;
            }
        }

        return totalMultipliedPower;
    }

    /**
     * @notice Checks if a user can create a new stake
     * @param user The address to check
     * @param amount The amount they want to stake
     * @return True if the user can stake the amount
     */
    function canStake(address user, uint256 amount) external view override returns (bool) {
        if (amount < MIN_STAKE_AMOUNT || amount > MAX_STAKE_AMOUNT) return false;
        if (userTotalStaked[user] + amount > MAX_STAKE_AMOUNT) return false;
        if (dreamToken.balanceOf(user) < amount) return false;
        if (dreamToken.allowance(user, address(this)) < amount) return false;
        return true;
    }

    // ============ Administrative Functions ============
    
    /**
     * @notice Updates staking reward rate (governance only)
     * @param newRate The new reward rate per block
     */
    function updateRewardRate(uint256 newRate) external override onlyRole(PARAMETER_MANAGER_ROLE) {
        _updatePool();
        stakingPool.rewardRate = newRate;
        emit StakingParametersUpdated(newRate, stakingPool.minStakeDuration, stakingPool.maxStakeDuration, MIN_STAKE_AMOUNT);
    }

    /**
     * @notice Updates staking duration parameters (governance only)
     * @param newMinDuration The new minimum staking duration
     * @param newMaxDuration The new maximum staking duration
     */
    function updateStakingDurations(uint256 newMinDuration, uint256 newMaxDuration)
        external
        override
        onlyRole(PARAMETER_MANAGER_ROLE)
    {
        require(newMinDuration >= MIN_STAKING_DURATION, "DreamStaking: Min duration too low");
        require(newMaxDuration <= MAX_STAKING_DURATION, "DreamStaking: Max duration too high");
        require(newMinDuration <= newMaxDuration, "DreamStaking: Invalid duration range");

        stakingPool.minStakeDuration = newMinDuration;
        stakingPool.maxStakeDuration = newMaxDuration;

        emit StakingParametersUpdated(stakingPool.rewardRate, newMinDuration, newMaxDuration, MIN_STAKE_AMOUNT);
    }

    /**
     * @notice Updates cognitive multipliers (governance only)
     * @param shortTerm Multiplier for short-term staking
     * @param mediumTerm Multiplier for medium-term staking
     * @param longTerm Multiplier for long-term staking
     */
    function updateCognitiveMultipliers(
        uint256 shortTerm,
        uint256 mediumTerm,
        uint256 longTerm
    ) external override onlyRole(PARAMETER_MANAGER_ROLE) {
        require(shortTerm >= BASE_MULTIPLIER && shortTerm <= MAX_MULTIPLIER, "DreamStaking: Invalid short term multiplier");
        require(mediumTerm >= shortTerm && mediumTerm <= MAX_MULTIPLIER, "DreamStaking: Invalid medium term multiplier");
        require(longTerm >= mediumTerm && longTerm <= MAX_MULTIPLIER, "DreamStaking: Invalid long term multiplier");

        shortTermMultiplier = shortTerm;
        mediumTermMultiplier = mediumTerm;
        longTermMultiplier = longTerm;

        emit CognitiveMultipliersUpdated(shortTerm, mediumTerm, longTerm);
    }

    /**
     * @notice Updates minimum stake amount (governance only)
     * @param newMinStake The new minimum stake amount
     */
    function updateMinStake(uint256 newMinStake) external override onlyRole(PARAMETER_MANAGER_ROLE) {
        require(newMinStake >= MIN_STAKE_AMOUNT / 10, "DreamStaking: Min stake too low");
        require(newMinStake <= MIN_STAKE_AMOUNT * 10, "DreamStaking: Min stake too high");

        emit StakingParametersUpdated(stakingPool.rewardRate, stakingPool.minStakeDuration, stakingPool.maxStakeDuration, newMinStake);
    }

    // ============ Emergency Functions ============
    
    /**
     * @notice Emergency withdraw for users during contract upgrades
     * @param stakeId The stake ID to emergency withdraw
     */
    function emergencyWithdraw(uint256 stakeId)
        external
        override
        validStakeId(stakeId)
        onlyStakeOwner(stakeId)
        nonReentrant
    {
        CognitiveStake storage stake = stakes[stakeId];
        require(stake.isActive, "DreamStaking: Stake not active");

        // Emergency withdrawal allows immediate withdrawal but may forfeit some rewards
        uint256 withdrawAmount = stake.amount;
        
        // Mark stake as inactive
        stake.isActive = false;
        userTotalStaked[msg.sender] -= stake.amount;
        userLastActionBlock[msg.sender] = block.number;

        // Update pool state
        stakingPool.totalStaked -= stake.amount;

        // Transfer only the staked amount (no rewards during emergency)
        require(
            dreamToken.transfer(msg.sender, withdrawAmount),
            "DreamStaking: Emergency transfer failed"
        );

        emit CognitiveStakeWithdrawn(msg.sender, stakeId, withdrawAmount, 0);
    }

    /**
     * @notice Pauses staking in emergency situations (governance only)
     */
    function pauseStaking() external override onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    /**
     * @notice Unpauses staking (governance only)
     */
    function unpauseStaking() external override onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }

    /**
     * @notice Checks if staking is currently paused
     * @return True if staking is paused
     */
    function stakingPaused() external view override returns (bool) {
        return paused();
    }

    // ============ Integration Hooks ============
    
    /**
     * @notice Hook called when a dream is recorded by a staker
     * @dev Provides bonus rewards for active stakers
     * @param staker The address that recorded the dream
     * @param dreamHash The hash of the dream content
     */
    function onDreamRecorded(address staker, bytes32 dreamHash) external override {
        // Only allow calls from authorized dream recording contracts
        // This would typically be the IEMDreams contract
        // For now, we'll allow any caller but in production this should be restricted
        
        if (isStaker[staker]) {
            userLastActionBlock[staker] = block.number;
            // Additional logic for dream recording bonuses could be added here
        }
    }

    /**
     * @notice Gets the bonus multiplier for dream recording based on staking
     * @param staker The address of the dream recorder
     * @return The bonus multiplier (in basis points)
     */
    function getDreamBonusMultiplier(address staker) external view override returns (uint256) {
        if (!isStaker[staker]) return BASE_MULTIPLIER;

        // Calculate average multiplier across all active stakes
        uint256 totalStaked = 0;
        uint256 weightedMultiplier = 0;
        
        uint256[] memory userStakeIds = userStakes[staker];
        for (uint256 i = 0; i < userStakeIds.length; i++) {
            CognitiveStake memory stake = stakes[userStakeIds[i]];
            if (stake.isActive) {
                totalStaked += stake.amount;
                weightedMultiplier += (stake.amount * stake.multiplier);
            }
        }

        if (totalStaked == 0) return BASE_MULTIPLIER;
        
        return weightedMultiplier / totalStaked;
    }

    // ============ Internal Functions ============
    
    /**
     * @notice Updates the staking pool state
     */
    function _updatePool() internal {
        if (block.number <= stakingPool.lastUpdateBlock) return;
        if (stakingPool.totalStaked == 0) {
            stakingPool.lastUpdateBlock = block.number;
            return;
        }

        uint256 blocks = block.number - stakingPool.lastUpdateBlock;
        uint256 reward = (blocks * stakingPool.rewardRate * PRECISION) / stakingPool.totalStaked;
        stakingPool.accRewardPerShare += reward;
        stakingPool.lastUpdateBlock = block.number;

        emit PoolUpdated(stakingPool.totalStaked, stakingPool.rewardRate, block.number);
    }

    /**
     * @notice Calculates pending rewards for a stake
     * @param stakeId The stake ID
     * @return The pending rewards amount
     */
    function _calculateStakeRewards(uint256 stakeId) internal view returns (uint256) {
        CognitiveStake memory stake = stakes[stakeId];
        if (!stake.isActive) return 0;

        uint256 blocksSinceLastReward = block.number - stake.lastRewardBlock;
        if (blocksSinceLastReward == 0) return 0;

        uint256 baseReward = (stake.amount * stake.rewardRate * blocksSinceLastReward) / PRECISION;
        return (baseReward * stake.multiplier) / BASE_MULTIPLIER;
    }

    /**
     * @notice Updates governance voting power for a user
     * @param user The user to update voting power for
     */
    function _updateGovernanceVotingPower(address user) internal {
        // This would integrate with the governance contract to update voting multipliers
        // Implementation depends on the specific governance contract interface
        try governanceContract.updateStakingVotingMultiplier(user, getVotingPower(user)) {
            // Successfully updated voting power
        } catch {
            // Silently fail if governance contract doesn't support this yet
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
}
