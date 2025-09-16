"""
Dream Advanced Visualizations
Enhanced visualization features for the Dream-Mind-Lucid dashboard
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
from scipy import stats

class DreamVisualizer:
    def __init__(self, theme="dark"):
        self.theme = theme
        self.color_palette = {
            "dream": "#7B68EE",  # Medium slate blue
            "mind": "#20B2AA",   # Light sea green
            "lucid": "#FFD700",  # Gold
            "positive": "#00FF7F",# Spring green
            "negative": "#FF4500",# Orange red
            "neutral": "#B8860B"  # Dark goldenrod
        }
        
    def create_3d_performance_plot(
        self,
        df: pd.DataFrame,
        agent_name: str
    ) -> go.Figure:
        """Create 3D performance visualization"""
        fig = go.Figure(data=[go.Scatter3d(
            x=df['dream_score'],
            y=df['mind_score'],
            z=df['lucid_score'],
            mode='markers+lines',
            marker=dict(
                size=8,
                color=df['reward_points'],
                colorscale='Viridis',
                opacity=0.8
            ),
            text=[f"Time: {t}" for t in df['timestamp']],
            hoverinfo='text'
        )])
        
        fig.update_layout(
            title=f"3D Performance Trajectory - {agent_name}",
            scene=dict(
                xaxis_title='Dream Score',
                yaxis_title='Mind Score',
                zaxis_title='Lucid Score'
            ),
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig
        
    def create_token_flow_sankey(
        self,
        flow_data: Dict[str, List[float]]
    ) -> go.Figure:
        """Create Sankey diagram for token flow"""
        nodes = []
        links = []
        
        # Define nodes
        node_labels = [
            "Total Supply", "Circulation", "Agent Pool",
            "Treasury", "Burned", "Owner Earnings",
            "Performance Rewards"
        ]
        
        for i, label in enumerate(node_labels):
            nodes.append({"label": label})
            
        # Define links
        for source, targets in flow_data.items():
            source_idx = node_labels.index(source)
            for target, value in targets:
                target_idx = node_labels.index(target)
                links.append({
                    "source": source_idx,
                    "target": target_idx,
                    "value": value
                })
                
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=list(self.color_palette.values())[:len(node_labels)]
            ),
            link=dict(
                source=[link["source"] for link in links],
                target=[link["target"] for link in links],
                value=[link["value"] for link in links]
            )
        )])
        
        fig.update_layout(
            title="Token Flow Visualization",
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig
        
    def create_performance_radar(
        self,
        metrics: Dict[str, float]
    ) -> go.Figure:
        """Create radar chart for performance metrics"""
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name='Current Performance'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1000]
                )
            ),
            showlegend=False,
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig
        
    def create_advanced_price_chart(
        self,
        price_data: pd.DataFrame,
        token_symbol: str,
        indicators: List[str],
        show_liquidity: bool = True
    ) -> go.Figure:
        """Create candlestick chart with technical indicators"""
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{token_symbol} Price', 'Volume')
        )
        
        # Calculate number of rows needed
        n_rows = 1 + ('RSI' in indicators) + ('MACD' in indicators)
        if show_liquidity:
            n_rows += 1

        # Create subplots
        fig = make_subplots(
            rows=n_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5] + [0.2] * (n_rows - 1)
        )

        # Main candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=price_data.index,
                open=price_data['open'],
                high=price_data['high'],
                low=price_data['low'],
                close=price_data['close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        current_row = 1

        # Add selected indicators
        if 'SMA' in indicators:
            for period in [20, 50, 200]:
                fig.add_trace(
                    go.Scatter(
                        x=price_data.index,
                        y=price_data[f'SMA_{period}'],
                        name=f'SMA {period}',
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )

        if 'BBANDS' in indicators:
            for band in ['Upper', 'Middle', 'Lower']:
                fig.add_trace(
                    go.Scatter(
                        x=price_data.index,
                        y=price_data[f'BB_{band}'],
                        name=f'BB {band}',
                        line=dict(dash='dash')
                    ),
                    row=1, col=1
                )

        if 'RSI' in indicators:
            current_row += 1
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=price_data['RSI'],
                    name='RSI'
                ),
                row=current_row, col=1
            )
            # Add RSI levels
            for level in [30, 70]:
                fig.add_hline(
                    y=level,
                    line_dash="dash",
                    line_color="gray",
                    row=current_row
                )

        if 'MACD' in indicators:
            current_row += 1
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=price_data['MACD'],
                    name='MACD'
                ),
                row=current_row, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=price_data['MACD_Signal'],
                    name='Signal'
                ),
                row=current_row, col=1
            )
            fig.add_trace(
                go.Bar(
                    x=price_data.index,
                    y=price_data['MACD_Hist'],
                    name='MACD Hist'
                ),
                row=current_row, col=1
            )

        # Add liquidity visualization
        if show_liquidity:
            current_row += 1
            fig.add_trace(
                go.Bar(
                    x=price_data.index,
                    y=price_data['depth'],
                    name='Market Depth'
                ),
                row=current_row, col=1
            )
            # Add bid-ask spread as a line
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=price_data['spread'],
                    name='Bid-Ask Spread',
                    line=dict(color='red')
                ),
                row=current_row, col=1
            )
        
        # Volume bars
        colors = ['red' if row['open'] > row['close'] else 'green'
                 for i, row in price_data.iterrows()]
        
        fig.add_trace(
            go.Bar(
                x=price_data['timestamp'],
                y=price_data['volume'],
                marker_color=colors,
                name='Volume'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"{token_symbol} Price Analysis",
            yaxis_title="Price (USD)",
            yaxis2_title="Volume",
            xaxis_rangeslider_visible=False,
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig
        
    def create_burn_heatmap(
        self, burn_data: pd.DataFrame
    ) -> go.Figure:
        """Create heatmap of token burns"""
        # Pivot data for heatmap
        pivot_data = burn_data.pivot(
            index='day_of_week',
            columns='hour',
            values='amount'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Token Burn Heatmap (by day and hour)",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig
        
    def create_network_graph(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> go.Figure:
        """Create network graph visualization"""
        edge_x = []
        edge_y = []
        
        for edge in edges:
            x0, y0 = edge['source']
            x1, y1 = edge['target']
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = [node['pos'][0] for node in nodes]
        node_y = [node['pos'][1] for node in nodes]
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node['label'] for node in nodes],
            marker=dict(
                size=10,
                color=[node['color'] for node in nodes],
                line_width=2
            )
        )
        
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Agent Interaction Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                template="plotly_dark" if self.theme == "dark" else "plotly_white"
            )
        )
        
        return fig
        
    def create_prediction_plot(
        self,
        historical_data: pd.DataFrame,
        forecast_data: pd.DataFrame,
        metric: str
    ) -> go.Figure:
        """Create prediction plot with confidence intervals"""
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data[metric],
            name='Historical',
            line=dict(color=self.color_palette['neutral'])
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_data['timestamp'],
            y=forecast_data['prediction'],
            name='Forecast',
            line=dict(color=self.color_palette['dream'])
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast_data['timestamp'].tolist() + forecast_data['timestamp'].tolist()[::-1],
            y=forecast_data['upper_bound'].tolist() + forecast_data['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(123, 104, 238, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.update_layout(
            title=f"{metric} Forecast",
            xaxis_title="Time",
            yaxis_title=metric,
            template="plotly_dark" if self.theme == "dark" else "plotly_white"
        )
        
        return fig

    @staticmethod
    def calculate_performance_stats(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate performance statistics"""
        return {
            'mean_dream_score': df['dream_score'].mean(),
            'mean_mind_score': df['mind_score'].mean(),
            'mean_lucid_score': df['lucid_score'].mean(),
            'success_rate': (df['successful_dreams'].sum() / df['total_dreams'].sum()) * 100,
            'dream_score_trend': stats.linregress(range(len(df)), df['dream_score']).slope,
            'reward_efficiency': df['reward_points'].sum() / df['total_dreams'].sum()
        }

# Example usage in dashboard
def add_advanced_visualizations(dashboard):
    visualizer = DreamVisualizer()
    
    # Add 3D performance plot
    st.subheader("3D Performance Analysis")
    performance_df = dashboard.get_performance_data()
    fig_3d = visualizer.create_3d_performance_plot(
        performance_df,
        "DreamKeeper"
    )
    st.plotly_chart(fig_3d)
    
    # Add token flow visualization
    st.subheader("Token Flow Analysis")
    flow_data = dashboard.get_token_flow_data()
    fig_sankey = visualizer.create_token_flow_sankey(flow_data)
    st.plotly_chart(fig_sankey)
    
    # Add performance radar
    st.subheader("Performance Metrics")
    metrics = dashboard.get_current_metrics()
    fig_radar = visualizer.create_performance_radar(metrics)
    st.plotly_chart(fig_radar)
    
    # Add price analysis
    st.subheader("Token Price Analysis")
    price_data = dashboard.get_price_data("DREAM")
    fig_price = visualizer.create_price_candlestick(
        price_data,
        "DREAM"
    )
    st.plotly_chart(fig_price)
    
    # Add burn heatmap
    st.subheader("Token Burn Analysis")
    burn_data = dashboard.get_burn_data()
    fig_heatmap = visualizer.create_burn_heatmap(burn_data)
    st.plotly_chart(fig_heatmap)
    
    # Add network graph
    st.subheader("Agent Interaction Network")
    nodes, edges = dashboard.get_network_data()
    fig_network = visualizer.create_network_graph(nodes, edges)
    st.plotly_chart(fig_network)
    
    # Add predictions
    st.subheader("Performance Predictions")
    historical = dashboard.get_historical_data()
    forecast = dashboard.get_forecast_data()
    fig_predict = visualizer.create_prediction_plot(
        historical,
        forecast,
        "dream_score"
    )
    st.plotly_chart(fig_predict)
