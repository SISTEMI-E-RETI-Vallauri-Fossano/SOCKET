import socket
import time

ip = '127.0.0.1'
porta = 5006
endpoint = (ip, porta)
buf_size = 1024

def start_client():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        skt.connect(endpoint)
        print("Connesso al server.")

        while True:
            # Receive initial prompt or previous response from server
            data_bytes = skt.recv(buf_size)
            if not data_bytes:
                print("Server disconnesso.")
                break
            server_response = data_bytes.decode("utf-8")
            print(f"Server: {server_response}")

            if "Goodbye" in server_response: # Simple way to detect server closing
                break

            message = input("You: ")
            if not message: # Don't send empty messages
                continue
            skt.sendall(message.encode("utf-8"))

            if message.lower() in ["bye", "goodbye", "exit"]:
                print("Closing connection.")
                break

            time.sleep(0.1) # Small delay

    except ConnectionRefusedError:
        print("Errore: Connessione rifiutata. Assicurati che il server sia in ascolto.")
    except socket.error as e:
        print(f"Errore socket: {e}")
    except Exception as e:
        print(f"Errore inaspettato: {e}")
    finally:
        skt.close()
        print("Client socket closed.")

if __name__ == "__main__":
    start_client()