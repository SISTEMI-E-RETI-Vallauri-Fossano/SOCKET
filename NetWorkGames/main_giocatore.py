import socket
from network.socket_utils import send_json, receive_json, get_local_ip
import curses

SERVER_HOST = "10.0.102.196"  # arbitro's host
SERVER_PORT = 5000  # arbitro's port

import curses

import curses

class UI_giocatore:
    def __init__(self, ip, nickname):
        self._ip = ip
        self._nickname = nickname
        self._last_window = None  # Internal: reference to the active window

    # IP property
    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

    def displayTerminal(self):
        pass

    def executecommand(self, cmd):
        pass

    def shiftCardgamesbarLeft(self):
        pass

    def shiftCardgamesbarRight(self):
        pass

    def tabOnlineplayers(self):
        pass

    def show(self):
        curses.wrapper(self._curses_show)

    def _curses_show(self, stdscr):
        self._render_box(stdscr, "")

    def writeOver(self, text):
        curses.wrapper(lambda stdscr: self._render_box(stdscr, text))

    def _render_box(self, stdscr, text):
        stdscr.clear()
        curses.curs_set(1)

        height, width = stdscr.getmaxyx()

        box_height = height // 2
        box_width = width // 2
        box_y = (height - box_height) // 2
        box_x = (width - box_width) // 2

        win = curses.newwin(box_height, box_width, box_y, box_x)
        win.box()
        win.keypad(True)

        # Save the window for reuse in getUserInput
        self._last_window = win

        if text:
            max_text_width = box_width - 2
            trimmed_text = text[:max_text_width]
            text_x = (box_width - len(trimmed_text)) // 2
            win.addstr(1, text_x, trimmed_text)

        center_y = box_height // 2
        center_x = box_width // 2
        win.move(center_y, center_x)

        win.refresh()
        win.getch()
        curses.curs_set(0)

    def getUserInput(self, prompt):
        return curses.wrapper(lambda stdscr: self._input_prompt_on_last_win(stdscr, prompt))

    def _input_prompt_on_last_win(self, stdscr, prompt):
        curses.curs_set(1)

        # Reuse the existing window if available
        win = self._last_window
        if not win:
            # fallback if writeOver wasn't called
            height, width = stdscr.getmaxyx()
            box_height = height // 2
            box_width = width // 2
            box_y = (height - box_height) // 2
            box_x = (width - box_width) // 2
            win = curses.newwin(box_height, box_width, box_y, box_x)
            win.box()

        win.keypad(True)

        box_height, box_width = win.getmaxyx()

        prompt_y = 2
        prompt_x = (box_width - len(prompt)) // 2
        win.addstr(prompt_y, prompt_x, prompt)

        input_y = box_height // 2
        input_x = 2
        user_input = ""

        win.move(input_y, input_x)
        win.refresh()

        while True:
            key = win.getch()

            if key in (curses.KEY_ENTER, 10, 13):
                break
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if user_input:
                    user_input = user_input[:-1]
                    win.move(input_y, input_x + len(user_input))
                    win.delch()
            elif 32 <= key <= 126:
                if len(user_input) < (box_width - 4):
                    user_input += chr(key)
                    win.addch(input_y, input_x + len(user_input) - 1, key)

            win.move(input_y, input_x + len(user_input))
            win.refresh()

        curses.curs_set(0)
        return user_input

def main():
    #if(!(logica di login(current_ip)))
    nickname = input("Enter your name: ")
    game_type = input("Enter game (tris/rps): ")

    console = UI_giocatore(get_local_ip(), nickname)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        send_json(sock, {"action": "join_game", "name": nickname, "game": game_type})
        while True:
            message = receive_json(sock)
            if message["type"] == "prompt_move":
                console.writeOver+(f"You need to write a bigger number than the opponent's one")    
                move = console.getUserInput("Your move: ")
                send_json(sock, {"action": "move", "value": move})
            elif message["type"] == "game_result":
                print(f"Game over! Result: {message['result']}")
                break

if __name__ == "__main__":
    main()
