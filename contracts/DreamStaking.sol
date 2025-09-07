// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "./DreamEconomicEngine.sol";

/**
 * @title DreamStaking
 * @dev Manages staking for DREAM, SMIND, and LUCID tokens with dynamic rewards
 */
contract DreamStaking is Ownable, ReentrancyGuard, Pausable {
    // Staking pool information
    struct Pool {
        IERC20 token;           // Staked token
        uint256 totalStaked;    // Total tokens staked
        uint256 rewardRate;     // Rewards per second
        uint256 lastUpdateTime; // Last reward update timestamp
        uint256 rewardPerToken; // Accumulated rewards per token
        uint256 minLockTime;    // Minimum lock period
        uint256 maxLockTime;    // Maximum lock period
        uint256 baseMultiplier; // Base reward multiplier (10000 = 1x)
    }
    
    // Staker information
    struct Staker {
        uint256 stakedAmount;   // Amount of tokens staked
        uint256 lockEndTime;    // When tokens can be withdrawn
        uint256 rewardDebt;     // Reward debt for accurate reward calculation
        uint256 pendingRewards; // Unclaimed rewards
        uint256 lastStakeTime;  // Timestamp of last stake
        uint256 multiplier;     // Current reward multiplier
    }
    
    // Mapping of token address to pool info
    mapping(address => Pool) public pools;
    
    // Mapping of token to staker to staker info
    mapping(address => mapping(address => Staker)) public stakers;
    
    // List of supported tokens
    address[] public supportedTokens;
    
    // Economic engine for dynamic calculations
    DreamEconomicEngine public economicEngine;
    
    // Constants
    uint256 public constant MULTIPLIER_DENOMINATOR = 10000;
    uint256 public constant MAX_LOCK_BONUS = 5000;    // 50% max bonus for locking
    uint256 public constant MIN_STAKE_AMOUNT = 1000;  // Minimum stake amount
    
    // Events
    event Staked(address indexed user, address indexed token, uint256 amount, uint256 lockTime);
    event Unstaked(address indexed user, address indexed token, uint256 amount);
    event RewardClaimed(address indexed user, address indexed token, uint256 amount);
    event PoolUpdated(address indexed token, uint256 rewardRate, uint256 totalStaked);
    event MultiplierUpdated(address indexed user, address indexed token, uint256 multiplier);
    
    constructor(
        address _dreamToken,
        address _smindToken,
        address _lucidToken,
        address _economicEngine
    ) {
        economicEngine = DreamEconomicEngine(_economicEngine);
        
        // Initialize pools
        _initializePool(_dreamToken, 7 days, 365 days, 10000); // 1x base multiplier
        _initializePool(_smindToken, 14 days, 730 days, 12000); // 1.2x base multiplier
        _initializePool(_lucidToken, 30 days, 1460 days, 15000); // 1.5x base multiplier
    }
    
    /**
     * @dev Initialize a new staking pool
     */
    function _initializePool(
        address tokenAddress,
        uint256 minLock,
        uint256 maxLock,
        uint256 baseMultiplier
    ) internal {
        require(tokenAddress != address(0), "Invalid token");
        
        Pool storage pool = pools[tokenAddress];
        pool.token = IERC20(tokenAddress);
        pool.minLockTime = minLock;
        pool.maxLockTime = maxLock;
        pool.baseMultiplier = baseMultiplier;
        pool.lastUpdateTime = block.timestamp;
        
        supportedTokens.push(tokenAddress);
    }
    
    /**
     * @dev Stake tokens with optional lock period
     */
    function stake(
        address token,
        uint256 amount,
        uint256 lockTime
    ) external nonReentrant whenNotPaused {
        require(amount >= MIN_STAKE_AMOUNT, "Below minimum stake");
        Pool storage pool = pools[token];
        require(address(pool.token) != address(0), "Token not supported");
        require(
            lockTime >= pool.minLockTime && lockTime <= pool.maxLockTime,
            "Invalid lock time"
        );
        
        // Update rewards first
        _updateRewards(token, msg.sender);
        
        // Transfer tokens to contract
        pool.token.transferFrom(msg.sender, address(this), amount);
        
        // Update staker info
        Staker storage staker = stakers[token][msg.sender];
        staker.stakedAmount += amount;
        staker.lockEndTime = block.timestamp + lockTime;
        staker.lastStakeTime = block.timestamp;
        
        // Update pool
        pool.totalStaked += amount;
        
        // Calculate new multiplier
        _updateMultiplier(token, msg.sender);
        
        emit Staked(msg.sender, token, amount, lockTime);
        emit PoolUpdated(token, pool.rewardRate, pool.totalStaked);
    }
    
    /**
     * @dev Unstake tokens if lock period has ended
     */
    function unstake(address token, uint256 amount) external nonReentrant {
        Pool storage pool = pools[token];
        Staker storage staker = stakers[token][msg.sender];
        
        require(staker.stakedAmount >= amount, "Insufficient stake");
        require(block.timestamp >= staker.lockEndTime, "Still locked");
        
        // Update rewards first
        _updateRewards(token, msg.sender);
        
        // Update staker info
        staker.stakedAmount -= amount;
        pool.totalStaked -= amount;
        
        // Transfer tokens back to user
        pool.token.transfer(msg.sender, amount);
        
        // Update multiplier
        _updateMultiplier(token, msg.sender);
        
        emit Unstaked(msg.sender, token, amount);
        emit PoolUpdated(token, pool.rewardRate, pool.totalStaked);
    }
    
    /**
     * @dev Claim pending rewards
     */
    function claimRewards(address token) external nonReentrant {
        _updateRewards(token, msg.sender);
        Staker storage staker = stakers[token][msg.sender];
        
        uint256 rewards = staker.pendingRewards;
        require(rewards > 0, "No rewards");
        
        staker.pendingRewards = 0;
        Pool storage pool = pools[token];
        pool.token.transfer(msg.sender, rewards);
        
        emit RewardClaimed(msg.sender, token, rewards);
    }
    
    /**
     * @dev Get pending rewards for a user
     */
    function getPendingRewards(
        address token,
        address user
    ) public view returns (uint256) {
        Pool storage pool = pools[token];
        Staker storage staker = stakers[token][user];
        
        if (staker.stakedAmount == 0) {
            return staker.pendingRewards;
        }
        
        uint256 timeElapsed = block.timestamp - pool.lastUpdateTime;
        uint256 newRewards = timeElapsed * pool.rewardRate * staker.multiplier / MULTIPLIER_DENOMINATOR;
        
        return staker.pendingRewards + newRewards;
    }
    
    /**
     * @dev Update rewards for a user
     */
    function _updateRewards(address token, address user) internal {
        Pool storage pool = pools[token];
        Staker storage staker = stakers[token][user];
        
        pool.rewardPerToken += (
            (block.timestamp - pool.lastUpdateTime) *
            pool.rewardRate *
            1e18 /
            pool.totalStaked
        );
        
        staker.pendingRewards += (
            staker.stakedAmount *
            (pool.rewardPerToken - staker.rewardDebt) /
            1e18 *
            staker.multiplier /
            MULTIPLIER_DENOMINATOR
        );
        
        staker.rewardDebt = pool.rewardPerToken;
        pool.lastUpdateTime = block.timestamp;
    }
    
    /**
     * @dev Update staker's reward multiplier
     */
    function _updateMultiplier(address token, address user) internal {
        Staker storage staker = stakers[token][user];
        Pool storage pool = pools[token];
        
        // Base multiplier from pool
        uint256 multiplier = pool.baseMultiplier;
        
        // Lock time bonus (linear increase up to MAX_LOCK_BONUS)
        uint256 remainingLock = 0;
        if (block.timestamp < staker.lockEndTime) {
            remainingLock = staker.lockEndTime - block.timestamp;
        }
        uint256 lockBonus = (remainingLock * MAX_LOCK_BONUS) / pool.maxLockTime;
        multiplier += lockBonus;
        
        // Amount bonus from economic engine
        uint256 amountMultiplier = economicEngine.calculateStakingMultiplier(
            staker.stakedAmount
        );
        multiplier = (multiplier * amountMultiplier) / MULTIPLIER_DENOMINATOR;
        
        staker.multiplier = multiplier;
        emit MultiplierUpdated(user, token, multiplier);
    }
    
    /**
     * @dev Update pool reward rate
     */
    function updateRewardRate(
        address token,
        uint256 newRate
    ) external onlyOwner {
        Pool storage pool = pools[token];
        require(address(pool.token) != address(0), "Token not supported");
        
        _updateRewards(token, msg.sender);
        pool.rewardRate = newRate;
        
        emit PoolUpdated(token, newRate, pool.totalStaked);
    }
    
    /**
     * @dev Get total staked amount for a token
     */
    function getTotalStaked(address token) external view returns (uint256) {
        return pools[token].totalStaked;
    }
    
    /**
     * @dev Get user's staking info
     */
    function getStakingInfo(
        address token,
        address user
    ) external view returns (
        uint256 stakedAmount,
        uint256 lockEndTime,
        uint256 pendingRewards,
        uint256 multiplier
    ) {
        Staker storage staker = stakers[token][user];
        return (
            staker.stakedAmount,
            staker.lockEndTime,
            getPendingRewards(token, user),
            staker.multiplier
        );
    }
    
    // Emergency functions
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function setEconomicEngine(address _engine) external onlyOwner {
        economicEngine = DreamEconomicEngine(_engine);
    }
}
