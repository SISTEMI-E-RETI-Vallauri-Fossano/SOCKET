import socket
from network.socket_utils import send_json, receive_json, get_local_ip

SERVER_HOST = "localhost"  # arbitro's host
SERVER_PORT = 5000  # arbitro's port

def main():
    if()
    nickname = input("Enter your name: ")
    game_type = input("Enter game (tris/rps): ")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        send_json(sock, {"action": "join_game", "name": nickname, "game": game_type})
        
        while True:
            message = receive_json(sock)
            if message["type"] == "prompt_move":
                move = input("Your move: ")
                send_json(sock, {"action": "move", "value": move})
            elif message["type"] == "game_result":
                print(f"Game over! Result: {message['result']}")
                break

if __name__ == "__main__":
    main()
