// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OneiroSphere - The Quantum Dream Network
 * @dev Core smart contract for The Oneiro-Sphere ecosystem
 * Handles dream interfacing with IPFS storage and quantum dream validation
 */
contract OneiroSphere {
    // State variables
    mapping(address => string[]) public dreams;
    mapping(address => uint256) public dreamCount;
    
    // Events
    event DreamInterfaced(address indexed dreamer, string ipfsHash);
    event QuantumDreamValidated(address indexed dreamer, string ipfsHash, uint256 timestamp);
    
    // Trusted forwarder for Biconomy gasless transactions
    address private _trustedForwarder;
    
    constructor(address trustedForwarder) {
        _trustedForwarder = trustedForwarder;
    }
    
    /**
     * @dev Interface a dream with the quantum network
     * @param ipfsHash The IPFS hash of the dream content
     */
    function interfaceDream(string memory ipfsHash) public {
        require(bytes(ipfsHash).length > 0, "IPFS hash cannot be empty");
        
        address dreamer = _msgSender();
        dreams[dreamer].push(ipfsHash);
        dreamCount[dreamer]++;
        
        emit DreamInterfaced(dreamer, ipfsHash);
        emit QuantumDreamValidated(dreamer, ipfsHash, block.timestamp);
    }
    
    /**
     * @dev Get all dreams for a specific dreamer
     * @param dreamer The address of the dreamer
     * @return Array of IPFS hashes
     */
    function getDreams(address dreamer) public view returns (string[] memory) {
        return dreams[dreamer];
    }
    
    /**
     * @dev Get the total number of dreams for a dreamer
     * @param dreamer The address of the dreamer
     * @return The total dream count
     */
    function getDreamCount(address dreamer) public view returns (uint256) {
        return dreamCount[dreamer];
    }
    
    /**
     * @dev Get the latest dream for a dreamer
     * @param dreamer The address of the dreamer
     * @return The IPFS hash of the latest dream
     */
    function getLatestDream(address dreamer) public view returns (string memory) {
        require(dreamCount[dreamer] > 0, "No dreams found for this dreamer");
        return dreams[dreamer][dreamCount[dreamer] - 1];
    }
    
    /**
     * @dev Support for meta-transactions via Biconomy
     */
    function isTrustedForwarder(address forwarder) public view returns (bool) {
        return forwarder == _trustedForwarder;
    }
    
    function _msgSender() internal view returns (address sender) {
        if (isTrustedForwarder(msg.sender)) {
            // The assembly code is more gas efficient
            assembly {
                sender := shr(96, calldataload(sub(calldatasize(), 20)))
            }
        } else {
            sender = msg.sender;
        }
    }
    
    function _msgData() internal view returns (bytes calldata) {
        if (isTrustedForwarder(msg.sender)) {
            return msg.data[:msg.data.length - 20];
        } else {
            return msg.data;
        }
    }
}