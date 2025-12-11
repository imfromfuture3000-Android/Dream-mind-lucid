from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json

# Connect to Calypso Mainnet
RPC_URL = "https://mainnet.skalenodes.com/v1/honorable-steel-rasalhague"
CHAIN_ID = 1564830818

print("🔌 Connecting to SKALE Calypso...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Failed to connect to network"
print("✅ Connected successfully")

# Account setup
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"📝 Using account: {account.address}")

# Check balance
balance = w3.eth.get_balance(account.address)
print(f"💰 Balance: {w3.from_wei(balance, 'ether')} sFUEL")

# Minimal Contract with Control
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DreamController {
    address public owner;
    mapping(address => bool) public operators;
    
    event DreamRecorded(address indexed dreamer, string dream);
    event OperatorAdded(address indexed operator);
    event OperatorRemoved(address indexed operator);
    
    constructor() {
        owner = msg.sender;
        operators[msg.sender] = true;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier onlyOperator() {
        require(operators[msg.sender], "Not operator");
        _;
    }
    
    function addOperator(address operator) external onlyOwner {
        operators[operator] = true;
        emit OperatorAdded(operator);
    }
    
    function removeOperator(address operator) external onlyOwner {
        require(operator != owner, "Cannot remove owner");
        operators[operator] = false;
        emit OperatorRemoved(operator);
    }
    
    function recordDream(string calldata dream) external {
        emit DreamRecorded(msg.sender, dream);
    }
    
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Zero address");
        owner = newOwner;
    }
}
"""

print("\n🔨 Compiling contract...")
install_solc("0.8.20")

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"DreamController.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            },
            "optimizer": {
                "enabled": True,
                "runs": 200
            }
        }
    },
    solc_version="0.8.20"
)

# Get bytecode and ABI
contract_interface = compiled["contracts"]["DreamController.sol"]["DreamController"]
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
    "gas": 500000,
    "gasPrice": w3.eth.gas_price,
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
        "contract": "DreamController",
        "address": contract_address,
        "network": "SKALE Calypso Mainnet",
        "rpc": RPC_URL,
        "chainId": CHAIN_ID,
        "owner": account.address,
        "transactionHash": tx_hash.hex(),
        "abi": abi,
        "features": {
            "ownerControl": True,
            "operatorManagement": True,
            "dreamRecording": True
        }
    }
    
    with open("skale_controller_deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    print("📝 Deployment information saved to skale_controller_deployment.json")
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Verify ownership
    owner = contract.functions.owner().call()
    is_operator = contract.functions.operators(account.address).call()
    
    print("\nContract verification:")
    print(f"Owner: {owner}")
    print(f"Deployer is operator: {is_operator}")
    
    print("\n📋 Contract Usage Instructions:")
    print("1. Owner Functions:")
    print("   - addOperator(address) - Add new operators")
    print("   - removeOperator(address) - Remove operators")
    print("   - transferOwnership(address) - Transfer ownership")
    print("2. Dream Recording:")
    print("   - recordDream(string) - Record a dream")
    print("3. View Functions:")
    print("   - owner() - Get current owner")
    print("   - operators(address) - Check if address is operator")
else:
    print("\n❌ Contract deployment failed!")
