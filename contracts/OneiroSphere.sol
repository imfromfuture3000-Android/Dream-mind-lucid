// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OneiroSphere
 * @dev Core quantum dream network contract for the Dream-Mind-Lucid ecosystem
 * Enables dream interfacing with IPFS storage and quantum-scale investment opportunities
 */
contract OneiroSphere {
    string public name = "OneiroSphere";
    string public version = "1.0.0";
    
    // Dream storage mapping: dreamer -> array of IPFS hashes
    mapping(address => string[]) public dreams;
    
    // Dream metadata
    mapping(string => DreamMetadata) public dreamMetadata;
    
    // Token economics for the quantum dream network
    uint256 public totalSupply = 333333333 * 10**18; // 333,333,333 LUCID tokens
    mapping(address => uint256) public balances;
    
    struct DreamMetadata {
        address dreamer;
        uint256 timestamp;
        uint256 lucidityScore;
        bool isQuantumEntangled;
    }
    
    // Events
    event DreamInterfaced(address indexed dreamer, string ipfsHash);
    event QuantumEntanglement(address indexed dreamer1, address indexed dreamer2, string sharedHash);
    event LucidityScored(string indexed ipfsHash, uint256 score);
    
    // Modifiers
    modifier onlyWithBalance() {
        require(balances[msg.sender] > 0, "Insufficient LUCID tokens");
        _;
    }
    
    constructor() {
        balances[msg.sender] = totalSupply; // Creator gets all LUCID tokens initially
    }
    
    /**
     * @dev Interface a dream with the quantum network via IPFS hash
     * @param ipfsHash The IPFS hash of the dream content
     */
    function interfaceDream(string memory ipfsHash) public onlyWithBalance {
        require(bytes(ipfsHash).length > 0, "Invalid IPFS hash");
        
        dreams[msg.sender].push(ipfsHash);
        
        dreamMetadata[ipfsHash] = DreamMetadata({
            dreamer: msg.sender,
            timestamp: block.timestamp,
            lucidityScore: 0, // To be scored later by oracles
            isQuantumEntangled: false
        });
        
        emit DreamInterfaced(msg.sender, ipfsHash);
    }
    
    /**
     * @dev Create quantum entanglement between two dreams
     * @param dreamer2 Address of the second dreamer
     * @param sharedHash IPFS hash of the entangled dream experience
     */
    function createQuantumEntanglement(address dreamer2, string memory sharedHash) public onlyWithBalance {
        require(dreamer2 != msg.sender, "Cannot entangle with yourself");
        require(balances[dreamer2] > 0, "Dreamer2 must have LUCID tokens");
        
        dreams[msg.sender].push(sharedHash);
        dreams[dreamer2].push(sharedHash);
        
        dreamMetadata[sharedHash].isQuantumEntangled = true;
        
        emit QuantumEntanglement(msg.sender, dreamer2, sharedHash);
    }
    
    /**
     * @dev Score the lucidity of a dream (oracle function)
     * @param ipfsHash The IPFS hash of the dream
     * @param score Lucidity score (0-100)
     */
    function scoreLucidity(string memory ipfsHash, uint256 score) public {
        require(score <= 100, "Score must be between 0-100");
        require(dreamMetadata[ipfsHash].dreamer != address(0), "Dream does not exist");
        
        dreamMetadata[ipfsHash].lucidityScore = score;
        
        // Reward high lucidity with LUCID tokens
        if (score >= 80) {
            address dreamer = dreamMetadata[ipfsHash].dreamer;
            balances[dreamer] += 100 * 10**18; // 100 LUCID reward
        }
        
        emit LucidityScored(ipfsHash, score);
    }
    
    /**
     * @dev Get all dreams for a specific dreamer
     * @param dreamer Address of the dreamer
     * @return Array of IPFS hashes
     */
    function getDreams(address dreamer) public view returns (string[] memory) {
        return dreams[dreamer];
    }
    
    /**
     * @dev Get dream count for a dreamer
     * @param dreamer Address of the dreamer
     * @return Number of dreams
     */
    function getDreamCount(address dreamer) public view returns (uint256) {
        return dreams[dreamer].length;
    }
    
    /**
     * @dev Check LUCID token balance
     * @param account Address to check
     * @return Token balance
     */
    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }
    
    /**
     * @dev Transfer LUCID tokens (simple implementation)
     * @param to Recipient address
     * @param amount Amount to transfer
     */
    function transfer(address to, uint256 amount) public returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(to != address(0), "Cannot transfer to zero address");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        return true;
    }
}