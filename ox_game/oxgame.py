import pyxel
import oxagent

SCREEN_WIDTH = 200 
SCREEN_HEIGHT = 150
SCREEN_GRID_SIZE = 90
SCREEN_CELL_SIZE = 30
GRID_POS_X = SCREEN_WIDTH // 2 - SCREEN_GRID_SIZE // 2
GRID_POS_Y = SCREEN_HEIGHT // 2 - SCREEN_GRID_SIZE // 2 + SCREEN_HEIGHT // 12
START_SCENE = "start"
PLAY_SCENE = "play"
PLAYER_O = 1
PLAYER_X = -1
PLAYER_NONE = 0
OUT_SCOPE = -1
GAME_OVER_DISPLAY_TIME = 60 * 2

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
        self.init_param()
        self.gui_param()
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)
    
    def init_param(self):
        self.current_scene = START_SCENE
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.current_player = PLAYER_O
        self.is_agent = False
        self.winner = None
        self.board = [None] * 9
    
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
                self.agent = oxagent.SimpleAgent()
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
        is_gui = True
        if self.is_agent == True:
            if self.current_player == self.agent.turn:
                self.agent.set_random_xy()
                x, y = self.agent.get_xy()
                is_gui = False

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
                 

        #範囲内かつOXがなければ追加できる
        if not (x == OUT_SCOPE or y == OUT_SCOPE) and self.board[y * 3 + x] == None: 
            if self.current_player == PLAYER_O:
                self.board[3 * y + x] = O(x,y)
                self.current_player = PLAYER_X
            elif self.current_player == PLAYER_X:
                self.board[3 * y + x] = X(x, y)
                self.current_player = PLAYER_O
            
            if self.is_agent and is_gui: #guiからのみboardに追加
                self.agent.set_gui(x, y)
        
        # 縦横斜めで3つそろうと勝者が決まる
        patterns = [[[0, 0], [0, 1], [0, 2]], [[1, 0], [1, 1], [1, 2]], [[2, 0], [2, 1], [2, 2]], \
                    [[0, 0], [1, 0], [2, 0]], [[0, 1], [1, 1], [2, 1]], [[0, 2], [1, 2], [2, 2]], \
                    [[0, 0], [1, 1], [2, 2]], [[0, 2], [1, 1], [2, 0]]]

        def is_winner(shape):
            for pattern in patterns:
                count = 0
                for pos in pattern:
                    if isinstance(self.board[3 * pos[1] + pos[0]], shape):
                        count += 1
                if count == 3:
                    return True
            return False

        # Noneの個数が0ならば置けるところがないのでゲーム終了
        if is_winner(O):
            self.winner = PLAYER_O
        elif is_winner(X):
            self.winner = PLAYER_X

        # Noneの個数が0ならば置けるところがないのでゲーム終了
        if self.board.count(None) == 0 and self.winner == None: #勝者が決まってなければ
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


        for shape in self.board:
            if shape != None:
                shape.draw()

        if self.is_agent == False:       
            if self.current_player == PLAYER_O and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "O Player" , pyxel.COLOR_PEACH)
            elif self.current_player == PLAYER_X and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "X Player" , pyxel.COLOR_PEACH)
        else:
            if self.current_player == self.agent.turn and self.winner == None:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Com Turn" , pyxel.COLOR_PEACH)
            elif self.current_player != self.agent.turn and self.winner == None:
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
                            "The Winner is Com !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_NONE:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "Draw !!!" , pyxel.COLOR_YELLOW)
            elif self.winner == None:
                pass
            else:
                pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                            "You are the winner !!!" , pyxel.COLOR_YELLOW)



App()