"""
Dream Technical Analysis Module
Advanced technical indicators and liquidity analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import talib
from scipy import stats

@dataclass
class LiquidityMetrics:
    bid_ask_spread: float
    depth: float
    slippage: float
    turnover_ratio: float
    liquidity_score: float
    maker_count: int
    taker_count: int
    order_book_imbalance: float

class DreamTechnicalAnalyst:
    def __init__(self):
        self.indicators = {
            'Basic': ['SMA', 'EMA', 'MACD', 'RSI'],
            'Advanced': ['BBANDS', 'STOCH', 'ADX', 'ATR'],
            'Volume': ['OBV', 'AD', 'VWAP'],
            'Momentum': ['MFI', 'CCI', 'CMO'],
            'Volatility': ['ATR', 'NATR', 'TRANGE'],
            'Trend': ['PSAR', 'DX', 'AROON']
        }

    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        selected_indicators: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Calculate selected technical indicators"""
        if selected_indicators is None:
            selected_indicators = [ind for group in self.indicators.values() for ind in group]

        # Ensure OHLCV data is available
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("DataFrame must contain OHLCV data")

        # Basic trend indicators
        if 'SMA' in selected_indicators:
            df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
            df['SMA_50'] = talib.SMA(df['close'], timeperiod=50)
            df['SMA_200'] = talib.SMA(df['close'], timeperiod=200)

        if 'EMA' in selected_indicators:
            df['EMA_12'] = talib.EMA(df['close'], timeperiod=12)
            df['EMA_26'] = talib.EMA(df['close'], timeperiod=26)

        # MACD
        if 'MACD' in selected_indicators:
            macd, signal, hist = talib.MACD(
                df['close'],
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            df['MACD'] = macd
            df['MACD_Signal'] = signal
            df['MACD_Hist'] = hist

        # RSI
        if 'RSI' in selected_indicators:
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)

        # Bollinger Bands
        if 'BBANDS' in selected_indicators:
            upper, middle, lower = talib.BBANDS(
                df['close'],
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            df['BB_Upper'] = upper
            df['BB_Middle'] = middle
            df['BB_Lower'] = lower
            df['BB_Width'] = (upper - lower) / middle

        # Stochastic
        if 'STOCH' in selected_indicators:
            slowk, slowd = talib.STOCH(
                df['high'],
                df['low'],
                df['close'],
                fastk_period=14,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0
            )
            df['STOCH_K'] = slowk
            df['STOCH_D'] = slowd

        # Average Directional Index
        if 'ADX' in selected_indicators:
            df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            df['DI_Plus'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
            df['DI_Minus'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=14)

        # Volume indicators
        if 'OBV' in selected_indicators:
            df['OBV'] = talib.OBV(df['close'], df['volume'])

        if 'AD' in selected_indicators:
            df['AD'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])

        if 'VWAP' in selected_indicators:
            df['VWAP'] = (df['volume'] * df['close']).cumsum() / df['volume'].cumsum()

        # Momentum indicators
        if 'MFI' in selected_indicators:
            df['MFI'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=14)

        if 'CCI' in selected_indicators:
            df['CCI'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)

        if 'CMO' in selected_indicators:
            df['CMO'] = talib.CMO(df['close'], timeperiod=14)

        # Volatility indicators
        if 'ATR' in selected_indicators:
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['NATR'] = talib.NATR(df['high'], df['low'], df['close'], timeperiod=14)

        # Trend indicators
        if 'PSAR' in selected_indicators:
            df['PSAR'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)

        if 'AROON' in selected_indicators:
            aroon_down, aroon_up = talib.AROON(df['high'], df['low'], timeperiod=14)
            df['AROON_Down'] = aroon_down
            df['AROON_Up'] = aroon_up

        return df

    def analyze_liquidity(
        self,
        order_book: Dict,
        recent_trades: List[Dict],
        price: float
    ) -> LiquidityMetrics:
        """Analyze market liquidity"""
        # Calculate bid-ask spread
        best_bid = max(order_book['bids'], key=lambda x: x[0])[0]
        best_ask = min(order_book['asks'], key=lambda x: x[0])[0]
        spread = (best_ask - best_bid) / price

        # Calculate market depth
        depth_usd = sum(bid[0] * bid[1] for bid in order_book['bids']) + \
                   sum(ask[0] * ask[1] for ask in order_book['asks'])

        # Calculate slippage for 10000 USD order
        target_amount = 10000 / price
        slippage = self._calculate_slippage(order_book, target_amount, price)

        # Calculate turnover ratio
        volume_24h = sum(trade['amount'] for trade in recent_trades)
        turnover = volume_24h * price / depth_usd

        # Count unique makers and takers
        makers = set(trade['maker'] for trade in recent_trades)
        takers = set(trade['taker'] for trade in recent_trades)

        # Calculate order book imbalance
        total_bids = sum(bid[1] for bid in order_book['bids'])
        total_asks = sum(ask[1] for ask in order_book['asks'])
        imbalance = (total_bids - total_asks) / (total_bids + total_asks)

        # Calculate liquidity score (0-100)
        score = self._calculate_liquidity_score(
            spread,
            depth_usd,
            slippage,
            turnover,
            len(makers),
            len(takers),
            imbalance
        )

        return LiquidityMetrics(
            bid_ask_spread=spread,
            depth=depth_usd,
            slippage=slippage,
            turnover_ratio=turnover,
            liquidity_score=score,
            maker_count=len(makers),
            taker_count=len(takers),
            order_book_imbalance=imbalance
        )

    def _calculate_slippage(
        self,
        order_book: Dict,
        target_amount: float,
        current_price: float
    ) -> float:
        """Calculate expected slippage for given order size"""
        remaining = target_amount
        total_cost = 0

        for ask in sorted(order_book['asks'], key=lambda x: x[0]):
            price, amount = ask
            if remaining <= 0:
                break
            filled = min(amount, remaining)
            total_cost += filled * price
            remaining -= filled

        if remaining > 0:
            return float('inf')  # Not enough liquidity

        avg_price = total_cost / target_amount
        return (avg_price - current_price) / current_price

    def _calculate_liquidity_score(
        self,
        spread: float,
        depth: float,
        slippage: float,
        turnover: float,
        maker_count: int,
        taker_count: int,
        imbalance: float
    ) -> float:
        """Calculate overall liquidity score"""
        # Normalize metrics
        spread_score = max(0, 1 - (spread * 100))  # Smaller spread is better
        depth_score = min(1, depth / 1000000)  # Cap at 1M USD
        slippage_score = max(0, 1 - (slippage * 100))
        turnover_score = min(1, turnover / 0.1)  # 10% daily turnover target
        participant_score = min(1, (maker_count + taker_count) / 100)
        balance_score = 1 - abs(imbalance)

        # Weighted average
        weights = {
            'spread': 0.25,
            'depth': 0.20,
            'slippage': 0.20,
            'turnover': 0.15,
            'participants': 0.10,
            'balance': 0.10
        }

        score = (
            weights['spread'] * spread_score +
            weights['depth'] * depth_score +
            weights['slippage'] * slippage_score +
            weights['turnover'] * turnover_score +
            weights['participants'] * participant_score +
            weights['balance'] * balance_score
        )

        return score * 100  # Convert to 0-100 scale

    def detect_market_making_patterns(
        self,
        trades: List[Dict],
        timeframe: str = '1h'
    ) -> Dict[str, float]:
        """Detect market making patterns and strategies"""
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Resample to specified timeframe
        volume = df['amount'].resample(timeframe).sum()
        trades_count = df['amount'].resample(timeframe).count()
        unique_makers = df.resample(timeframe)['maker'].nunique()
        
        patterns = {
            'wash_trading_probability': self._detect_wash_trading(df),
            'quote_stuffing_probability': self._detect_quote_stuffing(df),
            'momentum_ignition_probability': self._detect_momentum_ignition(df),
            'layering_probability': self._detect_layering(df),
            'market_making_score': self._calculate_mm_score(
                volume,
                trades_count,
                unique_makers
            )
        }

        return patterns

    def _detect_wash_trading(self, df: pd.DataFrame) -> float:
        """Detect potential wash trading"""
        # Look for rapid back-and-forth trades between same parties
        maker_taker_pairs = set(zip(df['maker'], df['taker']))
        reverse_pairs = set(zip(df['taker'], df['maker']))
        overlap = len(maker_taker_pairs.intersection(reverse_pairs))
        
        if len(maker_taker_pairs) == 0:
            return 0.0
            
        return overlap / len(maker_taker_pairs)

    def _detect_quote_stuffing(self, df: pd.DataFrame) -> float:
        """Detect potential quote stuffing"""
        # Look for periods of abnormally high order activity
        orders_per_second = df.resample('1S').size()
        zscore = stats.zscore(orders_per_second)
        high_activity = (zscore > 3).sum() / len(zscore)
        return min(1.0, high_activity * 2)

    def _detect_momentum_ignition(self, df: pd.DataFrame) -> float:
        """Detect potential momentum ignition"""
        # Look for large orders followed by price moves
        price_changes = df['price'].pct_change()
        large_orders = df['amount'] > df['amount'].quantile(0.95)
        
        # Calculate correlation between large orders and subsequent price moves
        correlation = price_changes[1:].corr(large_orders[:-1])
        return abs(correlation)

    def _detect_layering(self, df: pd.DataFrame) -> float:
        """Detect potential layering"""
        # Look for multiple orders at different price levels
        price_levels = df.groupby('price').size()
        max_levels = price_levels.max()
        avg_levels = price_levels.mean()
        
        if avg_levels == 0:
            return 0.0
            
        return min(1.0, (max_levels - avg_levels) / avg_levels)

    def _calculate_mm_score(
        self,
        volume: pd.Series,
        trades_count: pd.Series,
        unique_makers: pd.Series
    ) -> float:
        """Calculate market making effectiveness score"""
        # Factors to consider:
        # 1. Consistency of volume
        volume_consistency = 1 - volume.std() / volume.mean() if volume.mean() > 0 else 0
        
        # 2. Trade size distribution
        trade_size_efficiency = trades_count.mean() / trades_count.max() if trades_count.max() > 0 else 0
        
        # 3. Maker diversity
        maker_diversity = unique_makers.mean() / unique_makers.max() if unique_makers.max() > 0 else 0
        
        # Weighted average
        weights = {
            'volume': 0.4,
            'trades': 0.3,
            'makers': 0.3
        }
        
        score = (
            weights['volume'] * volume_consistency +
            weights['trades'] * trade_size_efficiency +
            weights['makers'] * maker_diversity
        )
        
        return score
