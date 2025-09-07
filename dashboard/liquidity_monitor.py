"""
Dream Liquidity Monitor
Monitors and analyzes market liquidity for Dream tokens
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from web3 import Web3
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from dex_liquidity import DexLiquidityFetcher, PoolInfo

@dataclass
class LiquidityState:
    token: str
    timestamp: datetime
    total_liquidity: float
    active_pairs: List[str]
    best_pair: str
    depth_distribution: Dict[str, float]
    market_impact: Dict[str, float]
    maker_stats: Dict[str, Dict]

class LiquidityMonitor:
    def __init__(self, web3_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.logger = logging.getLogger("LiquidityMonitor")
        
        # Initialize state
        self.liquidity_states: Dict[str, List[LiquidityState]] = {}
        self.alerts = []
        
        # Initialize DEX liquidity fetcher
        self.dex_fetcher = DexLiquidityFetcher(web3_provider)
        
        # Common stablecoin addresses on SKALE
        self.stablecoin_addresses = {
            'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  # Replace with actual SKALE addresses
            'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
            'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f'
        }
        
    async def monitor_liquidity(
        self,
        token_address: str,
        token_symbol: str,
        pairs: List[str]
    ):
        """Monitor liquidity across multiple pairs"""
        try:
            # Get current state
            state = await self._analyze_liquidity(token_address, token_symbol, pairs)
            
            # Store state
            if token_symbol not in self.liquidity_states:
                self.liquidity_states[token_symbol] = []
            self.liquidity_states[token_symbol].append(state)
            
            # Analyze for issues
            await self._check_liquidity_alerts(state)
            
            # Clean old states
            self._clean_old_states(token_symbol)
            
        except Exception as e:
            self.logger.error(f"Error monitoring liquidity: {e}")
            
    async def _analyze_liquidity(
        self,
        token_address: str,
        token_symbol: str,
        pairs: List[str]
    ) -> LiquidityState:
        """Analyze current liquidity state"""
        total_liquidity = 0
        depth_distribution = {}
        market_impact = {}
        maker_stats = {}
        
        active_pairs = []
        best_pair = None
        best_liquidity = 0
        
        for pair in pairs:
            # Get pair liquidity
            liquidity = await self._get_pair_liquidity(pair)
            if liquidity > 0:
                active_pairs.append(pair)
                total_liquidity += liquidity
                
                if liquidity > best_liquidity:
                    best_liquidity = liquidity
                    best_pair = pair
                    
                # Get market depth
                depth = await self._get_market_depth(pair)
                depth_distribution[pair] = depth
                
                # Calculate market impact
                impact = await self._calculate_market_impact(pair)
                market_impact[pair] = impact
                
                # Get maker statistics
                stats = await self._get_maker_stats(pair)
                maker_stats[pair] = stats
                
        return LiquidityState(
            token=token_symbol,
            timestamp=datetime.now(),
            total_liquidity=total_liquidity,
            active_pairs=active_pairs,
            best_pair=best_pair,
            depth_distribution=depth_distribution,
            market_impact=market_impact,
            maker_stats=maker_stats
        )
        
    async def _get_pair_liquidity(self, pair: str) -> float:
        """Get liquidity for a trading pair"""
        try:
            # Get pool info
            pool_info = await self.dex_fetcher.get_pool_info(pair)
            if not pool_info:
                return 0.0
                
            # Find a stablecoin in the pair
            stablecoin_address = None
            for _, address in self.stablecoin_addresses.items():
                if address.lower() in [pool_info.token0.lower(), pool_info.token1.lower()]:
                    stablecoin_address = address
                    break
                    
            if not stablecoin_address:
                # If no stablecoin in pair, estimate using token price
                # Here we could add price oracle integration for more accurate pricing
                return float(pool_info.reserves0 + pool_info.reserves1)
                
            # Get liquidity in USD
            liquidity = await self.dex_fetcher.get_pool_liquidity_usd(
                pair,
                stablecoin_address,
                Decimal('1.0')  # Assuming stablecoin price is $1
            )
            
            return float(liquidity if liquidity else 0.0)
            
        except Exception as e:
            self.logger.error(f"Error getting pair liquidity for {pair}: {e}")
            return 0.0
        
    async def _get_market_depth(self, pair: str) -> Dict[str, float]:
        """Get market depth for a trading pair"""
        try:
            pool_info = await self.dex_fetcher.get_pool_info(pair)
            if not pool_info:
                return {}
                
            # Find token and base token
            base_token = None
            token = None
            for _, address in self.stablecoin_addresses.items():
                if address.lower() == pool_info.token0.lower():
                    base_token = pool_info.token0
                    token = pool_info.token1
                    break
                elif address.lower() == pool_info.token1.lower():
                    base_token = pool_info.token1
                    token = pool_info.token0
                    break
                    
            if not base_token:
                # If no stablecoin found, use token0 as base
                base_token = pool_info.token0
                token = pool_info.token1
                
            # Get current price
            price = await self.dex_fetcher.get_token_price(
                token,
                pair,
                base_token
            )
            
            if not price:
                return {}
                
            # Get depth distribution
            depth = await self.dex_fetcher.get_depth_distribution(
                pair,
                token,
                base_token,
                price,
                depth_levels=10
            )
            
            return {k: float(v) for k, v in depth.items()}
            
        except Exception as e:
            self.logger.error(f"Error getting market depth for {pair}: {e}")
            return {}
        
    async def _calculate_market_impact(self, pair: str) -> Dict[str, float]:
        """Calculate market impact for different order sizes"""
        impacts = {}
        for size in [1000, 5000, 10000, 50000, 100000]:  # USD amounts
            impact = await self._estimate_price_impact(pair, size)
            impacts[f"impact_{size}"] = impact
        return impacts
        
    async def _estimate_price_impact(self, pair: str, size_usd: float) -> float:
        """Estimate price impact for given order size"""
        try:
            # Get pool info
            pool_info = await self.dex_fetcher.get_pool_info(pair)
            if not pool_info:
                return 0.0
                
            # Find base token (stablecoin if available)
            base_token = None
            token = None
            for _, address in self.stablecoin_addresses.items():
                if address.lower() == pool_info.token0.lower():
                    base_token = pool_info.token0
                    token = pool_info.token1
                    base_reserves = pool_info.reserves0
                    token_reserves = pool_info.reserves1
                    break
                elif address.lower() == pool_info.token1.lower():
                    base_token = pool_info.token1
                    token = pool_info.token0
                    base_reserves = pool_info.reserves1
                    token_reserves = pool_info.reserves0
                    break
                    
            if not base_token:
                # If no stablecoin, use token0 as base
                base_token = pool_info.token0
                token = pool_info.token1
                base_reserves = pool_info.reserves0
                token_reserves = pool_info.reserves1
                
            # Get current price
            price = await self.dex_fetcher.get_token_price(
                token,
                pair,
                base_token
            )
            
            if not price:
                return 0.0
                
            # Calculate tokens to buy for the USD amount
            tokens_to_buy = Decimal(size_usd) / price
            
            # Calculate price impact using constant product formula
            # new_price = (base_reserves) / (token_reserves - tokens_to_buy)
            # price_impact = (new_price - price) / price
            
            new_token_reserves = token_reserves - tokens_to_buy
            if new_token_reserves <= 0:
                return 1.0  # 100% impact for trades larger than pool
                
            new_price = base_reserves / new_token_reserves
            price_impact = abs((new_price - price) / price)
            
            return float(price_impact)
            
        except Exception as e:
            self.logger.error(f"Error calculating price impact for {pair}: {e}")
            return 0.0
        
    async def _get_maker_stats(self, pair: str) -> Dict:
        """Get statistics about market makers"""
        try:
            # Get recent trades and quotes
            trades = await self.dex_fetcher.get_recent_trades(pair, limit=100)
            quotes = await self.dex_fetcher.get_active_quotes(pair)
            
            if not trades or not quotes:
                return {
                    'active_makers': 0,
                    'avg_quote_size': 0,
                    'quote_refresh_rate': 0,
                    'avg_spread': 0
                }
                
            # Analyze maker activity
            active_makers = set()
            quote_sizes = []
            spreads = []
            quote_updates = {}
            
            # Process quotes
            for quote in quotes:
                active_makers.add(quote.maker_address)
                quote_sizes.append(quote.size)
                
                # Track quote updates
                if quote.maker_address not in quote_updates:
                    quote_updates[quote.maker_address] = []
                quote_updates[quote.maker_address].append(quote.timestamp)
                
                # Calculate spread
                if quote.bid_price and quote.ask_price:
                    spread = (quote.ask_price - quote.bid_price) / quote.bid_price
                    spreads.append(float(spread))
                    
            # Calculate quote refresh rate (updates per hour)
            refresh_rates = []
            for maker, timestamps in quote_updates.items():
                if len(timestamps) > 1:
                    # Calculate average time between updates
                    sorted_times = sorted(timestamps)
                    time_diffs = [(t2 - t1).total_seconds() / 3600  # Convert to hours
                                for t1, t2 in zip(sorted_times[:-1], sorted_times[1:])]
                    if time_diffs:
                        refresh_rates.append(1 / (sum(time_diffs) / len(time_diffs)))
                        
            return {
                'active_makers': len(active_makers),
                'avg_quote_size': sum(quote_sizes) / len(quote_sizes) if quote_sizes else 0,
                'quote_refresh_rate': sum(refresh_rates) / len(refresh_rates) if refresh_rates else 0,
                'avg_spread': sum(spreads) / len(spreads) if spreads else 0,
                'maker_details': {
                    'top_makers': list(active_makers)[:5],  # Top 5 makers by activity
                    'quote_count': len(quotes),
                    'trade_count': len(trades),
                    'min_spread': min(spreads) if spreads else 0,
                    'max_spread': max(spreads) if spreads else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting maker stats for {pair}: {e}")
            return {
                'active_makers': 0,
                'avg_quote_size': 0,
                'quote_refresh_rate': 0,
                'avg_spread': 0
            }
        
    async def _check_liquidity_alerts(self, state: LiquidityState):
        """Check for liquidity-related issues"""
        # Check total liquidity
        if state.total_liquidity < 100000:  # Less than $100k
            self._add_alert(
                state.token,
                'LOW_LIQUIDITY',
                f"Total liquidity below threshold: ${state.total_liquidity:,.2f}"
            )
            
        # Check market impact
        for pair, impacts in state.market_impact.items():
            if impacts.get('impact_10000', 0) > 0.01:  # >1% for $10k
                self._add_alert(
                    state.token,
                    'HIGH_IMPACT',
                    f"High market impact in {pair}: {impacts['impact_10000']*100:.2f}%"
                )
                
        # Check maker activity
        for pair, stats in state.maker_stats.items():
            if stats['active_makers'] < 3:
                self._add_alert(
                    state.token,
                    'LOW_MAKER_COUNT',
                    f"Low market maker count in {pair}: {stats['active_makers']}"
                )
                
    def _add_alert(self, token: str, alert_type: str, message: str):
        """Add new alert"""
        self.alerts.append({
            'timestamp': datetime.now(),
            'token': token,
            'type': alert_type,
            'message': message
        })
        
    def _clean_old_states(self, token: str):
        """Remove states older than 24 hours"""
        if token in self.liquidity_states:
            cutoff = datetime.now() - timedelta(hours=24)
            self.liquidity_states[token] = [
                state for state in self.liquidity_states[token]
                if state.timestamp > cutoff
            ]
            
    def get_liquidity_summary(self, token: str) -> Dict:
        """Get liquidity summary for a token"""
        if token not in self.liquidity_states:
            return {}
            
        states = self.liquidity_states[token]
        if not states:
            return {}
            
        latest = states[-1]
        
        # Calculate changes
        if len(states) > 1:
            previous = states[-2]
            liquidity_change = (
                (latest.total_liquidity - previous.total_liquidity)
                / previous.total_liquidity
            )
        else:
            liquidity_change = 0
            
        return {
            'timestamp': latest.timestamp,
            'total_liquidity': latest.total_liquidity,
            'liquidity_change_24h': liquidity_change,
            'active_pairs': len(latest.active_pairs),
            'best_pair': latest.best_pair,
            'depth_distribution': latest.depth_distribution,
            'market_impact': latest.market_impact,
            'maker_stats': latest.maker_stats
        }
        
    def get_alerts(self, token: Optional[str] = None) -> List[Dict]:
        """Get alerts, optionally filtered by token"""
        if token:
            return [
                alert for alert in self.alerts
                if alert['token'] == token
            ]
        return self.alerts
