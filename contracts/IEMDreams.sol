// SPDX-License-Identifier: MIT
// contracts/IEMDreams.sol - Dream-Mind-Lucid Investment Platform
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract IEMDreams is IERC20 {
    // Token metadata
    string public name = "DREAM Token";
    string public symbol = "DREAM";
    uint8 public decimals = 18;
    
    // Tokenomics
    uint256 private _totalSupply = 777777777 * 10**18; // 777,777,777 DREAM tokens
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    // Platform owner and treasury
    address public immutable owner;
    address public treasury;
    
    // Dream recording and rewards
    mapping(address => uint256) public dreamCount;
    mapping(address => string[]) public userDreams;
    mapping(bytes32 => bool) public dreamExists;
    
    // Staking and yield generation
    struct StakeInfo {
        uint256 amount;
        uint256 timestamp;
        uint256 rewardDebt;
    }
    mapping(address => StakeInfo) public stakes;
    uint256 public totalStaked;
    uint256 public rewardRate = 100; // 1% per day (100 basis points)
    uint256 constant REWARD_PRECISION = 10000;
    uint256 constant SECONDS_PER_DAY = 86400;
    
    // Events
    event DreamRecorded(address indexed dreamer, string dream, bytes32 indexed dreamHash, uint256 timestamp);
    event DreamReward(address indexed dreamer, uint256 amount);
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount, uint256 rewards);
    event RewardsClaimed(address indexed user, uint256 rewards);
    event TreasuryUpdated(address indexed oldTreasury, address indexed newTreasury);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = 0x4B1a58A3057d03888510d93B52ABad9Fee9b351d; // Owner address from requirements
        treasury = owner;
        _balances[owner] = _totalSupply;
        emit Transfer(address(0), owner, _totalSupply);
    }

    // ERC-20 Implementation
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function allowance(address owner_, address spender) public view override returns (uint256) {
        return _allowances[owner_][spender];
    }

    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from zero address");
        require(to != address(0), "ERC20: transfer to zero address");
        require(_balances[from] >= amount, "ERC20: transfer amount exceeds balance");

        _balances[from] -= amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _approve(address owner_, address spender, uint256 amount) internal {
        require(owner_ != address(0), "ERC20: approve from zero address");
        require(spender != address(0), "ERC20: approve to zero address");
        
        _allowances[owner_][spender] = amount;
        emit Approval(owner_, spender, amount);
    }

    // Dream Recording with Investment Rewards
    function recordDream(string memory dream) public {
        require(bytes(dream).length > 0, "Dream cannot be empty");
        require(bytes(dream).length <= 1000, "Dream too long");
        
        bytes32 dreamHash = keccak256(abi.encodePacked(dream, msg.sender, block.timestamp));
        require(!dreamExists[dreamHash], "Dream already recorded");
        
        dreamExists[dreamHash] = true;
        userDreams[msg.sender].push(dream);
        dreamCount[msg.sender]++;
        
        // Calculate reward based on dream quality factors
        uint256 reward = calculateDreamReward(dream);
        
        if (reward > 0) {
            _mint(msg.sender, reward);
            emit DreamReward(msg.sender, reward);
        }
        
        emit DreamRecorded(msg.sender, dream, dreamHash, block.timestamp);
    }

    function calculateDreamReward(string memory dream) internal pure returns (uint256) {
        uint256 length = bytes(dream).length;
        uint256 baseReward = 10 * 10**18; // 10 DREAM base reward
        
        // Bonus for longer, more detailed dreams
        if (length > 500) {
            baseReward += 5 * 10**18; // +5 DREAM for detailed dreams
        }
        if (length > 200) {
            baseReward += 3 * 10**18; // +3 DREAM for medium dreams
        }
        
        return baseReward;
    }

    // Staking for Yield Generation
    function stake(uint256 amount) public {
        require(amount > 0, "Cannot stake 0");
        require(_balances[msg.sender] >= amount, "Insufficient balance");
        
        // Claim any pending rewards first
        claimRewards();
        
        _transfer(msg.sender, address(this), amount);
        
        stakes[msg.sender].amount += amount;
        stakes[msg.sender].timestamp = block.timestamp;
        totalStaked += amount;
        
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) public {
        require(amount > 0, "Cannot unstake 0");
        require(stakes[msg.sender].amount >= amount, "Insufficient staked amount");
        
        uint256 rewards = calculateRewards(msg.sender);
        
        stakes[msg.sender].amount -= amount;
        totalStaked -= amount;
        
        _transfer(address(this), msg.sender, amount);
        
        if (rewards > 0) {
            _mint(msg.sender, rewards);
            emit RewardsClaimed(msg.sender, rewards);
        }
        
        stakes[msg.sender].timestamp = block.timestamp;
        stakes[msg.sender].rewardDebt = 0;
        
        emit Unstaked(msg.sender, amount, rewards);
    }

    function claimRewards() public {
        uint256 rewards = calculateRewards(msg.sender);
        require(rewards > 0, "No rewards to claim");
        
        _mint(msg.sender, rewards);
        stakes[msg.sender].timestamp = block.timestamp;
        stakes[msg.sender].rewardDebt = 0;
        
        emit RewardsClaimed(msg.sender, rewards);
    }

    function calculateRewards(address user) public view returns (uint256) {
        StakeInfo storage stake = stakes[user];
        if (stake.amount == 0) return 0;
        
        uint256 timeStaked = block.timestamp - stake.timestamp;
        uint256 dailyReward = (stake.amount * rewardRate) / REWARD_PRECISION;
        uint256 rewards = (dailyReward * timeStaked) / SECONDS_PER_DAY;
        
        return rewards;
    }

    // Investment and Treasury Management
    function _mint(address to, uint256 amount) internal {
        _totalSupply += amount;
        _balances[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    function setTreasury(address newTreasury) public onlyOwner {
        require(newTreasury != address(0), "Invalid treasury address");
        address oldTreasury = treasury;
        treasury = newTreasury;
        emit TreasuryUpdated(oldTreasury, newTreasury);
    }

    function setRewardRate(uint256 newRate) public onlyOwner {
        require(newRate <= 1000, "Rate too high"); // Max 10% per day
        rewardRate = newRate;
    }

    // View functions for investment tracking
    function getUserDreams(address user) public view returns (string[] memory) {
        return userDreams[user];
    }

    function getStakeInfo(address user) public view returns (uint256 amount, uint256 timestamp, uint256 pendingRewards) {
        StakeInfo storage stake = stakes[user];
        return (stake.amount, stake.timestamp, calculateRewards(user));
    }

    function getTotalValueLocked() public view returns (uint256) {
        return totalStaked;
    }

    // Emergency functions
    function emergencyWithdraw() public {
        uint256 stakedAmount = stakes[msg.sender].amount;
        require(stakedAmount > 0, "No staked amount");
        
        stakes[msg.sender].amount = 0;
        stakes[msg.sender].timestamp = block.timestamp;
        stakes[msg.sender].rewardDebt = 0;
        totalStaked -= stakedAmount;
        
        _transfer(address(this), msg.sender, stakedAmount);
        emit Unstaked(msg.sender, stakedAmount, 0);
    }
}
