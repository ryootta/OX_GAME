import pyxel
import random

SCREEN_WIDTH = 200 
SCREEN_HEIGHT = 150
SCREEN_GRID_SIZE = 90
SCREEN_CELL_SIZE = 30
GRID_POS_X = SCREEN_WIDTH // 2 - SCREEN_GRID_SIZE // 2
GRID_POS_Y = SCREEN_HEIGHT // 2 - SCREEN_GRID_SIZE // 2 + SCREEN_HEIGHT // 12
START_SCENE = "start"
PLAY_SCENE = "play"
PLAYER_O = "player_o"
PLAYER_X = "player_x"
PLAYER_NONE = "player_none"
OUT_SCOPE = -1
GAME_OVER_DISPLAY_TIME = 60 * 2
AGENT_THINK_TIME = 20

class Shape():
    def __init__(self, x, y):
        size = 16
        self.x = SCREEN_GRID_SIZE * x // 3 + GRID_POS_X + size // 2 - 1 
        self.y = SCREEN_GRID_SIZE * y // 3 + GRID_POS_Y + size // 2 - 1

class O(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
    def draw(self):
        pyxel.blt(self.x , self.y, 0, 0, 16, 16, 16, pyxel.COLOR_WHITE)

class X(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self):
        pyxel.blt(self.x , self.y, 0, 16, 16, 16, 16, pyxel.COLOR_WHITE)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="OX GAME")
        pyxel.mouse(True)
        self.grid = Grid()
        self.init_param()
        self.gui_param()
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)
    
    def init_param(self):
        self.current_scene = START_SCENE
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.player = PLAYER_O
        self.is_agent = False
        self.winner = None
        self.grid.init()
    
    def gui_param(self):
        self.pos_x_string = 20
        self.pos_y_alone = 60
        self.pos_y_together = 80
        self.blank = 5
        self.font_size = 5

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()

    def draw(self):
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()

    def update_start_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.init_param()
            button_x = SCREEN_WIDTH // 8 + self.pos_x_string - self.blank
            button_y_alone = self.pos_y_alone - self.blank
            button_y_together = self.pos_y_together - self.blank
            button_with = SCREEN_WIDTH // 3
            button_hight = self.font_size + self.blank * 2
            if button_x <= pyxel.mouse_x <= button_x + button_with and button_y_alone <= pyxel.mouse_y <= button_y_alone + button_hight:
                self.current_scene = PLAY_SCENE
                self.is_agent = True
                self.agent = Agent()
            elif button_x <= pyxel.mouse_x <= button_x + button_with and button_y_together <= pyxel.mouse_y <= button_y_together + button_hight:
                self.current_scene = PLAY_SCENE

    def update_play_scene(self):
        if self.winner != None:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
            return

        x =  y  = OUT_SCOPE
        is_gui = False
        if self.is_agent == True:
            if self.player != self.agent.turn:
                print("agent turn")
                self.agent.set_random_xy(self.grid)
                x, y = self.agent.get_xy()
            else:
                is_gui = True
        else:
            is_gui = True

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and is_gui:
            if GRID_POS_X <= pyxel.mouse_x < GRID_POS_X + SCREEN_GRID_SIZE * 1 // 3:
                x = 0
            elif GRID_POS_X + SCREEN_GRID_SIZE // 3 < pyxel.mouse_x < GRID_POS_X + SCREEN_GRID_SIZE * 2 // 3:
                x = 1 
            elif GRID_POS_X + SCREEN_GRID_SIZE * 2 // 3 < pyxel.mouse_x < GRID_POS_X + SCREEN_GRID_SIZE:
                x = 2
            if GRID_POS_Y <= pyxel.mouse_y < GRID_POS_Y + SCREEN_GRID_SIZE * 1 // 3:
                y = 0
            elif GRID_POS_Y + SCREEN_GRID_SIZE // 3 < pyxel.mouse_y < GRID_POS_Y + SCREEN_GRID_SIZE * 2 // 3:
                y = 1
            elif GRID_POS_Y + SCREEN_GRID_SIZE * 2 // 3 < pyxel.mouse_y < GRID_POS_Y + SCREEN_GRID_SIZE:
                y = 2
                 
        #範囲外またはすでにOXがあったら追加しない
        if not (x == OUT_SCOPE or y == OUT_SCOPE) and self.grid.state[y][x] == None: 
            if self.player == PLAYER_O:
                self.grid.state[y][x] = O(x,y)
                self.player = PLAYER_X
            elif self.player == PLAYER_X:
                self.grid.state[y][x] = X(x, y)
                self.player = PLAYER_O
        
        # 縦横斜めでそろうと勝者が決まる
        patterns = [[[0, 0], [0, 1], [0, 2]], [[1, 0], [1, 1], [1, 2]], [[2, 0], [2, 1], [2, 2]], \
                    [[0, 0], [1, 0], [2, 0]], [[0, 1], [1, 1], [2, 1]], [[0, 2], [1, 2], [2, 2]], \
                    [[0, 0], [1, 1], [2, 2]], [[0, 2], [1, 1], [2, 0]]]

        def is_winner(shape):
            for pattern in patterns:
                count = 0
                for pos in pattern:
                    if isinstance(self.grid.state[pos[0]][pos[1]], shape):
                        count += 1
                if count == 3:
                    return True
            return False

        if is_winner(O):
            self.winner = PLAYER_O
        elif is_winner(X):
            self.winner = PLAYER_X

        # Noneの個数が0ならば置けるところがないのでゲーム終了
        if self.grid.count_grid == 0 and self.winner == None: #勝者が決まってなければ
            self.winner = PLAYER_NONE

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(SCREEN_WIDTH // 8, 30, "OX Game", pyxel.COLOR_YELLOW)

        button_color = pyxel.COLOR_NAVY
        button_line_color = pyxel.COLOR_BLACK
        pyxel.rect(SCREEN_WIDTH // 8 + self.pos_x_string - self.blank, self.pos_y_alone - self.blank,\
                     SCREEN_WIDTH // 3, self.font_size + self.blank * 2, button_color)
        pyxel.rect(SCREEN_WIDTH // 8 + self.pos_x_string - self.blank, self.pos_y_together - self.blank,\
                     SCREEN_WIDTH // 3, self.font_size + self.blank * 2, button_color)
        
        pyxel.text(SCREEN_WIDTH // 8 + self.pos_x_string, self.pos_y_alone, "Play Alone", pyxel.COLOR_PEACH)
        pyxel.text(SCREEN_WIDTH // 8 + self.pos_x_string, self.pos_y_together, "Play Together", pyxel.COLOR_PEACH)

    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)

        #Draw GRID
        grid_color = pyxel.COLOR_BLACK
        pyxel.rectb(GRID_POS_X, GRID_POS_Y, SCREEN_GRID_SIZE, SCREEN_GRID_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE, GRID_POS_X + SCREEN_GRID_SIZE - 1 , GRID_POS_Y + SCREEN_CELL_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE * 2, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE * 2, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)


        for row in self.grid.state:
            for shape in row:
                if shape != None:
                    shape.draw()

        if self.is_agent == False:       
            if self.player == PLAYER_O and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "O Player" , pyxel.COLOR_PEACH)
            elif self.player == PLAYER_X and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "X Player" , pyxel.COLOR_PEACH)
        else:
            if self.player != self.agent.turn and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Com Turn" , pyxel.COLOR_PEACH)
            elif self.player == self.agent.turn and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Your Turn" , pyxel.COLOR_PEACH)

        if self.is_agent == False:
            if self.winner == PLAYER_O:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "The Winner is O Player !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_X:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "The Winner is X Player !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_NONE:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Draw !!!" , pyxel.COLOR_YELLOW)
            else:
                pass
        else:
            if self.winner == self.agent.turn:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "You are the winner !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_NONE:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Draw !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == None:
                pass
            else:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "The Winner is Com !!!" , pyxel.COLOR_YELLOW)


class Grid:
    def init(self):
        self.state = [[None, None, None], [None, None, None], [None, None, None]]

    # Noneの残りの数
    def count_grid(self):
        n = 0 
        for row in self.state:
            n += row.count(None)
        return n


class Agent:
    def __init__(self):
        self.x = OUT_SCOPE
        self.y = OUT_SCOPE
        self.think_time = AGENT_THINK_TIME
        if random.randrange(2) == 0:
            self.turn = PLAYER_O
        else:
            self.turn = PLAYER_X
    
    def update(self):
        self.think_time -= 1

    def get_xy(self):
        return self.x, self.y

    def set_random_xy(self, grid):
        self.update()
        if self.think_time == 0:
            self.think_time = AGENT_THINK_TIME
            self.x = random.randrange(3)
            self.y = random.randrange(3)


App()