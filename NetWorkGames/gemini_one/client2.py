import socket
import threading
import time
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Input, Static

ip = '127.0.0.1'
porta = 5007
endpoint = (ip, porta)
buf_size = 1024

class ChatUIApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        width: 90%;
        height: 100%;
        layout: vertical;
        align-horizontal: center;
    }

    #scroll-container {
        border: round gray;
        height: 80%;
        width: 100%;
        overflow-y: auto;
    }

    Input {
    height:20%;
        width: 100%;
    }

    .message {
        padding: 1;
        border-bottom: solid #555;
    }
    """

    def __init__(self):
        super().__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.connect(endpoint)
            # Start a thread to receive messages from the server
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

        except ConnectionRefusedError:
            print("Error: Connection refused. Ensure the server is running and accessible.")
        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            self.scroll_container = VerticalScroll(id="scroll-container")
            yield self.scroll_container
            self.input = Input(placeholder="Type your message...")
            yield self.input

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:
            return

        self.skt.sendall(message.encode("utf-8"))

        if message.lower() in ["bye", "goodbye", "exit"]:
            return

        time.sleep(0.1)

        if message:
            self.add_message(f"You: {message}")
            event.input.value = ""

    def add_message(self, message: str) -> None:
        """Appends a new message to the scroll container."""
        self.scroll_container.mount(Static(message, classes="message"))
        # Scroll to bottom
        self.call_after_refresh(self.scroll_container.scroll_end)

    def receive_messages(self):
        while True:
            try:
                data_bytes = self.skt.recv(buf_size)
                if not data_bytes:
                    self.call_from_thread(self.add_message, "\nServer disconnected.")
                    break
                server_response = data_bytes.decode("utf-8")
                self.call_from_thread(self.add_message, f"\nServer: {server_response}")

                if "Goodbye!" in server_response or "AI not available" in server_response:
                    break
            except socket.error as e:
                self.call_from_thread(self.add_message, f"Socket error: {e}")
                break

if __name__ == "__main__":
    app = ChatUIApp()
    app.run()
