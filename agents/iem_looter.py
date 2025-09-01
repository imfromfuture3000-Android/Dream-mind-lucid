#!/usr/bin/env python3
"""
IEM Looter - Event Listener for Dream-Mind-Lucid
-----------------------------------------------
Specialized script for real-time event monitoring and data persistence.
Listens for DreamRecorded and DreamInterfaced events, saves to iem_memory.json.
Last Updated: September 01, 2025
"""

import os
import json
import time
import logging
from typing import Dict, Any
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IEMLooter:
    """Event listener and data persistence for dream events"""
    
    def __init__(self):
        # SKALE Network Configuration
        self.rpc_url = os.getenv('SKALE_RPC', 'https://mainnet.skalenodes.com/v1/elated-tan-skat')
        self.chain_id = int(os.getenv('SKALE_CHAIN_ID', '2046399126'))
        
        # For Infura integration
        infura_project_id = os.getenv('INFURA_PROJECT_ID')
        if infura_project_id and infura_project_id != 'your-infura-api-key':
            self.infura_rpc = f"https://skale-mainnet.infura.io/v3/{infura_project_id}"
        else:
            self.infura_rpc = None
        
        # Initialize Web3
        self.w3 = self._init_web3()
        
        # Memory file for persistent storage
        self.memory_file = "iem_memory.json"
    
    def _init_web3(self) -> Web3:
        """Initialize Web3 connection with fallback options"""
        # Try primary SKALE RPC first
        try:
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if w3.is_connected():
                logger.info(f"🔗 Connected to SKALE Network via {self.rpc_url}")
                return w3
        except Exception as e:
            logger.warning(f"Primary RPC connection failed: {e}")
        
        # Try Infura as fallback if configured
        if self.infura_rpc:
            try:
                w3 = Web3(Web3.HTTPProvider(self.infura_rpc))
                if w3.is_connected():
                    logger.info(f"🔗 Connected via Infura RPC: {self.infura_rpc}")
                    return w3
            except Exception as e:
                logger.warning(f"Infura RPC connection failed: {e}")
        
        raise ConnectionError("Could not connect to any RPC endpoint")
    
    def load_memory(self) -> Dict[str, Any]:
        """Load persistent memory from JSON file"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "deployments": {},
                "lastDeployed": {},
                "events": [],
                "audits": {},
                "looter_stats": {
                    "total_events": 0,
                    "last_run": None,
                    "contracts_monitored": []
                }
            }
    
    def save_memory(self, memory: Dict[str, Any]) -> None:
        """Save memory to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def monitor_events(self, contract_address: str = None, duration: int = 300):
        """Monitor dream events and save to memory"""
        logger.info(f"👁️ Starting IEM Looter - monitoring for {duration} seconds...")
        
        memory = self.load_memory()
        
        # If no contract address provided, try to get the latest deployed contract
        if not contract_address:
            if memory["lastDeployed"]:
                # Get the most recent deployment
                latest_contract = None
                latest_timestamp = 0
                
                for name, info in memory["lastDeployed"].items():
                    if info.get("timestamp", 0) > latest_timestamp:
                        latest_timestamp = info["timestamp"]
                        latest_contract = info
                
                if latest_contract:
                    contract_address = latest_contract["address"]
                    logger.info(f"📍 Monitoring latest deployed contract: {contract_address}")
                else:
                    logger.error("❌ No deployed contracts found in memory")
                    return
            else:
                logger.error("❌ No contract address provided and no deployments found")
                return
        
        # Get contract ABI from memory
        contract_info = None
        for name, info in memory["lastDeployed"].items():
            if info["address"] == contract_address:
                contract_info = info
                break
        
        if not contract_info:
            logger.error(f"❌ Contract ABI not found for {contract_address}")
            return
        
        try:
            # Create contract instance
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=contract_info["abi"]
            )
            
            # Create event filters
            event_filters = []
            
            # Add filters for different event types
            try:
                if hasattr(contract.events, 'DreamRecorded'):
                    event_filters.append(('DreamRecorded', contract.events.DreamRecorded.create_filter(fromBlock='latest')))
                    logger.info("📡 Monitoring DreamRecorded events")
                
                if hasattr(contract.events, 'DreamInterfaced'):
                    event_filters.append(('DreamInterfaced', contract.events.DreamInterfaced.create_filter(fromBlock='latest')))
                    logger.info("📡 Monitoring DreamInterfaced events")
                
                if hasattr(contract.events, 'QuantumEntanglement'):
                    event_filters.append(('QuantumEntanglement', contract.events.QuantumEntanglement.create_filter(fromBlock='latest')))
                    logger.info("📡 Monitoring QuantumEntanglement events")
                
                if hasattr(contract.events, 'LucidityScored'):
                    event_filters.append(('LucidityScored', contract.events.LucidityScored.create_filter(fromBlock='latest')))
                    logger.info("📡 Monitoring LucidityScored events")
                    
            except Exception as e:
                logger.warning(f"Could not create all event filters: {e}")
            
            if not event_filters:
                logger.warning("⚠️ No event filters created - contract may not have the expected events")
                return
            
            # Update looter stats
            memory["looter_stats"]["last_run"] = time.time()
            if contract_address not in memory["looter_stats"]["contracts_monitored"]:
                memory["looter_stats"]["contracts_monitored"].append(contract_address)
            
            events_found = 0
            start_time = time.time()
            
            logger.info(f"🔍 Listening for events... (Press Ctrl+C to stop)")
            
            while time.time() - start_time < duration:
                for event_name, event_filter in event_filters:
                    try:
                        for event in event_filter.get_new_entries():
                            events_found += 1
                            logger.info(f"🌟 {event_name} event detected!")
                            logger.info(f"   📍 Contract: {contract_address}")
                            logger.info(f"   🧱 Block: {event.blockNumber}")
                            logger.info(f"   🔗 Transaction: {event.transactionHash.hex()}")
                            logger.info(f"   📊 Args: {dict(event.args)}")
                            
                            # Save event to memory
                            event_data = {
                                "type": event_name,
                                "contract_address": contract_address,
                                "tx_hash": event.transactionHash.hex(),
                                "block_number": event.blockNumber,
                                "timestamp": time.time(),
                                "args": {k: str(v) for k, v in event.args.items()},  # Convert to string for JSON serialization
                                "detected_by": "iem_looter"
                            }
                            
                            memory["events"].append(event_data)
                            memory["looter_stats"]["total_events"] += 1
                            self.save_memory(memory)
                            
                            logger.info(f"💾 Event saved to {self.memory_file}")
                            
                    except Exception as e:
                        logger.debug(f"Event filter error for {event_name}: {e}")
                
                time.sleep(2)  # Check every 2 seconds
                
                # Show progress every 30 seconds
                if int(time.time() - start_time) % 30 == 0:
                    elapsed = int(time.time() - start_time)
                    remaining = duration - elapsed
                    logger.info(f"⏱️ Monitoring... {elapsed}s elapsed, {remaining}s remaining, {events_found} events found")
            
            logger.info(f"✅ Event monitoring completed. Found {events_found} events in {duration} seconds.")
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Event monitoring failed: {str(e)}")
    
    def show_stats(self):
        """Show statistics about monitored events"""
        memory = self.load_memory()
        stats = memory.get("looter_stats", {})
        
        print("\n📊 IEM Looter Statistics")
        print("=" * 40)
        print(f"Total Events Detected: {stats.get('total_events', 0)}")
        print(f"Contracts Monitored: {len(stats.get('contracts_monitored', []))}")
        
        if stats.get('last_run'):
            print(f"Last Run: {time.ctime(stats['last_run'])}")
        
        print(f"\nRecent Events (last 5):")
        recent_events = memory.get("events", [])[-5:]
        if recent_events:
            for event in recent_events:
                print(f"  • {event['type']} - {time.ctime(event['timestamp'])}")
                print(f"    TX: {event['tx_hash']}")
        else:
            print("  No events recorded yet")
        
        print(f"\nTotal Events in Memory: {len(memory.get('events', []))}")

def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("IEM Looter - Dream Event Monitor")
        print("Usage:")
        print("  python iem_looter.py [contract_address] [duration]")
        print("  python iem_looter.py stats")
        print("")
        print("If no contract_address provided, monitors the latest deployed contract")
        print("Default duration is 300 seconds (5 minutes)")
        return
    
    looter = IEMLooter()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        looter.show_stats()
        return
    
    # Get contract address and duration from command line
    contract_address = sys.argv[1] if len(sys.argv) > 1 else None
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    try:
        looter.monitor_events(contract_address, duration)
    except KeyboardInterrupt:
        print("\n👋 IEM Looter stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()