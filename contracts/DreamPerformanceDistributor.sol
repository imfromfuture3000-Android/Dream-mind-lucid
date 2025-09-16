Integrate with price oracles for more accurate USD calculations
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title DreamPerformanceDistributor
 * @dev Handles performance-based distribution and burning of tokens
 */
contract DreamPerformanceDistributor is Ownable, ReentrancyGuard, Pausable {
    // Performance scoring
    struct AgentPerformance {
        uint256 dreamScore;      // Dream interpretation accuracy (0-1000)
        uint256 mindScore;       // Neural pattern analysis score (0-1000)
        uint256 lucidScore;      // Lucid gateway stability (0-1000)
        uint256 totalDreams;     // Total dreams processed
        uint256 successfulDreams; // Successfully processed dreams
        uint256 lastUpdateBlock; // Last performance update
        uint256 rewardPoints;    // Accumulated reward points
    }

    // Earnings distribution
    struct EarningsConfig {
        uint16 ownerShare;      // Owner's percentage of AI earnings (basis points)
        uint16 burnShare;       // Percentage to burn (basis points)
        uint16 rewardShare;     // Percentage for performance rewards (basis points)
        uint16 treasuryShare;   // Percentage for treasury (basis points)
    }

    // Token addresses
    IERC20 public dreamToken;
    IERC20 public smindToken;
    IERC20 public lucidToken;

    // Performance tracking
    mapping(address => AgentPerformance) public agentPerformance;
    mapping(address => bool) public registeredAgents;
    address[] public allAgents;

    // Earnings configuration
    EarningsConfig public earningsConfig;
    
    // Economic engine
    DreamEconomicEngine public economicEngine;
    
    // Minimum performance thresholds
    uint256 public constant MIN_PERFORMANCE_SCORE = 500; // out of 1000
    uint256 public constant REBALANCE_PERIOD = 7 days;
    uint256 public constant BURN_LOCK_PERIOD = 90 days;
    
    // Total burned amounts
    mapping(address => uint256) public totalBurned;
    
    // Performance oracle (for updating scores)
    address public performanceOracle;
    
    // Staking contract
    DreamStaking public stakingContract;
    
    // Events
    event PerformanceUpdated(address agent, uint256 dreamScore, uint256 mindScore, uint256 lucidScore);
    event TokensBurned(address token, uint256 amount);
    event RewardsDistributed(address agent, address token, uint256 amount);
    event OwnerEarningsClaimed(address token, uint256 amount);

    constructor(
        address _dreamToken,
        address _smindToken,
        address _lucidToken,
        address _economicEngine,
        address _stakingContract
    ) {
        dreamToken = IERC20(_dreamToken);
        smindToken = IERC20(_smindToken);
        lucidToken = IERC20(_lucidToken);

        // Configure earnings distribution (total 100%)
        earningsConfig = EarningsConfig({
            ownerShare: 1000,    // 10% to owner
            burnShare: 500,      // 5% burned
            rewardShare: 3500,   // 35% to performance rewards
            treasuryShare: 1000  // 10% to treasury
        });

        performanceOracle = msg.sender; // Initially set to owner
        economicEngine = DreamEconomicEngine(_economicEngine);
        stakingContract = DreamStaking(_stakingContract);
    }

    modifier onlyOracle() {
        require(msg.sender == performanceOracle, "Only oracle can call");
        _;
    }

    /**
     * @dev Register a new AI agent
     */
    function registerAgent(address agent) external onlyOwner {
        require(!registeredAgents[agent], "Agent already registered");
        registeredAgents[agent] = true;
        allAgents.push(agent);

        // Initialize performance metrics
        agentPerformance[agent] = AgentPerformance({
            dreamScore: 700,      // Initial neutral score
            mindScore: 700,
            lucidScore: 700,
            totalDreams: 0,
            successfulDreams: 0,
            lastUpdateBlock: block.number,
            rewardPoints: 0
        });
    }

    /**
     * @dev Update agent performance metrics
     */
    function updatePerformance(
        address agent,
        uint256 dreamScore,
        uint256 mindScore,
        uint256 lucidScore,
        uint256 successfulDreams,
        uint256 totalDreams
    ) external onlyOracle whenNotPaused {
        require(registeredAgents[agent], "Agent not registered");
        require(dreamScore <= 1000 && mindScore <= 1000 && lucidScore <= 1000, "Invalid score");

        AgentPerformance storage performance = agentPerformance[agent];
        
        // Update metrics
        performance.dreamScore = dreamScore;
        performance.mindScore = mindScore;
        performance.lucidScore = lucidScore;
        performance.totalDreams = totalDreams;
        performance.successfulDreams = successfulDreams;
        performance.lastUpdateBlock = block.number;

        // Calculate reward points
        uint256 avgScore = (dreamScore + mindScore + lucidScore) / 3;
        uint256 successRate = (successfulDreams * 1000) / totalDreams;
        
        // Get reward multiplier from economic engine
        uint256[3] memory scores = [dreamScore, mindScore, lucidScore];
        uint256 multiplier = economicEngine.calculateRewardMultiplier(
            scores,
            getAgentStakedAmount(agent)
        );
        
        // Apply multiplier to reward points
        performance.rewardPoints = (avgScore * successRate * multiplier) / 100000;

        emit PerformanceUpdated(agent, dreamScore, mindScore, lucidScore);
    }

    /**
     * @dev Distribute rewards based on performance
     */
    function distributeRewards(address token) external nonReentrant whenNotPaused {
        require(
            token == address(dreamToken) ||
            token == address(smindToken) ||
            token == address(lucidToken),
            "Invalid token"
        );

        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance > 0, "No tokens to distribute");

        // Get optimal burn rate from economic engine
        uint256 burnRate = economicEngine.calculateOptimalBurnRate();
        
        // Calculate shares with dynamic burn rate
        uint256 burnAmount = (balance * burnRate) / 10000;
        uint256 remainingBalance = balance - burnAmount;
        
        uint256 ownerAmount = (remainingBalance * earningsConfig.ownerShare) / 10000;
        uint256 rewardAmount = (remainingBalance * earningsConfig.rewardShare) / 10000;
        uint256 treasuryAmount = (remainingBalance * earningsConfig.treasuryShare) / 10000;

        // Distribute owner's share
        if (ownerAmount > 0) {
            IERC20(token).transfer(owner(), ownerAmount);
            emit OwnerEarningsClaimed(token, ownerAmount);
        }

        // Burn tokens
        if (burnAmount > 0) {
            burnTokens(token, burnAmount);
        }

        // Distribute performance rewards
        if (rewardAmount > 0) {
            distributePerformanceRewards(token, rewardAmount);
        }

        // Transfer to treasury
        if (treasuryAmount > 0) {
            address treasury = getTreasuryAddress();
            IERC20(token).transfer(treasury, treasuryAmount);
        }
    }

    /**
     * @dev Burn tokens based on configuration
     */
    function burnTokens(address token, uint256 amount) internal {
        // Burn by sending to dead address
        address burnAddress = address(0x000000000000000000000000000000000000dEaD);
        IERC20(token).transfer(burnAddress, amount);
        totalBurned[token] += amount;
        emit TokensBurned(token, amount);
    }

    /**
     * @dev Distribute rewards based on performance points
     */
    function distributePerformanceRewards(
        address token,
        uint256 totalReward
    ) internal {
        uint256 totalPoints = 0;
        
        // Calculate total points
        for (uint256 i = 0; i < allAgents.length; i++) {
            address agent = allAgents[i];
            if (agentPerformance[agent].rewardPoints >= MIN_PERFORMANCE_SCORE) {
                totalPoints += agentPerformance[agent].rewardPoints;
            }
        }

        require(totalPoints > 0, "No eligible agents");

        // Distribute rewards
        for (uint256 i = 0; i < allAgents.length; i++) {
            address agent = allAgents[i];
            if (agentPerformance[agent].rewardPoints >= MIN_PERFORMANCE_SCORE) {
                uint256 agentReward = (totalReward * agentPerformance[agent].rewardPoints) / totalPoints;
                if (agentReward > 0) {
                    IERC20(token).transfer(agent, agentReward);
                    emit RewardsDistributed(agent, token, agentReward);
                }
            }
        }
    }

    /**
     * @dev Force rebalancing of all agents
     */
    function forceRebalance() external onlyOwner {
        for (uint256 i = 0; i < allAgents.length; i++) {
            address agent = allAgents[i];
            AgentPerformance storage performance = agentPerformance[agent];
            
            // Decay scores if not updated recently
            if (block.timestamp - performance.lastUpdateBlock >= REBALANCE_PERIOD) {
                performance.dreamScore = performance.dreamScore * 95 / 100;
                performance.mindScore = performance.mindScore * 95 / 100;
                performance.lucidScore = performance.lucidScore * 95 / 100;
                performance.rewardPoints = performance.rewardPoints * 90 / 100;
            }
        }
    }

    // Admin functions
    function setPerformanceOracle(address _oracle) external onlyOwner {
        performanceOracle = _oracle;
    }

    function setEarningsConfig(
        uint16 _ownerShare,
        uint16 _burnShare,
        uint16 _rewardShare,
        uint16 _treasuryShare
    ) external onlyOwner {
        require(
            _ownerShare + _burnShare + _rewardShare + _treasuryShare == 10000,
            "Total must be 100%"
        );
        earningsConfig = EarningsConfig({
            ownerShare: _ownerShare,
            burnShare: _burnShare,
            rewardShare: _rewardShare,
            treasuryShare: _treasuryShare
        });
    }

    function getTreasuryAddress() public pure returns (address) {
        // TODO: Replace with actual treasury address
        return address(0x777D7e7777777777777777777777777De7777777);
    }
    
    /**
     * @dev Get the amount of tokens staked by an agent
     * This should be implemented to check actual staking contract
     */
    function getAgentStakedAmount(address agent) internal view returns (uint256) {
        // Get staking info for all token types
        (uint256 dreamStaked,,,) = stakingContract.getStakingInfo(address(dreamToken), agent);
        (uint256 smindStaked,,,) = stakingContract.getStakingInfo(address(smindToken), agent);
        (uint256 lucidStaked,,,) = stakingContract.getStakingInfo(address(lucidToken), agent);
        
        // Return total staked value
        return dreamStaked + smindStaked + lucidStaked;
    }
    
    /**
     * @dev Set staking contract address
     */
    function setStakingContract(address _stakingContract) external onlyOwner {
        stakingContract = DreamStaking(_stakingContract);
    }
    
    /**
     * @dev Update economic engine
     */
    function setEconomicEngine(address _engine) external onlyOwner {
        economicEngine = DreamEconomicEngine(_engine);
    }

    // Emergency functions
    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}
