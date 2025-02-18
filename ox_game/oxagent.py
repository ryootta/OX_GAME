import random
import copy

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
        action = int(3 * y + x)
        if self.turn == PLAYER_O:
            self.board_string[action] = PLAYER_X
        else:
            self.board_string[action] = PLAYER_O
    
    def check_board(self, action):
        if self.board_string[action] == 0:
            return True
        else:
            return False


class SimpleAgent(Agent):
    def __init__(self):
        super().__init__()

    def set_xy(self):
        if super().is_set():
            action = random.randrange(9)
            if self.check_board(action):
                self.board_string[action] = self.turn
                self.y, self.x = divmod(action, 3) #divmodで商と余りを取得
                self.is_agent_set = True
                print(self.board_string)

import rlagent
class RLAgent(Agent):
    def __init__(self):
        super().__init__()
        self.env = rlagent.TicTacToeEnv()
        self.agent = rlagent.TicTacToeAgent(self.env, epsilon = 0.1, min_alpha = 0.01, learning=False)
        import msgpack
        with open('LearningData/RL_learning_data.msgpack', 'rb') as f:
            self.agent.Q = msgpack.load(f) 

    def set_xy(self):
        if super().is_set():
            action = self.agent.get_action()
            if self.check_board(action): #確率は低いが一様
                next_state, reward, done = self.env.step(action)
                self.is_agent_set = True
                print("set_action", action)
                self.x, self.y = divmod(action, 3)

    def set_gui(self, x, y):
        super().set_gui(x, y)
        action = int(3 * y + x)
        self.env.step(action)


if __name__ == "__main__":
    agent = RLAgent()
    agent.set_xy()
    agent.is_agent_set = True
    print(agent.get_xy())
    x = input()
    y = input()
    agent.set_gui(x, y)
    agent.set_xy()
    print(agent.get_xy())
