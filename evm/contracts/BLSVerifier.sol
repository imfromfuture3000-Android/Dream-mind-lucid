// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BLSVerifier (stub)
 * @dev Minimal BLS verifier interface. On SKALE, replace the `verify` implementation
 * with a call to the SKALE pairing precompile or an optimized on-chain verifier.
 * For now this contract provides a toggleable precompile address and a fallback
 * mode (admin can enable `forceVerify` for production bootstrapping).
 */
contract BLSVerifier {
    address public admin;
    address public precompile; // precompile address for BLS pairing check (if available)
    bool public forceVerify; // if true, verify() returns true (use with caution)

    event PrecompileSet(address indexed precompile);
    event ForceVerifySet(bool enabled);

    modifier onlyAdmin() {
        require(msg.sender == admin, "BLSVerifier: not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function setPrecompile(address _precompile) external onlyAdmin {
        precompile = _precompile;
        emit PrecompileSet(_precompile);
    }

    function setForceVerify(bool v) external onlyAdmin {
        forceVerify = v;
        emit ForceVerifySet(v);
    }

    /// @notice Verify aggregated BLS signature over message
    /// @dev If `precompile` is configured, we call it with raw calldata
    ///      The expected precompile ABI is implementation-specific and must be set by admin.
    /// @param pubkey Aggregated public key bytes
    /// @param message Message bytes that was signed
    /// @param signature Aggregated signature bytes
    /// @return ok true if signature verifies (or forceVerify is enabled)
    function verify(bytes calldata pubkey, bytes calldata message, bytes calldata signature) external view returns (bool ok) {
        if (forceVerify) {
            return true;
        }
        if (precompile == address(0)) {
            return false;
        }
        // Call precompile with abi.encode(pubkey, message, signature)
        bytes memory input = abi.encode(pubkey, message, signature);
        (bool success, bytes memory out) = precompile.staticcall(input);
        if (!success) return false;
        // expect a nonzero first byte to mean true
        if (out.length == 0) return false;
        return out[0] != 0;
    }

    function transferAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }
}
