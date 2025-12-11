"""
Dream Token Distribution Manager
Handles deployment and management of token distribution
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import time

class TokenDistributionManager:
    def __init__(self):
        # Connect to SKALE network
        self.w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.skalenodes.com/v1/elated-tan-skat"
        ))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load configurations
        self.load_configs()
        
        # Contract instances
        self.distributor = None
        self.tokens = {}
        
    def load_configs(self):
        """Load necessary configurations"""
        config_dir = Path(__file__).parent.parent / 'config'
        
        # Load agent addresses
        with open(config_dir / 'agent_addresses.json', 'r') as f:
            self.agent_config = json.load(f)
            
        # Load distributor ABI
        with open(config_dir / 'abis' / 'DreamTokenDistributor.json', 'r') as f:
            self.distributor_abi = json.load(f)
            
        # Load token ABI
        with open(config_dir / 'abis' / 'ERC20.json', 'r') as f:
            self.token_abi = json.load(f)
            
    def deploy_distributor(
        self,
        private_key: str
    ) -> Tuple[str, Dict[str, str]]:
        """
        Deploy the token distributor contract
        Returns (distributor_address, transaction_hash)
        """
        account = Account.from_key(private_key)
        
        # Get token addresses
        dream_addr = self.agent_config['tokens']['DREAM']['address']
        smind_addr = self.agent_config['tokens']['SMIND']['address']
        lucid_addr = self.agent_config['tokens']['LUCID']['address']
        
        # Deploy contract
        contract = self.w3.eth.contract(
            abi=self.distributor_abi,
            bytecode=self.get_distributor_bytecode()
        )
        
        # Build constructor transaction
        construct_txn = contract.constructor(
            dream_addr,
            smind_addr,
            lucid_addr
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 5000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(
            construct_txn, 
            private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for deployment
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        distributor_address = tx_receipt['contractAddress']
        
        return distributor_address, tx_receipt
        
    def initialize_vesting(
        self,
        distributor_address: str,
        private_key: str
    ) -> Dict[str, str]:
        """Initialize vesting for all pools"""
        account = Account.from_key(private_key)
        
        # Get distributor contract
        self.distributor = self.w3.eth.contract(
            address=distributor_address,
            abi=self.distributor_abi
        )
        
        tx_hashes = {}
        
        # Start vesting for each agent
        for token_symbol in ['DREAM', 'SMIND', 'LUCID']:
            token_addr = self.agent_config['tokens'][token_symbol]['address']
            
            for agent_name, agent_data in self.agent_config['agents'].items():
                # Calculate vesting amount based on role
                amount = self.calculate_vesting_amount(
                    token_symbol,
                    agent_data['role']
                )
                
                if amount > 0:
                    # Build transaction
                    txn = self.distributor.functions.startVesting(
                        token_addr,
                        agent_data['address'],
                        amount
                    ).build_transaction({
                        'from': account.address,
                        'nonce': self.w3.eth.get_transaction_count(account.address),
                        'gas': 200000,
                        'gasPrice': self.w3.eth.gas_price
                    })
                    
                    # Sign and send
                    signed = self.w3.eth.account.sign_transaction(txn, private_key)
                    tx_hash = self.w3.eth.send_raw_transaction(
                        signed.rawTransaction
                    )
                    
                    tx_hashes[f"{token_symbol}_{agent_name}"] = tx_hash.hex()
                    
        return tx_hashes
        
    def calculate_vesting_amount(
        self,
        token_symbol: str,
        agent_role: str
    ) -> int:
        """Calculate vesting amount based on role"""
        total_supply = int(self.agent_config['tokens'][token_symbol]['totalSupply'])
        
        # Role-based allocation percentages (in basis points)
        allocations = {
            'DREAM_KEEPER': 200,  # 2%
            'MIND_WEAVER': 200,  # 2%
            'LUCID_GATE': 200,   # 2%
            'ONEIRO_SPHERE': 200, # 2%
            'SYNDICATE': 200      # 2%
        }
        
        allocation_bps = allocations.get(agent_role, 0)
        return (total_supply * allocation_bps) // 10000
        
    def get_vesting_status(
        self,
        distributor_address: str,
        token_symbol: str,
        agent_name: str
    ) -> Dict[str, int]:
        """Get vesting status for an agent"""
        if not self.distributor:
            self.distributor = self.w3.eth.contract(
                address=distributor_address,
                abi=self.distributor_abi
            )
            
        token_addr = self.agent_config['tokens'][token_symbol]['address']
        agent_addr = self.agent_config['agents'][agent_name]['address']
        
        claimable = self.distributor.functions.getClaimableAmount(
            token_addr,
            agent_addr
        ).call()
        
        vested = self.distributor.functions.vestedAmount(
            token_addr,
            agent_addr
        ).call()
        
        return {
            'claimable': claimable,
            'total_vested': vested
        }
        
    def get_distributor_bytecode(self) -> str:
        """Get contract bytecode from compilation artifacts"""
        # TODO: Implement bytecode loading from compilation artifacts
        return "0x..."  # Replace with actual bytecode
        
    @staticmethod
    def format_amount(amount: int, decimals: int) -> str:
        """Format token amount with proper decimals"""
        return f"{amount / (10 ** decimals):.9f}"

# Usage example
if __name__ == "__main__":
    manager = TokenDistributionManager()
    
    # Deploy distributor (replace with actual private key)
    private_key = "0x1234..."  # Deploy wallet private key
    distributor_addr, receipt = manager.deploy_distributor(private_key)
    print(f"Distributor deployed at: {distributor_addr}")
    
    # Initialize vesting
    tx_hashes = manager.initialize_vesting(distributor_addr, private_key)
    print("\nVesting initialized:")
    for pool, tx_hash in tx_hashes.items():
        print(f"{pool}: {tx_hash}")
        
    # Check vesting status
    print("\nVesting Status:")
    for token in ['DREAM', 'SMIND', 'LUCID']:
        for agent in manager.agent_config['agents']:
            status = manager.get_vesting_status(distributor_addr, token, agent)
            decimals = manager.agent_config['tokens'][token]['decimals']
            
            print(f"\n{token} - {agent}:")
            print(f"Claimable: {manager.format_amount(status['claimable'], decimals)}")
            print(f"Total Vested: {manager.format_amount(status['total_vested'], decimals)}")
