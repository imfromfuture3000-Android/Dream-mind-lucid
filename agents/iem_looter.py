#!/usr/bin/env python3
"""
IEM Looter - Dedicated Event Monitoring Agent
Specialized script for real-time event monitoring and data persistence
Dream-Mind-Lucid Investment Platform
"""

import os
import json
import time
import signal
import sys
from datetime import datetime
from web3 import Web3

# ====== CONFIG ======
RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))  # Europa Hub

w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print(f"❌ Cannot connect to SKALE RPC: {RPC}")
    sys.exit(1)

MEMORY_FILE = "iem_memory.json"
EVENTS_FILE = "dream_events.json"

class DreamLooter:
    def __init__(self):
        self.contracts = {}
        self.event_filters = []
        self.event_count = 0
        self.running = True
        self.events_data = self.load_events()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def load_memory(self):
        """Load deployment memory"""
        if os.path.exists(MEMORY_FILE):
            return json.load(open(MEMORY_FILE))
        return {"deployments": {}}
    
    def load_events(self):
        """Load existing events data"""
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        return {
            "events": [],
            "statistics": {
                "total_dreams": 0,
                "total_stakes": 0,
                "total_rewards": 0,
                "unique_dreamers": set(),
                "last_updated": None
            }
        }
    
    def save_events(self):
        """Save events data to file"""
        # Convert set to list for JSON serialization
        data_to_save = self.events_data.copy()
        data_to_save["statistics"]["unique_dreamers"] = list(self.events_data["statistics"]["unique_dreamers"])
        data_to_save["statistics"]["last_updated"] = datetime.now().isoformat()
        
        with open(EVENTS_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)
    
    def setup_contracts(self):
        """Setup contract instances and event filters"""
        mem = self.load_memory()
        
        if not mem.get("deployments"):
            print("❌ No contracts deployed yet! Run 'python agents/iem_syndicate.py deploy-all' first.")
            return False
        
        print("📡 Setting up contract monitoring...")
        
        for contract_name, deployment in mem["deployments"].items():
            try:
                contract = w3.eth.contract(
                    address=deployment["address"], 
                    abi=deployment["abi"]
                )
                self.contracts[contract_name] = {
                    "instance": contract,
                    "address": deployment["address"]
                }
                
                # Setup event filters
                self.setup_event_filters(contract_name, contract)
                
                print(f"✅ {contract_name:15} {deployment['address']}")
                
            except Exception as e:
                print(f"❌ Failed to setup {contract_name}: {e}")
        
        print(f"\n🎧 Monitoring {len(self.event_filters)} event types from {len(self.contracts)} contracts")
        return len(self.event_filters) > 0
    
    def setup_event_filters(self, contract_name, contract):
        """Setup event filters for a specific contract"""
        event_configs = {
            "IEMDreams": ["DreamRecorded", "DreamReward", "Staked", "Unstaked", "RewardsClaimed"],
            "OneiroSphere": ["DreamInterfaced", "DreamValidated", "MindNodeRegistered", "LucidGateAccessed"],
            "SMindToken": ["Transfer", "Mint", "Burn"],
            "LucidToken": ["Transfer", "Mint", "Burn"]
        }
        
        events_to_monitor = event_configs.get(contract_name, [])
        
        # If no specific events defined, try to get all events
        if not events_to_monitor:
            try:
                events_to_monitor = [event.event_name for event in contract.events]
            except:
                events_to_monitor = []
        
        for event_name in events_to_monitor:
            try:
                event_obj = getattr(contract.events, event_name, None)
                if event_obj:
                    event_filter = event_obj.create_filter(fromBlock="latest")
                    self.event_filters.append({
                        "contract": contract_name,
                        "event": event_name,
                        "filter": event_filter,
                        "address": contract.address
                    })
                    print(f"   📻 {event_name}")
            except Exception as e:
                print(f"   ⚠️  Could not create filter for {event_name}: {e}")
    
    def process_event(self, event_info, event_data):
        """Process and store a single event"""
        self.event_count += 1
        
        # Extract event details
        event_details = {
            "id": self.event_count,
            "timestamp": datetime.now().isoformat(),
            "block_number": event_data.blockNumber,
            "block_timestamp": w3.eth.get_block(event_data.blockNumber).timestamp,
            "contract": event_info["contract"],
            "event_name": event_info["event"],
            "contract_address": event_info["address"],
            "tx_hash": event_data.transactionHash.hex(),
            "args": {}
        }
        
        # Process event arguments
        if hasattr(event_data, 'args'):
            for key, value in event_data.args.items():
                # Handle different data types
                if hasattr(value, 'hex'):  # bytes
                    event_details["args"][key] = value.hex()
                elif isinstance(value, int) and value > 10**15:  # Large numbers (likely wei)
                    event_details["args"][key] = str(value)
                    event_details["args"][f"{key}_eth"] = str(w3.from_wei(value, 'ether'))
                else:
                    event_details["args"][key] = str(value)
        
        # Update statistics based on event type
        self.update_statistics(event_details)
        
        # Store event
        self.events_data["events"].append(event_details)
        
        # Keep only last 1000 events to prevent file bloat
        if len(self.events_data["events"]) > 1000:
            self.events_data["events"] = self.events_data["events"][-1000:]
        
        # Print event notification
        self.print_event_notification(event_details)
        
        # Save every 10 events or immediately for important events
        important_events = ["DreamRecorded", "DreamInterfaced", "Staked", "MindNodeRegistered"]
        if self.event_count % 10 == 0 or event_info["event"] in important_events:
            self.save_events()
    
    def update_statistics(self, event_details):
        """Update running statistics"""
        stats = self.events_data["statistics"]
        event_name = event_details["event_name"]
        args = event_details["args"]
        
        if event_name == "DreamRecorded":
            stats["total_dreams"] += 1
            if "dreamer" in args:
                stats["unique_dreamers"].add(args["dreamer"])
        
        elif event_name == "Staked":
            stats["total_stakes"] += 1
        
        elif event_name in ["RewardsClaimed", "DreamReward"]:
            stats["total_rewards"] += 1
            
        elif event_name == "DreamInterfaced":
            if "dreamer" in args:
                stats["unique_dreamers"].add(args["dreamer"])
    
    def print_event_notification(self, event_details):
        """Print formatted event notification"""
        print(f"\n💫 Event #{event_details['id']}: {event_details['contract']}.{event_details['event_name']}")
        print(f"   🕒 {datetime.fromisoformat(event_details['timestamp']).strftime('%H:%M:%S')}")
        print(f"   📦 Block: {event_details['block_number']}")
        print(f"   🔗 TX: {event_details['tx_hash'][:20]}...")
        
        # Show relevant args
        for key, value in event_details["args"].items():
            if key.endswith("_eth"):
                continue  # Skip ETH converted values in display
            
            display_value = value
            if isinstance(value, str) and len(value) > 50:
                display_value = value[:47] + "..."
            
            print(f"   📝 {key}: {display_value}")
    
    def print_statistics(self):
        """Print current statistics"""
        stats = self.events_data["statistics"]
        print(f"\n📊 DREAM MINING STATISTICS")
        print(f"   Total Dreams: {stats['total_dreams']}")
        print(f"   Total Stakes: {stats['total_stakes']}")
        print(f"   Total Rewards: {stats['total_rewards']}")
        print(f"   Unique Dreamers: {len(stats['unique_dreamers'])}")
        print(f"   Events Captured: {len(self.events_data['events'])}")
    
    def monitor_events(self):
        """Main monitoring loop"""
        if not self.setup_contracts():
            return
        
        print("\n🎯 Dream Looter is now monitoring the network...")
        print("   Press Ctrl+C to stop\n")
        
        last_stats_time = time.time()
        
        while self.running:
            try:
                # Check all event filters
                for event_info in self.event_filters:
                    try:
                        for event_data in event_info["filter"].get_new_entries():
                            self.process_event(event_info, event_data)
                    except Exception as e:
                        print(f"⚠️  Error reading {event_info['contract']}.{event_info['event']}: {e}")
                
                # Print statistics every 60 seconds
                if time.time() - last_stats_time > 60:
                    self.print_statistics()
                    last_stats_time = time.time()
                
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)
        
        # Final save and statistics
        self.save_events()
        self.print_statistics()
        print(f"\n🎯 Dream Looter stopped. Total events captured: {self.event_count}")

def main():
    print("🔍 IEM Dream Looter - Event Monitoring Agent")
    print("=" * 50)
    print(f"Network: SKALE Europa Hub ({CHAIN_ID})")
    print(f"RPC: {RPC}")
    print("=" * 50)
    
    looter = DreamLooter()
    looter.monitor_events()

if __name__ == "__main__":
    main()