from web3 import Web3
import json

# Connect to SKALE
w3 = Web3(Web3.HTTPProvider("https://mainnet.skalenodes.com/v1/elated-tan-skat"))
print(f"Connected to SKALE: {w3.is_connected()}")

# Load deployment info
with open("iem_memory.json", "r") as f:
    deployment_info = json.load(f)

print(f"\nContract address: {deployment_info['address']}")
print(f"Deployer address: {deployment_info['deployer']}")
print(f"Transaction hash: {deployment_info['transactionHash']}")

# Check if contract exists
code = w3.eth.get_code(deployment_info['address'])
print(f"\nContract code exists: {len(code) > 0}")
print(f"Code size: {len(code)} bytes")

# Get transaction receipt
receipt = w3.eth.get_transaction_receipt(deployment_info['transactionHash'])
print(f"\nTransaction status: {receipt.status}")
print(f"Block number: {receipt.blockNumber}")
print(f"Gas used: {receipt.gasUsed}")
