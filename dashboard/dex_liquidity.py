"""
DEX-specific liquidity fetchers for SKALE chain
"""

from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
import json
import logging
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class PoolInfo:
    address: str
    token0: str
    token1: str
    reserves0: Decimal
    reserves1: Decimal
    token0_decimals: int
    token1_decimals: int
    total_supply: Decimal
    
class DexLiquidityFetcher:
    # Standard DEX ABIs
    PAIR_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "getReserves",
            "outputs": [
                {"name": "_reserve0", "type": "uint112"},
                {"name": "_reserve1", "type": "uint112"},
                {"name": "_blockTimestampLast", "type": "uint32"}
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token0",
            "outputs": [{"name": "", "type": "address"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token1",
            "outputs": [{"name": "", "type": "address"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    def __init__(self, web3_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.logger = logging.getLogger("DexLiquidityFetcher")
        self.pool_cache: Dict[str, PoolInfo] = {}
        
    async def get_pool_info(self, pool_address: str) -> Optional[PoolInfo]:
        """Get pool information including reserves and token details"""
        try:
            # Check cache first
            if pool_address in self.pool_cache:
                return self.pool_cache[pool_address]
                
            # Create pool contract
            pool_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(pool_address),
                abi=self.PAIR_ABI
            )
            
            # Get tokens
            token0_address = pool_contract.functions.token0().call()
            token1_address = pool_contract.functions.token1().call()
            
            # Get token contracts
            token0_contract = self.w3.eth.contract(
                address=token0_address,
                abi=self.ERC20_ABI
            )
            token1_contract = self.w3.eth.contract(
                address=token1_address,
                abi=self.ERC20_ABI
            )
            
            # Get decimals
            token0_decimals = token0_contract.functions.decimals().call()
            token1_decimals = token1_contract.functions.decimals().call()
            
            # Get reserves
            reserves = pool_contract.functions.getReserves().call()
            reserve0 = Decimal(reserves[0]) / Decimal(10 ** token0_decimals)
            reserve1 = Decimal(reserves[1]) / Decimal(10 ** token1_decimals)
            
            # Get total supply
            total_supply = Decimal(pool_contract.functions.totalSupply().call())
            
            pool_info = PoolInfo(
                address=pool_address,
                token0=token0_address,
                token1=token1_address,
                reserves0=reserve0,
                reserves1=reserve1,
                token0_decimals=token0_decimals,
                token1_decimals=token1_decimals,
                total_supply=total_supply
            )
            
            # Cache the result
            self.pool_cache[pool_address] = pool_info
            return pool_info
            
        except Exception as e:
            self.logger.error(f"Error fetching pool info for {pool_address}: {e}")
            return None
            
    async def get_token_price(
        self,
        token_address: str,
        pool_address: str,
        base_token_address: str
    ) -> Optional[Decimal]:
        """Get token price in terms of the base token"""
        try:
            pool_info = await self.get_pool_info(pool_address)
            if not pool_info:
                return None
                
            # Determine which token is which
            if token_address.lower() == pool_info.token0.lower():
                token_reserves = pool_info.reserves0
                base_reserves = pool_info.reserves1
                token_decimals = pool_info.token0_decimals
                base_decimals = pool_info.token1_decimals
            else:
                token_reserves = pool_info.reserves1
                base_reserves = pool_info.reserves0
                token_decimals = pool_info.token1_decimals
                base_decimals = pool_info.token0_decimals
                
            if token_reserves == 0:
                return Decimal(0)
                
            # Calculate price
            price = (base_reserves / token_reserves)
            return price
            
        except Exception as e:
            self.logger.error(
                f"Error calculating price for {token_address} in pool {pool_address}: {e}"
            )
            return None
            
    async def get_pool_liquidity_usd(
        self,
        pool_address: str,
        base_token_address: str,
        base_token_price_usd: Decimal
    ) -> Optional[Decimal]:
        """Get pool liquidity in USD"""
        try:
            pool_info = await self.get_pool_info(pool_address)
            if not pool_info:
                return None
                
            # If base token is token0
            if base_token_address.lower() == pool_info.token0.lower():
                base_amount = pool_info.reserves0
            else:
                base_amount = pool_info.reserves1
                
            # Calculate total liquidity
            total_liquidity_usd = Decimal(2) * base_amount * base_token_price_usd
            return total_liquidity_usd
            
        except Exception as e:
            self.logger.error(
                f"Error calculating USD liquidity for pool {pool_address}: {e}"
            )
            return None
            
    async def get_depth_distribution(
        self,
        pool_address: str,
        token_address: str,
        base_token_address: str,
        price: Decimal,
        depth_levels: int = 10
    ) -> Dict[str, Decimal]:
        """Get market depth distribution at different price levels"""
        try:
            pool_info = await self.get_pool_info(pool_address)
            if not pool_info:
                return {}
                
            depth = {}
            # Calculate depth at different price impacts
            for impact in range(1, depth_levels + 1):
                impact_decimal = Decimal(impact) / Decimal(100)  # 1% steps
                
                # Price after impact
                price_after_impact = price * (1 + impact_decimal)
                
                # Calculate available liquidity at this price level
                if token_address.lower() == pool_info.token0.lower():
                    max_input = (
                        pool_info.reserves0 *
                        (Decimal(1) - Decimal(1) / (1 + impact_decimal))
                    )
                else:
                    max_input = (
                        pool_info.reserves1 *
                        (Decimal(1) - Decimal(1) / (1 + impact_decimal))
                    )
                    
                depth[f"{impact}%"] = max_input
                
            return depth
            
        except Exception as e:
            self.logger.error(
                f"Error calculating depth distribution for pool {pool_address}: {e}"
            )
            return {}
            
    async def get_recent_trades(self, pool_address: str, limit: int = 100) -> List[Dict]:
        """Get recent trades from the pool"""
        try:
            # Get recent blocks
            current_block = self.w3.eth.block_number
            from_block = max(0, current_block - 1000)  # Last ~1000 blocks
            
            # Create pool contract
            pool_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(pool_address),
                abi=self.PAIR_ABI + [{
                    "anonymous": False,
                    "inputs": [
                        {"indexed": True, "name": "sender", "type": "address"},
                        {"indexed": True, "name": "to", "type": "address"},
                        {"indexed": False, "name": "amount0In", "type": "uint256"},
                        {"indexed": False, "name": "amount1In", "type": "uint256"},
                        {"indexed": False, "name": "amount0Out", "type": "uint256"},
                        {"indexed": False, "name": "amount1Out", "type": "uint256"}
                    ],
                    "name": "Swap",
                    "type": "event"
                }]
            )
            
            # Get Swap events
            events = pool_contract.events.Swap.get_logs(fromBlock=from_block)
            trades = []
            
            for event in events[:limit]:
                # Get block timestamp
                block = self.w3.eth.get_block(event['blockNumber'])
                timestamp = block['timestamp']
                
                # Calculate amounts and price
                amount0_net = (
                    event['args']['amount0Out'] - event['args']['amount0In']
                )
                amount1_net = (
                    event['args']['amount1Out'] - event['args']['amount1In']
                )
                
                # Skip failed or zero-amount trades
                if amount0_net == 0 or amount1_net == 0:
                    continue
                    
                price = abs(Decimal(amount1_net) / Decimal(amount0_net))
                
                trade = {
                    'tx_hash': event['transactionHash'].hex(),
                    'sender': event['args']['sender'],
                    'receiver': event['args']['to'],
                    'amount0': str(amount0_net),
                    'amount1': str(amount1_net),
                    'price': str(price),
                    'timestamp': timestamp
                }
                trades.append(trade)
                
            return trades
            
        except Exception as e:
            self.logger.error(f"Error getting recent trades for pool {pool_address}: {e}")
            return []
            
    async def get_active_quotes(self, pool_address: str) -> List[Dict]:
        """Get active quotes from market makers"""
        try:
            # For simple pools, we'll simulate quotes based on reserve changes
            pool_info = await self.get_pool_info(pool_address)
            if not pool_info:
                return []
                
            # Get recent blocks for quote analysis
            current_block = self.w3.eth.block_number
            blocks_to_analyze = 100
            
            quotes = []
            last_reserves = None
            
            for block_number in range(current_block - blocks_to_analyze, current_block):
                # Get reserves at this block
                try:
                    reserves = await self._get_reserves_at_block(
                        pool_address,
                        block_number
                    )
                    
                    if last_reserves and reserves != last_reserves:
                        # Calculate implied quote
                        price = Decimal(reserves[1]) / Decimal(reserves[0])
                        size = min(
                            Decimal(reserves[0]) / Decimal(10),  # 10% of reserves
                            Decimal(reserves[1]) / Decimal(10)
                        )
                        
                        quote = {
                            'maker_address': pool_address,  # LP position as maker
                            'bid_price': str(price * Decimal('0.995')),  # 0.5% spread
                            'ask_price': str(price * Decimal('1.005')),
                            'size': str(size),
                            'block': block_number
                        }
                        quotes.append(quote)
                        
                    last_reserves = reserves
                    
                except Exception:
                    continue
                    
            return quotes
            
        except Exception as e:
            self.logger.error(f"Error getting active quotes for pool {pool_address}: {e}")
            return []
            
    async def _get_reserves_at_block(
        self,
        pool_address: str,
        block_number: int
    ) -> Tuple[int, int]:
        """Get pool reserves at a specific block"""
        pool_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(pool_address),
            abi=self.PAIR_ABI
        )
        
        # Get reserves at specific block
        reserves = pool_contract.functions.getReserves().call(
            block_identifier=block_number
        )
        
        return (reserves[0], reserves[1])
