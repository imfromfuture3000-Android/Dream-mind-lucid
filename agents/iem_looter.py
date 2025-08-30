#!/usr/bin/env python3
"""
IEM Looter — Dream Event Listener
---------------------------------
Listens for DreamRecorded events and saves them to iem_memory.json
Part of the IEM-Ω Syndicate crew for the Dream-Mind-Lucid ecosystem
"""

import os
import json
import time
from web3 import Web3

# ====== CONFIG ======
RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))  # Europa Hub

w3 = Web3(Web3.HTTPProvider(RPC))

MEMORY_FILE = "iem_memory.json"

# ====== UTILS ======
    return {"lastDeployed": {}}

def save_memory(mem):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(mem, f, indent=2)

def log_dream(dreamer, dream, tx_hash, block_number):
    """Log a dream to the memory file"""
    mem = load_memory()
    
    dream_entry = {
        "dreamer": dreamer,
        "dream": dream,
        "tx_hash": tx_hash,
        "block_number": block_number,
        "timestamp": int(time.time())
    }
    
    if "dreams" not in mem:
        mem["dreams"] = []
    
    mem["dreams"].append(dream_entry)
    save_memory(mem)
    
    print(f"💾 Dream saved: {dreamer[:10]}... -> '{dream[:50]}{'...' if len(dream) > 50 else ''}'")

def listen_for_dreams():
    """Main function to listen for DreamRecorded events"""
    mem = load_memory()
    
    if "lastDeployed" not in mem or "address" not in mem["lastDeployed"]:
        print("❌ No deployed contract found in iem_memory.json")
        print("💡 Run 'python agents/iem_syndicate.py deploy' first")
        return
    
    contract_address = mem["lastDeployed"]["address"]
    contract_abi = mem["lastDeployed"]["abi"]
    
    print(f"🎯 Connecting to SKALE Network: {RPC}")
    print(f"📍 Contract Address: {contract_address}")
    
    if not w3.is_connected():
        print("❌ Failed to connect to SKALE network")
        return
    
    print("✅ Connected to SKALE network")
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    # Create event filter for DreamRecorded events
    try:
        event_filter = contract.events.DreamRecorded.create_filter(fromBlock="latest")
        print("👂 Listening for dreams... (Press Ctrl+C to stop)")
        print("=" * 60)
        
        while True:
            try:
                # Check for new events
                for event in event_filter.get_new_entries():
                    dreamer = event.args.dreamer
                    dream = event.args.dream
                    tx_hash = event.transactionHash.hex()
                    block_number = event.blockNumber
                    
                    print(f"💭 Dream spotted!")
                    print(f"   👤 Dreamer: {dreamer}")
                    print(f"   🌙 Dream: {dream}")
                    print(f"   🔗 TX: {tx_hash}")
                    print(f"   📦 Block: {block_number}")
                    print("-" * 40)
                    
                    # Save to memory
                    log_dream(dreamer, dream, tx_hash, block_number)
                
                time.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Dream listening stopped by user")
                break
            except Exception as e:
                print(f"⚠️ Error while listening: {e}")
                time.sleep(5)  # Wait longer on error
                
    except Exception as e:
        print(f"❌ Failed to create event filter: {e}")
        print("💡 Make sure the contract is deployed and the ABI is correct")

if __name__ == "__main__":
    print("🌌 IEM Looter - Dream Event Listener")
    print("Part of the Dream-Mind-Lucid ecosystem")
    print("=" * 50)
    
    listen_for_dreams()