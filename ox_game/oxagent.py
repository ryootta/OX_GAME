import random

AGENT_THINK_TIME = 10
PLAYER_O = 1
PLAYER_X = -1
OUT_SCOPE = -1

class Agent:
    def __init__(self):
        self.think_time = AGENT_THINK_TIME
        self.is_agent_set = False
        if random.randrange(2) == 0:
            self.turn = PLAYER_O
        else:
            self.turn = PLAYER_X
        self.board_string = [0] * 9
    
    def is_set(self):
        if self.think_time == 0:
            self.think_time = AGENT_THINK_TIME
            return True
        else:
            self.think_time -= 1
            return False

    def get_xy(self):
        if self.is_agent_set:
            self.is_agent_set = False
            return self.x, self.y
        else:
            return OUT_SCOPE, OUT_SCOPE
    
    def set_gui(self, x, y):
        if self.turn == PLAYER_O:
            self.board_string[3*y + x] = PLAYER_X
        else:
            self.board_string[3*y + x] = PLAYER_O
    
    def check_board(self, action):
        if self.board_string[action] == 0:
            return True
        else:
            return False


class SimpleAgent(Agent):
    def __init__(self):
        super().__init__()

    def set_random_xy(self):
        if super().is_set():
            action = random.randrange(9)
            if self.check_board(action):
                self.board_string[action] = self.turn
                self.y, self.x = divmod(action, 3) #divmodで商と余りを取得
                self.is_agent_set = True
                print(self.board_string)
