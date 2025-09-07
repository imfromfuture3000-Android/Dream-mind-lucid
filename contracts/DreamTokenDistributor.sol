// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title DreamTokenDistributor
 * @dev Handles initial token distribution for DREAM, SMIND, and LUCID tokens
 */
contract DreamTokenDistributor is Ownable, ReentrancyGuard {
    // Token addresses
    IERC20 public dreamToken;
    IERC20 public smindToken;
    IERC20 public lucidToken;

    // Distribution pools (in basis points, 100% = 10000)
    struct DistributionPool {
        uint16 treasuryShare;     // Treasury allocation
        uint16 communityShare;    // Community rewards
        uint16 developmentShare;  // Development fund
        uint16 reserveShare;      // Strategic reserve
        uint16 agentShare;        // AI agent operations
    }

    mapping(address => DistributionPool) public tokenPools;
    
    // Vesting periods in seconds
    uint256 public constant TREASURY_VESTING = 365 days;
    uint256 public constant DEVELOPMENT_VESTING = 730 days;
    uint256 public constant AGENT_VESTING = 180 days;

    // Vesting tracking
    mapping(address => mapping(address => uint256)) public vestedAmount;
    mapping(address => mapping(address => uint256)) public lastClaimTime;
    mapping(address => mapping(address => uint256)) public startTime;

    // Events
    event PoolConfigured(address token, DistributionPool pool);
    event TokensClaimed(address token, address beneficiary, uint256 amount);
    event VestingStarted(address token, address beneficiary, uint256 amount);

    constructor(
        address _dreamToken,
        address _smindToken,
        address _lucidToken
    ) {
        dreamToken = IERC20(_dreamToken);
        smindToken = IERC20(_smindToken);
        lucidToken = IERC20(_lucidToken);

        // Configure DREAM token distribution (77.7777777% total)
        tokenPools[_dreamToken] = DistributionPool({
            treasuryShare: 2000,    // 20% - Long-term treasury
            communityShare: 3000,    // 30% - Community incentives
            developmentShare: 1000,  // 10% - Development funding
            reserveShare: 777,       // 7.77% - Strategic reserve
            agentShare: 1000         // 10% - AI agent operations
        });

        // Configure SMIND token distribution (77.7777777% total)
        tokenPools[_smindToken] = DistributionPool({
            treasuryShare: 1500,    // 15% - Long-term treasury
            communityShare: 3500,    // 35% - Community incentives
            developmentShare: 1000,  // 10% - Development funding
            reserveShare: 777,       // 7.77% - Strategic reserve
            agentShare: 1000         // 10% - AI agent operations
        });

        // Configure LUCID token distribution (33.3333333% total)
        tokenPools[_lucidToken] = DistributionPool({
            treasuryShare: 1000,    // 10% - Long-term treasury
            communityShare: 1333,    // 13.33% - Community incentives
            developmentShare: 500,   // 5% - Development funding
            reserveShare: 333,       // 3.33% - Strategic reserve
            agentShare: 167          // 1.67% - AI agent operations
        });
    }

    /**
     * @dev Starts vesting for a beneficiary
     * @param token Token address
     * @param beneficiary Beneficiary address
     * @param amount Amount to vest
     */
    function startVesting(
        address token,
        address beneficiary,
        uint256 amount
    ) external onlyOwner {
        require(
            token == address(dreamToken) ||
            token == address(smindToken) ||
            token == address(lucidToken),
            "Invalid token"
        );
        require(beneficiary != address(0), "Invalid beneficiary");
        require(amount > 0, "Invalid amount");

        vestedAmount[token][beneficiary] = amount;
        startTime[token][beneficiary] = block.timestamp;
        lastClaimTime[token][beneficiary] = block.timestamp;

        emit VestingStarted(token, beneficiary, amount);
    }

    /**
     * @dev Claims vested tokens
     * @param token Token address
     */
    function claimVestedTokens(address token) external nonReentrant {
        require(vestedAmount[token][msg.sender] > 0, "No vesting found");
        
        uint256 vestingPeriod;
        if (msg.sender == owner()) {
            vestingPeriod = TREASURY_VESTING;
        } else if (isDevAddress(msg.sender)) {
            vestingPeriod = DEVELOPMENT_VESTING;
        } else if (isAgentAddress(msg.sender)) {
            vestingPeriod = AGENT_VESTING;
        } else {
            revert("Invalid beneficiary");
        }

        uint256 vestedDuration = block.timestamp - lastClaimTime[token][msg.sender];
        uint256 totalDuration = block.timestamp - startTime[token][msg.sender];

        require(totalDuration <= vestingPeriod, "Vesting period exceeded");

        uint256 claimable = (vestedAmount[token][msg.sender] * vestedDuration) / vestingPeriod;
        require(claimable > 0, "Nothing to claim");

        lastClaimTime[token][msg.sender] = block.timestamp;
        
        IERC20(token).transfer(msg.sender, claimable);
        emit TokensClaimed(token, msg.sender, claimable);
    }

    /**
     * @dev Returns claimable amount for a beneficiary
     * @param token Token address
     * @param beneficiary Beneficiary address
     */
    function getClaimableAmount(
        address token,
        address beneficiary
    ) public view returns (uint256) {
        if (vestedAmount[token][beneficiary] == 0) return 0;

        uint256 vestingPeriod;
        if (beneficiary == owner()) {
            vestingPeriod = TREASURY_VESTING;
        } else if (isDevAddress(beneficiary)) {
            vestingPeriod = DEVELOPMENT_VESTING;
        } else if (isAgentAddress(beneficiary)) {
            vestingPeriod = AGENT_VESTING;
        } else {
            return 0;
        }

        uint256 vestedDuration = block.timestamp - lastClaimTime[token][beneficiary];
        uint256 totalDuration = block.timestamp - startTime[token][beneficiary];

        if (totalDuration > vestingPeriod) return 0;

        return (vestedAmount[token][beneficiary] * vestedDuration) / vestingPeriod;
    }

    // Internal helper functions
    function isDevAddress(address account) internal pure returns (bool) {
        // TODO: Implement development address validation
        return true;
    }

    function isAgentAddress(address account) internal pure returns (bool) {
        // TODO: Implement AI agent address validation
        return true;
    }
}
