#!/usr/bin/env python3
"""
Multi-Chain Deployment Script
============================
Handles zero-cost deployment across Solana, SKALE, and EVM chains
with relayer integration for gasless transactions.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Optional
from pathlib import Path

# Blockchain clients
from web3 import Web3
try:
    from solana.rpc.api import Client as SolanaClient
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_IMPORTS_OK = True
except ImportError:
    SOLANA_IMPORTS_OK = False

# Deployment modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.iem_syndicate import compile_contract, deploy_contract, load_memory, save_memory

class MultiChainDeployer:
    """Zero-cost multi-chain deployment system"""
    
    def __init__(self, chain: str, environment: str, gasless: bool = True):
        self.chain = chain
        self.environment = environment
        self.gasless = gasless
        self.deployment_config = self._load_deployment_config()
        self.clients = self._init_clients()
        
    def _load_deployment_config(self) -> Dict:
        """Load deployment configuration for all chains"""
        config = {
            "solana": {
                "mainnet": {
                    "rpc": os.getenv("SOLANA_RPC_URL", "https://mainnet.helius-rpc.com"),
                    "treasury": os.getenv("TREASURY_ADDRESS", "4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a"),
                    "cluster": "mainnet-beta"
                },
                "testnet": {
                    "rpc": "https://api.testnet.solana.com",
                    "treasury": "",
                    "cluster": "testnet"
                },
                "devnet": {
                    "rpc": "https://api.devnet.solana.com", 
                    "treasury": "",
                    "cluster": "devnet"
                }
            },
            "skale": {
                "mainnet": {
                    "rpc": os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat"),
                    "chain_id": int(os.getenv("SKALE_CHAIN_ID", "2046399126")),
                    "gas_price": 0,
                    "name": "Europa Hub"
                }
            },
            "polygon": {
                "mainnet": {
                    "rpc": "https://polygon.llamarpc.com",
                    "chain_id": 137,
                    "gas_price": "auto",
                    "name": "Polygon Mainnet",
                    "relayers": ["biconomy", "gelato"]
                },
                "testnet": {
                    "rpc": "https://rpc-mumbai.maticvigil.com",
                    "chain_id": 80001,
                    "gas_price": "auto", 
                    "name": "Polygon Mumbai",
                    "relayers": ["biconomy"]
                }
            },
            "base": {
                "mainnet": {
                    "rpc": "https://base.llamarpc.com",
                    "chain_id": 8453,
                    "gas_price": "auto",
                    "name": "Base Mainnet",
                    "relayers": ["biconomy"]
                },
                "testnet": {
                    "rpc": "https://sepolia.base.org",
                    "chain_id": 84532,
                    "gas_price": "auto",
                    "name": "Base Sepolia",
                    "relayers": ["biconomy"]
                }
            },
            "arbitrum": {
                "mainnet": {
                    "rpc": "https://arbitrum.llamarpc.com",
                    "chain_id": 42161,
                    "gas_price": "auto",
                    "name": "Arbitrum One",
                    "relayers": ["biconomy", "gelato"]
                }
            }
        }
        return config.get(self.chain, {}).get(self.environment, {})
    
    def _init_clients(self) -> Dict:
        """Initialize blockchain clients"""
        clients = {}
        
        if self.chain == "solana" and SOLANA_IMPORTS_OK:
            clients['solana'] = SolanaClient(self.deployment_config.get("rpc"))
        elif self.chain != "solana":
            # EVM-compatible chains
            rpc_url = self.deployment_config.get("rpc")
            if rpc_url:
                clients['evm'] = Web3(Web3.HTTPProvider(rpc_url))
                
        return clients
    
    def deploy_dream_contracts(self) -> Dict:
        """Deploy Dream ecosystem contracts to target chain"""
        print(f"🚀 Deploying Dream contracts to {self.chain} ({self.environment})")
        
        deployment_results = {}
        
        if self.chain == "solana":
            # Deploy SPL Token 2022 suite
            deployment_results = self._deploy_solana_contracts()
        else:
            # Deploy EVM contracts
            deployment_results = self._deploy_evm_contracts()
            
        # Save deployment info
        self._save_deployment_info(deployment_results)
        
        return deployment_results
    
    def _deploy_solana_contracts(self) -> Dict:
        """Deploy contracts to Solana"""
        print("📦 Deploying SPL Token 2022 suite...")
        
        # Use existing Solana agent
        import subprocess
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "deploy_tokens"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Solana contracts deployed successfully!")
            return {"status": "success", "output": result.stdout}
        else:
            print("❌ Solana deployment failed:")
            print(result.stderr)
            return {"status": "failed", "error": result.stderr}
    
    def _deploy_evm_contracts(self) -> Dict:
        """Deploy contracts to EVM-compatible chains"""
        print(f"📦 Deploying EVM contracts to {self.deployment_config.get('name', self.chain)}...")
        
        results = {}
        contracts = ["IEMDreams", "OneiroSphere"]
        
        # Set environment variables for deployment
        os.environ["BLOCKCHAIN_MODE"] = "skale" if self.chain == "skale" else "evm"
        os.environ["CHAIN_ID"] = str(self.deployment_config.get("chain_id", 1))
        
        # Deploy each contract
        for contract_name in contracts:
            try:
                print(f"🔨 Deploying {contract_name}...")
                
                # Use existing deployment system with modifications for target chain
                if self.chain != "skale":
                    # For non-SKALE chains, need to handle gas properly
                    self._configure_evm_deployment()
                
                # Deploy contract
                address, abi = deploy_contract(contract_name)
                
                results[contract_name] = {
                    "address": address,
                    "abi": abi,
                    "chain": self.chain,
                    "environment": self.environment,
                    "gasless": self.gasless,
                    "deployed_at": time.time()
                }
                
                print(f"✅ {contract_name} deployed at: {address}")
                
                # Setup relayers if gasless is enabled
                if self.gasless and self.chain != "skale":
                    self._setup_relayers_for_contract(contract_name, address)
                    
            except Exception as e:
                print(f"❌ Failed to deploy {contract_name}: {e}")
                results[contract_name] = {
                    "status": "failed",
                    "error": str(e),
                    "chain": self.chain
                }
        
        return results
    
    def _configure_evm_deployment(self):
        """Configure deployment for non-SKALE EVM chains"""
        # Get chain-specific RPC
        rpc_url = self.deployment_config.get("rpc")
        os.environ["SKALE_RPC"] = rpc_url
        
        # Update chain ID
        chain_id = self.deployment_config.get("chain_id")
        os.environ["SKALE_CHAIN_ID"] = str(chain_id)
        
        print(f"🔧 Configured deployment for {self.deployment_config.get('name')}")
        print(f"   RPC: {rpc_url}")
        print(f"   Chain ID: {chain_id}")
    
    def _setup_relayers_for_contract(self, contract_name: str, contract_address: str):
        """Setup gasless relayers for deployed contract"""
        print(f"⚡ Setting up relayers for {contract_name}...")
        
        relayers = self.deployment_config.get("relayers", [])
        
        for relayer in relayers:
            try:
                if relayer == "biconomy":
                    self._setup_biconomy_relayer(contract_name, contract_address)
                elif relayer == "gelato":
                    self._setup_gelato_relayer(contract_name, contract_address)
                    
            except Exception as e:
                print(f"⚠️  Failed to setup {relayer} relayer: {e}")
    
    def _setup_biconomy_relayer(self, contract_name: str, contract_address: str):
        """Setup Biconomy gasless relayer"""
        biconomy_api_key = os.getenv("BICONOMY_API_KEY")
        if not biconomy_api_key:
            print("⚠️  BICONOMY_API_KEY not set, skipping Biconomy setup")
            return
            
        print(f"🤖 Setting up Biconomy relayer for {contract_name}")
        
        # Biconomy configuration
        biconomy_config = {
            "contract_address": contract_address,
            "contract_name": contract_name,
            "chain": self.chain,
            "api_key": biconomy_api_key,
            "methods": self._get_gasless_methods(contract_name)
        }
        
        # Save configuration for frontend
        self._save_relayer_config("biconomy", biconomy_config)
        
        print(f"✅ Biconomy relayer configured for {contract_name}")
    
    def _setup_gelato_relayer(self, contract_name: str, contract_address: str):
        """Setup Gelato gasless relayer"""
        gelato_api_key = os.getenv("GELATO_API_KEY")
        if not gelato_api_key:
            print("⚠️  GELATO_API_KEY not set, skipping Gelato setup")
            return
            
        print(f"🍦 Setting up Gelato relayer for {contract_name}")
        
        # Gelato configuration
        gelato_config = {
            "contract_address": contract_address,
            "contract_name": contract_name,
            "chain": self.chain,
            "api_key": gelato_api_key,
            "methods": self._get_gasless_methods(contract_name)
        }
        
        # Save configuration for frontend
        self._save_relayer_config("gelato", gelato_config)
        
        print(f"✅ Gelato relayer configured for {contract_name}")
    
    def _get_gasless_methods(self, contract_name: str) -> List[str]:
        """Get methods that should be gasless for each contract"""
        gasless_methods = {
            "IEMDreams": ["recordDream"],
            "OneiroSphere": ["interfaceDream", "recordDream"],
            "DreamStaking": ["stake", "unstake", "claimRewards"],
            "DreamTokenDistributor": ["claimTokens", "distributeRewards"]
        }
        return gasless_methods.get(contract_name, [])
    
    def _save_deployment_info(self, deployment_results: Dict):
        """Save deployment information"""
        deployment_dir = Path("deployments")
        deployment_dir.mkdir(exist_ok=True)
        
        # Save chain-specific deployment info
        chain_file = deployment_dir / f"{self.chain}_{self.environment}.json"
        
        deployment_info = {
            "chain": self.chain,
            "environment": self.environment,
            "config": self.deployment_config,
            "deployed_at": time.time(),
            "gasless_enabled": self.gasless,
            "contracts": deployment_results
        }
        
        with open(chain_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"💾 Deployment info saved to {chain_file}")
    
    def _save_relayer_config(self, relayer_name: str, config: Dict):
        """Save relayer configuration for frontend"""
        relayer_dir = Path("deployments/relayers")
        relayer_dir.mkdir(parents=True, exist_ok=True)
        
        relayer_file = relayer_dir / f"{relayer_name}_{self.chain}_{self.environment}.json"
        
        with open(relayer_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"🔧 Relayer config saved to {relayer_file}")
    
    def verify_deployment(self) -> bool:
        """Verify that deployment was successful"""
        print(f"🔍 Verifying deployment on {self.chain}...")
        
        try:
            if self.chain == "solana":
                return self._verify_solana_deployment()
            else:
                return self._verify_evm_deployment()
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def _verify_solana_deployment(self) -> bool:
        """Verify Solana deployment"""
        # Check if treasury exists and has tokens
        import subprocess
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "treasury_status"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Solana deployment verified!")
            return True
        else:
            print("❌ Solana verification failed")
            return False
    
    def _verify_evm_deployment(self) -> bool:
        """Verify EVM deployment"""
        try:
            memory = load_memory()
            
            # Check if contracts are deployed
            for contract_name in ["IEMDreams", "OneiroSphere"]:
                if contract_name not in memory.get("lastDeployed", {}):
                    print(f"❌ {contract_name} not found in deployment memory")
                    return False
                
                deployment = memory["lastDeployed"][contract_name]
                address = deployment.get("address")
                
                if not address:
                    print(f"❌ {contract_name} address not found")
                    return False
                
                # Check if contract code exists
                client = self.clients.get('evm')
                if client:
                    code = client.eth.get_code(address)
                    if len(code) == 0:
                        print(f"❌ {contract_name} code not found at {address}")
                        return False
                    else:
                        print(f"✅ {contract_name} verified at {address}")
            
            print("✅ EVM deployment verified!")
            return True
            
        except Exception as e:
            print(f"❌ EVM verification error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Multi-chain deployment script')
    parser.add_argument('--chain', required=True, choices=['solana', 'skale', 'polygon', 'base', 'arbitrum'],
                       help='Target blockchain')
    parser.add_argument('--environment', required=True, choices=['mainnet', 'testnet', 'devnet'],
                       help='Target environment')
    parser.add_argument('--gasless', action='store_true', default=True,
                       help='Enable gasless transactions')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing deployment')
    
    args = parser.parse_args()
    
    print(f"🌌 DreamMindLucid Multi-Chain Deployer")
    print(f"Target: {args.chain} ({args.environment})")
    print(f"Gasless: {args.gasless}")
    print("=" * 50)
    
    deployer = MultiChainDeployer(args.chain, args.environment, args.gasless)
    
    if args.verify_only:
        success = deployer.verify_deployment()
        sys.exit(0 if success else 1)
    else:
        # Deploy contracts
        results = deployer.deploy_dream_contracts()
        
        # Verify deployment
        verification_success = deployer.verify_deployment()
        
        if verification_success:
            print("🎉 Deployment completed successfully!")
            sys.exit(0)
        else:
            print("❌ Deployment verification failed")
            sys.exit(1)

if __name__ == "__main__":
    main()