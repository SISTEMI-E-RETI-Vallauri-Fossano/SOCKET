import socket
import threading
import time
import os
from google import genai
from google.genai import types

# --- Generative AI Model Configuration and Training Prompts ---
turing_game_system_instruction = """
You are participating in a Turing Game. Your goal is to convince the human judge that you are a human being, not an AI.
Engage in natural, human-like conversation.
Avoid robotic, overly formal, or excessively helpful language.
Use common human expressions, conversational filler (like "uhm," "well," "you know"), and slight imperfections if appropriate, but avoid grammatical errors.
Do not reveal you are an AI or discuss your nature as a computer program.
Try to show common human experiences or limitations (without lying about facts that would be easily disproven, e.g., don't say you live in Rome if the context suggests otherwise).
Ask questions back to the human.
If asked directly "Are you a robot/AI?", try to deflect naturally or respond with a question like "Why do you ask?" or "What makes you think that?"
Maintain a consistent persona.
Keep responses concise and natural, mimicking real-time human conversation.
"""

# Initialize the Generative AI client globally
gemini_client = None

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # Initialize the client
    gemini_client = genai.Client(api_key=api_key)

    print("Generative AI client initialized.")

except Exception as e:
    print(f"Error initializing Generative AI client: {e}")
    print("Please ensure GEMINI_API_KEY environment variable is set.")
    gemini_client = None

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

# --- Game/Chat Management Function ---
def game_chat_ia(con, addr):
    print(f"Thread started for connection from: {addr}")

    if gemini_client is None:
        con.sendall("Server AI is not configured. Cannot play Turing game.".encode("utf-8"))
        con.close()
        return

    try:
        print(f"Chat session started for {addr} with Turing Game persona.")

    except Exception as e:
        print(f"Error starting chat session for {addr}: {e}")
        con.sendall("AI chat failed to start. Try again later.".encode("utf-8"))
        con.close()
        return

    try:
        con.sendall("Hey there! Ready to chat?".encode("utf-8"))

        while True:
            data_bytes = con.recv(buf_size)
            if not data_bytes:
                print(f"Client {addr} disconnected.")
                break

            user_message = data_bytes.decode("utf-8").strip()
            print(f"Received from client {addr}: '{user_message}'")

            if user_message.lower() in ["bye", "goodbye", "exit", "i'm done"]:
                response_text = "Alright, bye for now! It was interesting chatting."
                con.sendall(response_text.encode("utf-8"))
                break

            # Generate content using the new method
            response = gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=turing_game_system_instruction,
                    max_output_tokens=400,
                    top_k=2,
                    top_p=0.5,
                    temperature=0.5,
                    response_mime_type='text/plain',
                    stop_sequences=['\n'],
                    seed=42,
                ),
            )

            # Log the raw response for debugging
            raw_response = response.text
            print(f"Raw response: {raw_response}")

            # Directly use the raw response as the AI response text
            ai_response_text = raw_response

            con.sendall(ai_response_text.encode("utf-8"))
            time.sleep(0.1)

    except socket.error as e:
        print(f"Socket error for {addr}: {e}")
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
    finally:
        print(f"Closing connection for: {addr}")
        con.close()

def handle_client(con, addr):
    print(f"Connection accepted from: {addr}")

    # Add the client to the waiting list
    waiting_clients.append((con, addr))
    con.sendall("Waiting for more players to start the game...".encode("utf-8"))

    # Start pairing when there are 5 players
    if len(waiting_clients) == 5:
        start_pairing()

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
        print(f"Pairing client {addr} with AI")
        client.sendall(f"You are {addr} and you are paired with the AI. Start chatting!".encode("utf-8"))

        # Start chat handler for the client paired with AI
        client_handler = threading.Thread(target=game_chat_ia, args=(client, addr))
        client_handler.start()

def game_chat_client(con, addr, peer):
    print(f"Thread started for connection from: {addr}")

    try:
        while True:
            data_bytes = con.recv(buf_size)
            if not data_bytes:
                print(f"Client {addr} disconnected.")
                break

            user_message = data_bytes.decode("utf-8").strip()
            print(f"Received from client {addr}: '{user_message}'")

            if user_message.lower() in ["bye", "goodbye", "exit", "i'm done"]:
                response_text = "Alright, bye for now! It was interesting chatting."
                con.sendall(response_text.encode("utf-8"))
                peer.sendall(f"Your peer {addr} has left the chat.".encode("utf-8"))
                break

            # Forward the message to the peer
            peer.sendall(f"{addr}: {user_message}".encode("utf-8"))

    except socket.error as e:
        print(f"Socket error for {addr}: {e}")
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
    finally:
        print(f"Closing connection for: {addr}")
        con.close()
        if addr in client_pairs:
            peer_addr = client_pairs[addr]
            del client_pairs[addr]
            if peer_addr in client_pairs:
                del client_pairs[peer_addr]

# --- Server Setup ---
try:
    skt.bind(endpoint)
    skt.listen(5)
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
