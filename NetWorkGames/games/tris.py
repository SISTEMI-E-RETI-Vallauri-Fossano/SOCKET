from network.socket_utils import send_json, receive_json
from sender import send_score_to_castle
from castle_db import save_game_result

class GameSession:
    def __init__(self, p1, p2):
        self.conn1, self.name1, _ = p1
        self.conn2, self.name2, _ = p2

    def play(self):
        send_json(self.conn1, {"type": "prompt_move"})
        move1 = receive_json(self.conn1)["value"]

        send_json(self.conn2, {"type": "prompt_move"})
        move2 = receive_json(self.conn2)["value"]

        # Dummy logic
        winner = self.name1 if move1 > move2 else self.name2
        result = f"{winner} wins!"

        send_json(self.conn1, {"type": "game_result", "result": result})
        send_json(self.conn2, {"type": "game_result", "result": result})

        send_score_to_castle({"p1": self.name1, "p2": self.name2, "winner": winner})
        save_game_result(self.name1, self.name2, winner)
