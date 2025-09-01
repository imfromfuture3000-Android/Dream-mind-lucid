#!/usr/bin/env python3
"""
IEM Syndicate - Multi-Agent Dream Deployment System
-------------------------------------------------
Handles deployment, auditing, event listening, and oracle functions
for the Dream-Mind-Lucid ecosystem on SKALE Network.
Last Updated: September 01, 2025
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, Optional
from web3 import Web3
from solcx import compile_standard, install_solc
from eth_account import Account
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IEMSyndicate:
    """Multi-agent system for Dream-Mind-Lucid operations"""
    
    def __init__(self):
        # SKALE Network Configuration
        self.rpc_url = os.getenv('SKALE_RPC', 'https://mainnet.skalenodes.com/v1/elated-tan-skat')
        self.chain_id = int(os.getenv('SKALE_CHAIN_ID', '2046399126'))
        self.private_key = os.getenv('DEPLOYER_KEY', '')
        
        # For Infura integration (if using Infura as backup RPC)
        infura_project_id = os.getenv('INFURA_PROJECT_ID')
        if infura_project_id and infura_project_id != 'your-infura-api-key':
            self.infura_rpc = f"https://skale-mainnet.infura.io/v3/{infura_project_id}"
        else:
            self.infura_rpc = None
            
        # Biconomy configuration
        self.biconomy_api_key = os.getenv('BICONOMY_API_KEY')
        self.forwarder_address = os.getenv('FORWARDER_ADDRESS')
        
        # Initialize Web3
        self.w3 = self._init_web3()
        
        # Memory file for persistent storage
        self.memory_file = "iem_memory.json"
        
        # Ensure Solidity compiler is installed
        try:
            install_solc("0.8.20")
        except Exception as e:
            logger.warning(f"Solidity compiler installation warning: {e}")
    
    def _init_web3(self) -> Web3:
        """Initialize Web3 connection with fallback options"""
        # Try primary SKALE RPC first
        try:
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if w3.is_connected():
                logger.info(f"Connected to SKALE Network via {self.rpc_url}")
                return w3
        except Exception as e:
            logger.warning(f"Primary RPC connection failed: {e}")
        
        # Try Infura as fallback if configured
        if self.infura_rpc:
            try:
                w3 = Web3(Web3.HTTPProvider(self.infura_rpc))
                if w3.is_connected():
                    logger.info(f"Connected via Infura RPC: {self.infura_rpc}")
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
                "audits": {}
            }
    
    def save_memory(self, memory: Dict[str, Any]) -> None:
        """Save memory to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def compile_contract(self, contract_name: str) -> Dict[str, Any]:
        """Compile Solidity contract"""
        contract_path = f"contracts/{contract_name}.sol"
        
        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
        
        with open(contract_path, 'r') as f:
            source_code = f.read()
        
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                f"{contract_name}.sol": {
                    "content": source_code
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode", "evm.deployedBytecode"]
                    }
                }
            }
        }, solc_version="0.8.20")
        
        return compiled_sol["contracts"][f"{contract_name}.sol"][contract_name]
    
    def deploy_contract(self, contract_name: str) -> Optional[str]:
        """Deploy a smart contract to SKALE Network"""
        logger.info(f"🚀 Deploying {contract_name} contract...")
        
        if not self.private_key or self.private_key == 'your-wallet-private-key':
            logger.error("❌ DEPLOYER_KEY not set in environment variables")
            return None
        
        try:
            # Compile contract
            compiled_contract = self.compile_contract(contract_name)
            bytecode = compiled_contract["evm"]["bytecode"]["object"]
            abi = compiled_contract["abi"]
            
            # Create account from private key
            account = Account.from_key(self.private_key)
            
            # Create contract instance
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # For SKALE, gas price is 0 (zero-gas transactions)
            transaction = contract.constructor().build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 5000000,  # High gas limit for safety
                'gasPrice': 0,   # Zero gas price on SKALE
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"⏳ Transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                logger.info(f"✅ {contract_name} deployed successfully!")
                logger.info(f"📍 Contract Address: {contract_address}")
                logger.info(f"🔗 Transaction Hash: {tx_hash.hex()}")
                
                # Save deployment info
                memory = self.load_memory()
                memory["lastDeployed"][contract_name] = {
                    "address": contract_address,
                    "abi": abi,
                    "timestamp": time.time(),
                    "tx_hash": tx_hash.hex(),
                    "deployer": account.address
                }
                memory["deployments"][contract_address] = {
                    "name": contract_name,
                    "deployed_at": time.time(),
                    "deployer": account.address
                }
                self.save_memory(memory)
                
                return contract_address
            else:
                logger.error(f"❌ Transaction failed: {tx_receipt}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Deployment failed: {str(e)}")
            return None
    
    def audit_contract(self, contract_address: str) -> Dict[str, Any]:
        """Audit deployed contract and compute integrity hash"""
        logger.info(f"🔍 Auditing contract at {contract_address}...")
        
        try:
            # Get contract bytecode
            bytecode = self.w3.eth.get_code(contract_address)
            
            # Compute SHA-256 hash for integrity
            integrity_hash = hashlib.sha256(bytecode).hexdigest()
            
            # Get basic contract info
            balance = self.w3.eth.get_balance(contract_address)
            
            audit_result = {
                "address": contract_address,
                "bytecode_hash": integrity_hash,
                "balance": balance,
                "timestamp": time.time(),
                "bytecode_size": len(bytecode)
            }
            
            # Save audit result
            memory = self.load_memory()
            memory["audits"][contract_address] = audit_result
            self.save_memory(memory)
            
            logger.info(f"✅ Audit completed. Hash: {integrity_hash[:16]}...")
            return audit_result
            
        except Exception as e:
            logger.error(f"❌ Audit failed: {str(e)}")
            return {}
    
    def record_test_dream(self, contract_address: str, dream_text: str) -> Optional[str]:
        """Record a test dream transaction to verify deployment"""
        logger.info("🌙 Recording test dream...")
        
        try:
            # Load contract ABI from memory
            memory = self.load_memory()
            contract_info = None
            
            for name, info in memory["lastDeployed"].items():
                if info["address"] == contract_address:
                    contract_info = info
                    break
            
            if not contract_info:
                logger.error("❌ Contract ABI not found in memory")
                return None
            
            # Create contract instance
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=contract_info["abi"]
            )
            
            # Create account
            account = Account.from_key(self.private_key)
            
            # For OneiroSphere, we need to use interfaceDream function
            # For IEMDreams, we use recordDream function
            if "interfaceDream" in [func.function_identifier for func in contract.all_functions()]:
                # This is OneiroSphere - need IPFS hash
                ipfs_hash = f"QmTest{int(time.time())}"  # Mock IPFS hash for testing
                function_call = contract.functions.interfaceDream(ipfs_hash)
                logger.info(f"📡 Using interfaceDream with IPFS hash: {ipfs_hash}")
            else:
                # This is IEMDreams - use direct dream text
                function_call = contract.functions.recordDream(dream_text)
                logger.info(f"📝 Using recordDream with text: {dream_text[:50]}...")
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(account.address)
            transaction = function_call.build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': 0,
                'chainId': self.chain_id
            })
            
            # Sign and send
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"⏳ Dream transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            if tx_receipt.status == 1:
                logger.info("✅ Test dream recorded successfully!")
                logger.info(f"🔗 Transaction Hash: {tx_hash.hex()}")
                
                # Save event
                memory = self.load_memory()
                memory["events"].append({
                    "type": "test_dream",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": time.time(),
                    "contract": contract_address,
                    "dream": dream_text
                })
                self.save_memory(memory)
                
                return tx_hash.hex()
            else:
                logger.error(f"❌ Dream transaction failed: {tx_receipt}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Dream recording failed: {str(e)}")
            return None
    
    def listen_for_events(self, contract_address: str, duration: int = 60):
        """Listen for contract events (Oracle agent functionality)"""
        logger.info(f"👂 Listening for events from {contract_address} for {duration} seconds...")
        
        try:
            memory = self.load_memory()
            contract_info = None
            
            for name, info in memory["lastDeployed"].items():
                if info["address"] == contract_address:
                    contract_info = info
                    break
            
            if not contract_info:
                logger.error("❌ Contract ABI not found")
                return
            
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
                if hasattr(contract.events, 'DreamInterfaced'):
                    event_filters.append(('DreamInterfaced', contract.events.DreamInterfaced.create_filter(fromBlock='latest')))
                if hasattr(contract.events, 'QuantumEntanglement'):
                    event_filters.append(('QuantumEntanglement', contract.events.QuantumEntanglement.create_filter(fromBlock='latest')))
            except Exception as e:
                logger.warning(f"Could not create all event filters: {e}")
            
            if not event_filters:
                logger.warning("No event filters created")
                return
            
            start_time = time.time()
            while time.time() - start_time < duration:
                for event_name, event_filter in event_filters:
                    try:
                        for event in event_filter.get_new_entries():
                            logger.info(f"🌟 {event_name} event detected!")
                            logger.info(f"   Block: {event.blockNumber}")
                            logger.info(f"   Transaction: {event.transactionHash.hex()}")
                            logger.info(f"   Args: {dict(event.args)}")
                            
                            # Save event to memory
                            memory = self.load_memory()
                            memory["events"].append({
                                "type": event_name,
                                "tx_hash": event.transactionHash.hex(),
                                "block_number": event.blockNumber,
                                "timestamp": time.time(),
                                "args": dict(event.args)
                            })
                            self.save_memory(memory)
                    except Exception as e:
                        logger.debug(f"Event filter error: {e}")
                
                time.sleep(2)  # Check every 2 seconds
                
        except Exception as e:
            logger.error(f"❌ Event listening failed: {str(e)}")

def main():
    """Main function for command-line usage"""
    syndicate = IEMSyndicate()
    
    if len(sys.argv) < 2:
        print("Usage: python iem_syndicate.py <command> [args]")
        print("Commands:")
        print("  deploy <contract_name>  - Deploy contract (IEMDreams or OneiroSphere)")
        print("  audit <contract_address> - Audit deployed contract")
        print("  test <contract_address> <dream_text> - Record test dream")
        print("  listen <contract_address> [duration] - Listen for events")
        print("  status - Show deployment status")
        return
    
    command = sys.argv[1].lower()
    
    if command == "deploy":
        if len(sys.argv) < 3:
            print("Usage: python iem_syndicate.py deploy <contract_name>")
            return
        
        contract_name = sys.argv[2]
        if contract_name not in ["IEMDreams", "OneiroSphere"]:
            print("❌ Invalid contract name. Use 'IEMDreams' or 'OneiroSphere'")
            return
        
        address = syndicate.deploy_contract(contract_name)
        if address:
            print(f"\n🎉 Deployment successful!")
            print(f"Contract Address: {address}")
            print(f"SKALE Explorer: https://elated-tan-skat.explorer.mainnet.skalenodes.com/address/{address}")
    
    elif command == "audit":
        if len(sys.argv) < 3:
            print("Usage: python iem_syndicate.py audit <contract_address>")
            return
        
        result = syndicate.audit_contract(sys.argv[2])
        if result:
            print(f"\n🔍 Audit Results:")
            print(f"Address: {result['address']}")
            print(f"Bytecode Hash: {result['bytecode_hash']}")
            print(f"Balance: {result['balance']} wei")
            print(f"Bytecode Size: {result['bytecode_size']} bytes")
    
    elif command == "test":
        if len(sys.argv) < 4:
            print("Usage: python iem_syndicate.py test <contract_address> <dream_text>")
            return
        
        tx_hash = syndicate.record_test_dream(sys.argv[2], " ".join(sys.argv[3:]))
        if tx_hash:
            print(f"\n🌙 Test dream recorded!")
            print(f"Transaction Hash: {tx_hash}")
    
    elif command == "listen":
        if len(sys.argv) < 3:
            print("Usage: python iem_syndicate.py listen <contract_address> [duration]")
            return
        
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        syndicate.listen_for_events(sys.argv[2], duration)
    
    elif command == "status":
        memory = syndicate.load_memory()
        print("\n📊 Deployment Status:")
        print("=" * 50)
        
        if memory["lastDeployed"]:
            for name, info in memory["lastDeployed"].items():
                print(f"Contract: {name}")
                print(f"  Address: {info['address']}")
                print(f"  Deployed: {time.ctime(info['timestamp'])}")
                print(f"  Deployer: {info['deployer']}")
                print()
        else:
            print("No deployments found.")
        
        if memory["events"]:
            print(f"Total Events Recorded: {len(memory['events'])}")
            recent_events = memory["events"][-3:]  # Show last 3 events
            for event in recent_events:
                print(f"  {event['type']} - {time.ctime(event['timestamp'])}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()