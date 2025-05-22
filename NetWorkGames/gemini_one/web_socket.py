import asyncio
import websockets
import socket

TCP_HOST = '127.0.0.1'
TCP_PORT = 5006  # Match this to your AI server's port

async def handle_websocket(websocket, path):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_HOST, TCP_PORT))
    tcp_socket.setblocking(False)

    async def tcp_to_websocket():
        while True:
            await asyncio.sleep(0.1)
            try:
                data = tcp_socket.recv(1024)
                if data:
                    await websocket.send(data.decode("utf-8"))
            except BlockingIOError:
                continue

    async def websocket_to_tcp():
        async for message in websocket:
            tcp_socket.sendall(message.encode("utf-8"))

    await asyncio.gather(websocket_to_tcp(), tcp_to_websocket())

start_server = websockets.serve(handle_websocket, "localhost", 8765)

print("WebSocket bridge running on ws://localhost:8765/")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
