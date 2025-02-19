import pyxel
import random
import oxagent
from ttt_rules import check_winner, convert_app_board

# 画面・グリッド関連の定数
SCREEN_WIDTH = 200 
SCREEN_HEIGHT = 150
SCREEN_GRID_SIZE = 90
SCREEN_CELL_SIZE = 30
GRID_POS_X = SCREEN_WIDTH // 2 - SCREEN_GRID_SIZE // 2
GRID_POS_Y = SCREEN_HEIGHT // 2 - SCREEN_GRID_SIZE // 2 + SCREEN_HEIGHT // 12

# シーン識別子
START_SCENE = "start"
PLAY_SCENE = "play"

# プレイヤー識別子
PLAYER_O = 1
PLAYER_X = -1
PLAYER_NONE = 0
OUT_SCOPE = -1

GAME_OVER_DISPLAY_TIME = 60 * 2

# GUI用定数
POS_X_STRING = 20
POS_Y_ALONE = 60
POS_Y_TOGETHER = 80
BLANK = 5
FONT_SIZE = 5

# 盤面上のマーク描画用クラス
class Shape():
    def __init__(self, x, y):
        size = 16
        self.x = SCREEN_GRID_SIZE * x // 3 + GRID_POS_X + size // 2 - 1 
        self.y = SCREEN_GRID_SIZE * y // 3 + GRID_POS_Y + size // 2 - 1

class O(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 16, 16, 16, pyxel.COLOR_WHITE)

class X(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, pyxel.COLOR_WHITE)

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
        self.current_player = PLAYER_O  # 初期手番は PLAYER_O 固定
        self.is_agent = False
        self.winner = None
        self.board = [None] * 9  # 盤面は 9 要素のリスト（各セルは None またはマークのインスタンス）
        self.agent = None

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
            button_x = SCREEN_WIDTH // 8 + POS_X_STRING - BLANK
            button_y_alone = POS_Y_ALONE - BLANK
            button_y_together = POS_Y_TOGETHER - BLANK
            button_width = SCREEN_WIDTH // 3
            button_height = FONT_SIZE + BLANK * 2
            if (button_x <= pyxel.mouse_x <= button_x + button_width and 
                button_y_alone <= pyxel.mouse_y <= button_y_alone + button_height):
                self.current_scene = PLAY_SCENE
                self.is_agent = True
                # エージェントの担当記号をランダムに決定
                agent_turn = random.choice([PLAYER_O, PLAYER_X])
                self.agent = oxagent.MinimaxAgent(agent_turn)
            elif (button_x <= pyxel.mouse_x <= button_x + button_width and 
                  button_y_together <= pyxel.mouse_y <= button_y_together + button_height):
                self.current_scene = PLAY_SCENE

    def update_play_scene(self):
        if self.winner is not None:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
            return

        x = y = OUT_SCOPE
        is_gui = True
        if self.is_agent and self.agent is not None:
            # エージェントの手番の場合、エージェントから最適手を取得
            if self.current_player == self.agent.turn:
                self.agent.set_xy()
                x, y = self.agent.get_xy()
                is_gui = False
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and is_gui:
            if GRID_POS_X <= pyxel.mouse_x < GRID_POS_X + SCREEN_GRID_SIZE // 3:
                x = 0
            elif GRID_POS_X + SCREEN_GRID_SIZE // 3 <= pyxel.mouse_x < GRID_POS_X + 2 * SCREEN_GRID_SIZE // 3:
                x = 1 
            elif GRID_POS_X + 2 * SCREEN_GRID_SIZE // 3 <= pyxel.mouse_x < GRID_POS_X + SCREEN_GRID_SIZE:
                x = 2
            if GRID_POS_Y <= pyxel.mouse_y < GRID_POS_Y + SCREEN_GRID_SIZE // 3:
                y = 0
            elif GRID_POS_Y + SCREEN_GRID_SIZE // 3 <= pyxel.mouse_y < GRID_POS_Y + 2 * SCREEN_GRID_SIZE // 3:
                y = 1
            elif GRID_POS_Y + 2 * SCREEN_GRID_SIZE // 3 <= pyxel.mouse_y < GRID_POS_Y + SCREEN_GRID_SIZE:
                y = 2

        if x != OUT_SCOPE and y != OUT_SCOPE and self.board[y * 3 + x] is None:
            if self.current_player == PLAYER_O:
                self.board[3 * y + x] = O(x, y)
                self.current_player = PLAYER_X
            elif self.current_player == PLAYER_X:
                self.board[3 * y + x] = X(x, y)
                self.current_player = PLAYER_O
            if self.is_agent and is_gui and self.agent is not None:
                self.agent.set_gui(x, y)
        
        # 盤面（flatなリスト）を2次元リストに変換して勝利判定
        converted_board = convert_app_board(self.board, O, X)
        if check_winner(converted_board, "O"):
            self.winner = PLAYER_O
        elif check_winner(converted_board, "X"):
            self.winner = PLAYER_X
        elif self.board.count(None) == 0:
            self.winner = PLAYER_NONE

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(SCREEN_WIDTH // 8, 30, "OX Game", pyxel.COLOR_YELLOW)
        button_color = pyxel.COLOR_NAVY
        pyxel.rect(SCREEN_WIDTH // 8 + POS_X_STRING - BLANK, POS_Y_ALONE - BLANK,
                     SCREEN_WIDTH // 3, FONT_SIZE + BLANK * 2, button_color)
        pyxel.rect(SCREEN_WIDTH // 8 + POS_X_STRING - BLANK, POS_Y_TOGETHER - BLANK,
                     SCREEN_WIDTH // 3, FONT_SIZE + BLANK * 2, button_color)
        pyxel.text(SCREEN_WIDTH // 8 + POS_X_STRING, POS_Y_ALONE, "Play Alone", pyxel.COLOR_PEACH)
        pyxel.text(SCREEN_WIDTH // 8 + POS_X_STRING, POS_Y_TOGETHER, "Play Together", pyxel.COLOR_PEACH)
    
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        grid_color = pyxel.COLOR_BLACK
        pyxel.rectb(GRID_POS_X, GRID_POS_Y, SCREEN_GRID_SIZE, SCREEN_GRID_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE * 2, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE * 2, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)

        for shape in self.board:
            if shape is not None:
                shape.draw()

        # 状態表示
        if not self.is_agent:       
            if self.current_player == PLAYER_O and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "O Player", pyxel.COLOR_PEACH)
            elif self.current_player == PLAYER_X and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "X Player", pyxel.COLOR_PEACH)
        else:
            if self.agent is not None:
                if self.current_player == self.agent.turn and self.winner is None:
                    pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Com Turn", pyxel.COLOR_PEACH)
                elif self.current_player != self.agent.turn and self.winner is None:
                    pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Your Turn", pyxel.COLOR_PEACH)

        if not self.is_agent:
            if self.winner == PLAYER_O:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is O Player !!!", pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_X:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is X Player !!!", pyxel.COLOR_YELLOW)
            elif self.winner == PLAYER_NONE:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Draw !!!", pyxel.COLOR_YELLOW)
        else:
            if self.agent is not None:
                if self.winner == self.agent.turn:
                    pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is Com !!!", pyxel.COLOR_YELLOW)
                elif self.winner == PLAYER_NONE:
                    pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Draw !!!", pyxel.COLOR_YELLOW)
                elif self.winner is not None:
                    pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "You are the winner !!!", pyxel.COLOR_YELLOW)

App()
