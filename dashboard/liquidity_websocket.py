"""
WebSocket server for real-time liquidity updates
"""

import asyncio
import json
import websockets
import logging
from datetime import datetime
from typing import Dict, Set
from liquidity_monitor import LiquidityMonitor

class LiquidityWebsocketServer:
    def __init__(self, liquidity_monitor: LiquidityMonitor, host='localhost', port=8765):
        self.liquidity_monitor = liquidity_monitor
        self.host = host
        self.port = port
        self.logger = logging.getLogger("LiquidityWebsocket")
        
        # Track connected clients
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.token_subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        
    async def start(self):
        """Start the WebSocket server"""
        self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        try:
            server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            await server.wait_closed()
            
        except Exception as e:
            self.logger.error(f"Error starting WebSocket server: {e}")
            
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle individual client connections"""
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Client disconnected")
            
        finally:
            self.clients.remove(websocket)
            # Remove from token subscriptions
            for subs in self.token_subscriptions.values():
                subs.discard(websocket)
                
    async def process_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Process incoming messages from clients"""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'subscribe':
                token = data.get('token')
                if token:
                    await self.subscribe_to_token(websocket, token)
                    
            elif action == 'unsubscribe':
                token = data.get('token')
                if token:
                    await self.unsubscribe_from_token(websocket, token)
                    
            elif action == 'get_summary':
                token = data.get('token')
                if token:
                    await self.send_liquidity_summary(websocket, token)
                    
            elif action == 'get_alerts':
                token = data.get('token')
                await self.send_alerts(websocket, token)
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
            
        except Exception as e:
            await self.send_error(websocket, f"Error processing message: {str(e)}")
            
    async def subscribe_to_token(self, websocket: websockets.WebSocketServerProtocol, token: str):
        """Subscribe client to token updates"""
        if token not in self.token_subscriptions:
            self.token_subscriptions[token] = set()
        self.token_subscriptions[token].add(websocket)
        
        await self.send_message(websocket, {
            'event': 'subscribed',
            'token': token,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send initial summary
        await self.send_liquidity_summary(websocket, token)
        
    async def unsubscribe_from_token(self, websocket: websockets.WebSocketServerProtocol, token: str):
        """Unsubscribe client from token updates"""
        if token in self.token_subscriptions:
            self.token_subscriptions[token].discard(websocket)
            
        await self.send_message(websocket, {
            'event': 'unsubscribed',
            'token': token,
            'timestamp': datetime.now().isoformat()
        })
        
    async def broadcast_liquidity_update(self, token: str):
        """Broadcast liquidity updates to subscribed clients"""
        if token not in self.token_subscriptions:
            return
            
        summary = self.liquidity_monitor.get_liquidity_summary(token)
        if not summary:
            return
            
        message = {
            'event': 'liquidity_update',
            'token': token,
            'data': summary,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all subscribed clients
        websockets_to_remove = set()
        for websocket in self.token_subscriptions[token]:
            try:
                await self.send_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
                
        # Clean up closed connections
        for websocket in websockets_to_remove:
            self.token_subscriptions[token].discard(websocket)
            
    async def broadcast_alert(self, alert: Dict):
        """Broadcast alerts to relevant clients"""
        token = alert.get('token')
        
        # If token-specific alert, only send to subscribers
        if token and token in self.token_subscriptions:
            clients = self.token_subscriptions[token]
        else:
            # Otherwise send to all clients
            clients = self.clients
            
        message = {
            'event': 'alert',
            'data': alert,
            'timestamp': datetime.now().isoformat()
        }
        
        websockets_to_remove = set()
        for websocket in clients:
            try:
                await self.send_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
                
        # Clean up closed connections
        for websocket in websockets_to_remove:
            self.clients.discard(websocket)
            for subs in self.token_subscriptions.values():
                subs.discard(websocket)
                
    async def send_liquidity_summary(self, websocket: websockets.WebSocketServerProtocol, token: str):
        """Send liquidity summary to client"""
        summary = self.liquidity_monitor.get_liquidity_summary(token)
        
        await self.send_message(websocket, {
            'event': 'liquidity_summary',
            'token': token,
            'data': summary,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_alerts(self, websocket: websockets.WebSocketServerProtocol, token: str = None):
        """Send alerts to client"""
        alerts = self.liquidity_monitor.get_alerts(token)
        
        await self.send_message(websocket, {
            'event': 'alerts',
            'token': token,
            'data': alerts,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_error(self, websocket: websockets.WebSocketServerProtocol, error: str):
        """Send error message to client"""
        await self.send_message(websocket, {
            'event': 'error',
            'message': error,
            'timestamp': datetime.now().isoformat()
        })
        
    @staticmethod
    async def send_message(websocket: websockets.WebSocketServerProtocol, message: Dict):
        """Send message to client"""
        await websocket.send(json.dumps(message))
        
# Example usage:
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize liquidity monitor
    rpc_url = os.getenv('SKALE_RPC', 'https://mainnet.skalenodes.com/v1/elated-tan-skat')
    monitor = LiquidityMonitor(rpc_url)
    
    # Create and start WebSocket server
    server = LiquidityWebsocketServer(monitor)
    
    # Run the server
    asyncio.get_event_loop().run_until_complete(server.start())
