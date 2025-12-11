// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.20;

interface IDreamMarionetteProxy {
    // Events
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event DreamProxyDeployed(address indexed proxy, bytes32 salt);
    event DreamMarionetteBound(address indexed proxy, address indexed marionette);

    // Functions
    function initialize(address _owner) external;
    function bindMarionette(address _marionette) external;
    function owner() external view returns (address);
    function transferOwnership(address newOwner) external;
    function implementation() external view returns (address);
    function salt() external view returns (bytes32);
}

interface IDreamMarionette {
    // Events
    event DreamStateUpdated(bytes32 indexed stateHash, uint256 indexed blockNumber);
    event LucidityProofSubmitted(bytes32 indexed proofHash, address indexed validator);
    event ConsensusRoundStarted(uint256 indexed roundId, uint256 timestamp);
    
    // Core functions
    function initialize(
        address _owner,
        address _validator,
        bytes32 _initialState
    ) external;
    
    function submitLucidityProof(
        bytes32 stateHash,
        bytes calldata proof,
        bytes calldata signature
    ) external returns (bool);
    
    function updateDreamState(
        bytes32 newStateHash,
        bytes calldata transitions,
        bytes[] calldata validatorSignatures
    ) external returns (bool);
    
    // View functions
    function getCurrentState() external view returns (bytes32);
    function getLastRoundId() external view returns (uint256);
    function isValidator(address account) external view returns (bool);
    function getValidatorCount() external view returns (uint256);
    
    // Admin functions
    function addValidator(address validator) external;
    function removeValidator(address validator) external;
    function pause() external;
    function unpause() external;
}

interface IDreamMarionetteFactory {
    event ProxyCreated(address indexed proxy, bytes32 indexed salt);
    
    function createProxy(
        bytes32 salt,
        address implementation,
        bytes calldata initData
    ) external returns (address);
    
    function computeProxyAddress(
        bytes32 salt,
        address implementation
    ) external view returns (address);
}
