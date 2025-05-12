import socket
import threading
from network.socket_utils import send_json, receive_json
from games import tris, rps

HOST = '10.0.102.196'
PORT = 5000

games = {
    "tris": tris.GameSession,
    "rps": rps.GameSession,
}

connected_players = []

def handle_player(conn, addr):
    info = receive_json(conn)
    game_type = info["game"]
    name = info["name"]

    print(f"{name} wants to play {game_type}")

    connected_players.append((conn, name, game_type))

    if len(connected_players) >= 2:
        p1, p2 = connected_players.pop(0), connected_players.pop(0)
        if p1[2] == p2[2]:
            session = games[game_type](p1, p2)
            session.play()
        else:
            send_json(p1[0], {"type": "error", "message": "Game mismatch"})
            send_json(p2[0], {"type": "error", "message": "Game mismatch"})

def start_arbitro():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[Arbitro] Listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_player, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_arbitro()
