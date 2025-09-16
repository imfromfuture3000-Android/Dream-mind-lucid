// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title OneirobotNFT - Mint Gene Integration for Dream-Mind-Lucid
 * @author AI Gene Deployer - OneirobotNFT Syndicate
 * @notice Enhanced ERC-721 with SYNDICATE_MASTER_ROLE allowlist and pseudorandom attributes
 * @dev Mainnet-only deployment for SKALE Europa Hub with zero-gas operations
 */
contract OneirobotNFT is ERC721, ERC721URIStorage, AccessControl, ReentrancyGuard {
    using Counters for Counters.Counter;

    // ===================== STATE VARIABLES =====================
    bytes32 public constant SYNDICATE_MASTER_ROLE = keccak256("SYNDICATE_MASTER_ROLE");
    Counters.Counter private _tokenIdCounter;
    
    // Quantum Core attributes for pseudorandom generation
    mapping(uint256 => OneirobotAttributes) public tokenAttributes;
    mapping(address => bool) public syndicateMasters;
    
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public mintPrice = 0; // Zero-gas on SKALE
    
    // ===================== STRUCTS =====================
    struct OneirobotAttributes {
        string quantumCore;
        uint8 dreamLevel;
        uint8 lucidPower;
        uint8 mindStrength;
        string ipfsHash;
        uint256 mintTimestamp;
        uint256 randomSeed;
    }

    // ===================== EVENTS =====================
    event OneirobotMinted(
        address indexed to,
        uint256 indexed tokenId,
        string quantumCore,
        uint8 dreamLevel,
        uint8 lucidPower,
        uint8 mindStrength,
        string ipfsHash
    );
    
    event SyndicateMasterAdded(address indexed account);
    event SyndicateMasterRemoved(address indexed account);
    event AttributesGenerated(uint256 indexed tokenId, uint256 randomSeed);

    // ===================== CONSTRUCTOR =====================
    constructor() ERC721("OneirobotNFT", "ONEIROBOT") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SYNDICATE_MASTER_ROLE, msg.sender);
        syndicateMasters[msg.sender] = true;
        
        // Initialize with some syndicate masters
        address[] memory initialMasters = new address[](3);
        initialMasters[0] = 0x1234567890AbcdEF1234567890aBcdef12345678; // Example addresses
        initialMasters[1] = 0xaBcDeF1234567890aBcDeF1234567890AbCdEf12;
        initialMasters[2] = 0x9876543210FeDcBa9876543210fEdCbA98765432;
        
        for (uint256 i = 0; i < initialMasters.length; i++) {
            _grantRole(SYNDICATE_MASTER_ROLE, initialMasters[i]);
            syndicateMasters[initialMasters[i]] = true;
        }
    }

    // ===================== CORE MINTING FUNCTIONS =====================
    
    /**
     * @notice Mint Oneirobot NFT - Restricted to SYNDICATE_MASTER_ROLE
     * @dev Generates pseudorandom attributes using blockhash + nonce
     * @param to Address to mint NFT to
     * @param ipfsMetadataHash IPFS hash for metadata
     * @return tokenId The minted token ID
     */
    function mintOneirobot(address to, string memory ipfsMetadataHash) 
        public 
        onlyRole(SYNDICATE_MASTER_ROLE) 
        nonReentrant 
        returns (uint256) 
    {
        require(to != address(0), "OneirobotNFT: Cannot mint to zero address");
        require(_tokenIdCounter.current() < MAX_SUPPLY, "OneirobotNFT: Max supply reached");
        require(bytes(ipfsMetadataHash).length > 0, "OneirobotNFT: IPFS hash required");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        // Generate pseudorandom attributes
        uint256 randomSeed = _generatePseudoRandomSeed(tokenId, to);
        OneirobotAttributes memory attributes = _generateAttributes(randomSeed, ipfsMetadataHash);
        
        // Store attributes
        tokenAttributes[tokenId] = attributes;
        
        // Mint NFT
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, _buildTokenURI(ipfsMetadataHash));

        emit OneirobotMinted(
            to,
            tokenId,
            attributes.quantumCore,
            attributes.dreamLevel,
            attributes.lucidPower,
            attributes.mindStrength,
            attributes.ipfsHash
        );
        
        emit AttributesGenerated(tokenId, randomSeed);

        return tokenId;
    }

    // ===================== ATTRIBUTE GENERATION =====================
    
    /**
     * @dev Generate pseudorandom seed using blockhash + nonce
     * @param tokenId Current token ID as nonce
     * @param to Minting address for additional entropy
     * @return Random seed for attribute generation
     */
    function _generatePseudoRandomSeed(uint256 tokenId, address to) private view returns (uint256) {
        // WARNING: For mainnet, suggest Chainlink VRF or Helius RNG for true randomness
        bytes32 blockHash = blockhash(block.number - 1);
        if (blockHash == 0) {
            blockHash = blockhash(block.number - 2);
        }
        
        return uint256(keccak256(abi.encodePacked(
            blockHash,
            to,
            tokenId,
            block.timestamp,
            block.difficulty,
            msg.sender
        )));
    }
    
    /**
     * @dev Generate OneirobotAttributes from random seed
     * @param randomSeed Pseudorandom seed
     * @param ipfsHash IPFS metadata hash
     * @return Generated attributes
     */
    function _generateAttributes(uint256 randomSeed, string memory ipfsHash) 
        private 
        view 
        returns (OneirobotAttributes memory) 
    {
        string[] memory quantumCores = new string[](7);
        quantumCores[0] = "Quantum Core Alpha";
        quantumCores[1] = "Quantum Core Beta";
        quantumCores[2] = "Quantum Core Gamma";
        quantumCores[3] = "Quantum Core Delta";
        quantumCores[4] = "Quantum Core Epsilon";
        quantumCores[5] = "Quantum Core Zeta";
        quantumCores[6] = "Quantum Core Omega";
        
        return OneirobotAttributes({
            quantumCore: quantumCores[randomSeed % quantumCores.length],
            dreamLevel: uint8((randomSeed >> 8) % 100) + 1,  // 1-100
            lucidPower: uint8((randomSeed >> 16) % 100) + 1, // 1-100
            mindStrength: uint8((randomSeed >> 24) % 100) + 1, // 1-100
            ipfsHash: ipfsHash,
            mintTimestamp: block.timestamp,
            randomSeed: randomSeed
        });
    }

    // ===================== ALLOWLIST MANAGEMENT =====================
    
    /**
     * @notice Add address to Syndicate Masters allowlist
     * @param account Address to add
     */
    function addSyndicateMaster(address account) public onlyRole(DEFAULT_ADMIN_ROLE) {
        require(account != address(0), "OneirobotNFT: Cannot add zero address");
        _grantRole(SYNDICATE_MASTER_ROLE, account);
        syndicateMasters[account] = true;
        emit SyndicateMasterAdded(account);
    }
    
    /**
     * @notice Remove address from Syndicate Masters allowlist
     * @param account Address to remove
     */
    function removeSyndicateMaster(address account) public onlyRole(DEFAULT_ADMIN_ROLE) {
        _revokeRole(SYNDICATE_MASTER_ROLE, account);
        syndicateMasters[account] = false;
        emit SyndicateMasterRemoved(account);
    }

    // ===================== VIEW FUNCTIONS =====================
    
    /**
     * @notice Get token attributes
     * @param tokenId Token ID to query
     * @return OneirobotAttributes struct
     */
    function getTokenAttributes(uint256 tokenId) public view returns (OneirobotAttributes memory) {
        require(_exists(tokenId), "OneirobotNFT: Token does not exist");
        return tokenAttributes[tokenId];
    }
    
    /**
     * @notice Get total supply
     * @return Current total supply
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
    
    /**
     * @notice Check if address is Syndicate Master
     * @param account Address to check
     * @return True if address has SYNDICATE_MASTER_ROLE
     */
    function isSyndicateMaster(address account) public view returns (bool) {
        return hasRole(SYNDICATE_MASTER_ROLE, account);
    }

    // ===================== INTERNAL FUNCTIONS =====================
    
    /**
     * @dev Build token URI for IPFS metadata
     * @param ipfsHash IPFS hash
     * @return Complete IPFS URI
     */
    function _buildTokenURI(string memory ipfsHash) private pure returns (string memory) {
        return string(abi.encodePacked("ipfs://", ipfsHash));
    }

    // ===================== OVERRIDES =====================
    
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}