from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc

# Connect to SKALE
w3 = Web3(Web3.HTTPProvider("https://mainnet.skalenodes.com/v1/elated-tan-skat"))
print(f"Connected to SKALE: {w3.is_connected()}")

# Set up account
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"Account address: {account.address}")

# Get current gas price
gas_price = w3.eth.gas_price
print(f"Current gas price: {w3.from_wei(gas_price, 'gwei')} gwei")

# Install Solidity compiler
print("Installing Solidity compiler...")
install_solc("0.8.20")

# Compile contract
print("Compiling IEMDreams contract...")
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IEMDreams {
    string public name;
    uint256 public totalSupply;
    mapping(address => uint256) public balances;

    event DreamRecorded(address indexed dreamer, string dream);

    constructor() {
        name = "IEM Dreams";
        totalSupply = 777777777 * 10**18;
        balances[msg.sender] = totalSupply;
    }

    function recordDream(string memory dream) public {
        emit DreamRecorded(msg.sender, dream);
    }

    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }
}
"""

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IEMDreams.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
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
print(f"Nonce: {nonce}")

# Build constructor transaction with fixed gas values
constructor_txn = Contract.constructor().build_transaction(
    {
        "chainId": 2046399126,
        "gas": 2000000,  # Lower fixed gas limit
        "gasPrice": w3.to_wei("1", "gwei"),  # Fixed gas price
        "nonce": nonce,
    }
)

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)
print("Transaction signed successfully")

# Send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction sent: {tx_hash.hex()}")

# Wait for transaction receipt
print("Waiting for transaction confirmation...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print(f"Contract deployed successfully at: {contract_address}")
print(f"Transaction status: {tx_receipt.status}")
print(f"Gas used: {tx_receipt.gasUsed}")

# Save deployment info
import json
deployment_info = {
    "contract": "IEMDreams",
    "address": contract_address,
    "deployer": account.address,
    "transactionHash": tx_hash.hex(),
    "abi": abi,
    "status": tx_receipt.status
}

with open("iem_memory.json", "w") as f:
    json.dump(deployment_info, f, indent=2)
print("Deployment information saved to iem_memory.json")

# Verify contract code exists
code = w3.eth.get_code(contract_address)
print(f"\nVerifying deployment:")
print(f"Contract code exists: {len(code) > 0}")
print(f"Code size: {len(code)} bytes")

if len(code) > 0:
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Check deployer balance
    balance = contract.functions.balanceOf(account.address).call()
    print(f"\nDeployer DREAM token balance: {w3.from_wei(balance, 'ether')} DREAM")
