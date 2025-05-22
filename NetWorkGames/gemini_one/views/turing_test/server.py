# server.py
import socket
import threading
import time
import random
from views.turing_test.turing_test_logic import game_chat_ia, game_chat_client, esito

# --- Server Configuration ---
ip = '127.0.0.1'
porta = 5006
endpoint = (ip, porta)
buf_size = 1024
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# --- Global Variables ---
waiting_clients = []
client_pairs = {}

def start_pairing():
    print("Starting pairing process...")

    # Pair clients
    while len(waiting_clients) >= 2:
        client1, addr1 = waiting_clients.pop(0)
        client2, addr2 = waiting_clients.pop(0)

        # Pair the clients
        client_pairs[addr1] = client2
        client_pairs[addr2] = client1

        print(f"Pairing clients: {addr1} and {addr2}")

        # Notify clients that they are paired
        client1.sendall(f"You are {addr1} and you are paired with {addr2}. Start chatting!".encode("utf-8"))
        client2.sendall(f"You are {addr2} and you are paired with {addr1}. Start chatting!".encode("utf-8"))

        # Start chat handlers for the paired clients
        client_handler1 = threading.Thread(target=game_chat_client, args=(client1, addr1, client2))
        client_handler2 = threading.Thread(target=game_chat_client, args=(client2, addr2, client1))

        client_handler1.start()
        client_handler2.start()

    # Pair remaining client with AI if any
    if waiting_clients:
        client, addr = waiting_clients.pop(0)
        random_addr = random.choice([addr1, addr2])  # Random choice for AI pairing message
        print(f"Pairing client {addr} with AI")
        client.sendall(f"You are {addr} and you are paired with {random_addr}. Start chatting!".encode("utf-8"))

        # Start chat handler for the client paired with AI
        client_handler = threading.Thread(target=game_chat_ia, args=(client, addr))
        client_handler.start()

def handle_client(con, addr):
    print(f"Connection accepted from: {addr}")

    # Add the client to the waiting list
    waiting_clients.append((con, addr))
    con.sendall("Waiting for more players to start the game...".encode("utf-8"))

    # Start pairing when there are 3 players
    if len(waiting_clients) == 3:
        start_pairing()

# --- Server Setup ---
try:
    skt.bind(endpoint)
    skt.listen(3)
    print(f"Server listening on {ip}:{porta}...")
    print("AI is ready to play the Turing Game.")

    while True:
        try:
            con, addr = skt.accept()

            client_handler = threading.Thread(target=handle_client, args=(con, addr))
            client_handler.start()

        except socket.error as e:
            print(f"Error accepting connection: {e}")
        except KeyboardInterrupt:
            print("Server shutting down.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in main server loop: {e}")

finally:
    skt.close()
    print("Server socket closed.")
