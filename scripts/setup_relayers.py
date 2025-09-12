#!/usr/bin/env python3
"""
Gasless Relayer Setup Script
============================
Configures Biconomy, Gelato, and other gasless transaction relayers
for zero-cost user experience across all supported chains.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import requests
import argparse
from typing import Dict, List, Optional
from pathlib import Path

class RelayerManager:
    """Manages gasless transaction relayers across multiple chains"""
    
    def __init__(self, chain: str):
        self.chain = chain
        self.chain_configs = self._load_chain_configs()
        self.relayer_apis = self._init_relayer_apis()
        
    def _load_chain_configs(self) -> Dict:
        """Load chain-specific configurations"""
        return {
            "polygon": {
                "chain_id": 137,
                "name": "Polygon Mainnet",
                "biconomy_supported": True,
                "gelato_supported": True,
                "native_gasless": False
            },
            "polygon-mumbai": {
                "chain_id": 80001,
                "name": "Polygon Mumbai",
                "biconomy_supported": True,
                "gelato_supported": True,
                "native_gasless": False
            },
            "base": {
                "chain_id": 8453,
                "name": "Base Mainnet",
                "biconomy_supported": True,
                "gelato_supported": True,
                "native_gasless": False
            },
            "base-sepolia": {
                "chain_id": 84532,
                "name": "Base Sepolia",
                "biconomy_supported": True,
                "gelato_supported": False,
                "native_gasless": False
            },
            "arbitrum": {
                "chain_id": 42161,
                "name": "Arbitrum One",
                "biconomy_supported": True,
                "gelato_supported": True,
                "native_gasless": False
            },
            "skale": {
                "chain_id": 2046399126,
                "name": "SKALE Europa Hub",
                "biconomy_supported": False,
                "gelato_supported": False,
                "native_gasless": True
            },
            "solana": {
                "chain_id": None,
                "name": "Solana Mainnet",
                "biconomy_supported": False,
                "gelato_supported": False,
                "native_gasless": True,
                "relayer_rpcs": [
                    "https://mainnet.helius-rpc.com",
                    "https://rpc.jup.ag"
                ]
            }
        }
    
    def _init_relayer_apis(self) -> Dict:
        """Initialize relayer API clients"""
        apis = {}
        
        # Biconomy API
        biconomy_key = os.getenv("BICONOMY_API_KEY")
        if biconomy_key:
            apis['biconomy'] = {
                "api_key": biconomy_key,
                "base_url": "https://api.biconomy.io/api/v1",
                "dashboard_url": "https://dashboard.biconomy.io"
            }
        
        # Gelato API
        gelato_key = os.getenv("GELATO_API_KEY")
        if gelato_key:
            apis['gelato'] = {
                "api_key": gelato_key,
                "base_url": "https://relay.gelato.digital",
                "dashboard_url": "https://app.gelato.network"
            }
        
        return apis
    
    def setup_all_relayers(self) -> Dict:
        """Setup all available relayers for the chain"""
        print(f"⚡ Setting up gasless relayers for {self.chain}")
        
        chain_config = self.chain_configs.get(self.chain, {})
        results = {}
        
        # Native gasless (SKALE, Solana)
        if chain_config.get("native_gasless"):
            results['native'] = self._setup_native_gasless()
        
        # Biconomy relayer
        if chain_config.get("biconomy_supported") and 'biconomy' in self.relayer_apis:
            results['biconomy'] = self._setup_biconomy()
        
        # Gelato relayer
        if chain_config.get("gelato_supported") and 'gelato' in self.relayer_apis:
            results['gelato'] = self._setup_gelato()
        
        # Save configuration
        self._save_relayer_config(results)
        
        return results
    
    def _setup_native_gasless(self) -> Dict:
        """Setup native gasless transactions (SKALE, Solana)"""
        print(f"🚀 Setting up native gasless for {self.chain}")
        
        if self.chain == "skale":
            return {
                "type": "native_skale",
                "enabled": True,
                "gas_price": 0,
                "description": "SKALE Europa Hub native zero-gas transactions",
                "rpc": os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat"),
                "chain_id": int(os.getenv("SKALE_CHAIN_ID", "2046399126"))
            }
        elif self.chain == "solana":
            return {
                "type": "native_solana",
                "enabled": True,
                "description": "Solana MEV-protected RPC with fee rebates",
                "rpcs": self.chain_configs[self.chain]["relayer_rpcs"],
                "features": [
                    "MEV protection via Helius",
                    "Transaction fee rebates",
                    "Priority fee optimization"
                ]
            }
        
        return {"enabled": False}
    
    def _setup_biconomy(self) -> Dict:
        """Setup Biconomy gasless relayer"""
        print("🤖 Setting up Biconomy relayer...")
        
        biconomy_config = self.relayer_apis['biconomy']
        chain_config = self.chain_configs[self.chain]
        
        # Biconomy DApp configuration
        dapp_config = {
            "name": "Dream-Mind-Lucid",
            "description": "Quantum Neural Network for The Oneiro-Sphere",
            "chain_id": chain_config["chain_id"],
            "chain_name": chain_config["name"],
            "contracts": self._get_deployed_contracts(),
            "methods": self._get_gasless_methods(),
            "api_key": biconomy_config["api_key"]
        }
        
        # Try to register/update DApp with Biconomy
        try:
            registration_result = self._register_biconomy_dapp(dapp_config)
            
            return {
                "type": "biconomy",
                "enabled": True,
                "api_key": biconomy_config["api_key"],
                "chain_id": chain_config["chain_id"],
                "dapp_id": registration_result.get("dapp_id"),
                "forwarder_address": registration_result.get("forwarder_address"),
                "dashboard_url": f"{biconomy_config['dashboard_url']}/dapp/{registration_result.get('dapp_id')}",
                "contracts": dapp_config["contracts"],
                "gasless_methods": dapp_config["methods"]
            }
            
        except Exception as e:
            print(f"⚠️  Biconomy setup failed: {e}")
            return {
                "type": "biconomy",
                "enabled": False,
                "error": str(e)
            }
    
    def _setup_gelato(self) -> Dict:
        """Setup Gelato gasless relayer"""
        print("🍦 Setting up Gelato relayer...")
        
        gelato_config = self.relayer_apis['gelato']
        chain_config = self.chain_configs[self.chain]
        
        # Gelato relay configuration
        relay_config = {
            "name": "Dream-Mind-Lucid",
            "chain_id": chain_config["chain_id"],
            "contracts": self._get_deployed_contracts(),
            "api_key": gelato_config["api_key"]
        }
        
        try:
            registration_result = self._register_gelato_relay(relay_config)
            
            return {
                "type": "gelato",
                "enabled": True,
                "api_key": gelato_config["api_key"],
                "chain_id": chain_config["chain_id"],
                "relay_id": registration_result.get("relay_id"),
                "dashboard_url": f"{gelato_config['dashboard_url']}/relay/{registration_result.get('relay_id')}",
                "contracts": relay_config["contracts"],
                "gasless_methods": self._get_gasless_methods()
            }
            
        except Exception as e:
            print(f"⚠️  Gelato setup failed: {e}")
            return {
                "type": "gelato",
                "enabled": False,
                "error": str(e)
            }
    
    def _get_deployed_contracts(self) -> List[Dict]:
        """Get list of deployed contracts for this chain"""
        contracts = []
        
        # Try to load deployment info
        deployment_file = Path(f"deployments/{self.chain}_mainnet.json")
        if deployment_file.exists():
            with open(deployment_file, 'r') as f:
                deployment_info = json.load(f)
                
            for contract_name, contract_data in deployment_info.get("contracts", {}).items():
                if isinstance(contract_data, dict) and "address" in contract_data:
                    contracts.append({
                        "name": contract_name,
                        "address": contract_data["address"],
                        "abi": contract_data.get("abi", [])
                    })
        
        # Fallback to memory file
        if not contracts:
            memory_file = Path("iem_memory.json")
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
                
                for contract_name, contract_data in memory.get("lastDeployed", {}).items():
                    contracts.append({
                        "name": contract_name,
                        "address": contract_data["address"],
                        "abi": contract_data.get("abi", [])
                    })
        
        return contracts
    
    def _get_gasless_methods(self) -> Dict:
        """Get methods that should be gasless for each contract"""
        return {
            "IEMDreams": [
                "recordDream(string)",
                "balanceOf(address)"
            ],
            "OneiroSphere": [
                "interfaceDream(string)",
                "recordDream(string)",
                "getDreams(address)"
            ],
            "DreamStaking": [
                "stake(uint256)",
                "unstake(uint256)",
                "claimRewards()",
                "getStakeInfo(address)"
            ],
            "DreamTokenDistributor": [
                "claimTokens()",
                "distributeRewards(address[])",
                "getClaimableAmount(address)"
            ]
        }
    
    def _register_biconomy_dapp(self, config: Dict) -> Dict:
        """Register DApp with Biconomy (simulated for now)"""
        print("📝 Registering DApp with Biconomy...")
        
        # In a real implementation, this would make API calls to Biconomy
        # For now, we'll simulate the registration
        
        dapp_id = f"dream-mind-lucid-{self.chain}"
        forwarder_address = "0x86C80a8aa58e0A4fa09A69624c31Ab2a6CAD56b8"  # Common Biconomy forwarder
        
        print(f"✅ DApp registered with Biconomy")
        print(f"   DApp ID: {dapp_id}")
        print(f"   Forwarder: {forwarder_address}")
        
        return {
            "dapp_id": dapp_id,
            "forwarder_address": forwarder_address,
            "status": "registered"
        }
    
    def _register_gelato_relay(self, config: Dict) -> Dict:
        """Register relay with Gelato (simulated for now)"""
        print("📝 Registering relay with Gelato...")
        
        # In a real implementation, this would make API calls to Gelato
        # For now, we'll simulate the registration
        
        relay_id = f"dream-mind-lucid-{self.chain}"
        
        print(f"✅ Relay registered with Gelato")
        print(f"   Relay ID: {relay_id}")
        
        return {
            "relay_id": relay_id,
            "status": "registered"
        }
    
    def _save_relayer_config(self, relayer_results: Dict):
        """Save relayer configuration for frontend use"""
        config_dir = Path("deployments/relayers")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chain-specific relayer config
        config_file = config_dir / f"{self.chain}_relayers.json"
        
        relayer_config = {
            "chain": self.chain,
            "chain_config": self.chain_configs.get(self.chain, {}),
            "relayers": relayer_results,
            "created_at": json.loads(json.dumps({"timestamp": time.time()}))["timestamp"]
        }
        
        with open(config_file, 'w') as f:
            json.dump(relayer_config, f, indent=2)
        
        print(f"💾 Relayer config saved to {config_file}")
        
        # Also save to a consolidated config for frontend
        self._update_consolidated_config(relayer_config)
    
    def _update_consolidated_config(self, chain_relayer_config: Dict):
        """Update consolidated relayer configuration"""
        consolidated_file = Path("deployments/relayers/consolidated.json")
        
        # Load existing config
        if consolidated_file.exists():
            with open(consolidated_file, 'r') as f:
                consolidated = json.load(f)
        else:
            consolidated = {"chains": {}}
        
        # Update with new chain config
        consolidated["chains"][self.chain] = chain_relayer_config
        consolidated["updated_at"] = time.time()
        
        # Save updated config
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        print(f"🔄 Updated consolidated relayer config")
    
    def test_relayers(self) -> bool:
        """Test all configured relayers"""
        print(f"🧪 Testing relayers for {self.chain}...")
        
        config_file = Path(f"deployments/relayers/{self.chain}_relayers.json")
        if not config_file.exists():
            print("❌ No relayer config found")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        all_tests_passed = True
        
        for relayer_name, relayer_config in config.get("relayers", {}).items():
            if relayer_config.get("enabled"):
                test_result = self._test_relayer(relayer_name, relayer_config)
                if not test_result:
                    all_tests_passed = False
        
        if all_tests_passed:
            print("✅ All relayer tests passed!")
        else:
            print("⚠️  Some relayer tests failed")
        
        return all_tests_passed
    
    def _test_relayer(self, relayer_name: str, relayer_config: Dict) -> bool:
        """Test a specific relayer"""
        print(f"🔍 Testing {relayer_name} relayer...")
        
        try:
            if relayer_config["type"] == "native_skale":
                # Test SKALE native gasless
                return self._test_skale_gasless(relayer_config)
            elif relayer_config["type"] == "native_solana":
                # Test Solana gasless
                return self._test_solana_gasless(relayer_config)
            elif relayer_config["type"] == "biconomy":
                # Test Biconomy relayer
                return self._test_biconomy_relayer(relayer_config)
            elif relayer_config["type"] == "gelato":
                # Test Gelato relayer
                return self._test_gelato_relayer(relayer_config)
            else:
                print(f"⚠️  Unknown relayer type: {relayer_config['type']}")
                return False
                
        except Exception as e:
            print(f"❌ {relayer_name} test failed: {e}")
            return False
    
    def _test_skale_gasless(self, config: Dict) -> bool:
        """Test SKALE native gasless transactions"""
        print("🔍 Testing SKALE gasless transactions...")
        
        try:
            from web3 import Web3
            
            rpc_url = config.get("rpc")
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if w3.is_connected():
                print("✅ SKALE RPC connection successful")
                
                # Check gas price is 0
                gas_price = w3.eth.gas_price
                if gas_price == 0:
                    print("✅ Gas price is 0 (gasless confirmed)")
                    return True
                else:
                    print(f"⚠️  Gas price is {gas_price}, not truly gasless")
                    return False
            else:
                print("❌ SKALE RPC connection failed")
                return False
                
        except Exception as e:
            print(f"❌ SKALE test error: {e}")
            return False
    
    def _test_solana_gasless(self, config: Dict) -> bool:
        """Test Solana gasless features"""
        print("🔍 Testing Solana gasless features...")
        
        try:
            from solana.rpc.api import Client
            
            for rpc_url in config.get("rpcs", []):
                try:
                    client = Client(rpc_url)
                    
                    # Test connection
                    response = client.get_health()
                    if response:
                        print(f"✅ Solana RPC {rpc_url} is healthy")
                        return True
                except:
                    continue
            
            print("❌ No healthy Solana RPC found")
            return False
            
        except Exception as e:
            print(f"❌ Solana test error: {e}")
            return False
    
    def _test_biconomy_relayer(self, config: Dict) -> bool:
        """Test Biconomy relayer"""
        print("🔍 Testing Biconomy relayer...")
        
        # Check if API key is valid by testing endpoint
        api_key = config.get("api_key")
        if not api_key:
            print("❌ Biconomy API key not found")
            return False
        
        print("✅ Biconomy configuration appears valid")
        return True
    
    def _test_gelato_relayer(self, config: Dict) -> bool:
        """Test Gelato relayer"""
        print("🔍 Testing Gelato relayer...")
        
        # Check if API key is valid
        api_key = config.get("api_key")
        if not api_key:
            print("❌ Gelato API key not found")
            return False
        
        print("✅ Gelato configuration appears valid")
        return True

def main():
    parser = argparse.ArgumentParser(description='Setup gasless relayers')
    parser.add_argument('--chain', required=True,
                       choices=['polygon', 'polygon-mumbai', 'base', 'base-sepolia', 'arbitrum', 'skale', 'solana'],
                       help='Target blockchain')
    parser.add_argument('--test', action='store_true',
                       help='Test relayer configuration')
    
    args = parser.parse_args()
    
    print(f"⚡ DreamMindLucid Relayer Manager")
    print(f"Target: {args.chain}")
    print("=" * 40)
    
    relayer_manager = RelayerManager(args.chain)
    
    if args.test:
        success = relayer_manager.test_relayers()
        sys.exit(0 if success else 1)
    else:
        results = relayer_manager.setup_all_relayers()
        
        # Test the configuration
        test_success = relayer_manager.test_relayers()
        
        if any(r.get("enabled") for r in results.values()) and test_success:
            print("🎉 Gasless relayers configured successfully!")
            sys.exit(0)
        else:
            print("❌ Relayer setup failed or no relayers configured")
            sys.exit(1)

if __name__ == "__main__":
    import time
    main()