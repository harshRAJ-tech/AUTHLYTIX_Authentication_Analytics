# test_ws.py — simulates a browser sending behavior events
import asyncio
import websockets
import json

# PASTE YOUR SESSION ID HERE between the quotes
SESSION_ID = "9f28a52c-5dd2-45c9-94aa-52ad7f78263c"

async def test():
    url = f"ws://localhost:8000/ws/{SESSION_ID}"
    print(f"Connecting to {url}")

    async with websockets.connect(url) as ws:
        # Read the welcome message
        welcome = await ws.recv()
        print(f"Server says: {welcome}")

        # Send 5 batches of fake behavior events
        for i in range(5):
            events = [
                {"type": "ks_down", "key": "KeyA", "flight": 150 + i*10, "ts": 1000 + i*250},
                {"type": "ks_up",   "key": "KeyA", "ts": 1080 + i*250},
                {"type": "mm", "x": 300 + i*5, "y": 200 + i*3, "ts": 1100 + i*250},
                {"type": "mm", "x": 310 + i*5, "y": 205 + i*3, "ts": 1150 + i*250},
                {"type": "click",   "x": 320, "y": 210, "ts": 1200 + i*250},
            ]

            payload = json.dumps({"events": events, "ts": 1000 + i*250})
            await ws.send(payload)
            print(f"Sent batch {i+1}")

            # Read the trust score response
            response = await ws.recv()
            data = json.loads(response)
            print(f"Trust score: {data.get('trust_score')} | Risk: {data.get('risk_level')} | Anomaly: {data.get('is_anomaly')}")

            await asyncio.sleep(0.25)

        print("✅ Test complete!")

asyncio.run(test())


