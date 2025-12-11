// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.20;

import "./interfaces/IDreamMarionette.sol";

contract DreamMarionetteFactory is IDreamMarionetteFactory {
    function createProxy(
        bytes32 salt,
        address implementation,
        bytes calldata initData
    ) external returns (address) {
        bytes memory deploymentData = abi.encodePacked(
            type(DreamMarionetteProxy).creationCode,
            abi.encode(implementation, salt)
        );
        
        address proxy;
        assembly {
            proxy := create2(0, add(deploymentData, 0x20), mload(deploymentData), salt)
            if iszero(extcodesize(proxy)) { revert(0, 0) }
        }
        
        // Initialize the proxy if initData is provided
        if (initData.length > 0) {
            (bool success,) = proxy.call(initData);
            require(success, "DreamFactory: initialization failed");
        }
        
        emit ProxyCreated(proxy, salt);
        return proxy;
    }
    
    function computeProxyAddress(
        bytes32 salt,
        address implementation
    ) external view returns (address) {
        bytes memory deploymentData = abi.encodePacked(
            type(DreamMarionetteProxy).creationCode,
            abi.encode(implementation, salt)
        );
        
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                keccak256(deploymentData)
            )
        );
        
        return address(uint160(uint256(hash)));
    }
}
