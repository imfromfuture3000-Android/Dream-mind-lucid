from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json

# Connect to Europa Testnet
RPC_URL = "https://testnet.skalenodes.com/v1/juicy-low-small-testnet"
CHAIN_ID = 1444673419

print("🔌 Connecting to SKALE Europa Testnet...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Failed to connect to network"
print("✅ Connected successfully")

# Account setup
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"📝 Using account: {account.address}")

# Check balance and gas price
balance = w3.eth.get_balance(account.address)
gas_price = w3.eth.gas_price
print(f"💰 Balance: {w3.from_wei(balance, 'ether')} sFUEL")
print(f"⛽ Gas Price: {w3.from_wei(gas_price, 'gwei')} gwei")

# Contract source - simplified version first
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IEMDreams {
    event DreamRecorded(address indexed dreamer, string dream);
    string public name = "IEM Dreams";
    
    function recordDream(string memory dream) public {
        emit DreamRecorded(msg.sender, dream);
    }
}
"""

print("\n🔨 Compiling contract...")
install_solc("0.8.20")

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IEMDreams.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        }
    },
    solc_version="0.8.20"
)

# Get bytecode and ABI
contract_interface = compiled["contracts"]["IEMDreams.sol"]["IEMDreams"]
bytecode = contract_interface["evm"]["bytecode"]["object"]
abi = contract_interface["abi"]

# Create contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(account.address)

print("\n⚡ Preparing transaction...")
# Build constructor transaction
constructor_txn = Contract.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "gas": 1000000,
    "maxFeePerGas": gas_price,
    "maxPriorityFeePerGas": gas_price,
    "nonce": nonce,
})

print("✍️ Signing transaction...")
signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)

print("📤 Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

print("\n⏳ Waiting for confirmation...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print(f"Contract deployed at: {contract_address}")
print(f"Transaction status: {tx_receipt.status}")
print(f"Gas used: {tx_receipt.gasUsed}")

# Verify contract code exists
code = w3.eth.get_code(contract_address)
print(f"\nVerifying deployment:")
print(f"Contract code exists: {len(code) > 0}")
print(f"Code size: {len(code)} bytes")

if len(code) > 0:
    print("\n✅ Contract deployed successfully!")
    
    # Save deployment info
    deployment_info = {
        "contract": "IEMDreams",
        "address": contract_address,
        "network": "SKALE Europa Testnet",
        "rpc": RPC_URL,
        "chainId": CHAIN_ID,
        "deployer": account.address,
        "transactionHash": tx_hash.hex(),
        "abi": abi
    }
    
    with open("skale_europa_deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    print("📝 Deployment information saved to skale_europa_deployment.json")
    
    # Create contract instance and verify functionality
    contract = w3.eth.contract(address=contract_address, abi=abi)
    name = contract.functions.name().call()
    print(f"\nContract verification:")
    print(f"Name: {name}")
else:
    print("\n❌ Contract deployment failed!")
