import socket
import threading
import time

ip = '127.0.0.1'
porta = 5006
endpoint = (ip, porta)
buf_size = 1024

def receive_messages(skt):
    while True:
        try:
            data_bytes = skt.recv(buf_size)
            if not data_bytes:
                print("\nServer disconnected.")
                break
            server_response = data_bytes.decode("utf-8")
            print(f"\nServer: {server_response}")

            if "Goodbye!" in server_response or "AI not available" in server_response:
                break
        except socket.error as e:
            print(f"Socket error: {e}")
            break

def start_client():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        skt.connect(endpoint)
        # Start a thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_messages, args=(skt,))
        receive_thread.start()

        while True:
            message = input("You: ")
            if not message.strip():
                continue  # Don't send empty messages

            skt.sendall(message.encode("utf-8"))

            if message.lower() in ["bye", "goodbye", "exit"]:
                print("Closing connection.")
                break

            time.sleep(0.1)

    except ConnectionRefusedError:
        print("Error: Connection refused. Ensure the server is running and accessible.")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        skt.close()
        print("Client socket closed.")

if __name__ == "__main__":
    start_client()
# The client connects to the server and allows the user to send messages.