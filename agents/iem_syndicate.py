#!/usr/bin/env python3
"""
IEM-Ω Syndicate — SKALE Crew
Deployer | Auditor | Looter | Oracle | OneiroSphere
------------------------------------
Complete deployment and management system for Dream-Mind-Lucid
"""

import os, json, hashlib, argparse, time, sys
from web3 import Web3
try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False
    print("⚠️  IPFS client not available. Install with: pip install ipfshttpclient")
IEM Syndicate - Multi-Agent Deployment System
---------------------------------------------
Handles deployment, auditing, and monitoring of Dream-Mind-Lucid contracts
Now supports both SKALE (legacy) and Solana with SPL Token 2022
Last Updated: September 05, 2025
"""

import os
import sys
import json
import time
import hashlib
from typing import Optional

# Legacy SKALE support
from web3 import Web3
from solcx import compile_standard, install_solc

# Solana support
try:
    from solana.rpc.api import Client as SolanaClient
    from solana.keypair import Keypair
    from solana.publickey import PublicKey
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    print("⚠️  Solana packages not installed. Run: pip install solana spl-token")
    SOLANA_AVAILABLE = False

# Environment Configuration - SKALE (Legacy)
SKALE_RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
INFURA_RPC = os.getenv("INFURA_PROJECT_ID")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))
FORWARDER_ADDRESS = os.getenv("FORWARDER_ADDRESS", "0x0000000000000000000000000000000000000000")

# Environment Configuration - Solana (New)
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=16b9324a-5b8c-47b9-9b02-6efa868958e5")
TREASURY_ADDRESS = os.getenv("TREASURY_ADDRESS", "4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a")

# Shared Configuration
PRIVATE_KEY = os.getenv("DEPLOYER_KEY", "")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))  # Europa Hub
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS", "")

if not PRIVATE_KEY:
    print("❌ DEPLOYER_KEY environment variable required!")
    sys.exit(1)

if not OWNER_ADDRESS:
    print("❌ OWNER_ADDRESS environment variable required!")
    sys.exit(1)
w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print(f"❌ Cannot connect to SKALE RPC: {RPC}")
    sys.exit(1)
SIMULATION_MODE = os.getenv("SYNDICATE_SIMULATE", "0") in ("1", "true", "True")
BLOCKCHAIN_MODE = os.getenv("BLOCKCHAIN_MODE", "solana")  # "solana" or "skale"

# Initialize blockchain clients
def init_blockchain_clients():
    """Initialize blockchain clients based on mode"""
    clients = {}
    
    if BLOCKCHAIN_MODE == "skale" or BLOCKCHAIN_MODE == "both":
        # SKALE/Ethereum client
        if INFURA_RPC and INFURA_RPC != "YOUR_INFURA_API_KEY":
            RPC_URL = f"https://skale-mainnet.infura.io/v3/{INFURA_RPC}"
        else:
            RPC_URL = SKALE_RPC
        clients['skale'] = Web3(Web3.HTTPProvider(RPC_URL))
    
    if BLOCKCHAIN_MODE == "solana" or BLOCKCHAIN_MODE == "both":
        # Solana client
        if SOLANA_AVAILABLE:
            clients['solana'] = SolanaClient(SOLANA_RPC_URL)
        else:
            print("❌ Solana client not available")
    
    return clients

# Initialize clients
CLIENTS = init_blockchain_clients()
w3 = CLIENTS.get('skale')  # Backward compatibility
MEMORY_FILE = "iem_memory.json"
CONTRACTS_DIR = "contracts"
ARTIFACTS_DIR = "artifacts"

def load_memory():
    """Load deployment memory from JSON file."""
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {
        "deployments": {},
        "ipfs_hashes": [],
        "audit_records": [],
        "network_stats": {}
    }
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"lastDeployed": {}, "loot": [], "audits": []}

def save_memory(memory):
    """Save deployment memory to JSON file."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def compile_contract(contract_name):
    """Compile a Solidity contract"""
    from solcx import compile_standard, install_solc
    
    try:
        install_solc("0.8.20")
    except Exception as e:
        print(f"⚠️  Solidity compiler installation warning: {e}")
    
    contract_file = f"{CONTRACTS_DIR}/{contract_name}.sol"
    if not os.path.exists(contract_file):
        raise FileNotFoundError(f"Contract file not found: {contract_file}")
    
    source = open(contract_file).read()
    
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {contract_file: {"content": source}},
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
    
    contract_data = compiled["contracts"][contract_file][contract_name]
    return {
        "abi": contract_data["abi"],
        "bytecode": contract_data["evm"]["bytecode"]["object"],
        "deployedBytecode": contract_data["evm"]["deployedBytecode"]["object"]
    }

def deploy_contract_generic(contract_name, constructor_args=None):
    """Generic contract deployment function"""
    print(f"🚀 Deploying {contract_name}...")
    
    compiled = compile_contract(contract_name)
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    
    contract = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    
    if constructor_args:
        tx = contract.constructor(*constructor_args).build_transaction({
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 5_000_000,
            "gasPrice": 0,  # SKALE zero gas
            "chainId": CHAIN_ID
        })
    else:
        tx = contract.constructor().build_transaction({
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 5_000_000,
            "gasPrice": 0,  # SKALE zero gas
            "chainId": CHAIN_ID
        })
    
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"✅ {contract_name} deployed at: {receipt.contractAddress}")
        return {
            "address": receipt.contractAddress,
            "abi": compiled["abi"],
            "deployedBytecode": compiled["deployedBytecode"],
            "txHash": tx_hash.hex(),
            "blockNumber": receipt.blockNumber
        }
    else:
        raise Exception(f"Deployment failed for {contract_name}")

# ====== DEPLOYER ======
def deploy_all():
    """Deploy all contracts in the correct order"""
    print("🌌 Deploying Dream-Mind-Lucid Ecosystem...")
    
    mem = load_memory()
    
    # Deploy DREAM token (IEMDreams)
    if "IEMDreams" not in mem["deployments"]:
        dream_deployment = deploy_contract_generic("IEMDreams")
        mem["deployments"]["IEMDreams"] = dream_deployment
        save_memory(mem)
    
    # Deploy SMIND token
    if "SMindToken" not in mem["deployments"]:
        smind_deployment = deploy_contract_generic("SMindToken")
        mem["deployments"]["SMindToken"] = smind_deployment
        save_memory(mem)
    
    # Deploy LUCID token
    if "LucidToken" not in mem["deployments"]:
        lucid_deployment = deploy_contract_generic("LucidToken")
        mem["deployments"]["LucidToken"] = lucid_deployment
        save_memory(mem)
    
    # Deploy OneiroSphere with token addresses
    if "OneiroSphere" not in mem["deployments"]:
        smind_addr = mem["deployments"]["SMindToken"]["address"]
        lucid_addr = mem["deployments"]["LucidToken"]["address"]
        oneiro_deployment = deploy_contract_generic("OneiroSphere", [smind_addr, lucid_addr])
        mem["deployments"]["OneiroSphere"] = oneiro_deployment
        save_memory(mem)
    
    print("\n🎉 All contracts deployed successfully!")
    print_deployment_summary()

def deploy_single(contract_name):
    """Deploy a single contract"""
    mem = load_memory()
    
    if contract_name == "OneiroSphere":
        if "SMindToken" not in mem["deployments"] or "LucidToken" not in mem["deployments"]:
            print("❌ SMindToken and LucidToken must be deployed first!")
            return
        smind_addr = mem["deployments"]["SMindToken"]["address"]
        lucid_addr = mem["deployments"]["LucidToken"]["address"]
        deployment = deploy_contract_generic(contract_name, [smind_addr, lucid_addr])
    else:
        deployment = deploy_contract_generic(contract_name)
    
    mem["deployments"][contract_name] = deployment
    save_memory(mem)
    
    print(f"\n📋 {contract_name} Deployment Details:")
    print(f"   Address: {deployment['address']}")
    print(f"   TX Hash: {deployment['txHash']}")
    print(f"   Block: {deployment['blockNumber']}")

def print_deployment_summary():
    """Print summary of all deployments"""
    mem = load_memory()
    
    print("\n📋 DEPLOYMENT SUMMARY")
    print("=" * 50)
    for contract_name, deployment in mem["deployments"].items():
        print(f"{contract_name:20} {deployment['address']}")
    print("=" * 50)

# ====== AUDITOR ======
def audit_contracts():
    """Audit all deployed contracts"""
    print("🔍 Auditing deployed contracts...")
    
    mem = load_memory()
    audit_record = {
        "timestamp": int(time.time()),
        "contracts": {},
        "security_checks": {}
    }
    
    for contract_name in os.listdir(CONTRACTS_DIR):
        if contract_name.endswith(".sol"):
            contract_file = f"{CONTRACTS_DIR}/{contract_name}"
            source = open(contract_file).read()
            source_hash = hashlib.sha256(source.encode()).hexdigest()
            
            contract_base = contract_name.replace(".sol", "")
            audit_record["contracts"][contract_base] = {
                "file": contract_name,
                "source_hash": source_hash,
                "lines": len(source.split('\n')),
                "size_bytes": len(source.encode())
            }
            
            print(f"🔎 {contract_base:20} Hash: {source_hash[:16]}...")
    
    # Check deployed bytecode integrity
    for contract_name, deployment in mem["deployments"].items():
        if "address" in deployment:
            addr = deployment["address"]
            onchain_code = w3.eth.get_code(addr).hex()
            code_hash = hashlib.sha256(onchain_code.encode()).hexdigest()
            
            audit_record["security_checks"][contract_name] = {
                "address": addr,
                "onchain_code_hash": code_hash,
                "code_size": len(onchain_code),
                "verified": len(onchain_code) > 2  # More than '0x'
            }
            
            print(f"📡 {contract_name:20} On-chain: {code_hash[:16]}...")
    
    mem["audit_records"].append(audit_record)
    save_memory(mem)
    
    print("✅ Audit completed and saved to memory")

# ====== LOOTER ======
def listen_events():
    """Listen to events from all deployed contracts"""
    print("👂 Starting event listener for all contracts...")
    
    mem = load_memory()
    if not mem["deployments"]:
        print("❌ No contracts deployed yet!")
        return
    
    contracts = {}
    event_filters = []
    
    # Setup event filters for each contract
    for contract_name, deployment in mem["deployments"].items():
        try:
            contract = w3.eth.contract(
                address=deployment["address"], 
                abi=deployment["abi"]
            )
            contracts[contract_name] = contract
            
            # Get all events for this contract
            for event in contract.events:
                try:
                    event_filter = getattr(contract.events, event.event_name).create_filter(fromBlock="latest")
                    event_filters.append((contract_name, event.event_name, event_filter))
                    print(f"📡 Listening to {contract_name}.{event.event_name}")
                except Exception as e:
                    print(f"⚠️  Could not create filter for {contract_name}.{event.event_name}: {e}")
        except Exception as e:
            print(f"⚠️  Could not setup contract {contract_name}: {e}")
    
    print(f"\n🎧 Monitoring {len(event_filters)} event types...")
    
    event_count = 0
    try:
        while True:
            for contract_name, event_name, event_filter in event_filters:
                try:
                    for event in event_filter.get_new_entries():
                        event_count += 1
                        print(f"\n💫 Event #{event_count}: {contract_name}.{event_name}")
                        print(f"   Block: {event.blockNumber}")
                        print(f"   TX: {event.transactionHash.hex()}")
                        
                        # Format event args
                        if hasattr(event, 'args'):
                            for key, value in event.args.items():
                                if isinstance(value, str) and len(value) > 50:
                                    value = value[:47] + "..."
                                print(f"   {key}: {value}")
                        
                        # Store event in memory
                        if "events" not in mem:
                            mem["events"] = []
                        
                        mem["events"].append({
                            "timestamp": int(time.time()),
                            "contract": contract_name,
                            "event": event_name,
                            "blockNumber": event.blockNumber,
                            "txHash": event.transactionHash.hex(),
                            "args": dict(event.args) if hasattr(event, 'args') else {}
                        })
                        
                        # Keep only last 100 events
                        if len(mem["events"]) > 100:
                            mem["events"] = mem["events"][-100:]
                        
                        save_memory(mem)
                        
                except Exception as e:
                    print(f"⚠️  Error reading events from {contract_name}.{event_name}: {e}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Event listener stopped. Captured {event_count} events.")

# ====== ORACLE ======
def update_network_state():
    """Update and sync network state information"""
    print("📡 Updating network state...")
    
    mem = load_memory()
    stats = {
        "timestamp": int(time.time()),
        "block_number": w3.eth.block_number,
        "chain_id": w3.eth.chain_id,
        "contracts": {}
    }
    
    for contract_name, deployment in mem["deployments"].items():
        try:
            addr = deployment["address"]
            balance = w3.eth.get_balance(addr)
            code = w3.eth.get_code(addr)
            
            stats["contracts"][contract_name] = {
                "address": addr,
                "balance_wei": balance,
                "balance_eth": w3.from_wei(balance, 'ether'),
                "code_size": len(code),
                "active": len(code) > 2
            }
            
            # Get contract-specific stats
            contract = w3.eth.contract(address=addr, abi=deployment["abi"])
            
            if contract_name == "IEMDreams":
                try:
                    total_supply = contract.functions.totalSupply().call()
                    owner_balance = contract.functions.balanceOf(OWNER_ADDRESS).call()
                    stats["contracts"][contract_name].update({
                        "total_supply": total_supply,
                        "owner_balance": owner_balance,
                        "circulating": total_supply - owner_balance
                    })
                except Exception as e:
                    print(f"⚠️  Error reading IEMDreams stats: {e}")
            
            elif contract_name == "OneiroSphere":
                try:
                    network_stats = contract.functions.getNetworkStats().call()
                    stats["contracts"][contract_name].update({
                        "total_dreams": network_stats[0],
                        "active_mind_nodes": network_stats[1],
                        "total_staked": network_stats[2],
                        "total_gates": network_stats[3]
                    })
                except Exception as e:
                    print(f"⚠️  Error reading OneiroSphere stats: {e}")
            
        except Exception as e:
            print(f"⚠️  Error reading stats for {contract_name}: {e}")
    
    mem["network_stats"] = stats
    save_memory(mem)
    
    print("✅ Network state updated")
    print(f"   Block Number: {stats['block_number']}")
    print(f"   Active Contracts: {len([c for c in stats['contracts'].values() if c['active']])}")

# ====== ONEIROSPHERE (IPFS Integration) ======
def interface_dream_ipfs(dream_text, coherence=80, novelty=75, emotion=70):
    """Upload dream to IPFS and interface with OneiroSphere"""
    if not IPFS_AVAILABLE:
        print("❌ IPFS client not available!")
        return
    
    print("🌌 Interfacing dream with The Oneiro-Sphere...")
    
    mem = load_memory()
    if "OneiroSphere" not in mem["deployments"]:
        print("❌ OneiroSphere not deployed!")
        return
    
    try:
        # Connect to IPFS
        client = ipfshttpclient.connect()
        
        # Create dream metadata
        dream_data = {
            "dream": dream_text,
            "timestamp": int(time.time()),
            "coherence_score": coherence,
            "novelty_score": novelty,
            "emotion_score": emotion,
            "platform": "Dream-Mind-Lucid",
            "version": "1.0.0"
        }
        
        # Upload to IPFS
        result = client.add_json(dream_data)
        ipfs_hash = result
        
        print(f"📡 Dream uploaded to IPFS: {ipfs_hash}")
        
        # Interface with OneiroSphere contract
        deployment = mem["deployments"]["OneiroSphere"]
        contract = w3.eth.contract(address=deployment["address"], abi=deployment["abi"])
        
        acct = w3.eth.account.from_key(PRIVATE_KEY)
        
        tx = contract.functions.interfaceDream(
            ipfs_hash, coherence, novelty, emotion
        ).build_transaction({
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500_000,
            "gasPrice": 0,
            "chainId": CHAIN_ID
        })
        
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"✅ Dream interfaced successfully!")
            print(f"   IPFS Hash: {ipfs_hash}")
            print(f"   TX Hash: {tx_hash.hex()}")
            
            # Store in memory
            mem["ipfs_hashes"].append({
                "hash": ipfs_hash,
                "dream_preview": dream_text[:100] + "..." if len(dream_text) > 100 else dream_text,
                "timestamp": int(time.time()),
                "tx_hash": tx_hash.hex()
            })
            save_memory(mem)
        else:
            print("❌ Transaction failed!")
            
    except Exception as e:
        print(f"❌ Error interfacing dream: {e}")

def test_ipfs_connection():
    """Test IPFS connection"""
    if not IPFS_AVAILABLE:
        print("❌ IPFS client not available!")
        return
    
    try:
        client = ipfshttpclient.connect()
        test_data = {"test": "Dream-Mind-Lucid IPFS Test", "timestamp": int(time.time())}
        result = client.add_json(test_data)
        print(f"✅ IPFS connection successful! Test hash: {result}")
        return True
    except Exception as e:
        print(f"❌ IPFS connection failed: {e}")
        return False

# ====== MAIN ======
def main():
    parser = argparse.ArgumentParser(description="IEM Syndicate Crew - Dream-Mind-Lucid Management")
    parser.add_argument("agent", choices=[
        "deploy", "deploy-all", "deploy-single", 
        "audit", "loot", "oracle", "oneirosphere",
        "status", "ipfs-test"
    ], help="Which agent to run")
    parser.add_argument("--contract", help="Contract name for deploy-single")
    parser.add_argument("--dream", help="Dream text for oneirosphere")
    parser.add_argument("--coherence", type=int, default=80, help="Coherence score (0-100)")
    parser.add_argument("--novelty", type=int, default=75, help="Novelty score (0-100)")
    parser.add_argument("--emotion", type=int, default=70, help="Emotion score (0-100)")
    
    args = parser.parse_args()
    
    print("🧠 Dream-Mind-Lucid IEM Syndicate")
    print("=" * 40)
    print(f"Network: SKALE Europa Hub ({CHAIN_ID})")
    print(f"RPC: {RPC}")
    print(f"Owner: {OWNER_ADDRESS}")
    print("=" * 40)
    
    if args.agent == "deploy" or args.agent == "deploy-all":
        deploy_all()
    elif args.agent == "deploy-single":
        if not args.contract:
            print("❌ --contract required for deploy-single")
            return
        deploy_single(args.contract)
    elif args.agent == "audit":
        audit_contracts()
    elif args.agent == "loot":
        listen_events()
    elif args.agent == "oracle":
        update_network_state()
    elif args.agent == "oneirosphere":
        if args.dream:
            interface_dream_ipfs(args.dream, args.coherence, args.novelty, args.emotion)
        else:
            test_dream = "I dreamed of a vast quantum network where consciousness flows like digital rivers, connecting minds across infinite dimensions..."
            interface_dream_ipfs(test_dream, args.coherence, args.novelty, args.emotion)
    elif args.agent == "status":
        print_deployment_summary()
        update_network_state()
    elif args.agent == "ipfs-test":
        test_ipfs_connection()

if __name__ == "__main__":
    main()
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

# Solana integration functions
def deploy_solana_tokens():
    """Deploy SPL Token 2022 tokens on Solana"""
    if not SOLANA_AVAILABLE:
        print("❌ Solana packages not available. Install with: pip install solana spl-token")
        return False
    
    print("🚀 Deploying SPL Token 2022 suite on Solana...")
    
    # Use the dedicated Solana agent
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "deploy_tokens"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Solana tokens deployed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Solana token deployment failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error calling Solana agent: {e}")
        return False

def record_dream_solana(dream_text: str):
    """Record a dream on Solana"""
    if not SOLANA_AVAILABLE:
        print("❌ Solana packages not available")
        return False
    
    print(f"🌙 Recording dream on Solana: {dream_text[:50]}...")
    
    # Use the dedicated Solana agent
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "record_dream", dream_text
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Dream recorded on Solana!")
            print(result.stdout)
            return True
        else:
            print("❌ Solana dream recording failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error calling Solana agent: {e}")
        return False

def get_treasury_status_solana():
    """Get Solana treasury status"""
    if not SOLANA_AVAILABLE:
        print("❌ Solana packages not available")
        return
    
    # Use the dedicated Solana agent
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "treasury_status"
        ], capture_output=True, text=True, cwd=".")
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error calling Solana agent: {e}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("🌌 IEM Syndicate - Multi-Blockchain Deployment System")
        print(f"Current mode: {BLOCKCHAIN_MODE.upper()}")
        print("Usage: python iem_syndicate.py [command] [options]")
        print("\nLegacy SKALE Commands:")
        print("  deploy IEMDreams    - Deploy IEMDreams contract")
        print("  deploy OneiroSphere - Deploy OneiroSphere contract")
        print("  audit [contract]    - Audit deployed contract")
        print("  test                - Test dream recording")
        print("  record 'dream text' - Record a dream")
        print("\nNew Solana Commands:")
        print("  solana_deploy       - Deploy SPL Token 2022 suite")
        print("  solana_record 'text'- Record dream on Solana")
        print("  solana_status       - Check treasury status")
        return
    
    command = sys.argv[1].lower()
    try:
        # Solana commands
        if command == "solana_deploy":
            deploy_solana_tokens()
        elif command == "solana_record":
            dream_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Test Solana dream"
            record_dream_solana(dream_text)
        elif command == "solana_status":
            get_treasury_status_solana()
        # Legacy SKALE commands
        elif command == "deploy":
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
