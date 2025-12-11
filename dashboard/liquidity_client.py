"""
Test client for liquidity WebSocket server
"""

import asyncio
import json
import websockets
import logging
from datetime import datetime
from typing import Optional

class LiquidityWebsocketClient:
    def __init__(self, uri: str = 'ws://localhost:8765'):
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.logger = logging.getLogger("LiquidityClient")
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info("Connected to WebSocket server")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
            
    async def subscribe(self, token: str):
        """Subscribe to token updates"""
        if not self.websocket:
            self.logger.error("Not connected")
            return
            
        await self.websocket.send(json.dumps({
            'action': 'subscribe',
            'token': token
        }))
        
    async def unsubscribe(self, token: str):
        """Unsubscribe from token updates"""
        if not self.websocket:
            self.logger.error("Not connected")
            return
            
        await self.websocket.send(json.dumps({
            'action': 'unsubscribe',
            'token': token
        }))
        
    async def get_summary(self, token: str):
        """Request liquidity summary"""
        if not self.websocket:
            self.logger.error("Not connected")
            return
            
        await self.websocket.send(json.dumps({
            'action': 'get_summary',
            'token': token
        }))
        
    async def get_alerts(self, token: Optional[str] = None):
        """Request alerts"""
        if not self.websocket:
            self.logger.error("Not connected")
            return
            
        await self.websocket.send(json.dumps({
            'action': 'get_alerts',
            'token': token
        }))
        
    async def listen(self):
        """Listen for messages"""
        if not self.websocket:
            self.logger.error("Not connected")
            return
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection closed")
            
        except Exception as e:
            self.logger.error(f"Error in message loop: {e}")
            
    async def handle_message(self, data: dict):
        """Handle incoming messages"""
        event = data.get('event')
        
        if event == 'liquidity_update':
            await self.handle_liquidity_update(data)
            
        elif event == 'alert':
            await self.handle_alert(data)
            
        elif event == 'liquidity_summary':
            await self.handle_summary(data)
            
        elif event == 'alerts':
            await self.handle_alerts_list(data)
            
        elif event in ['subscribed', 'unsubscribed']:
            self.logger.info(f"{event.capitalize()} to {data.get('token')}")
            
        elif event == 'error':
            self.logger.error(f"Server error: {data.get('message')}")
            
    async def handle_liquidity_update(self, data: dict):
        """Handle liquidity update"""
        token = data.get('token')
        update = data.get('data', {})
        
        self.logger.info(f"Liquidity update for {token}:")
        self.logger.info(f"Total liquidity: ${update.get('total_liquidity', 0):,.2f}")
        self.logger.info(f"24h change: {update.get('liquidity_change_24h', 0)*100:.2f}%")
        self.logger.info(f"Active pairs: {update.get('active_pairs', 0)}")
        
    async def handle_alert(self, data: dict):
        """Handle alert"""
        alert = data.get('data', {})
        self.logger.warning(
            f"ALERT [{alert.get('type')}] {alert.get('token')}: "
            f"{alert.get('message')}"
        )
        
    async def handle_summary(self, data: dict):
        """Handle liquidity summary"""
        token = data.get('token')
        summary = data.get('data', {})
        
        self.logger.info(f"Liquidity summary for {token}:")
        self.logger.info(json.dumps(summary, indent=2))
        
    async def handle_alerts_list(self, data: dict):
        """Handle alerts list"""
        token = data.get('token')
        alerts = data.get('data', [])
        
        self.logger.info(f"Alerts for {token or 'all tokens'}:")
        for alert in alerts:
            self.logger.info(
                f"[{alert.get('timestamp')}] {alert.get('type')}: "
                f"{alert.get('message')}"
            )
            
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            
# Example usage:
async def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create client
    client = LiquidityWebsocketClient()
    
    # Connect
    if not await client.connect():
        return
        
    try:
        # Subscribe to DREAM token updates
        await client.subscribe('DREAM')
        
        # Get initial summary
        await client.get_summary('DREAM')
        
        # Listen for updates
        await client.listen()
        
    finally:
        await client.close()
        
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
