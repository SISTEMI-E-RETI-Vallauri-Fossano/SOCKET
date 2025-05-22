# turing_test_logic.py
import socket
import threading
import time
import os
import random
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

        message_count = 0  # Counter to track the number of messages

        while message_count < 10:  # Limit the conversation to 10 messages
            # Set a random timeout for the socket
            con.settimeout(random.randint(5, 10))

            try:
                data_bytes = con.recv(1024)
                if not data_bytes:
                    print(f"Client {addr} disconnected.")
                    break

                user_message = data_bytes.decode("utf-8").strip()
                print(f"Received from client {addr}: '{user_message}'")

                if user_message.lower() in ["bye", "goodbye", "exit", "i'm done"]:
                    response_text = "Alright, bye for now! It was interesting chatting."
                    con.sendall(response_text.encode("utf-8"))
                    break

                # Add a random delay before responding
                delay = random.randint(5, 15)
                time.sleep(delay)

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

                message_count += 1  # Increment the message counter

            except socket.timeout:
                # Generate a conversation starter
                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents='Ask a casual question to start a conversation.',
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

                ai_response_text = response.text
                con.sendall(ai_response_text.encode("utf-8"))

                message_count += 1  # Increment the message counter

            finally:
                # Reset the socket timeout
                con.settimeout(None)

        # End the conversation and ask the user if they thought the chat was a bot or a human
        esito(con, addr, "AI model")

    except socket.error as e:
        print(f"Socket error for {addr}: {e}")
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
    finally:
        print(f"Closing connection for: {addr}")
        con.close()

def esito(con, addr, who):
    con.sendall("The conversation has ended. Do you think you were chatting with a bot?".encode("utf-8"))
    data_bytes = con.recv(1024)
    if not data_bytes:
        print(f"Client {addr} disconnected.")

    user_message = data_bytes.decode("utf-8").strip()
    print(f"Received from client {addr}: '{user_message}'")
    con.sendall(f"Well you were talking with a {who}".encode("utf-8"))

def game_chat_client(con, addr, peer):
    print(f"Thread started for connection from: {addr}")

    message_count = 0  # Counter to track the number of messages

    try:
        while message_count < 10:  # Limit the conversation to 10 messages
            data_bytes = con.recv(1024)
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

            message_count += 1  # Increment the message counter

        # End the conversation and ask the user if they thought the chat was a bot or a human
        esito(con, addr, "Person")
        esito(peer, peer.getpeername(), "Person")

    except socket.error as e:
        print(f"Socket error for {addr}: {e}")
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
    finally:
        print(f"Closing connection for: {addr}")
        con.close()
