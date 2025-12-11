// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title DreamBridge
 * @dev Cross-chain bridge for Dream-Mind-Lucid tokens between Solana and SKALE
 * Enables wrapped DREAM, SMIND, and LUCID tokens on SKALE with zero-gas operations
 */
contract DreamBridge is ERC20, Ownable, ReentrancyGuard {
    
    // Token supply constants matching Solana program
    uint256 public constant DREAM_TOTAL_SUPPLY = 777_777_777 * 10**18;
    uint256 public constant SMIND_TOTAL_SUPPLY = 777_777_777 * 10**18;
    uint256 public constant LUCID_TOTAL_SUPPLY = 333_333_333 * 10**18;
    
    // Bridge state
    mapping(address => bool) public authorizedRelayers;
    mapping(bytes32 => bool) public processedTransactions;
    mapping(address => uint256) public bridgedBalances;
    
    // Events for cross-chain communication
    event TokensBridgedToSolana(address indexed user, uint256 amount, string solanaAddress);
    event TokensBridgedFromSolana(address indexed user, uint256 amount, bytes32 indexed txHash);
    event RelayerAuthorized(address indexed relayer);
    event RelayerDeauthorized(address indexed relayer);
    
    // Errors
    error UnauthorizedRelayer();
    error TransactionAlreadyProcessed();
    error InsufficientBalance();
    error InvalidAmount();
    
    constructor(
        string memory name,
        string memory symbol,
        address initialOwner
    ) ERC20(name, symbol) Ownable(initialOwner) {
        // Initialize with partial supply for bridging
        _mint(initialOwner, DREAM_TOTAL_SUPPLY / 10); // 10% available initially
    }
    
    modifier onlyAuthorizedRelayer() {
        if (!authorizedRelayers[msg.sender]) revert UnauthorizedRelayer();
        _;
    }
    
    /**
     * @dev Bridge tokens from SKALE to Solana
     * Burns tokens on SKALE and emits event for relayer
     */
    function bridgeToSolana(uint256 amount, string calldata solanaAddress) 
        external 
        nonReentrant 
    {
        if (amount == 0) revert InvalidAmount();
        if (balanceOf(msg.sender) < amount) revert InsufficientBalance();
        
        // Burn tokens on SKALE
        _burn(msg.sender, amount);
        
        // Update bridged balance tracking
        bridgedBalances[msg.sender] += amount;
        
        emit TokensBridgedToSolana(msg.sender, amount, solanaAddress);
    }
    
    /**
     * @dev Bridge tokens from Solana to SKALE
     * Called by authorized relayers with Solana transaction proof
     */
    function bridgeFromSolana(
        address user,
        uint256 amount,
        bytes32 solanaTxHash
    ) external onlyAuthorizedRelayer nonReentrant {
        if (processedTransactions[solanaTxHash]) revert TransactionAlreadyProcessed();
        if (amount == 0) revert InvalidAmount();
        
        // Mark transaction as processed
        processedTransactions[solanaTxHash] = true;
        
        // Mint tokens on SKALE
        _mint(user, amount);
        
        emit TokensBridgedFromSolana(user, amount, solanaTxHash);
    }
    
    /**
     * @dev Authorize a relayer for cross-chain operations
     */
    function authorizeRelayer(address relayer) external onlyOwner {
        authorizedRelayers[relayer] = true;
        emit RelayerAuthorized(relayer);
    }
    
    /**
     * @dev Deauthorize a relayer
     */
    function deauthorizeRelayer(address relayer) external onlyOwner {
        authorizedRelayers[relayer] = false;
        emit RelayerDeauthorized(relayer);
    }
    
    /**
     * @dev Emergency mint function for bridge liquidity
     */
    function emergencyMint(address to, uint256 amount) external onlyOwner {
        require(totalSupply() + amount <= DREAM_TOTAL_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }
    
    /**
     * @dev Get bridge statistics
     */
    function getBridgeStats() external view returns (
        uint256 totalBridged,
        uint256 totalSupplyOnSkale,
        uint256 availableLiquidity
    ) {
        totalSupplyOnSkale = totalSupply();
        availableLiquidity = DREAM_TOTAL_SUPPLY - totalSupplyOnSkale;
        
        // Calculate total bridged amount (simplified)
        totalBridged = totalSupplyOnSkale;
    }
}