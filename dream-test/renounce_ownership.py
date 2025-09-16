from web3 import Web3
from eth_account import Account
import json
import time

# SKALE chains to try
SKALE_CHAINS = [
    {
        "name": "Europa Hub",
        "rpc": "https://mainnet.skalenodes.com/v1/elated-tan-skat",
        "chain_id": 2046399126,
        "contract": "0xF874AeC485733971a7dAEE9167E388f218aa93D5"
    },
    {
        "name": "Calypso",
        "rpc": "https://mainnet.skalenodes.com/v1/honorable-steel-rasalhague",
        "chain_id": 1564830818,
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    },
    {
        "name": "Nebula",
        "rpc": "https://mainnet.skalenodes.com/v1/green-giddy-denebola",
        "chain_id": 1482601649,
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    },
    {
        "name": "Titan",
        "rpc": "https://mainnet.skalenodes.com/v1/parallel-stormy-spica",
        "chain_id": 1350216234,
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    }
]

# Contract ABI for ownership functions
ABI = [
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"type": "address", "name": ""}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address", "name": "newOwner"}],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def handle_ownership(chain_info):
    print(f"\n🌟 Working with {chain_info['name']}")
    print(f"RPC: {chain_info['rpc']}")
    print(f"Contract: {chain_info['contract']}")
    
    try:
        # Connect to chain
        w3 = Web3(Web3.HTTPProvider(chain_info['rpc']))
        if not w3.is_connected():
            print("❌ Failed to connect to network")
            return False
        
        print("✅ Connected to network")
        
        # Set up account
        private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
        account = Account.from_key(private_key)
        print(f"📝 Using account: {account.address}")
        
        # Create contract instance
        contract = w3.eth.contract(address=chain_info['contract'], abi=ABI)
        
        # Check current owner
        try:
            current_owner = contract.functions.owner().call()
            print(f"Current owner: {current_owner}")
        except Exception as e:
            print(f"❌ Failed to get current owner: {e}")
            return False
        
        if current_owner.lower() != account.address.lower():
            print("❌ We are not the current owner")
            return False
        
        # 1. Renounce ownership
        print("\n1️⃣ Renouncing ownership...")
        nonce = w3.eth.get_transaction_count(account.address)
        
        renounce_txn = contract.functions.renounceOwnership().build_transaction({
            "chainId": chain_info["chain_id"],
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
        })
        
        signed_txn = w3.eth.account.sign_transaction(renounce_txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("✅ Ownership renounced successfully")
        else:
            print("❌ Failed to renounce ownership")
            return False
        
        time.sleep(2)  # Wait a bit between transactions
        
        # 2. Transfer ownership back
        print("\n2️⃣ Transferring ownership back...")
        nonce = w3.eth.get_transaction_count(account.address)
        
        transfer_txn = contract.functions.transferOwnership(account.address).build_transaction({
            "chainId": chain_info["chain_id"],
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
        })
        
        signed_txn = w3.eth.account.sign_transaction(transfer_txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("✅ Ownership transferred back successfully")
        else:
            print("❌ Failed to transfer ownership")
            return False
        
        # Verify final owner
        final_owner = contract.functions.owner().call()
        print(f"\nFinal owner: {final_owner}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Try each chain
for chain in SKALE_CHAINS:
    success = handle_ownership(chain)
    if success:
        print(f"✨ Successfully managed ownership on {chain['name']}")
    else:
        print(f"❌ Failed to manage ownership on {chain['name']}")
    print("\n" + "="*50)
    time.sleep(2)  # Wait between chains
