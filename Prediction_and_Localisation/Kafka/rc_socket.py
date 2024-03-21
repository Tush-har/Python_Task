import asyncio
import websockets
import json

async def test_consumer():
    uri = "ws://localhost:8200/ws"  # WebSocket server URI
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")
        try:
            while True:
                message = await websocket.recv()
                print("Received message:", json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")

# Run the WebSocket consumer
asyncio.get_event_loop().run_until_complete(test_consumer())
