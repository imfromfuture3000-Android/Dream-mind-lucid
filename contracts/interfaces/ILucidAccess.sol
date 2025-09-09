// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ILucidAccess
 * @dev Interface for LUCID token-based access control in the OneiroSphere
 * @notice Manages access levels and permissions based on LUCID token holdings and staking
 */
interface ILucidAccess {
    // ============ Structs ============
    
    /**
     * @notice Structure representing an access tier
     * @param id Unique tier identifier
     * @param name Human-readable tier name
     * @param requiredLucid Minimum LUCID tokens required
     * @param requiredStaking Minimum staking requirement
     * @param maxDreamsPerDay Maximum dreams allowed per day
     * @param dreamStorageLimit Storage limit for dreams (in bytes)
     * @param priorityMultiplier Priority multiplier for dream processing
     * @param specialPermissions Bitmap of special permissions
     * @param isActive Whether the tier is currently active
     */
    struct AccessTier {
        uint256 id;
        string name;
        uint256 requiredLucid;
        uint256 requiredStaking;
        uint256 maxDreamsPerDay;
        uint256 dreamStorageLimit;
        uint256 priorityMultiplier;
        uint256 specialPermissions;
        bool isActive;
    }

    /**
     * @notice Structure for user access information
     * @param currentTier The user's current access tier
     * @param lucidBalance Current LUCID token balance
     * @param stakedLucid Amount of LUCID tokens staked
     * @param dreamsToday Number of dreams recorded today
     * @param lastDreamTimestamp Timestamp of last dream recording
     * @param totalStorageUsed Total storage used for dreams
     * @param specialAccess Bitmap of special access permissions
     */
    struct UserAccess {
        uint256 currentTier;
        uint256 lucidBalance;
        uint256 stakedLucid;
        uint256 dreamsToday;
        uint256 lastDreamTimestamp;
        uint256 totalStorageUsed;
        uint256 specialAccess;
    }

    // ============ Events ============
    
    /**
     * @notice Emitted when a new access tier is created
     * @param tierId The ID of the created tier
     * @param name The name of the tier
     * @param requiredLucid LUCID tokens required for this tier
     * @param requiredStaking Staking requirement for this tier
     */
    event AccessTierCreated(
        uint256 indexed tierId,
        string name,
        uint256 requiredLucid,
        uint256 requiredStaking
    );

    /**
     * @notice Emitted when an access tier is updated
     * @param tierId The ID of the updated tier
     * @param requiredLucid New LUCID requirement
     * @param maxDreamsPerDay New daily dream limit
     * @param dreamStorageLimit New storage limit
     */
    event AccessTierUpdated(
        uint256 indexed tierId,
        uint256 requiredLucid,
        uint256 maxDreamsPerDay,
        uint256 dreamStorageLimit
    );

    /**
     * @notice Emitted when a user's access tier changes
     * @param user The user whose tier changed
     * @param oldTier The previous tier ID
     * @param newTier The new tier ID
     * @param reason The reason for the tier change
     */
    event UserTierChanged(
        address indexed user,
        uint256 oldTier,
        uint256 newTier,
        string reason
    );

    /**
     * @notice Emitted when LUCID tokens are staked for access
     * @param user The user who staked tokens
     * @param amount The amount of LUCID tokens staked
     * @param newTier The new access tier achieved
     */
    event LucidStaked(address indexed user, uint256 amount, uint256 newTier);

    /**
     * @notice Emitted when LUCID tokens are unstaked
     * @param user The user who unstaked tokens
     * @param amount The amount of LUCID tokens unstaked
     * @param newTier The new access tier after unstaking
     */
    event LucidUnstaked(address indexed user, uint256 amount, uint256 newTier);

    /**
     * @notice Emitted when special access is granted
     * @param user The user granted special access
     * @param permissions The permissions granted (bitmap)
     * @param grantedBy The address that granted the access
     * @param reason The reason for granting access
     */
    event SpecialAccessGranted(
        address indexed user,
        uint256 permissions,
        address indexed grantedBy,
        string reason
    );

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
        returns (bool canRecord, string memory reason);

    /**
     * @notice Checks if a user can access a specific feature
     * @param user The address to check
     * @param feature The feature identifier
     * @return hasAccess Whether the user has access
     */
    function hasAccess(address user, bytes32 feature) external view returns (bool hasAccess);

    /**
     * @notice Gets the current access tier for a user
     * @param user The address to check
     * @return tierId The current access tier ID
     */
    function getUserTier(address user) external view returns (uint256 tierId);

    /**
     * @notice Gets complete access information for a user
     * @param user The address to check
     * @return The UserAccess struct
     */
    function getUserAccess(address user) external view returns (UserAccess memory);

    /**
     * @notice Records a dream access event (updates daily limits)
     * @param user The user recording the dream
     * @param dreamSize The size of the dream data
     */
    function recordDreamAccess(address user, uint256 dreamSize) external;

    // ============ LUCID Staking Functions ============
    
    /**
     * @notice Stakes LUCID tokens to increase access tier
     * @param amount The amount of LUCID tokens to stake
     */
    function stakeLucid(uint256 amount) external;

    /**
     * @notice Unstakes LUCID tokens (may reduce access tier)
     * @param amount The amount of LUCID tokens to unstake
     */
    function unstakeLucid(uint256 amount) external;

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
        returns (
            uint256 staked,
            uint256 unstakeTime,
            uint256 stakingRewards
        );

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
    ) external returns (uint256 tierId);

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
    ) external;

    /**
     * @notice Activates or deactivates an access tier (governance only)
     * @param tierId The ID of the tier
     * @param active Whether the tier should be active
     */
    function setTierActive(uint256 tierId, bool active) external;

    /**
     * @notice Gets details of a specific access tier
     * @param tierId The ID of the tier
     * @return The AccessTier struct
     */
    function getAccessTier(uint256 tierId) external view returns (AccessTier memory);

    /**
     * @notice Gets all available access tiers
     * @return Array of all AccessTier structs
     */
    function getAllAccessTiers() external view returns (AccessTier[] memory);

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
    ) external;

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
    ) external;

    /**
     * @notice Checks if a user has specific special permissions
     * @param user The address to check
     * @param permissions The permissions to check (bitmap)
     * @return hasPermissions Whether the user has the permissions
     */
    function hasSpecialAccess(address user, uint256 permissions)
        external
        view
        returns (bool hasPermissions);

    // ============ View Functions ============
    
    /**
     * @notice Gets the minimum LUCID requirement for the highest tier
     * @return The minimum LUCID tokens required
     */
    function getMaxTierRequirement() external view returns (uint256);

    /**
     * @notice Calculates the recommended tier for a LUCID balance
     * @param lucidBalance The LUCID token balance
     * @param stakedLucid The amount of staked LUCID
     * @return tierId The recommended tier ID
     */
    function calculateRecommendedTier(uint256 lucidBalance, uint256 stakedLucid)
        external
        view
        returns (uint256 tierId);

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
        returns (
            uint256 nextTierId,
            uint256 additionalLucidNeeded,
            uint256 additionalStakingNeeded
        );

    // ============ Constants ============
    
    /**
     * @notice Feature identifier for dream recording
     * @return The feature identifier
     */
    function FEATURE_DREAM_RECORDING() external pure returns (bytes32);

    /**
     * @notice Feature identifier for quantum dream access
     * @return The feature identifier
     */
    function FEATURE_QUANTUM_DREAMS() external pure returns (bytes32);

    /**
     * @notice Feature identifier for lucid gate access
     * @return The feature identifier
     */
    function FEATURE_LUCID_GATES() external pure returns (bytes32);

    /**
     * @notice Feature identifier for cognitive staking bonuses
     * @return The feature identifier
     */
    function FEATURE_COGNITIVE_BONUSES() external pure returns (bytes32);

    /**
     * @notice Special permission for unlimited dream recording
     * @return The permission bitmap
     */
    function PERMISSION_UNLIMITED_DREAMS() external pure returns (uint256);

    /**
     * @notice Special permission for premium storage
     * @return The permission bitmap
     */
    function PERMISSION_PREMIUM_STORAGE() external pure returns (uint256);

    /**
     * @notice Special permission for governance participation
     * @return The permission bitmap
     */
    function PERMISSION_GOVERNANCE() external pure returns (uint256);
}