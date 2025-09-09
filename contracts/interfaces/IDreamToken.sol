// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title IDreamToken
 * @dev Interface for the DREAM token with enhanced dream ecosystem functionality
 * @notice This interface extends ERC20 with dream-specific features and governance hooks
 */
interface IDreamToken is IERC20 {
    // ============ Events ============
    
    /**
     * @notice Emitted when a dream is recorded and tokens are distributed
     * @param dreamer The address that recorded the dream
     * @param dreamHash The hash of the dream content
     * @param rewardAmount The amount of DREAM tokens rewarded
     * @param burnAmount The amount of DREAM tokens burned for recording
     */
    event DreamRewardDistributed(
        address indexed dreamer,
        bytes32 indexed dreamHash,
        uint256 rewardAmount,
        uint256 burnAmount
    );

    /**
     * @notice Emitted when mining parameters are updated via governance
     * @param newMiningRate The new dream mining reward rate
     * @param newBurnRate The new dream recording burn rate
     * @param effectiveBlock The block number when changes take effect
     */
    event MiningParametersUpdated(
        uint256 newMiningRate,
        uint256 newBurnRate,
        uint256 effectiveBlock
    );

    /**
     * @notice Emitted when staking parameters are updated
     * @param newMinStake The new minimum stake amount for cognitive staking
     * @param newMaxStake The new maximum stake amount
     * @param newStakingRewardRate The new staking reward rate
     */
    event StakingParametersUpdated(
        uint256 newMinStake,
        uint256 newMaxStake,
        uint256 newStakingRewardRate
    );

    // ============ Dream Mining Functions ============
    
    /**
     * @notice Records a dream and handles token economics
     * @dev Called by authorized dream recording contracts
     * @param dreamer The address recording the dream
     * @param dreamHash The hash of the dream content
     * @return rewardAmount The amount of DREAM tokens rewarded
     */
    function recordDreamReward(address dreamer, bytes32 dreamHash)
        external
        returns (uint256 rewardAmount);

    /**
     * @notice Gets the current dream mining reward rate
     * @return The current reward rate in DREAM tokens per dream
     */
    function getCurrentMiningRate() external view returns (uint256);

    /**
     * @notice Gets the current dream recording burn rate
     * @return The current burn rate in DREAM tokens per dream recorded
     */
    function getCurrentBurnRate() external view returns (uint256);

    // ============ Cognitive Staking Functions ============
    
    /**
     * @notice Stakes DREAM tokens for cognitive mining rewards
     * @param amount The amount of DREAM tokens to stake
     * @param duration The staking duration in blocks
     */
    function stakeDream(uint256 amount, uint256 duration) external;

    /**
     * @notice Unstakes DREAM tokens and claims rewards
     * @param stakeId The ID of the stake to unstake
     */
    function unstakeDream(uint256 stakeId) external;

    /**
     * @notice Claims cognitive staking rewards without unstaking
     * @param stakeId The ID of the stake to claim rewards for
     */
    function claimStakingRewards(uint256 stakeId) external;

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
        returns (
            uint256 totalStaked,
            uint256 activeStakes,
            uint256 pendingRewards
        );

    // ============ Governance Interface ============
    
    /**
     * @notice Updates mining parameters (governance only)
     * @param newMiningRate The new mining reward rate
     * @param newBurnRate The new burn rate for dream recording
     */
    function updateMiningParameters(uint256 newMiningRate, uint256 newBurnRate)
        external;

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
    ) external;

    // ============ Extension Hooks ============
    
    /**
     * @notice Hook for future adaptive logic extensions
     * @dev Reserved for future upgrades and extensions
     * @param functionId The ID of the function being called
     * @param data Encoded function parameters
     * @return result The result of the extension function
     */
    function extensionHook(bytes4 functionId, bytes calldata data)
        external
        returns (bytes memory result);

    // ============ View Functions ============
    
    /**
     * @notice Gets the total supply cap of DREAM tokens
     * @return The maximum total supply (777,777,777 tokens)
     */
    function totalSupplyCap() external pure returns (uint256);

    /**
     * @notice Checks if an address is authorized for dream recording
     * @param recorder The address to check
     * @return True if authorized for dream recording
     */
    function isAuthorizedRecorder(address recorder) external view returns (bool);
}