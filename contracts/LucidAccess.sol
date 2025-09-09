// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";
import "./interfaces/ILucidAccess.sol";

/**
 * @title LucidAccess - LUCID Token-Based Access Control
 * @dev Upgradeable access control system based on LUCID token holdings and staking
 * @notice Manages access tiers and permissions for the OneiroSphere quantum dream network
 * 
 * Key Features:
 * - Tiered access system based on LUCID token holdings
 * - Additional benefits through LUCID token staking
 * - Daily dream limits and storage quotas per tier
 * - Special permissions for governance and premium features
 * - Flexible tier management through governance
 * - SKALE network optimization for zero-gas operations
 */
contract LucidAccess is
    Initializable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable,
    UUPSUpgradeable,
    ILucidAccess
{
    using CountersUpgradeable for CountersUpgradeable.Counter;

    // ============ Constants ============
    
    /// @notice Maximum number of tiers allowed
    uint256 public constant MAX_TIERS = 10;
    
    /// @notice Maximum daily dream limit for any tier
    uint256 public constant MAX_DAILY_DREAMS = 1000;
    
    /// @notice Maximum storage limit (100GB in bytes)
    uint256 public constant MAX_STORAGE_LIMIT = 100 * 1024 * 1024 * 1024;
    
    /// @notice Minimum LUCID staking period (7 days in seconds)
    uint256 public constant MIN_STAKING_PERIOD = 7 days;
    
    /// @notice Maximum LUCID staking period (2 years in seconds)
    uint256 public constant MAX_STAKING_PERIOD = 730 days;

    // ============ Roles ============
    
    /// @notice Role for governance operations
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    /// @notice Role for tier management
    bytes32 public constant TIER_MANAGER_ROLE = keccak256("TIER_MANAGER_ROLE");
    
    /// @notice Role for emergency operations
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");

    // ============ Feature Constants ============
    
    /// @notice Feature identifier for dream recording
    bytes32 public constant override FEATURE_DREAM_RECORDING = keccak256("DREAM_RECORDING");
    
    /// @notice Feature identifier for quantum dream access
    bytes32 public constant override FEATURE_QUANTUM_DREAMS = keccak256("QUANTUM_DREAMS");
    
    /// @notice Feature identifier for lucid gate access
    bytes32 public constant override FEATURE_LUCID_GATES = keccak256("LUCID_GATES");
    
    /// @notice Feature identifier for cognitive staking bonuses
    bytes32 public constant override FEATURE_COGNITIVE_BONUSES = keccak256("COGNITIVE_BONUSES");

    // ============ Permission Constants ============
    
    /// @notice Special permission for unlimited dream recording
    uint256 public constant override PERMISSION_UNLIMITED_DREAMS = 1 << 0;
    
    /// @notice Special permission for premium storage
    uint256 public constant override PERMISSION_PREMIUM_STORAGE = 1 << 1;
    
    /// @notice Special permission for governance participation
    uint256 public constant override PERMISSION_GOVERNANCE = 1 << 2;

    // ============ State Variables ============
    
    /// @notice Counter for access tier IDs
    CountersUpgradeable.Counter private _tierIdCounter;
    
    /// @notice Address of the LUCID token contract
    IERC20Upgradeable public lucidToken;
    
    /// @notice Default tier ID for users with no LUCID
    uint256 public defaultTierId;
    
    /// @notice LUCID staking reward rate per second
    uint256 public stakingRewardRate;

    // ============ Mappings ============
    
    /// @notice Mapping of tier ID to AccessTier
    mapping(uint256 => AccessTier) public accessTiers;
    
    /// @notice Mapping to track all tier IDs
    mapping(uint256 => bool) public tierExists;
    
    /// @notice Array of all tier IDs for enumeration
    uint256[] public allTierIds;
    
    /// @notice Mapping of user to their LUCID staking info
    mapping(address => LucidStakingInfo) public lucidStaking;
    
    /// @notice Mapping of user to daily dream count (user => day => count)
    mapping(address => mapping(uint256 => uint256)) public dailyDreamCount;
    
    /// @notice Mapping of user to total storage used
    mapping(address => uint256) public userStorageUsed;
    
    /// @notice Mapping of user to special permissions
    mapping(address => uint256) public userSpecialPermissions;
    
    /// @notice Mapping of user to last tier calculation block
    mapping(address => uint256) public userLastTierUpdate;

    // ============ Structs ============
    
    /// @notice Structure for LUCID staking information
    struct LucidStakingInfo {
        uint256 stakedAmount;
        uint256 stakingStartTime;
        uint256 stakingEndTime;
        uint256 accumulatedRewards;
        uint256 lastRewardClaim;
        bool isActive;
    }

    // ============ Events ============
    
    /// @notice Additional events beyond interface requirements
    event DefaultTierSet(uint256 newDefaultTier);
    
    event StakingRewardRateUpdated(uint256 newRate);
    
    event UserTierCacheUpdated(
        address indexed user,
        uint256 newTier,
        uint256 updateBlock
    );

    // ============ Modifiers ============
    
    /// @notice Validates tier ID
    modifier validTier(uint256 tierId) {
        require(tierExists[tierId], "LucidAccess: Invalid tier ID");
        _;
    }

    // ============ Initialization ============
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the LucidAccess contract
     * @param lucidTokenAddr The address of the LUCID token contract
     * @param initialOwner The initial owner and admin
     * @param initialStakingRate Initial staking reward rate per second
     */
    function initialize(
        address lucidTokenAddr,
        address initialOwner,
        uint256 initialStakingRate
    ) public initializer {
        require(lucidTokenAddr != address(0), "LucidAccess: Invalid token address");
        require(initialOwner != address(0), "LucidAccess: Invalid owner address");

        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();
        __UUPSUpgradeable_init();

        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(GOVERNANCE_ROLE, initialOwner);
        _grantRole(TIER_MANAGER_ROLE, initialOwner);
        _grantRole(EMERGENCY_ROLE, initialOwner);

        // Set contract addresses
        lucidToken = IERC20Upgradeable(lucidTokenAddr);
        stakingRewardRate = initialStakingRate;

        // Create default tier for users with no LUCID
        _createDefaultTier();
    }

    // ============ Access Control Functions ============
    
    /**
     * @notice Checks if a user can record a dream
     * @param user The address to check
     * @param dreamSize The size of the dream data in bytes
     * @return canRecord Whether the user can record the dream
     * @return reason The reason if recording is not allowed
     */
    function canRecordDream(address user, uint256 dreamSize)
        external
        view
        override
        returns (bool canRecord, string memory reason)
    {
        uint256 tierId = getUserTier(user);
        AccessTier memory tier = accessTiers[tierId];

        // Check special permissions first
        if (userSpecialPermissions[user] & PERMISSION_UNLIMITED_DREAMS != 0) {
            return (true, "");
        }

        // Check daily limit
        uint256 today = block.timestamp / 1 days;
        uint256 todayCount = dailyDreamCount[user][today];
        if (todayCount >= tier.maxDreamsPerDay) {
            return (false, "Daily dream limit exceeded");
        }

        // Check storage limit
        uint256 currentStorage = userStorageUsed[user];
        if (currentStorage + dreamSize > tier.dreamStorageLimit) {
            // Check for premium storage permission
            if (userSpecialPermissions[user] & PERMISSION_PREMIUM_STORAGE == 0) {
                return (false, "Storage limit exceeded");
            }
        }

        return (true, "");
    }

    /**
     * @notice Checks if a user can access a specific feature
     * @param user The address to check
     * @param feature The feature identifier
     * @return hasAccess Whether the user has access
     */
    function hasAccess(address user, bytes32 feature) external view override returns (bool hasAccess) {
        uint256 tierId = getUserTier(user);
        AccessTier memory tier = accessTiers[tierId];

        // Basic features available to all tiers
        if (feature == FEATURE_DREAM_RECORDING) {
            return true;
        }

        // Quantum dreams require tier 2+
        if (feature == FEATURE_QUANTUM_DREAMS) {
            return tierId >= 2;
        }

        // Lucid gates require tier 3+
        if (feature == FEATURE_LUCID_GATES) {
            return tierId >= 3;
        }

        // Cognitive bonuses require tier 4+ or special permission
        if (feature == FEATURE_COGNITIVE_BONUSES) {
            return tierId >= 4 || (userSpecialPermissions[user] & PERMISSION_GOVERNANCE != 0);
        }

        return false;
    }

    /**
     * @notice Gets the current access tier for a user
     * @param user The address to check
     * @return tierId The current access tier ID
     */
    function getUserTier(address user) public view override returns (uint256 tierId) {
        uint256 lucidBalance = lucidToken.balanceOf(user);
        uint256 stakedLucid = lucidStaking[user].stakedAmount;
        
        return calculateRecommendedTier(lucidBalance, stakedLucid);
    }

    /**
     * @notice Gets complete access information for a user
     * @param user The address to check
     * @return The UserAccess struct
     */
    function getUserAccess(address user) external view override returns (UserAccess memory) {
        uint256 tierId = getUserTier(user);
        uint256 today = block.timestamp / 1 days;
        
        return UserAccess({
            currentTier: tierId,
            lucidBalance: lucidToken.balanceOf(user),
            stakedLucid: lucidStaking[user].stakedAmount,
            dreamsToday: dailyDreamCount[user][today],
            lastDreamTimestamp: 0, // This would need additional tracking
            totalStorageUsed: userStorageUsed[user],
            specialAccess: userSpecialPermissions[user]
        });
    }

    /**
     * @notice Records a dream access event (updates daily limits)
     * @param user The user recording the dream
     * @param dreamSize The size of the dream data
     */
    function recordDreamAccess(address user, uint256 dreamSize) external override whenNotPaused {
        // In production, this should be restricted to authorized dream recording contracts
        uint256 today = block.timestamp / 1 days;
        dailyDreamCount[user][today]++;
        userStorageUsed[user] += dreamSize;
    }

    // ============ LUCID Staking Functions ============
    
    /**
     * @notice Stakes LUCID tokens to increase access tier
     * @param amount The amount of LUCID tokens to stake
     */
    function stakeLucid(uint256 amount) external override whenNotPaused nonReentrant {
        require(amount > 0, "LucidAccess: Amount must be greater than 0");
        require(
            lucidToken.transferFrom(msg.sender, address(this), amount),
            "LucidAccess: Transfer failed"
        );

        LucidStakingInfo storage stakingInfo = lucidStaking[msg.sender];
        
        // If user has existing stake, claim rewards first
        if (stakingInfo.isActive) {
            _claimStakingRewards(msg.sender);
        }

        // Update staking info
        stakingInfo.stakedAmount += amount;
        stakingInfo.stakingStartTime = block.timestamp;
        stakingInfo.stakingEndTime = block.timestamp + MIN_STAKING_PERIOD;
        stakingInfo.lastRewardClaim = block.timestamp;
        stakingInfo.isActive = true;

        uint256 newTier = getUserTier(msg.sender);
        
        emit LucidStaked(msg.sender, amount, newTier);
    }

    /**
     * @notice Unstakes LUCID tokens (may reduce access tier)
     * @param amount The amount of LUCID tokens to unstake
     */
    function unstakeLucid(uint256 amount) external override nonReentrant {
        LucidStakingInfo storage stakingInfo = lucidStaking[msg.sender];
        require(stakingInfo.isActive, "LucidAccess: No active stake");
        require(stakingInfo.stakedAmount >= amount, "LucidAccess: Insufficient staked amount");
        require(
            block.timestamp >= stakingInfo.stakingEndTime,
            "LucidAccess: Staking period not ended"
        );

        // Claim rewards first
        _claimStakingRewards(msg.sender);

        // Update staking info
        stakingInfo.stakedAmount -= amount;
        if (stakingInfo.stakedAmount == 0) {
            stakingInfo.isActive = false;
        }

        // Transfer tokens back
        require(
            lucidToken.transfer(msg.sender, amount),
            "LucidAccess: Transfer failed"
        );

        uint256 newTier = getUserTier(msg.sender);
        
        emit LucidUnstaked(msg.sender, amount, newTier);
    }

    /**
     * @notice Gets the LUCID staking information for a user
     * @param user The address to check
     * @return staked The amount of LUCID tokens staked
     * @return unstakeTime The earliest time tokens can be unstaked
     * @return stakingRewards The accumulated staking rewards
     */
    function getLucidStakingInfo(address user)
        external
        view
        override
        returns (
            uint256 staked,
            uint256 unstakeTime,
            uint256 stakingRewards
        )
    {
        LucidStakingInfo memory stakingInfo = lucidStaking[user];
        
        staked = stakingInfo.stakedAmount;
        unstakeTime = stakingInfo.stakingEndTime;
        stakingRewards = stakingInfo.accumulatedRewards;
        
        // Calculate pending rewards
        if (stakingInfo.isActive && stakingRewardRate > 0) {
            uint256 timeStaked = block.timestamp - stakingInfo.lastRewardClaim;
            stakingRewards += (stakingInfo.stakedAmount * stakingRewardRate * timeStaked) / 1e18;
        }
    }

    // ============ Tier Management ============
    
    /**
     * @notice Creates a new access tier (governance only)
     * @param name The name of the tier
     * @param requiredLucid LUCID tokens required
     * @param requiredStaking Staking requirement
     * @param maxDreamsPerDay Daily dream limit
     * @param dreamStorageLimit Storage limit in bytes
     * @param priorityMultiplier Priority multiplier
     * @param specialPermissions Special permissions bitmap
     * @return tierId The ID of the created tier
     */
    function createAccessTier(
        string memory name,
        uint256 requiredLucid,
        uint256 requiredStaking,
        uint256 maxDreamsPerDay,
        uint256 dreamStorageLimit,
        uint256 priorityMultiplier,
        uint256 specialPermissions
    ) external override onlyRole(TIER_MANAGER_ROLE) returns (uint256 tierId) {
        require(allTierIds.length < MAX_TIERS, "LucidAccess: Maximum tiers reached");
        require(maxDreamsPerDay <= MAX_DAILY_DREAMS, "LucidAccess: Daily dreams exceeds maximum");
        require(dreamStorageLimit <= MAX_STORAGE_LIMIT, "LucidAccess: Storage limit exceeds maximum");

        _tierIdCounter.increment();
        tierId = _tierIdCounter.current();

        accessTiers[tierId] = AccessTier({
            id: tierId,
            name: name,
            requiredLucid: requiredLucid,
            requiredStaking: requiredStaking,
            maxDreamsPerDay: maxDreamsPerDay,
            dreamStorageLimit: dreamStorageLimit,
            priorityMultiplier: priorityMultiplier,
            specialPermissions: specialPermissions,
            isActive: true
        });

        tierExists[tierId] = true;
        allTierIds.push(tierId);

        emit AccessTierCreated(tierId, name, requiredLucid, requiredStaking);

        return tierId;
    }

    /**
     * @notice Updates an existing access tier (governance only)
     * @param tierId The ID of the tier to update
     * @param requiredLucid New LUCID requirement
     * @param requiredStaking New staking requirement
     * @param maxDreamsPerDay New daily dream limit
     * @param dreamStorageLimit New storage limit
     * @param priorityMultiplier New priority multiplier
     */
    function updateAccessTier(
        uint256 tierId,
        uint256 requiredLucid,
        uint256 requiredStaking,
        uint256 maxDreamsPerDay,
        uint256 dreamStorageLimit,
        uint256 priorityMultiplier
    ) external override onlyRole(TIER_MANAGER_ROLE) validTier(tierId) {
        require(maxDreamsPerDay <= MAX_DAILY_DREAMS, "LucidAccess: Daily dreams exceeds maximum");
        require(dreamStorageLimit <= MAX_STORAGE_LIMIT, "LucidAccess: Storage limit exceeds maximum");

        AccessTier storage tier = accessTiers[tierId];
        tier.requiredLucid = requiredLucid;
        tier.requiredStaking = requiredStaking;
        tier.maxDreamsPerDay = maxDreamsPerDay;
        tier.dreamStorageLimit = dreamStorageLimit;
        tier.priorityMultiplier = priorityMultiplier;

        emit AccessTierUpdated(tierId, requiredLucid, maxDreamsPerDay, dreamStorageLimit);
    }

    /**
     * @notice Activates or deactivates an access tier (governance only)
     * @param tierId The ID of the tier
     * @param active Whether the tier should be active
     */
    function setTierActive(uint256 tierId, bool active)
        external
        override
        onlyRole(TIER_MANAGER_ROLE)
        validTier(tierId)
    {
        accessTiers[tierId].isActive = active;
    }

    /**
     * @notice Gets details of a specific access tier
     * @param tierId The ID of the tier
     * @return The AccessTier struct
     */
    function getAccessTier(uint256 tierId)
        external
        view
        override
        validTier(tierId)
        returns (AccessTier memory)
    {
        return accessTiers[tierId];
    }

    /**
     * @notice Gets all available access tiers
     * @return Array of all AccessTier structs
     */
    function getAllAccessTiers() external view override returns (AccessTier[] memory) {
        AccessTier[] memory tiers = new AccessTier[](allTierIds.length);
        for (uint256 i = 0; i < allTierIds.length; i++) {
            tiers[i] = accessTiers[allTierIds[i]];
        }
        return tiers;
    }

    // ============ Special Access Management ============
    
    /**
     * @notice Grants special access permissions to a user (governance only)
     * @param user The user to grant access to
     * @param permissions The permissions to grant (bitmap)
     * @param reason The reason for granting access
     */
    function grantSpecialAccess(
        address user,
        uint256 permissions,
        string memory reason
    ) external override onlyRole(GOVERNANCE_ROLE) {
        userSpecialPermissions[user] |= permissions;
        
        emit SpecialAccessGranted(user, permissions, msg.sender, reason);
    }

    /**
     * @notice Revokes special access permissions from a user (governance only)
     * @param user The user to revoke access from
     * @param permissions The permissions to revoke (bitmap)
     * @param reason The reason for revoking access
     */
    function revokeSpecialAccess(
        address user,
        uint256 permissions,
        string memory reason
    ) external override onlyRole(GOVERNANCE_ROLE) {
        userSpecialPermissions[user] &= ~permissions;
        
        // Note: We emit SpecialAccessGranted with 0 permissions to indicate revocation
        emit SpecialAccessGranted(user, 0, msg.sender, reason);
    }

    /**
     * @notice Checks if a user has specific special permissions
     * @param user The address to check
     * @param permissions The permissions to check (bitmap)
     * @return hasPermissions Whether the user has the permissions
     */
    function hasSpecialAccess(address user, uint256 permissions)
        external
        view
        override
        returns (bool hasPermissions)
    {
        return (userSpecialPermissions[user] & permissions) == permissions;
    }

    // ============ View Functions ============
    
    /**
     * @notice Gets the minimum LUCID requirement for the highest tier
     * @return The minimum LUCID tokens required
     */
    function getMaxTierRequirement() external view override returns (uint256) {
        uint256 maxRequirement = 0;
        for (uint256 i = 0; i < allTierIds.length; i++) {
            uint256 tierId = allTierIds[i];
            if (accessTiers[tierId].isActive && accessTiers[tierId].requiredLucid > maxRequirement) {
                maxRequirement = accessTiers[tierId].requiredLucid;
            }
        }
        return maxRequirement;
    }

    /**
     * @notice Calculates the recommended tier for a LUCID balance
     * @param lucidBalance The LUCID token balance
     * @param stakedLucid The amount of staked LUCID
     * @return tierId The recommended tier ID
     */
    function calculateRecommendedTier(uint256 lucidBalance, uint256 stakedLucid)
        public
        view
        override
        returns (uint256 tierId)
    {
        uint256 totalLucid = lucidBalance + stakedLucid;
        uint256 bestTier = defaultTierId;

        for (uint256 i = 0; i < allTierIds.length; i++) {
            uint256 currentTierId = allTierIds[i];
            AccessTier memory tier = accessTiers[currentTierId];
            
            if (tier.isActive && totalLucid >= tier.requiredLucid && stakedLucid >= tier.requiredStaking) {
                if (tier.requiredLucid > accessTiers[bestTier].requiredLucid) {
                    bestTier = currentTierId;
                }
            }
        }

        return bestTier;
    }

    /**
     * @notice Gets the next tier upgrade requirement for a user
     * @param user The address to check
     * @return nextTierId The next tier ID
     * @return additionalLucidNeeded Additional LUCID tokens needed
     * @return additionalStakingNeeded Additional staking needed
     */
    function getUpgradeRequirement(address user)
        external
        view
        override
        returns (
            uint256 nextTierId,
            uint256 additionalLucidNeeded,
            uint256 additionalStakingNeeded
        )
    {
        uint256 currentTier = getUserTier(user);
        uint256 userLucid = lucidToken.balanceOf(user);
        uint256 userStaked = lucidStaking[user].stakedAmount;
        uint256 totalLucid = userLucid + userStaked;

        nextTierId = 0;
        additionalLucidNeeded = type(uint256).max;
        additionalStakingNeeded = 0;

        for (uint256 i = 0; i < allTierIds.length; i++) {
            uint256 tierId = allTierIds[i];
            AccessTier memory tier = accessTiers[tierId];
            
            if (tier.isActive && tier.requiredLucid > accessTiers[currentTier].requiredLucid) {
                uint256 lucidNeeded = tier.requiredLucid > totalLucid ? tier.requiredLucid - totalLucid : 0;
                uint256 stakingNeeded = tier.requiredStaking > userStaked ? tier.requiredStaking - userStaked : 0;
                
                if (lucidNeeded < additionalLucidNeeded) {
                    nextTierId = tierId;
                    additionalLucidNeeded = lucidNeeded;
                    additionalStakingNeeded = stakingNeeded;
                }
            }
        }

        if (nextTierId == 0) {
            additionalLucidNeeded = 0; // User is already at highest tier
        }
    }

    // ============ Internal Functions ============
    
    /**
     * @notice Creates the default tier for users with no LUCID
     */
    function _createDefaultTier() internal {
        _tierIdCounter.increment();
        uint256 tierId = _tierIdCounter.current();
        
        accessTiers[tierId] = AccessTier({
            id: tierId,
            name: "Basic",
            requiredLucid: 0,
            requiredStaking: 0,
            maxDreamsPerDay: 5,
            dreamStorageLimit: 100 * 1024 * 1024, // 100MB
            priorityMultiplier: 10000, // 1x
            specialPermissions: 0,
            isActive: true
        });

        tierExists[tierId] = true;
        allTierIds.push(tierId);
        defaultTierId = tierId;

        emit AccessTierCreated(tierId, "Basic", 0, 0);
    }

    /**
     * @notice Claims staking rewards for a user
     * @param user The user to claim rewards for
     */
    function _claimStakingRewards(address user) internal {
        LucidStakingInfo storage stakingInfo = lucidStaking[user];
        if (!stakingInfo.isActive || stakingRewardRate == 0) return;

        uint256 timeStaked = block.timestamp - stakingInfo.lastRewardClaim;
        uint256 rewards = (stakingInfo.stakedAmount * stakingRewardRate * timeStaked) / 1e18;
        
        if (rewards > 0) {
            stakingInfo.accumulatedRewards += rewards;
            stakingInfo.lastRewardClaim = block.timestamp;
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
        require(to != address(0), "LucidAccess: Invalid recovery address");
        if (token == address(0)) {
            // Recover ETH
            payable(to).transfer(amount);
        } else {
            // Recover ERC20 tokens
            IERC20Upgradeable(token).transfer(to, amount);
        }
    }

    // ============ Administrative Functions ============
    
    /**
     * @notice Updates the default tier (governance only)
     * @param newDefaultTier The new default tier ID
     */
    function setDefaultTier(uint256 newDefaultTier)
        external
        onlyRole(GOVERNANCE_ROLE)
        validTier(newDefaultTier)
    {
        defaultTierId = newDefaultTier;
        emit DefaultTierSet(newDefaultTier);
    }

    /**
     * @notice Updates the staking reward rate (governance only)
     * @param newRate The new reward rate per second
     */
    function setStakingRewardRate(uint256 newRate) external onlyRole(GOVERNANCE_ROLE) {
        stakingRewardRate = newRate;
        emit StakingRewardRateUpdated(newRate);
    }

    // ============ Receive ETH ============
    
    receive() external payable {
        // Allow contract to receive ETH for gas optimization on SKALE
    }
}