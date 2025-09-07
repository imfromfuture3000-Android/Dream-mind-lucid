// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./interfaces/IDreamOracle.sol";

/**
 * @title DreamEconomicEngine
 * @dev Economic modeling and incentive optimization for the Dream ecosystem
 */
contract DreamEconomicEngine is Ownable {
    // Network health metrics
    struct NetworkMetrics {
        uint256 activeAgents;      // Number of active AI agents
        uint256 dreamVolume24h;    // Dream processing volume in 24h
        uint256 avgGasPrice;       // Average gas price on SKALE
        uint256 tvl;               // Total value locked in USD
        uint256 liquidityDepth;    // Market depth in stable pairs
    }
    
    // Market conditions
    struct MarketConditions {
        uint256 dreamPrice;        // DREAM token price in USD
        uint256 smindPrice;        // SMIND token price in USD
        uint256 lucidPrice;        // LUCID token price in USD
        uint256 marketCap;         // Total market cap in USD
        uint256 volume24h;         // 24h trading volume
    }
    
    // Reward multipliers
    struct RewardMultipliers {
        uint256 networkHealth;     // Based on network metrics (0-200)
        uint256 marketStability;   // Based on price stability (0-200)
        uint256 utilityScore;      // Based on token utility (0-200)
        uint256 stakingRatio;      // Based on staking participation (0-200)
    }
    
    // Economic parameters
    struct EconomicParams {
        uint256 baseRewardRate;    // Base rate for rewards
        uint256 burnRateMin;       // Minimum burn rate (basis points)
        uint256 burnRateMax;       // Maximum burn rate (basis points)
        uint256 stakingWeight;     // Weight of staking in calculations
        uint256 performanceWeight; // Weight of performance metrics
    }
    
    // State variables
    NetworkMetrics public networkMetrics;
    MarketConditions public marketConditions;
    RewardMultipliers public rewardMultipliers;
    EconomicParams public economicParams;
    
    // Price feeds
    AggregatorV3Interface private dreamPriceFeed;
    AggregatorV3Interface private smindPriceFeed;
    AggregatorV3Interface private lucidPriceFeed;
    
    // Dream oracle interface
    IDreamOracle private dreamOracle;
    
    // Events
    event MultipliersUpdated(
        uint256 networkHealth,
        uint256 marketStability,
        uint256 utilityScore,
        uint256 stakingRatio
    );
    
    event EconomicParamsUpdated(
        uint256 baseRewardRate,
        uint256 burnRateMin,
        uint256 burnRateMax,
        uint256 stakingWeight,
        uint256 performanceWeight
    );
    
    constructor(
        address _dreamPriceFeed,
        address _smindPriceFeed,
        address _lucidPriceFeed,
        address _dreamOracle
    ) {
        dreamPriceFeed = AggregatorV3Interface(_dreamPriceFeed);
        smindPriceFeed = AggregatorV3Interface(_smindPriceFeed);
        lucidPriceFeed = AggregatorV3Interface(_lucidPriceFeed);
        dreamOracle = IDreamOracle(_dreamOracle);
        
        // Initialize economic parameters
        economicParams = EconomicParams({
            baseRewardRate: 1000,   // 10% base rate
            burnRateMin: 200,       // 2% minimum burn
            burnRateMax: 1000,      // 10% maximum burn
            stakingWeight: 4000,    // 40% weight for staking
            performanceWeight: 6000  // 60% weight for performance
        });
    }
    
    /**
     * @dev Update network metrics
     * @param metrics New network metrics
     */
    function updateNetworkMetrics(NetworkMetrics memory metrics) external onlyOwner {
        networkMetrics = metrics;
        _updateMultipliers();
    }
    
    /**
     * @dev Update market conditions using price feeds
     */
    function updateMarketConditions() external {
        // Get latest prices from Chainlink feeds
        (, int256 dreamPrice,,,) = dreamPriceFeed.latestRoundData();
        (, int256 smindPrice,,,) = smindPriceFeed.latestRoundData();
        (, int256 lucidPrice,,,) = lucidPriceFeed.latestRoundData();
        
        marketConditions.dreamPrice = uint256(dreamPrice);
        marketConditions.smindPrice = uint256(smindPrice);
        marketConditions.lucidPrice = uint256(lucidPrice);
        
        // Calculate market cap and volume (implement with actual token supplies)
        marketConditions.marketCap = calculateMarketCap();
        marketConditions.volume24h = get24hVolume();
        
        _updateMultipliers();
    }
    
    /**
     * @dev Calculate reward multiplier for an agent
     * @param performance Agent's performance scores
     * @param stakedAmount Amount of tokens staked
     * @return Multiplier as a percentage (100 = 1x, 200 = 2x, etc)
     */
    function calculateRewardMultiplier(
        uint256[3] memory performance,
        uint256 stakedAmount
    ) public view returns (uint256) {
        // Get base multiplier from network health
        uint256 multiplier = rewardMultipliers.networkHealth;
        
        // Adjust for market stability
        multiplier = (multiplier * rewardMultipliers.marketStability) / 100;
        
        // Factor in utility score
        multiplier = (multiplier * rewardMultipliers.utilityScore) / 100;
        
        // Consider staking ratio
        uint256 stakingMultiplier = calculateStakingMultiplier(stakedAmount);
        multiplier = (multiplier * stakingMultiplier) / 100;
        
        // Apply performance adjustment
        uint256 perfMultiplier = calculatePerformanceMultiplier(performance);
        multiplier = (multiplier * perfMultiplier) / 100;
        
        return multiplier;
    }
    
    /**
     * @dev Calculate optimal burn rate based on market conditions
     * @return Burn rate in basis points
     */
    function calculateOptimalBurnRate() public view returns (uint256) {
        // Start with base rate
        uint256 burnRate = economicParams.burnRateMin;
        
        // Adjust based on market cap trend
        int256 mcapTrend = getMarketCapTrend();
        if (mcapTrend < 0) {
            // Increase burn rate if market cap is declining
            burnRate += uint256(-mcapTrend) * 10;  // 0.1% increase per % decline
        }
        
        // Adjust based on volume
        uint256 volumeRatio = (marketConditions.volume24h * 10000) / marketConditions.marketCap;
        if (volumeRatio > 1000) {  // If 24h volume > 10% of mcap
            burnRate += volumeRatio / 100;  // Increase burn rate with volume
        }
        
        // Adjust based on network health
        uint256 healthScore = calculateNetworkHealth();
        if (healthScore < 7000) {  // If health score < 70%
            burnRate += (7000 - healthScore) / 100;  // Increase burn rate
        }
        
        // Cap at maximum
        return burnRate > economicParams.burnRateMax ? 
            economicParams.burnRateMax : burnRate;
    }
    
    /**
     * @dev Update economic parameters
     */
    function updateEconomicParams(EconomicParams memory params) external onlyOwner {
        require(
            params.burnRateMax >= params.burnRateMin,
            "Max burn rate must be >= min"
        );
        require(
            params.stakingWeight + params.performanceWeight == 10000,
            "Weights must sum to 100%"
        );
        
        economicParams = params;
        emit EconomicParamsUpdated(
            params.baseRewardRate,
            params.burnRateMin,
            params.burnRateMax,
            params.stakingWeight,
            params.performanceWeight
        );
    }
    
    // Internal functions
    
    function _updateMultipliers() internal {
        rewardMultipliers = RewardMultipliers({
            networkHealth: calculateNetworkHealth(),
            marketStability: calculateMarketStability(),
            utilityScore: calculateUtilityScore(),
            stakingRatio: calculateStakingRatio()
        });
        
        emit MultipliersUpdated(
            rewardMultipliers.networkHealth,
            rewardMultipliers.marketStability,
            rewardMultipliers.utilityScore,
            rewardMultipliers.stakingRatio
        );
    }
    
    function calculateNetworkHealth() internal view returns (uint256) {
        // Calculate health score based on:
        // - Active agents ratio
        // - Dream processing volume
        // - Gas price stability
        // - TVL growth
        // - Liquidity depth
        
        uint256 healthScore = 100;  // Base score
        
        // Adjust for active agents
        if (networkMetrics.activeAgents > 100) {
            healthScore += 20;  // Bonus for high participation
        }
        
        // Adjust for dream volume
        uint256 volumeScore = (networkMetrics.dreamVolume24h * 40) / 1000000;
        healthScore += volumeScore > 40 ? 40 : volumeScore;
        
        // Adjust for TVL
        uint256 tvlScore = (networkMetrics.tvl * 20) / 10000000;  // $10M = +20
        healthScore += tvlScore > 20 ? 20 : tvlScore;
        
        // Adjust for liquidity
        uint256 liqScore = (networkMetrics.liquidityDepth * 20) / 1000000;
        healthScore += liqScore > 20 ? 20 : liqScore;
        
        return healthScore;
    }
    
    function calculateMarketStability() internal view returns (uint256) {
        // Calculate stability score based on:
        // - Price volatility
        // - Volume consistency
        // - Market cap trend
        // - Liquidity ratios
        return 100;  // Placeholder
    }
    
    function calculateUtilityScore() internal view returns (uint256) {
        // Calculate utility score based on:
        // - Transaction volume
        // - Unique users
        // - Contract interactions
        // - Token velocity
        return 100;  // Placeholder
    }
    
    function calculateStakingRatio() internal view returns (uint256) {
        // Calculate staking participation score
        return 100;  // Placeholder
    }
    
    function calculateMarketCap() internal view returns (uint256) {
        // Calculate total market cap
        return 0;  // Placeholder
    }
    
    function get24hVolume() internal view returns (uint256) {
        // Get 24h trading volume
        return 0;  // Placeholder
    }
    
    function getMarketCapTrend() internal view returns (int256) {
        // Calculate market cap trend
        return 0;  // Placeholder
    }
    
    function calculateStakingMultiplier(uint256 stakedAmount) 
        internal view returns (uint256) 
    {
        // Calculate multiplier based on staking amount
        return 100;  // Placeholder
    }
    
    function calculatePerformanceMultiplier(uint256[3] memory performance)
        internal view returns (uint256)
    {
        // Calculate multiplier based on performance metrics
        uint256 avgPerformance = (
            performance[0] + performance[1] + performance[2]
        ) / 3;
        return (avgPerformance * 200) / 1000;  // Scale to 0-200%
    }
}
