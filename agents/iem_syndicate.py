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

# ====== CONFIG ======
RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
PRIVATE_KEY = os.getenv("DEPLOYER_KEY", "")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))  # Europa Hub
OWNER_ADDRESS = "0x4B1a58A3057d03888510d93B52ABad9Fee9b351d"

if not PRIVATE_KEY:
    print("❌ DEPLOYER_KEY environment variable required!")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print(f"❌ Cannot connect to SKALE RPC: {RPC}")
    sys.exit(1)

MEMORY_FILE = "iem_memory.json"
CONTRACTS_DIR = "contracts"
ARTIFACTS_DIR = "artifacts"

# ====== UTILS ======
def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {
        "deployments": {},
        "ipfs_hashes": [],
        "audit_records": [],
        "network_stats": {}
    }

def save_memory(mem):
    json.dump(mem, open(MEMORY_FILE, "w"), indent=2)

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
