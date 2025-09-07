// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.20;

import "./IDreamMarionette.sol";

contract DreamMarionetteProxy {
    address public immutable implementation;
    address public owner;
    bytes32 public immutable salt;
    bool private initialized;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "DreamProxy: caller is not the owner");
        _;
    }
    
    modifier notInitialized() {
        require(!initialized, "DreamProxy: already initialized");
        _;
    }
    
    constructor(address _implementation, bytes32 _salt) {
        implementation = _implementation;
        salt = _salt;
    }
    
    function initialize(address _owner) external notInitialized {
        owner = _owner;
        initialized = true;
        emit OwnershipTransferred(address(0), _owner);
    }
    
    function bindMarionette(address _marionette) external onlyOwner {
        // Logic to bind marionette implementation
        emit DreamMarionetteBound(address(this), _marionette);
    }
    
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "DreamProxy: new owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }
    
    // Delegate all other calls to the implementation
    fallback() external payable {
        address _implementation = implementation;
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), _implementation, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
    
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event DreamProxyDeployed(address indexed proxy, bytes32 salt);
    event DreamMarionetteBound(address indexed proxy, address indexed marionette);
}
