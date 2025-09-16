from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

def deploy_dreams():
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider('https://mainnet.skalenodes.com/v1/elated-tan-skat'))
    print(f'Connected to SKALE: {w3.is_connected()}')

    # Set up account
    private_key = '1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108'
    account = w3.eth.account.from_key(private_key)
    print(f'Deploying from account: {account.address}')
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    print(f'Account balance: {w3.from_wei(balance, "ether")} SKALE')

    # Install Solidity compiler
    print('Installing Solidity compiler...')
    install_solc('0.8.20')

    # Compile contract
    print('Compiling IEMDreams contract...')
    with open('contracts/IEMDreams.sol', 'r') as file:
        source = file.read()

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
    contract_interface = compiled['contracts']['IEMDreams.sol']['IEMDreams']
    bytecode = contract_interface['evm']['bytecode']['object']
    abi = contract_interface['abi']

    # Create contract
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Get transaction count
    nonce = w3.eth.get_transaction_count(account.address)
    print(f'Nonce: {nonce}')

    # Build deployment transaction
    transaction = {
        'chainId': 2046399126,
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'data': Contract.bytecode
    }

    # Sign transaction
    signed = account.sign_transaction(transaction)
    print('Transaction signed successfully')

    try:
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        print(f'Transaction sent: {tx_hash.hex()}')

        # Wait for transaction receipt
        print('Waiting for transaction confirmation...')
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = receipt.contractAddress
        print(f'Contract deployed successfully at: {contract_address}')

        # Save deployment info
        deployment_info = {
            'contract': 'IEMDreams',
            'address': contract_address,
            'deployer': account.address,
            'transactionHash': tx_hash.hex(),
            'abi': abi
        }

        with open('iem_memory.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        print('Deployment information saved to iem_memory.json')

        return contract_address

    except Exception as e:
        print(f'Error during deployment: {e}')
        return None

if __name__ == '__main__':
    deploy_dreams()
