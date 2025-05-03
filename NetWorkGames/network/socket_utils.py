import json
import socket
def send_json(sock, data):
    message = json.dumps(data).encode()
    sock.sendall(len(message).to_bytes(4, 'big') + message)

def receive_json(sock):
    length = int.from_bytes(sock.recv(4), 'big')
    message = sock.recv(length).decode()
    return json.loads(message)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually need to reach the internet
        s.connect(("8.8.8.8", 80))  
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip