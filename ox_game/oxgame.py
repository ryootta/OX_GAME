import pyxel

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
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)
    
    def init_param(self):
        self.current_scene = START_SCENE
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.player = PLAYER_O
        self.winner = None
        self.grid = [[None, None, None], [None, None, None], [None, None, None]]

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
            self.current_scene = PLAY_SCENE  
    
    def update_play_scene(self):
        print(self.winner)
        if self.winner != None:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
            return

        x = OUT_SCOPE
        y = OUT_SCOPE
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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
        if not (x == OUT_SCOPE or y == OUT_SCOPE) and self.grid[y][x] == None: 
            if self.player == PLAYER_O:
                self.grid[y][x] = O(x,y)
                self.player = PLAYER_X
            elif self.player == PLAYER_X:
                self.grid[y][x] = X(x, y)
                self.player = PLAYER_O
        
        # 縦横斜めでそろうと勝者が決まる
        patterns = [[[0, 0], [0, 1], [0, 2]], [[1, 0], [1, 1], [1, 2]], [[2, 0], [2, 1], [2, 2]], \
                    [[0, 0], [1, 0], [2, 0]], [[0, 1], [1, 1], [2, 1]], [[0, 2], [1, 2], [2, 2]], \
                    [[0, 0], [1, 1], [2, 2]], [[0, 2], [1, 1], [2, 0]]]

        def is_winner(shape):
            for pattern in patterns:
                count = 0
                for pos in pattern:
                    if isinstance(self.grid[pos[0]][pos[1]], shape):
                        count += 1
                if count == 3:
                    return True
            return False

        if is_winner(O):
            self.winner = PLAYER_O
        elif is_winner(X):
            self.winner = PLAYER_X

        # Noneの個数が0ならば置けるところがないのでゲーム終了
        n = 0 
        for row in self.grid:
            n += row.count(None)
        if n == 0 and self.winner == None: #勝者が決まってなければ
            self.winner = PLAYER_NONE

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(SCREEN_WIDTH // 8, 30, "OX Game", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 8, 60, "Click to Start !", pyxel.COLOR_YELLOW)
        
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)

        #Draw GRID
        grid_color = pyxel.COLOR_BLACK
        pyxel.rectb(GRID_POS_X, GRID_POS_Y, SCREEN_GRID_SIZE, SCREEN_GRID_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE, GRID_POS_X + SCREEN_GRID_SIZE - 1 , GRID_POS_Y + SCREEN_CELL_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE * 2, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE * 2, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)


        for row in self.grid:
            for shape in row:
                if shape != None:
                    shape.draw()
        
        if self.player == PLAYER_O and self.winner == None:
            pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                        "O Player" , pyxel.COLOR_PEACH)
        elif self.player == PLAYER_X and self.winner == None:
            pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                        "X Player" , pyxel.COLOR_PEACH)


        if self.winner == PLAYER_O:
            pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                        "Winner is O Player !!!" , pyxel.COLOR_YELLOW)
        elif self.winner == PLAYER_X:
            pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                        "Winner is X Player !!!" , pyxel.COLOR_YELLOW)
        elif self.winner == PLAYER_NONE:
            pyxel.text(GRID_POS_X , SCREEN_HEIGHT // 8, 
                        "Draw !!!" , pyxel.COLOR_YELLOW)


App()