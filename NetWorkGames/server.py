import socket
import threading
import time # For simulating delays

# --- Server Configuration ---
ip = '127.0.0.1'
porta = 5006
endpoint = (ip, porta)
buf_size = 1024
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Global lists (consider using locks if multiple threads modify them often)
tris_games = [] # Placeholder for game states if you implement specific games
chat_messages = [] # A simple global chat log
import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) # Set the API key using the GOOGLE_API_KEY env var.
                        # Alternatively, you could set the API key explicitly:
                        # client = genai.Client(api_key="your_api_key")
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Tell me a story in 300 words.'
)
print(response.text)

print(response.model_dump_json(
    exclude_none=True, indent=4))

# Configure your API key
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# OR, if you use the Client:
# client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# If you configure with genai.configure, you can get the model like this:
# model = genai.GenerativeModel('gemini-pro')

# If you use the Client, it's typically:
# model = client.models.get('gemini-pro') # Or list to see available models

# You'll then call generate_content on the model or the client depending on the setup.

def get_ai_response(prompt):
    try:
        # Assuming you've configured with genai.configure(api_key=...)
        # model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content(prompt)

        # Or, if you have a client instance:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) # Re-instantiate or pass client
        response = client.models.generate_content(
            model='gemini-pro', # Or 'gemini-1.5-flash', etc.
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error calling AI model: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again."

# Replace get_ai_response_mock with this real function in your actual code.
# You might want to instantiate the client or model once outside the function
# if you pass it as an argument or use global scope.
def get_ai_response_mock(prompt):
    """
    Mocks an AI model's response for demonstration purposes.
    In a real scenario, this would call an actual AI API.
    """
    prompt_lower = prompt.lower()
    if "human" in prompt_lower or "ai" in prompt_lower or "robot" in prompt_lower:
        return "I am an AI, a large language model trained by Google. How can I assist you?"
    elif "hello" in prompt_lower or "hi" in prompt_lower:
        return "Hello there! What's on your mind?"
    elif "game" in prompt_lower or "play" in prompt_lower or "tictactoe" in prompt_lower or "tris" in prompt_lower:
        return "I can play simple text-based games. What game would you like to play, or are you just here for a chat?"
    elif "weather" in prompt_lower:
        return "I cannot provide real-time weather information as I do not have access to current external data."
    elif "bye" in prompt_lower or "goodbye" in prompt_lower:
        return "Goodbye! It was nice chatting with you."
    else:
        return f"You said: '{prompt}'. I'm an AI designed to assist. How can I help you further?"

# --- Game/Chat Management Function ---
def game_chat_ia(con, addr):
    """
    This function will be executed by each new thread.
    It manages a chat session where the AI determines the conversation mode.
    """
    print(f"Thread started for connection from: {addr}")

    conversation_state = "initial_discovery" # States: initial_discovery, ai_identity_confirmed, game_mode_selection, general_chat, playing_game
    detection_attempts = 0
    MAX_DETECTION_ATTEMPTS = 3 # How many messages to try to detect intent

    # Loop for initial discovery phase
    while conversation_state == "initial_discovery" and detection_attempts < MAX_DETECTION_ATTEMPTS:
        try:
            con.sendall("Hello! What brings you here? Are you looking to chat or play a game?".encode("utf-8"))
            data_bytes = con.recv(buf_size)
            if not data_bytes: # Client disconnected
                print(f"Client {addr} disconnected during initial discovery.")
                break

            data_str = data_bytes.decode("utf-8").strip()
            print(f"Received from client {addr} (discovery): '{data_str}'")
            chat_messages.append(f"{addr} (discovery): {data_str}")

            # --- Simple Intent Detection (The "Guessing" Part) ---
            prompt_lower = data_str.lower()
            if "human" in prompt_lower or "ai" in prompt_lower or "robot" in prompt_lower or "bot" in prompt_lower:
                response = get_ai_response("are you human or ai?") # Ask the AI model
                con.sendall(response.encode("utf-8"))
                conversation_state = "ai_identity_confirmed"
                print(f"Client {addr} determined to be inquiring about AI identity.")
            elif "game" in prompt_lower or "play" in prompt_lower or "tris" in prompt_lower or "tic-tac-toe" in prompt_lower:
                response = get_ai_response("want to play a game") # Ask the AI model
                con.sendall(response.encode("utf-8"))
                conversation_state = "game_mode_selection"
                print(f"Client {addr} determined to be interested in a game.")
            else:
                response = get_ai_response(data_str) # Get a general AI response
                con.sendall(response.encode("utf-8"))
                detection_attempts += 1
                if detection_attempts >= MAX_DETECTION_ATTEMPTS:
                    conversation_state = "general_chat" # Default to general chat if no clear intent after attempts
                    print(f"Client {addr} defaulted to general chat mode after {MAX_DETECTION_ATTEMPTS} attempts.")

            time.sleep(0.1) # Small delay to prevent tight loop issues

        except socket.error as e:
            print(f"Socket error during initial discovery for {addr}: {e}")
            break
        except Exception as e:
            print(f"Unexpected error during initial discovery for {addr}: {e}")
            break

    # Once a state is determined, or max attempts reached, enter the main loop
    if conversation_state == "initial_discovery": # If loop broke without determination
        print(f"No clear intent determined for {addr}, closing connection.")
        con.close()
        return

    # --- Main Chat/Game Loop based on determined state ---
    print(f"Entering main interaction loop for {addr} in state: {conversation_state}")
    try:
        while True:
            data_bytes = con.recv(buf_size)
            if not data_bytes: # Client disconnected
                print(f"Client {addr} disconnected.")
                break

            data_str = data_bytes.decode("utf-8").strip()
            print(f"Received from client {addr}: '{data_str}' (State: {conversation_state})")
            chat_messages.append(f"{addr}: {data_str}") # Add to global chat log

            response = ""
            if conversation_state == "ai_identity_confirmed" or conversation_state == "general_chat":
                # Continue general AI chat
                response = get_ai_response(data_str)
                if data_str.lower() in ["bye", "goodbye", "exit"]:
                    response = "Goodbye! Hope to chat again soon."
                    con.sendall(response.encode("utf-8"))
                    break # End conversation
            elif conversation_state == "game_mode_selection":
                # Logic for selecting and starting a game
                if "tictactoe" in data_str.lower() or "tris" in data_str.lower():
                    response = "Great! Let's play Tic-Tac-Toe. (Game logic goes here)"
                    conversation_state = "playing_game"
                    # Initialize game here, perhaps add to tris_games list
                else:
                    response = "I can play Tic-Tac-Toe. Do you want to play that, or just chat?"
            elif conversation_state == "playing_game":
                # Logic for the specific game (e.g., Tic-Tac-Toe moves)
                response = f"You made a move: '{data_str}'. (Game processing... AI's turn)"
                # This is where game state would be updated and moves validated
                # If game ends, potentially transition back to "general_chat" or close connection

            con.sendall(response.encode("utf-8"))
            time.sleep(0.1) # Small delay

    except socket.error as e:
        print(f"Socket error in main loop for {addr}: {e}")
    except Exception as e:
        print(f"Unexpected error in main loop for {addr}: {e}")
    finally:
        print(f"Closing connection for: {addr}")
        con.close()

# --- Server Setup ---
try:
    skt.bind(endpoint)
    skt.listen(5) # Listen for up to 5 pending connections
    print(f"Server in ascolto su {ip}:{porta}...")

    while True:
        try:
            con, addr = skt.accept()
            print(f"Connessione accettata da: {addr}")

            # Create and start a new thread for each connection
            client_handler = threading.Thread(target=game_chat_ia, args=(con, addr))
            client_handler.start()

        except socket.error as e:
            print(f"Si è verificato un errore durante l'accettazione della connessione: {e}")
        except KeyboardInterrupt:
            print("Server shutting down due to user interrupt.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in main server loop: {e}")

finally:
    skt.close()
    print("Server socket closed.")