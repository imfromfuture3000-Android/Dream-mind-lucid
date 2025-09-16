from web3 import Web3
from solcx import compile_standard, install_solc
import os
import json

# Configure Web3 with SKALE
w3 = Web3(Web3.HTTPProvider('https://mainnet.skalenodes.com/v1/elated-tan-skat'))
print(f'Connected to SKALE: {w3.is_connected()}')

# Get account from private key
private_key = '16db936de7342b075849d74a66460007772fab88cf4ab509a3487f23398823d6'
account = w3.eth.account.from_key(private_key)
print(f'Using account: {account.address}')

# Install and compile Solidity
print('Installing solc...')
install_solc('0.8.20')

print('Compiling IEMDreams.sol...')
with open('contracts/IEMDreams.sol', 'r') as f:
    source = f.read()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IEMDreams.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
            }
        }
    },
    solc_version="0.8.20"
)

# Get contract bytecode and ABI
contract_interface = compiled['contracts']['IEMDreams.sol']['IEMDreams']
bytecode = contract_interface['evm']['bytecode']['object']
abi = contract_interface['abi']

# Create contract instance
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(account.address)
print(f'Current nonce: {nonce}')

# Build constructor tx
tx = {
    'nonce': nonce,
    'gas': 5000000,
    'gasPrice': 0,  # SKALE has zero gas fees
    'chainId': 2046399126,
    'from': account.address,
    'data': Contract.constructor()._encode_constructor_data()
}

# Sign transaction
signed = w3.eth.account.sign_transaction(tx, private_key)

try:
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f'Transaction sent: {tx_hash.hex()}')
    
    # Wait for transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt.contractAddress
    print(f'Contract deployed at: {contract_address}')
    
    # Save deployment info
    deployment_info = {
        'address': contract_address,
        'abi': abi,
        'txHash': tx_hash.hex(),
        'deployer': account.address,
        'chainId': 2046399126
    }
    
    with open('iem_memory.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    print('Deployment info saved to iem_memory.json')
    
except Exception as e:
    print(f'Error deploying contract: {e}')
