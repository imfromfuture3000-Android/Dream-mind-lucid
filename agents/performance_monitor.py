"""
Dream Performance Monitor and Rebalancer
Monitors AI agent performance and manages reward distribution
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import time
import numpy as np
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self):
        # Connect to SKALE network
        self.w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.skalenodes.com/v1/elated-tan-skat"
        ))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load configurations
        self.load_configs()
        
        # Performance metrics history
        self.performance_history = {}
        
    def load_configs(self):
        """Load necessary configurations"""
        config_dir = Path(__file__).parent.parent / 'config'
        
        # Load agent addresses
        with open(config_dir / 'agent_addresses.json', 'r') as f:
            self.agent_config = json.load(f)
            
        # Load distributor ABI
        with open(config_dir / 'abis' / 'DreamPerformanceDistributor.json', 'r') as f:
            self.distributor_abi = json.load(f)
            
        # Initialize performance history
        for agent_name in self.agent_config['agents']:
            self.performance_history[agent_name] = []
            
    def analyze_dream_performance(
        self,
        agent_name: str,
        dream_data: Dict
    ) -> Tuple[int, bool]:
        """
        Analyze a single dream processing performance
        Returns (score 0-1000, success boolean)
        """
        score = 0
        success = False
        
        try:
            # Dream interpretation accuracy
            if 'interpretation_confidence' in dream_data:
                score += int(dream_data['interpretation_confidence'] * 400)
                
            # Pattern recognition quality
            if 'pattern_match_score' in dream_data:
                score += int(dream_data['pattern_match_score'] * 300)
                
            # Response time
            if 'processing_time' in dream_data:
                time_score = max(0, 300 - (dream_data['processing_time'] * 10))
                score += int(time_score)
                
            # Success criteria
            success = (
                dream_data.get('completed', False) and
                dream_data.get('error_count', 0) == 0 and
                score >= 500
            )
            
        except Exception as e:
            print(f"Error analyzing dream performance: {e}")
            return 0, False
            
        return min(1000, score), success
        
    def calculate_agent_scores(
        self,
        agent_name: str,
        recent_dreams: List[Dict]
    ) -> Dict[str, int]:
        """Calculate comprehensive agent scores"""
        scores = {
            'dreamScore': 0,
            'mindScore': 0,
            'lucidScore': 0,
            'successfulDreams': 0,
            'totalDreams': len(recent_dreams)
        }
        
        if not recent_dreams:
            return scores
            
        # Process each dream
        dream_scores = []
        mind_scores = []
        lucid_scores = []
        
        for dream in recent_dreams:
            score, success = self.analyze_dream_performance(agent_name, dream)
            
            if success:
                scores['successfulDreams'] += 1
                
            # Split score into components
            dream_scores.append(score * 0.4)  # Dream interpretation
            mind_scores.append(score * 0.3)   # Neural patterns
            lucid_scores.append(score * 0.3)  # Lucidity control
            
        # Calculate final scores
        if dream_scores:
            scores['dreamScore'] = int(np.mean(dream_scores))
            scores['mindScore'] = int(np.mean(mind_scores))
            scores['lucidScore'] = int(np.mean(lucid_scores))
            
        return scores
        
    def update_agent_performance(
        self,
        distributor_address: str,
        agent_name: str,
        private_key: str
    ) -> str:
        """
        Update agent performance metrics on-chain
        Returns transaction hash
        """
        # Get recent dreams (last 24 hours)
        recent_dreams = self.get_recent_dreams(agent_name)
        
        # Calculate scores
        scores = self.calculate_agent_scores(agent_name, recent_dreams)
        
        # Update on-chain
        account = Account.from_key(private_key)
        distributor = self.w3.eth.contract(
            address=distributor_address,
            abi=self.distributor_abi
        )
        
        # Build transaction
        txn = distributor.functions.updatePerformance(
            self.agent_config['agents'][agent_name]['address'],
            scores['dreamScore'],
            scores['mindScore'],
            scores['lucidScore'],
            scores['successfulDreams'],
            scores['totalDreams']
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send
        signed = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        # Store in history
        self.performance_history[agent_name].append({
            'timestamp': datetime.now().isoformat(),
            'scores': scores,
            'tx_hash': tx_hash.hex()
        })
        
        return tx_hash.hex()
        
    def get_recent_dreams(self, agent_name: str) -> List[Dict]:
        """Get recent dreams from storage"""
        # TODO: Implement dream retrieval from storage
        # This should connect to your dream storage system
        return []
        
    def trigger_reward_distribution(
        self,
        distributor_address: str,
        token_symbol: str,
        private_key: str
    ) -> str:
        """
        Trigger reward distribution for a token
        Returns transaction hash
        """
        account = Account.from_key(private_key)
        distributor = self.w3.eth.contract(
            address=distributor_address,
            abi=self.distributor_abi
        )
        
        token_address = self.agent_config['tokens'][token_symbol]['address']
        
        # Build transaction
        txn = distributor.functions.distributeRewards(
            token_address
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send
        signed = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        return tx_hash.hex()
        
    def check_rebalance_needed(self, agent_name: str) -> bool:
        """Check if agent needs rebalancing"""
        if not self.performance_history[agent_name]:
            return True
            
        last_update = datetime.fromisoformat(
            self.performance_history[agent_name][-1]['timestamp']
        )
        
        return datetime.now() - last_update > timedelta(days=7)
        
    def force_rebalance(
        self,
        distributor_address: str,
        private_key: str
    ) -> str:
        """
        Force rebalancing of all agents
        Returns transaction hash
        """
        account = Account.from_key(private_key)
        distributor = self.w3.eth.contract(
            address=distributor_address,
            abi=self.distributor_abi
        )
        
        # Build transaction
        txn = distributor.functions.forceRebalance().build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send
        signed = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        return tx_hash.hex()
        
    def get_performance_summary(self, agent_name: str) -> Dict:
        """Get performance summary for an agent"""
        if not self.performance_history[agent_name]:
            return {}
            
        recent = self.performance_history[agent_name][-10:]
        
        dream_scores = [h['scores']['dreamScore'] for h in recent]
        mind_scores = [h['scores']['mindScore'] for h in recent]
        lucid_scores = [h['scores']['lucidScore'] for h in recent]
        
        return {
            'average_dream_score': np.mean(dream_scores),
            'average_mind_score': np.mean(mind_scores),
            'average_lucid_score': np.mean(lucid_scores),
            'trend': 'improving' if dream_scores[-1] > dream_scores[0] else 'declining',
            'last_update': recent[-1]['timestamp']
        }

# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    # Configuration
    distributor_address = "0x..."  # Deploy the distributor first
    private_key = "0x..."  # Oracle private key
    
    # Update performance for all agents
    for agent_name in monitor.agent_config['agents']:
        if monitor.check_rebalance_needed(agent_name):
            tx_hash = monitor.update_agent_performance(
                distributor_address,
                agent_name,
                private_key
            )
            print(f"Updated {agent_name} performance: {tx_hash}")
            
    # Distribute rewards for each token
    for token in ['DREAM', 'SMIND', 'LUCID']:
        tx_hash = monitor.trigger_reward_distribution(
            distributor_address,
            token,
            private_key
        )
        print(f"Distributed {token} rewards: {tx_hash}")
        
    # Print performance summaries
    for agent_name in monitor.agent_config['agents']:
        summary = monitor.get_performance_summary(agent_name)
        print(f"\n{agent_name} Performance Summary:")
        for metric, value in summary.items():
            print(f"{metric}: {value}")
