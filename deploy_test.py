from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

# Initialize Web3
w3 = Web3(Web3.HTTPProvider('https://mainnet.skalenodes.com/v1/elated-tan-skat'))
print(f'Connected to SKALE: {w3.is_connected()}')

# Compile contract
print('Installing solc...')
install_solc("0.8.20")

print('Compiling contract...')
with open('contracts/IEMDreams.sol', 'r') as f:
    source = f.read()

compiled = compile_standard({
    "language": "Solidity",
    "sources": {"IEMDreams.sol": {"content": source}},
    "settings": {
        "outputSelection": {
            "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
        }
    }
}, solc_version="0.8.20")

# Get bytecode and ABI
bytecode = compiled["contracts"]["IEMDreams.sol"]["IEMDreams"]["evm"]["bytecode"]["object"]
abi = compiled["contracts"]["IEMDreams.sol"]["IEMDreams"]["abi"]

# Deploy contract
print('Deploying contract...')
private_key = os.getenv('DEPLOYER_KEY', '0x16db936de7342b075849d74a66460007772fab88cf4ab509a3487f23398823d6')
if private_key.startswith('0x'):
    private_key = private_key[2:]  # Remove 0x prefix if present
    
account = w3.eth.account.from_key(private_key)
print(f'Deploying from address: {account.address}')

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account.address)

# Build transaction
transaction = Contract.constructor().build_transaction({
    "chainId": 2046399126,
    "gas": 5000000,
    "gasPrice": w3.eth.gas_price,
    "nonce": nonce,
})

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print('Transaction signed, sending...')

# Send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(f'Transaction sent: {tx_hash.hex()}')

# Wait for receipt
print('Waiting for transaction receipt...')
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Contract deployed at: {tx_receipt.contractAddress}')

# Save deployment info
deployment_info = {
    "address": tx_receipt.contractAddress,
    "abi": abi,
    "txHash": tx_hash.hex(),
    "deployer": account.address
}

with open('iem_memory.json', 'w') as f:
    json.dump(deployment_info, f, indent=2)
print('Deployment info saved to iem_memory.json')
