import random


class AI:
    def __init__(self, game_state):
        self.game_state = game_state

    def return_random_move(self):
        length = len(self.game_state.current_valid_moves)
        return self.game_state.current_valid_moves[random.randint(0, length - 1)]
