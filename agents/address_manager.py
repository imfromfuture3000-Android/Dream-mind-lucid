"""
Dream-Mind-Lucid Agent Address Manager
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from web3 import Web3

class AgentAddressManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                Path(__file__).parent.parent, 
                'config', 
                'agent_addresses.json'
            )
        self.config_path = config_path
        self.load_config()
        
        # Connect to SKALE network
        self.w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.skalenodes.com/v1/elated-tan-skat"
        ))
        
    def load_config(self) -> None:
        """Load agent configuration from JSON"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
    def save_config(self) -> None:
        """Save current configuration to JSON"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def get_agent_address(self, agent_name: str) -> Optional[str]:
        """Get address for specific agent"""
        return self.config['agents'].get(agent_name, {}).get('address')
    
    def get_token_address(self, token_symbol: str) -> Optional[str]:
        """Get address for specific token"""
        return self.config['tokens'].get(token_symbol, {}).get('address')
    
    def get_agent_permissions(self, agent_name: str) -> List[str]:
        """Get permissions for specific agent"""
        return self.config['agents'].get(agent_name, {}).get('permissions', [])
    
    def check_permission(self, agent_name: str, permission: str) -> bool:
        """Check if agent has specific permission"""
        return permission in self.get_agent_permissions(agent_name)
    
    def validate_addresses(self) -> Dict[str, bool]:
        """Validate all addresses are valid SKALE addresses"""
        results = {}
        
        # Validate agent addresses
        for agent_name, agent_data in self.config['agents'].items():
            addr = agent_data['address']
            results[f"agent_{agent_name}"] = self.w3.is_address(addr)
            
        # Validate token addresses
        for token_symbol, token_data in self.config['tokens'].items():
            addr = token_data['address']
            results[f"token_{token_symbol}"] = self.w3.is_address(addr)
            
        return results
    
    def get_agent_balance(self, agent_name: str) -> float:
        """Get SKALE balance for an agent address"""
        addr = self.get_agent_address(agent_name)
        if not addr:
            return 0.0
        balance_wei = self.w3.eth.get_balance(addr)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_token_balance(self, agent_name: str, token_symbol: str) -> float:
        """Get token balance for an agent"""
        agent_addr = self.get_agent_address(agent_name)
        token_addr = self.get_token_address(token_symbol)
        
        if not (agent_addr and token_addr):
            return 0.0
            
        # Get ERC20 contract
        abi = self.get_erc20_abi()  # Simplified for example
        token_contract = self.w3.eth.contract(
            address=token_addr,
            abi=abi
        )
        
        # Get balance
        balance = token_contract.functions.balanceOf(agent_addr).call()
        decimals = self.config['tokens'][token_symbol]['decimals']
        return balance / (10 ** decimals)
    
    @staticmethod
    def get_erc20_abi() -> List[Dict]:
        """Get basic ERC20 ABI for balance checks"""
        return [
            {
                "constant": True,
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

# Example usage
if __name__ == "__main__":
    manager = AgentAddressManager()
    
    # Print all agent addresses
    print("Agent Addresses:")
    for agent_name in manager.config['agents']:
        addr = manager.get_agent_address(agent_name)
        balance = manager.get_agent_balance(agent_name)
        print(f"{agent_name}: {addr}")
        print(f"SKALE Balance: {balance}")
        
        # Check token balances
        for token in ['DREAM', 'SMIND', 'LUCID']:
            token_balance = manager.get_token_balance(agent_name, token)
            print(f"{token} Balance: {token_balance}")
        print("-" * 50)
    
    # Validate addresses
    print("\nAddress Validation:")
    for key, is_valid in manager.validate_addresses().items():
        print(f"{key}: {'✓' if is_valid else '✗'}")
