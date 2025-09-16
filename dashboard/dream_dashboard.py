"""
Dream Performance Dashboard
Monitors AI agent performance, token distributions, and earnings
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from web3 import Web3
from pathlib import Path
import json
from typing import Dict, List
import numpy as np

from performance_monitor import PerformanceMonitor
from address_manager import AgentAddressManager

class DreamDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Dream-Mind-Lucid Dashboard",
            page_icon="🌠",
            layout="wide"
        )
        
        self.performance_monitor = PerformanceMonitor()
        self.address_manager = AgentAddressManager()
        
        # Initialize connection to SKALE
        self.w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.skalenodes.com/v1/elated-tan-skat"
        ))
        
        self.load_contracts()
        
    def load_contracts(self):
        """Load contract configurations"""
        config_dir = Path(__file__).parent.parent / 'config'
        
        # Load ABIs
        with open(config_dir / 'abis' / 'DreamPerformanceDistributor.json', 'r') as f:
            self.distributor_abi = json.load(f)
            
        # TODO: Replace with actual deployed address
        self.distributor_address = "0x..."
        
        self.distributor = self.w3.eth.contract(
            address=self.distributor_address,
            abi=self.distributor_abi
        )
        
    def run(self):
        """Run the dashboard"""
        st.title("🌠 Dream-Mind-Lucid Performance Dashboard")
        
        # Sidebar
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Select Page",
            ["Overview", "Agent Performance", "Token Distribution", "Earnings & Burns"]
        )
        
        if page == "Overview":
            self.show_overview()
        elif page == "Agent Performance":
            self.show_agent_performance()
        elif page == "Token Distribution":
            self.show_token_distribution()
        else:
            self.show_earnings_burns()
            
    def show_overview(self):
        """Display system overview"""
        col1, col2, col3 = st.columns(3)
        
        # Total dreams processed
        with col1:
            total_dreams = self.get_total_dreams_processed()
            st.metric("Total Dreams Processed", f"{total_dreams:,}")
            
        # Success rate
        with col2:
            success_rate = self.get_system_success_rate()
            st.metric("System Success Rate", f"{success_rate:.2f}%")
            
        # Active agents
        with col3:
            active_agents = self.get_active_agent_count()
            st.metric("Active Agents", active_agents)
            
        # Performance overview
        st.subheader("System Performance")
        fig = self.create_performance_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity")
        recent_df = self.get_recent_activity()
        st.dataframe(recent_df)
        
    def show_agent_performance(self):
        """Display detailed agent performance"""
        st.subheader("Agent Performance Metrics")
        
        # Agent selector
        agent = st.selectbox(
            "Select Agent",
            list(self.address_manager.config['agents'].keys())
        )
        
        col1, col2, col3 = st.columns(3)
        
        # Performance scores
        with col1:
            scores = self.get_agent_scores(agent)
            st.metric("Dream Score", f"{scores['dreamScore']}/1000")
            st.metric("Mind Score", f"{scores['mindScore']}/1000")
            st.metric("Lucid Score", f"{scores['lucidScore']}/1000")
            
        # Success metrics
        with col2:
            metrics = self.get_agent_metrics(agent)
            st.metric("Success Rate", f"{metrics['success_rate']:.2f}%")
            st.metric("Dreams Processed", metrics['total_dreams'])
            st.metric("Reward Points", metrics['reward_points'])
            
        # Token balances
        with col3:
            balances = self.get_agent_balances(agent)
            for token, balance in balances.items():
                st.metric(f"{token} Balance", f"{balance:.4f}")
                
        # Performance history
        st.subheader("Performance History")
        fig = self.create_agent_history_chart(agent)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent rewards
        st.subheader("Recent Rewards")
        rewards_df = self.get_agent_rewards(agent)
        st.dataframe(rewards_df)
        
    def show_token_distribution(self):
        """Display token distribution metrics"""
        st.subheader("Token Distribution Overview")
        
        # Token selector
        token = st.selectbox(
            "Select Token",
            ["DREAM", "SMIND", "LUCID"]
        )
        
        col1, col2 = st.columns(2)
        
        # Distribution metrics
        with col1:
            dist = self.get_token_distribution(token)
            fig = go.Figure(data=[go.Pie(
                labels=list(dist.keys()),
                values=list(dist.values()),
                hole=.3
            )])
            st.plotly_chart(fig)
            
        # Supply metrics
        with col2:
            supply = self.get_token_supply_metrics(token)
            st.metric("Total Supply", f"{supply['total']:,}")
            st.metric("Circulating Supply", f"{supply['circulating']:,}")
            st.metric("Burned", f"{supply['burned']:,}")
            
        # Distribution history
        st.subheader("Distribution History")
        fig = self.create_distribution_history_chart(token)
        st.plotly_chart(fig, use_container_width=True)
        
    def show_earnings_burns(self):
        """Display earnings and burn metrics with price impact"""
        st.subheader("Earnings & Burns Overview")
        
        # Price overview
        st.subheader("Token Prices")
        prices = self.get_current_prices()
        cols = st.columns(len(prices))
        
        for i, (token, price_data) in enumerate(prices.items()):
            with cols[i]:
                st.metric(
                    token,
                    f"${price_data['price']:.4f}",
                    f"{price_data['change']}%",
                    delta_color="normal" if price_data['change'] >= 0 else "inverse"
                )
                st.caption(f"Vol: ${price_data['volume']:,.2f}")
        
        # Advanced visualizations
        col1, col2 = st.columns(2)
        
        # Price and volume analysis
        with col1:
            st.subheader("Price Analysis")
            token = st.selectbox("Select Token", ["DREAM", "SMIND", "LUCID"])
            timeframe = st.select_slider(
                "Timeframe",
                options=["1D", "1W", "1M", "3M", "6M", "1Y"],
                value="1M"
            )
            
            price_data = self.get_price_data(token, timeframe)
            fig = self.visualizer.create_price_candlestick(price_data, token)
            st.plotly_chart(fig)
            
        # Burn metrics
        with col2:
            st.subheader("Token Burns")
            burns = self.get_burn_metrics()
            fig = self.create_burn_chart(burns)
            st.plotly_chart(fig)
            
        # Historical data
        st.subheader("Historical Earnings & Burns")
        fig = self.create_historical_metrics_chart()
        st.plotly_chart(fig, use_container_width=True)
        
    # Utility methods
    def get_total_dreams_processed(self) -> int:
        """Get total dreams processed by all agents"""
        total = 0
        for agent in self.address_manager.config['agents']:
            total += self.distributor.functions.agentPerformance(
                self.address_manager.get_agent_address(agent)
            ).call()[4]  # totalDreams
        return total
        
    def get_system_success_rate(self) -> float:
        """Calculate system-wide success rate"""
        total_dreams = 0
        successful_dreams = 0
        
        for agent in self.address_manager.config['agents']:
            perf = self.distributor.functions.agentPerformance(
                self.address_manager.get_agent_address(agent)
            ).call()
            total_dreams += perf[4]  # totalDreams
            successful_dreams += perf[5]  # successfulDreams
            
        return (successful_dreams / total_dreams * 100) if total_dreams > 0 else 0
        
    def get_active_agent_count(self) -> int:
        """Get number of active agents"""
        active = 0
        for agent in self.address_manager.config['agents']:
            perf = self.distributor.functions.agentPerformance(
                self.address_manager.get_agent_address(agent)
            ).call()
            if perf[6] > 0:  # lastUpdateBlock
                active += 1
        return active
        
    def create_performance_chart(self) -> go.Figure:
        """Create system performance chart"""
        data = []
        for agent in self.address_manager.config['agents']:
            history = self.performance_monitor.performance_history.get(agent, [])
            for entry in history[-30:]:  # Last 30 updates
                data.append({
                    'Agent': agent,
                    'Date': datetime.fromisoformat(entry['timestamp']),
                    'Dream Score': entry['scores']['dreamScore'],
                    'Mind Score': entry['scores']['mindScore'],
                    'Lucid Score': entry['scores']['lucidScore']
                })
                
        df = pd.DataFrame(data)
        fig = px.line(
            df,
            x='Date',
            y=['Dream Score', 'Mind Score', 'Lucid Score'],
            color='Agent',
            title='System Performance Over Time'
        )
        return fig
        
    def get_recent_activity(self) -> pd.DataFrame:
        """Get recent system activity"""
        activities = []
        
        # Get recent transactions
        for agent in self.address_manager.config['agents']:
            history = self.performance_monitor.performance_history.get(agent, [])
            for entry in history[-10:]:  # Last 10 updates
                activities.append({
                    'Timestamp': datetime.fromisoformat(entry['timestamp']),
                    'Agent': agent,
                    'Action': 'Performance Update',
                    'Details': f"Scores - Dream: {entry['scores']['dreamScore']}, Mind: {entry['scores']['mindScore']}, Lucid: {entry['scores']['lucidScore']}"
                })
                
        return pd.DataFrame(activities).sort_values('Timestamp', ascending=False)
        
    # Add other utility methods here...

if __name__ == "__main__":
    dashboard = DreamDashboard()
    dashboard.run()
