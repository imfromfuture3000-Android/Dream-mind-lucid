// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.20;

import "./interfaces/IDreamMarionette.sol";

contract DreamMarionette is IDreamMarionette {
    // State variables
    address public owner;
    mapping(address => bool) public validators;
    uint256 public validatorCount;
    bytes32 public currentState;
    uint256 public lastRoundId;
    bool public paused;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "DreamMarionette: caller is not the owner");
        _;
    }
    
    modifier onlyValidator() {
        require(validators[msg.sender], "DreamMarionette: caller is not a validator");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused, "DreamMarionette: contract is paused");
        _;
    }
    
    // Constructor is empty since we're using initialize pattern
    constructor() {}
    
    function initialize(
        address _owner,
        address _validator,
        bytes32 _initialState
    ) external {
        require(owner == address(0), "DreamMarionette: already initialized");
        owner = _owner;
        validators[_validator] = true;
        validatorCount = 1;
        currentState = _initialState;
        emit DreamStateUpdated(_initialState, block.number);
    }
    
    function submitLucidityProof(
        bytes32 stateHash,
        bytes calldata proof,
        bytes calldata signature
    ) external onlyValidator whenNotPaused returns (bool) {
        // Validate proof and signature
        // This would typically involve BLS signature verification
        emit LucidityProofSubmitted(keccak256(abi.encodePacked(stateHash, proof)), msg.sender);
        return true;
    }
    
    function updateDreamState(
        bytes32 newStateHash,
        bytes calldata transitions,
        bytes[] calldata validatorSignatures
    ) external whenNotPaused returns (bool) {
        // Verify signatures cover at least 2/3 of validators
        require(validatorSignatures.length * 3 >= validatorCount * 2, 
                "DreamMarionette: insufficient validator signatures");
        
        // Update state
        currentState = newStateHash;
        lastRoundId++;
        
        emit DreamStateUpdated(newStateHash, block.number);
        emit ConsensusRoundStarted(lastRoundId, block.timestamp);
        
        return true;
    }
    
    // View functions
    function getCurrentState() external view returns (bytes32) {
        return currentState;
    }
    
    function getLastRoundId() external view returns (uint256) {
        return lastRoundId;
    }
    
    function isValidator(address account) external view returns (bool) {
        return validators[account];
    }
    
    function getValidatorCount() external view returns (uint256) {
        return validatorCount;
    }
    
    // Admin functions
    function addValidator(address validator) external onlyOwner {
        require(!validators[validator], "DreamMarionette: validator already exists");
        validators[validator] = true;
        validatorCount++;
    }
    
    function removeValidator(address validator) external onlyOwner {
        require(validators[validator], "DreamMarionette: validator does not exist");
        require(validatorCount > 1, "DreamMarionette: cannot remove last validator");
        validators[validator] = false;
        validatorCount--;
    }
    
    function pause() external onlyOwner {
        paused = true;
    }
    
    function unpause() external onlyOwner {
        paused = false;
    }
}
