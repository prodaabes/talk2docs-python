import asyncio
import websockets

async def hello():
    uri = 'ws://192.168.0.130:8765'
    async with websockets.connect(uri) as websocket:
        question = input('Question: ')

        await websocket.send(question)

        answer = await websocket.recv()
        print(f'Answer: {answer}')

if __name__ == "__main__":
    asyncio.run(hello())