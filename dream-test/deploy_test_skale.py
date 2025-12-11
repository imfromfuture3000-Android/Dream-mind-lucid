from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json

# Simple test contract
CONTRACT_SOURCE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TestContract {
    string public message;
    
    constructor() {
        message = "Hello SKALE!";
    }
}
"""

# Try Europa Hub first
RPC_URL = "https://mainnet.skalenodes.com/v1/elated-tan-skat"
CHAIN_ID = 2046399126

print("🔧 Installing Solidity compiler...")
install_solc("0.8.20")

print("\n📝 Compiling contract...")
compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"TestContract.sol": {"content": CONTRACT_SOURCE}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
            },
            "optimizer": {
                "enabled": true,
                "runs": 200
            }
        }
    },
    solc_version="0.8.20"
)

# Get bytecode and ABI
contract_interface = compiled["contracts"]["TestContract.sol"]["TestContract"]
bytecode = contract_interface["evm"]["bytecode"]["object"]
abi = contract_interface["abi"]

print("\n🌐 Connecting to SKALE Europa Hub...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Failed to connect to network")

# Set up account
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"📝 Using account: {account.address}")

# Check balance
balance = w3.eth.get_balance(account.address)
print(f"💰 Account balance: {w3.from_wei(balance, 'ether')} SKALE")

# Create contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(account.address)

# Estimate gas
gas_estimate = Contract.constructor().estimate_gas() + 100000  # Add buffer
print(f"\n⛽ Estimated gas (with buffer): {gas_estimate}")

print("\n🚀 Preparing deployment transaction...")
# Build constructor transaction with minimal gas price
constructor_txn = Contract.constructor().build_transaction(
    {
        "chainId": CHAIN_ID,
        "gas": gas_estimate,
        "gasPrice": 100000,  # Minimal gas price
        "nonce": nonce,
    }
)

print("✍️ Signing transaction...")
signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)

print("📤 Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

print("\n⏳ Waiting for confirmation...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress

print(f"\n📋 Deployment Results:")
print(f"Contract address: {contract_address}")
print(f"Transaction status: {tx_receipt.status}")
print(f"Gas used: {tx_receipt.gasUsed}")

# Verify contract code exists
code = w3.eth.get_code(contract_address)
print(f"\n🔍 Verification:")
print(f"Contract code exists: {len(code) > 0}")
print(f"Code size: {len(code)} bytes")

if len(code) > 0:
    # Try to interact with the contract
    contract = w3.eth.contract(address=contract_address, abi=abi)
    try:
        message = contract.functions.message().call()
        print(f"\n✅ Contract is working! Current message: {message}")
    except Exception as e:
        print(f"\n❌ Failed to call contract: {e}")
else:
    print("\n❌ No contract code found at deployed address")

print("\nTransaction details:")
print(json.dumps({
    "from": account.address,
    "to": None,  # Contract creation
    "chainId": CHAIN_ID,
    "gas": gas_estimate,
    "gasPrice": 100000,
    "nonce": nonce,
    "value": 0,
    "data": bytecode
}, indent=2))
