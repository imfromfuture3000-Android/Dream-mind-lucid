// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title OneiroSphereV2
 * @dev Enhanced quantum dream network with MEV protection and yield farming
 * Integrates with Solana via bridge for cross-chain dream synchronization
 */
contract OneiroSphereV2 is Ownable, ReentrancyGuard {
    
    struct DreamRecord {
        address dreamer;
        string ipfsHash;
        uint256 timestamp;
        uint256 yieldGenerated;
        bool mevProtected;
        uint8 accessLevel;
    }
    
    struct YieldFarmInfo {
        uint256 totalStaked;
        uint256 rewardRate; // Rewards per second
        uint256 lastUpdateTime;
        uint256 rewardPerTokenStored;
    }
    
    // State variables
    mapping(address => DreamRecord[]) public userDreams;
    mapping(address => uint256) public stakedBalances;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;
    mapping(bytes32 => bool) public dreamHashes;
    
    YieldFarmInfo public yieldFarm;
    address public dreamToken; // Bridge token address
    
    uint256 public constant DREAM_REWARD_BASE = 10 ether; // 10 DREAM per dream
    uint256 public constant MEV_PROTECTION_BONUS = 2 ether; // 2 DREAM bonus for MEV protection
    
    // Events
    event DreamInterfaced(address indexed dreamer, string ipfsHash, uint256 yieldGenerated);
    event YieldClaimed(address indexed user, uint256 amount);
    event TokensStaked(address indexed user, uint256 amount);
    event TokensUnstaked(address indexed user, uint256 amount);
    event MEVProtectionEnabled(address indexed dreamer, bytes32 dreamHash);
    
    // Errors
    error DreamAlreadyExists();
    error InsufficientStake();
    error NoRewardsAvailable();
    error InvalidAccessLevel();
    
    constructor(address initialOwner, address _dreamToken) Ownable(initialOwner) {
        dreamToken = _dreamToken;
        yieldFarm.rewardRate = 1 ether; // 1 DREAM per second base rate
        yieldFarm.lastUpdateTime = block.timestamp;
    }
    
    modifier updateReward(address account) {
        yieldFarm.rewardPerTokenStored = rewardPerToken();
        yieldFarm.lastUpdateTime = block.timestamp;
        
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = yieldFarm.rewardPerTokenStored;
        }
        _;
    }
    
    /**
     * @dev Interface a dream with IPFS storage and yield generation
     */
    function interfaceDream(
        string calldata ipfsHash,
        bool enableMevProtection
    ) external nonReentrant updateReward(msg.sender) {
        bytes32 dreamHash = keccak256(abi.encodePacked(msg.sender, ipfsHash));
        
        if (dreamHashes[dreamHash]) revert DreamAlreadyExists();
        dreamHashes[dreamHash] = true;
        
        // Calculate yield based on staking and MEV protection
        uint256 yieldGenerated = calculateDreamYield(msg.sender, enableMevProtection);
        uint8 accessLevel = getAccessLevel(msg.sender);
        
        DreamRecord memory newDream = DreamRecord({
            dreamer: msg.sender,
            ipfsHash: ipfsHash,
            timestamp: block.timestamp,
            yieldGenerated: yieldGenerated,
            mevProtected: enableMevProtection,
            accessLevel: accessLevel
        });
        
        userDreams[msg.sender].push(newDream);
        
        // Add to rewards
        rewards[msg.sender] += yieldGenerated;
        
        if (enableMevProtection) {
            emit MEVProtectionEnabled(msg.sender, dreamHash);
        }
        
        emit DreamInterfaced(msg.sender, ipfsHash, yieldGenerated);
    }
    
    /**
     * @dev Stake DREAM tokens for enhanced yield
     */
    function stakeDreamTokens(uint256 amount) 
        external 
        nonReentrant 
        updateReward(msg.sender) 
    {
        require(amount > 0, "Cannot stake 0");
        
        // Transfer tokens from user (requires bridge token integration)
        // IERC20(dreamToken).transferFrom(msg.sender, address(this), amount);
        
        yieldFarm.totalStaked += amount;
        stakedBalances[msg.sender] += amount;
        
        emit TokensStaked(msg.sender, amount);
    }
    
    /**
     * @dev Unstake DREAM tokens
     */
    function unstakeDreamTokens(uint256 amount) 
        external 
        nonReentrant 
        updateReward(msg.sender) 
    {
        if (stakedBalances[msg.sender] < amount) revert InsufficientStake();
        
        yieldFarm.totalStaked -= amount;
        stakedBalances[msg.sender] -= amount;
        
        // Transfer tokens back to user
        // IERC20(dreamToken).transfer(msg.sender, amount);
        
        emit TokensUnstaked(msg.sender, amount);
    }
    
    /**
     * @dev Claim accumulated yield rewards
     */
    function claimYield() external nonReentrant updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        if (reward == 0) revert NoRewardsAvailable();
        
        rewards[msg.sender] = 0;
        
        // Mint or transfer reward tokens
        // IERC20(dreamToken).transfer(msg.sender, reward);
        
        emit YieldClaimed(msg.sender, reward);
    }
    
    /**
     * @dev Calculate dream yield based on user's stake and MEV protection
     */
    function calculateDreamYield(address user, bool mevProtected) 
        internal 
        view 
        returns (uint256) 
    {
        uint256 baseYield = DREAM_REWARD_BASE;
        
        // Bonus for staking
        if (stakedBalances[user] > 0) {
            uint256 stakingBonus = (stakedBalances[user] * 10) / 100; // 10% of stake as bonus
            baseYield += stakingBonus;
        }
        
        // MEV protection bonus
        if (mevProtected) {
            baseYield += MEV_PROTECTION_BONUS;
        }
        
        return baseYield;
    }
    
    /**
     * @dev Get user's access level based on stake
     */
    function getAccessLevel(address user) internal view returns (uint8) {
        uint256 stake = stakedBalances[user];
        
        if (stake >= 100 ether) return 4; // Quantum
        if (stake >= 10 ether) return 3;  // VIP
        if (stake >= 1 ether) return 2;   // Premium
        return 1; // Basic
    }
    
    /**
     * @dev Calculate reward per token
     */
    function rewardPerToken() public view returns (uint256) {
        if (yieldFarm.totalStaked == 0) {
            return yieldFarm.rewardPerTokenStored;
        }
        
        return yieldFarm.rewardPerTokenStored + 
            (((block.timestamp - yieldFarm.lastUpdateTime) * yieldFarm.rewardRate * 1e18) / yieldFarm.totalStaked);
    }
    
    /**
     * @dev Calculate earned rewards for a user
     */
    function earned(address account) public view returns (uint256) {
        return ((stakedBalances[account] * 
            (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18) + rewards[account];
    }
    
    /**
     * @dev Get user's dream count
     */
    function getUserDreamCount(address user) external view returns (uint256) {
        return userDreams[user].length;
    }
    
    /**
     * @dev Get user's total yield generated
     */
    function getUserTotalYield(address user) external view returns (uint256) {
        uint256 totalYield = 0;
        for (uint256 i = 0; i < userDreams[user].length; i++) {
            totalYield += userDreams[user][i].yieldGenerated;
        }
        return totalYield + earned(user);
    }
    
    /**
     * @dev Emergency functions for owner
     */
    function setRewardRate(uint256 newRate) external onlyOwner {
        yieldFarm.rewardRate = newRate;
    }
    
    function setDreamToken(address newToken) external onlyOwner {
        dreamToken = newToken;
    }
}