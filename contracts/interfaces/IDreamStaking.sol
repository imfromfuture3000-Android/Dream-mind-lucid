// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IDreamStaking
 * @dev Interface for cognitive staking in the Dream ecosystem
 * @notice Enables staking of DREAM tokens for enhanced dream mining and governance participation
 */
interface IDreamStaking {
    // ============ Structs ============
    
    /**
     * @notice Structure representing a cognitive staking position
     * @param staker The address that created the stake
     * @param amount The amount of DREAM tokens staked
     * @param duration The staking duration in blocks
     * @param startBlock The block when staking started
     * @param endBlock The block when staking ends
     * @param rewardRate The reward rate at the time of staking
     * @param lastRewardBlock The last block when rewards were calculated
     * @param accumulatedRewards The total rewards accumulated
     * @param multiplier The cognitive multiplier based on staking duration
     * @param isActive Whether the stake is currently active
     */
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

    /**
     * @notice Structure for staking pool information
     * @param totalStaked Total amount of DREAM tokens staked in the pool
     * @param totalStakers Number of unique stakers
     * @param rewardRate Current reward rate per block
     * @param lastUpdateBlock Last block when pool was updated
     * @param accRewardPerShare Accumulated reward per share
     * @param minStakeDuration Minimum staking duration in blocks
     * @param maxStakeDuration Maximum staking duration in blocks
     */
    struct StakingPool {
        uint256 totalStaked;
        uint256 totalStakers;
        uint256 rewardRate;
        uint256 lastUpdateBlock;
        uint256 accRewardPerShare;
        uint256 minStakeDuration;
        uint256 maxStakeDuration;
    }

    // ============ Events ============
    
    /**
     * @notice Emitted when DREAM tokens are staked
     * @param staker The address that staked tokens
     * @param stakeId The ID of the created stake
     * @param amount The amount of tokens staked
     * @param duration The staking duration in blocks
     * @param multiplier The cognitive multiplier applied
     */
    event CognitiveStakeCreated(
        address indexed staker,
        uint256 indexed stakeId,
        uint256 amount,
        uint256 duration,
        uint256 multiplier
    );

    /**
     * @notice Emitted when staked tokens are withdrawn
     * @param staker The address that withdrew tokens
     * @param stakeId The ID of the withdrawn stake
     * @param amount The amount of tokens withdrawn
     * @param rewards The amount of rewards claimed
     */
    event CognitiveStakeWithdrawn(
        address indexed staker,
        uint256 indexed stakeId,
        uint256 amount,
        uint256 rewards
    );

    /**
     * @notice Emitted when staking rewards are claimed
     * @param staker The address that claimed rewards
     * @param stakeId The stake ID rewards were claimed for
     * @param amount The amount of rewards claimed
     */
    event StakingRewardsClaimed(
        address indexed staker,
        uint256 indexed stakeId,
        uint256 amount
    );

    /**
     * @notice Emitted when staking parameters are updated
     * @param newRewardRate The new reward rate per block
     * @param newMinDuration The new minimum staking duration
     * @param newMaxDuration The new maximum staking duration
     * @param newMinStake The new minimum stake amount
     */
    event StakingParametersUpdated(
        uint256 newRewardRate,
        uint256 newMinDuration,
        uint256 newMaxDuration,
        uint256 newMinStake
    );

    /**
     * @notice Emitted when cognitive multipliers are updated
     * @param shortTermMultiplier New multiplier for short-term staking
     * @param mediumTermMultiplier New multiplier for medium-term staking
     * @param longTermMultiplier New multiplier for long-term staking
     */
    event CognitiveMultipliersUpdated(
        uint256 shortTermMultiplier,
        uint256 mediumTermMultiplier,
        uint256 longTermMultiplier
    );

    // ============ Staking Functions ============
    
    /**
     * @notice Stakes DREAM tokens for cognitive mining
     * @param amount The amount of DREAM tokens to stake
     * @param duration The staking duration in blocks
     * @return stakeId The ID of the created stake
     */
    function stakeDream(uint256 amount, uint256 duration) external returns (uint256 stakeId);

    /**
     * @notice Unstakes DREAM tokens and claims all accumulated rewards
     * @param stakeId The ID of the stake to unstake
     */
    function unstakeDream(uint256 stakeId) external;

    /**
     * @notice Claims accumulated rewards without unstaking
     * @param stakeId The ID of the stake to claim rewards for
     */
    function claimRewards(uint256 stakeId) external;

    /**
     * @notice Extends the duration of an existing stake
     * @param stakeId The ID of the stake to extend
     * @param additionalDuration Additional blocks to extend
     */
    function extendStake(uint256 stakeId, uint256 additionalDuration) external;

    /**
     * @notice Compounds rewards back into the stake
     * @param stakeId The ID of the stake to compound
     */
    function compoundRewards(uint256 stakeId) external;

    // ============ View Functions ============
    
    /**
     * @notice Gets details of a specific stake
     * @param stakeId The ID of the stake
     * @return The CognitiveStake struct
     */
    function getStake(uint256 stakeId) external view returns (CognitiveStake memory);

    /**
     * @notice Gets all stake IDs for a user
     * @param user The address to get stakes for
     * @return Array of stake IDs
     */
    function getUserStakes(address user) external view returns (uint256[] memory);

    /**
     * @notice Calculates pending rewards for a stake
     * @param stakeId The ID of the stake
     * @return The amount of pending rewards
     */
    function pendingRewards(uint256 stakeId) external view returns (uint256);

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
        returns (
            uint256 totalStaked,
            uint256 totalRewards,
            uint256 activeStakes,
            uint256 votingPower
        );

    /**
     * @notice Gets current staking pool information
     * @return The StakingPool struct
     */
    function getStakingPool() external view returns (StakingPool memory);

    /**
     * @notice Calculates the cognitive multiplier for a duration
     * @param duration The staking duration in blocks
     * @return The multiplier (in basis points, 10000 = 1x)
     */
    function calculateCognitiveMultiplier(uint256 duration) external view returns (uint256);

    /**
     * @notice Gets the voting power of an address from staking
     * @param user The address to check
     * @return The voting power derived from staking
     */
    function getVotingPower(address user) external view returns (uint256);

    /**
     * @notice Checks if a user can create a new stake
     * @param user The address to check
     * @param amount The amount they want to stake
     * @return True if the user can stake the amount
     */
    function canStake(address user, uint256 amount) external view returns (bool);

    // ============ Administrative Functions ============
    
    /**
     * @notice Updates staking reward rate (governance only)
     * @param newRate The new reward rate per block
     */
    function updateRewardRate(uint256 newRate) external;

    /**
     * @notice Updates staking duration parameters (governance only)
     * @param newMinDuration The new minimum staking duration
     * @param newMaxDuration The new maximum staking duration
     */
    function updateStakingDurations(uint256 newMinDuration, uint256 newMaxDuration) external;

    /**
     * @notice Updates cognitive multipliers (governance only)
     * @param shortTerm Multiplier for short-term staking (< 1 month)
     * @param mediumTerm Multiplier for medium-term staking (1-6 months)
     * @param longTerm Multiplier for long-term staking (> 6 months)
     */
    function updateCognitiveMultipliers(
        uint256 shortTerm,
        uint256 mediumTerm,
        uint256 longTerm
    ) external;

    /**
     * @notice Updates minimum stake amount (governance only)
     * @param newMinStake The new minimum stake amount
     */
    function updateMinStake(uint256 newMinStake) external;

    // ============ Emergency Functions ============
    
    /**
     * @notice Emergency withdraw for users during contract upgrades
     * @param stakeId The stake ID to emergency withdraw
     */
    function emergencyWithdraw(uint256 stakeId) external;

    /**
     * @notice Pauses staking in emergency situations (governance only)
     */
    function pauseStaking() external;

    /**
     * @notice Unpauses staking (governance only)
     */
    function unpauseStaking() external;

    /**
     * @notice Checks if staking is currently paused
     * @return True if staking is paused
     */
    function stakingPaused() external view returns (bool);

    // ============ Integration Hooks ============
    
    /**
     * @notice Hook called when a dream is recorded by a staker
     * @dev Provides bonus rewards for active stakers
     * @param staker The address that recorded the dream
     * @param dreamHash The hash of the dream content
     */
    function onDreamRecorded(address staker, bytes32 dreamHash) external;

    /**
     * @notice Gets the bonus multiplier for dream recording based on staking
     * @param staker The address of the dream recorder
     * @return The bonus multiplier (in basis points)
     */
    function getDreamBonusMultiplier(address staker) external view returns (uint256);

    // ============ Constants ============
    
    /**
     * @notice The precision factor for calculations
     * @return The precision factor (1e18)
     */
    function PRECISION() external pure returns (uint256);

    /**
     * @notice The maximum cognitive multiplier possible
     * @return The maximum multiplier (in basis points)
     */
    function MAX_MULTIPLIER() external pure returns (uint256);

    /**
     * @notice The base multiplier (no bonus)
     * @return The base multiplier (10000 basis points = 1x)
     */
    function BASE_MULTIPLIER() external pure returns (uint256);
}