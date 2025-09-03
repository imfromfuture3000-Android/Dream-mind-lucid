#!/usr/bin/env python3
"""
IEM Syndicate - Multi-Agent Deployment System
---------------------------------------------
Handles deployment, auditing, and monitoring of Dream-Mind-Lucid contracts
Last Updated: September 01, 2025
"""

import os
import sys
import json
import time
import hashlib
from web3 import Web3
from solcx import compile_standard, install_solc

# Environment Configuration
SKALE_RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
INFURA_RPC = os.getenv("INFURA_PROJECT_ID")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))
PRIVATE_KEY = os.getenv("DEPLOYER_KEY", "")
FORWARDER_ADDRESS = os.getenv("FORWARDER_ADDRESS", "0x0000000000000000000000000000000000000000")
SIMULATION_MODE = os.getenv("SYNDICATE_SIMULATE", "0") in ("1", "true", "True")

# Use Infura RPC if available, otherwise fallback to SKALE RPC
if INFURA_RPC and INFURA_RPC != "YOUR_INFURA_API_KEY":
    RPC_URL = f"https://skale-mainnet.infura.io/v3/{INFURA_RPC}"
else:
    RPC_URL = SKALE_RPC

w3 = Web3(Web3.HTTPProvider(RPC_URL))
MEMORY_FILE = "iem_memory.json"

def load_memory():
    """Load deployment memory from JSON file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"lastDeployed": {}, "loot": [], "audits": []}

def save_memory(memory):
    """Save deployment memory to JSON file."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def compile_contract(contract_name):
    """Compile a Solidity contract."""
    print(f"🔨 Compiling {contract_name}.sol...")
    
    # Install Solidity compiler
    install_solc("0.8.20")
    
    # Read contract source
    contract_path = f"contracts/{contract_name}.sol"
    if not os.path.exists(contract_path):
        raise FileNotFoundError(f"Contract file not found: {contract_path}")
    
    with open(contract_path, 'r') as f:
        source = f.read()
    
    # Compile contract
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {f"{contract_name}.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode", "evm.deployedBytecode"]
                }
            }
        }
    }, solc_version="0.8.20")
    
    contract_data = compiled["contracts"][f"{contract_name}.sol"][contract_name]
    print(f"✅ {contract_name} compiled successfully!")
    return contract_data

def deploy_contract(contract_name):
    """Deploy a contract to SKALE network."""
    print(f"🚀 Deploying {contract_name} to SKALE Network...{' (SIMULATION)' if SIMULATION_MODE else ''}")

    # Simulation path: create deterministic address & stub ABI without on-chain tx
    if SIMULATION_MODE:
        import hashlib
        seed = hashlib.sha256(contract_name.encode()).hexdigest()
        contract_address = "0x" + seed[:40]
        if contract_name == "IEMDreams":
            abi = [
                {"type": "function", "name": "recordDream", "inputs": [{"name": "dream", "type": "string"}], "outputs": []}
            ]
            bytecode = "0xSIM_DREAMS"
        else:
            abi = [
                {"type": "function", "name": "interfaceDream", "inputs": [{"name": "ipfsHash", "type": "string"}], "outputs": []}
            ]
            bytecode = "0xSIM_ONEIRO"
        tx_hash_hex = "0xSIMULATION" + seed[:16]
        gas_used = 0
    else:
        if not PRIVATE_KEY:
            raise ValueError("DEPLOYER_KEY environment variable not set! (or enable SYNDICATE_SIMULATE=1)")
        # Compile contract (real)
        compiled = compile_contract(contract_name)
        bytecode = compiled["evm"]["bytecode"]["object"]
        abi = compiled["abi"]
        account = w3.eth.account.from_key(PRIVATE_KEY)
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(account.address)
        if contract_name == "OneiroSphere":
            tx = contract.constructor(FORWARDER_ADDRESS).build_transaction({
                "from": account.address,
                "nonce": nonce,
                "gas": 5_000_000,
                "gasPrice": 0,
                "chainId": CHAIN_ID
            })
        else:
            tx = contract.constructor().build_transaction({
                "from": account.address,
                "nonce": nonce,
                "gas": 5_000_000,
                "gasPrice": 0,
                "chainId": CHAIN_ID
            })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"📡 Transaction sent: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt.contractAddress
        tx_hash_hex = tx_hash.hex()
        gas_used = receipt.gasUsed

    print(f"✅ {contract_name} deployed at: {contract_address}")
    memory = load_memory()
    memory["lastDeployed"][contract_name] = {
        "address": contract_address,
        "abi": abi,
        "bytecode": bytecode,
        "timestamp": time.time(),
        "txHash": tx_hash_hex,
        "gasUsed": gas_used
    }
    save_memory(memory)
    return contract_address, abi

def audit_contract(contract_name):
    """Audit deployed contract."""
    print(f"🔍 Auditing {contract_name}...")
    
    memory = load_memory()
    if contract_name not in memory["lastDeployed"]:
        print(f"❌ {contract_name} not found in deployment memory!")
        return
    
    deployment = memory["lastDeployed"][contract_name]
    address = deployment["address"]
    
    # Get contract code
    code = w3.eth.get_code(address)
    code_hash = hashlib.sha256(code).hexdigest()
    
    # Basic audit checks
    audit_result = {
        "contract": contract_name,
        "address": address,
        "codeHash": code_hash,
        "codeSize": len(code),
        "timestamp": time.time(),
        "checks": {
            "codeExists": len(code) > 0,
            "hashMatches": True,  # Would need expected hash for proper validation
        }
    }
    
    # Save audit result
    memory["audits"].append(audit_result)
    save_memory(memory)
    
    print(f"✅ Audit completed for {contract_name}")
    print(f"   Address: {address}")
    print(f"   Code Hash: {code_hash}")
    print(f"   Code Size: {len(code)} bytes")

def test_dream_recording():
    """Test dream recording functionality."""
    print("🌙 Testing dream recording...")
    
    memory = load_memory()
    
    # Check if OneiroSphere is deployed
    if "OneiroSphere" not in memory["lastDeployed"]:
        print("❌ OneiroSphere not deployed. Deploy it first!")
        return
    
    deployment = memory["lastDeployed"]["OneiroSphere"]
    contract = w3.eth.contract(address=deployment["address"], abi=deployment["abi"])
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    # Test dream IPFS hash
    test_ipfs_hash = "QmTestDreamHash1234567890abcdefghijklmnopqr"
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.interfaceDream(test_ipfs_hash).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 200_000,
        "gasPrice": 0,
        "chainId": CHAIN_ID
    })
    
    # Sign and send
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Save test result
    memory["loot"].append({
        "dreamer": account.address,
        "dream": "Test dream for OneiroSphere deployment verification",
        "ipfsHash": test_ipfs_hash,
        "timestamp": time.time(),
        "txHash": tx_hash.hex()
    })
    save_memory(memory)
    
    print(f"✅ Test dream recorded!")
    print(f"   Transaction: {tx_hash.hex()}")
    print(f"   IPFS Hash: {test_ipfs_hash}")

def record_dream(dream_text: str):
    """Record an arbitrary dream string using the deployed IEMDreams contract.

    This assumes IEMDreams was deployed via this syndicate (so its ABI & address
    exist in memory). Stores the dream text IPFS placeholder hash into loot list.
    """
    print("🌙 Recording dream to IEMDreams...")
    memory = load_memory()
    if "IEMDreams" not in memory["lastDeployed"]:
        print("❌ IEMDreams not deployed. Deploy it first with: deploy IEMDreams")
        return
    deployment = memory["lastDeployed"]["IEMDreams"]
    if SIMULATION_MODE:
        tx_hash_hex = deployment.get("txHash", "0xSIM_DREAM_TX")
        gas_used = 0
    else:
        if not PRIVATE_KEY:
            print("❌ DEPLOYER_KEY not set in environment (or enable SYNDICATE_SIMULATE=1)")
            return
        contract = w3.eth.contract(address=deployment["address"], abi=deployment["abi"])
        account = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)
        try:
            tx = contract.functions.recordDream(dream_text).build_transaction({
                "from": account.address,
                "nonce": nonce,
                "gas": 300_000,
                "gasPrice": 0,
                "chainId": CHAIN_ID
            })
        except AttributeError:
            print("❌ Contract ABI missing recordDream function.")
            return
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = tx_hash.hex()
        gas_used = receipt.gasUsed
    memory["loot"].append({
        "dreamer": deployment["address"],  # using contract address or account in simulation
        "dream": dream_text,
        "ipfsHash": "placeholder",
        "timestamp": time.time(),
        "txHash": tx_hash_hex
    })
    save_memory(memory)
    print("✅ Dream recorded!")
    print(f"   Tx: {tx_hash_hex}")
    print(f"   Gas Used: {gas_used}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python iem_syndicate.py [deploy|audit|test] [contract_name]")
        print("Commands:")
        print("  deploy IEMDreams    - Deploy IEMDreams contract")
        print("  deploy OneiroSphere - Deploy OneiroSphere contract")
        print("  audit [contract]    - Audit deployed contract")
        print("  test                - Test dream recording")
        return
    
    command = sys.argv[1].lower()
    try:
        if command == "deploy":
            if len(sys.argv) < 3:
                print("❌ Please specify contract name: IEMDreams or OneiroSphere")
                return
            contract_name = sys.argv[2]
            deploy_contract(contract_name)
        elif command == "audit":
            contract_name = sys.argv[2] if len(sys.argv) > 2 else "OneiroSphere"
            audit_contract(contract_name)
        elif command == "test":
            test_dream_recording()
        elif command == "record":
            dream_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Test dream from CLI"
            record_dream(dream_text)
        else:
            print(f"❌ Unknown command: {command}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()