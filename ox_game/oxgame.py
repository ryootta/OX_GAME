import pyxel
import random
import oxagent
from ttt_rules import check_winner, convert_app_board, convert_app_xy
import ttt_rules
from device_checker import DeviceChecker

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

# ゲームモード識別子
GAME_MODE_1 = "game1"
GAME_MODE_2 = "game2"

# プレイヤー識別子
OUT_SCOPE = -1
AGENT_CHANGE_RATE = 0.6
NO_HINT_RATE = 0.8

GAME_OVER_DISPLAY_TIME = 150

# スタート画面のGUI用定数
BLANK = 5
MIN_BLANK = 3
FONT_SIZE = 5
START_BUTTON_X = SCREEN_WIDTH // 8 + 20 - BLANK
ALONE_START_BUTTON_Y = SCREEN_HEIGHT * 6 // 10 - BLANK
TOGETHER_START_BUTTON_Y = ALONE_START_BUTTON_Y + FONT_SIZE + BLANK * 3 
START_BUTTON_WIDTH = SCREEN_WIDTH // 3
START_BUTTON_HEIGHT = FONT_SIZE + BLANK * 2

TITLE_Y = SCREEN_HEIGHT * 15 // 100
CHANGE_BUTTON_X = SCREEN_WIDTH * 5 // 8
CHANGE_BUTTON_Y = SCREEN_HEIGHT * 1 // 10
CHANGE_BUTTON_Y = SCREEN_HEIGHT * 15 // 100
CHANGE_BUTTON_WIDTH = FONT_SIZE * 10 + MIN_BLANK * 2
CHANGE_BUTTON_HEIGHT = FONT_SIZE * 2 + MIN_BLANK * 3

# 盤面上のマーク描画用クラス
class Shape():
    def __init__(self, x, y, game_mode, win_rate):
        size = 16
        self.x = SCREEN_GRID_SIZE * x // 3 + GRID_POS_X + size // 2 - 1 
        self.y = SCREEN_GRID_SIZE * y // 3 + GRID_POS_Y + size // 2 - 1
        self.life = 7
        self.game_mode = game_mode
        self.rate = win_rate

    def update(self):
        # ゲームモードが２の場合のみ、ライフを更新
        self.life -= 1 if self.game_mode == GAME_MODE_2 else 0
    
    def is_dead(self):
        if self.life == 0:
            return True 
        else:
            return False

class O(Shape):
    def __init__(self, x, y, game_mode, win_rate):
        super().__init__(x, y, game_mode, win_rate)
    def draw(self):
        if self.life == 2:
            if self.rate > NO_HINT_RATE:
                pyxel.blt(self.x, self.y, 0, 0, 16, 16, 16, pyxel.COLOR_WHITE)
            else:
                pyxel.blt(self.x, self.y, 0, 0, 16*2, 16, 16, pyxel.COLOR_WHITE)
        else:
            pyxel.blt(self.x, self.y, 0, 0, 16, 16, 16, pyxel.COLOR_WHITE)

class X(Shape):
    def __init__(self, x, y, game_mode, win_rate):
        super().__init__(x, y, game_mode, win_rate)
    def draw(self):
        if self.life == 2:
            if self.rate > NO_HINT_RATE:
                pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, pyxel.COLOR_WHITE)
            else:
                pyxel.blt(self.x, self.y, 0, 16, 16*2, 16, 16, pyxel.COLOR_WHITE)
        else:
            pyxel.blt(self.x, self.y, 0, 16, 16, 16, 16, pyxel.COLOR_WHITE)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Tic Tac Toe")

        # PC(非タップ端末)からの実行時のみマウスカーソルを表示する
        deviceChecker = DeviceChecker()
        pyxel.mouse(deviceChecker.is_pc())

        #pyxel.mouse(True)
        # parameterの初期化
        self.init_param()
        self.win_count = 0
        self.game_count = 0
        self.rate = 0.5
        self.game_mode = GAME_MODE_1 #game1とgame2の差分のパラメータ

        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)
    
    def init_param(self):
        self.current_scene = START_SCENE
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        self.current_player = ttt_rules.PLAYER_O  # 初期手番は PLAYER_O 固定
        self.is_agent = False
        self.winner = None
        self.is_rate_calc = False
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
            # ゲームのモードの変更
            if (CHANGE_BUTTON_X <= pyxel.mouse_x <= CHANGE_BUTTON_X + CHANGE_BUTTON_WIDTH and
                CHANGE_BUTTON_Y <= pyxel.mouse_y <= CHANGE_BUTTON_Y + CHANGE_BUTTON_HEIGHT):
                self.game_mode = GAME_MODE_2 if self.game_mode == GAME_MODE_1 else GAME_MODE_1

            # ゲームスタート
            if (START_BUTTON_X <= pyxel.mouse_x <= START_BUTTON_X + START_BUTTON_WIDTH and 
                ALONE_START_BUTTON_Y <= pyxel.mouse_y <= ALONE_START_BUTTON_Y + START_BUTTON_HEIGHT):
                self.current_scene = PLAY_SCENE
                self.is_agent = True
                # エージェントの担当記号をランダムに決定
                agent_turn = random.choice([ttt_rules.PLAYER_O, ttt_rules.PLAYER_X])
                if self.rate > AGENT_CHANGE_RATE:
                    self.agent = oxagent.MinimaxAgent(agent_turn)
                else:
                    self.agent = oxagent.MCTSAgent(agent_turn)
            elif (START_BUTTON_X <= pyxel.mouse_x <= START_BUTTON_X + START_BUTTON_WIDTH and 
                  TOGETHER_START_BUTTON_Y <= pyxel.mouse_y <= TOGETHER_START_BUTTON_Y + START_BUTTON_HEIGHT):
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
                x, y = convert_app_xy(x, y)
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
            if self.current_player == ttt_rules.PLAYER_O:
                self.board[y * 3 + x] = O(x, y, self.game_mode, self.rate)
                self.current_player = ttt_rules.PLAYER_X
            else:
                self.board[y * 3 + x] = X(x, y, self.game_mode, self.rate)
                self.current_player = ttt_rules.PLAYER_O

            """ 盤面に置いてあるshapeの状態を変更 """
            for i, shape in enumerate(self.board):
                if shape != None:
                    shape.update()
                    self.board[i] = None if shape.is_dead() else shape
        
        # 盤面を2次元リストに変換
        converted_board = convert_app_board(self.board, O, X)

        # GUI側で人間が入力した手 (x, y) をAgentが持つ盤面に反映
        if self.is_agent:
            self.agent.update_board(converted_board)

        # 勝利判定
        if check_winner(converted_board, "O"):
            self.winner = ttt_rules.PLAYER_O
        elif check_winner(converted_board, "X"):
            self.winner = ttt_rules.PLAYER_X
        elif self.board.count(None) == 0:
            self.winner = ttt_rules.PLAYER_NONE

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        change_game_button_color = pyxel.COLOR_NAVY
        change_game_string_color = pyxel.COLOR_PEACH
        rule_color = pyxel.COLOR_WHITE
        title_color = pyxel.COLOR_PEACH
        pyxel.text(START_BUTTON_X , SCREEN_HEIGHT * 3 // 10, "Game Rules", rule_color)
        pyxel.text(START_BUTTON_X + FONT_SIZE, SCREEN_HEIGHT * 3 // 10 + FONT_SIZE + MIN_BLANK, 
                   "1. Align three of your marks.", rule_color)
        if (self.game_mode == GAME_MODE_1):
            pyxel.text(SCREEN_WIDTH // 8, TITLE_Y, "Tic Tac Toe", title_color)
            pyxel.rect(CHANGE_BUTTON_X, CHANGE_BUTTON_Y,
                    CHANGE_BUTTON_WIDTH , CHANGE_BUTTON_HEIGHT, change_game_button_color)
            pyxel.text(CHANGE_BUTTON_X + MIN_BLANK, CHANGE_BUTTON_Y + MIN_BLANK, "Tic Tac Toe 2", change_game_string_color)
            pyxel.text(CHANGE_BUTTON_X + MIN_BLANK, CHANGE_BUTTON_Y + FONT_SIZE + MIN_BLANK * 2, "Click Here!!", change_game_string_color)
        else:
            pyxel.text(SCREEN_WIDTH // 8, TITLE_Y, "Tic Tac Toe 2", title_color)
            pyxel.rect(CHANGE_BUTTON_X, CHANGE_BUTTON_Y,
                    CHANGE_BUTTON_WIDTH , CHANGE_BUTTON_HEIGHT, change_game_button_color)
            pyxel.text(CHANGE_BUTTON_X + MIN_BLANK, CHANGE_BUTTON_Y + MIN_BLANK, "Tic Tac Toe", change_game_string_color)
            pyxel.text(CHANGE_BUTTON_X + MIN_BLANK, CHANGE_BUTTON_Y + FONT_SIZE + MIN_BLANK * 2, "Click Here!!", change_game_string_color)

            pyxel.text(START_BUTTON_X + FONT_SIZE, SCREEN_HEIGHT * 3 // 10 + FONT_SIZE * 2 + MIN_BLANK * 2, 
                       "2. Each mark displayed on the screen", rule_color)
            pyxel.text(START_BUTTON_X + FONT_SIZE, SCREEN_HEIGHT * 3 // 10 + FONT_SIZE * 3 + MIN_BLANK * 3, 
                       "   is limited to three.", rule_color)

        button_color = pyxel.COLOR_NAVY
        pyxel.rect(START_BUTTON_X, ALONE_START_BUTTON_Y,
                   START_BUTTON_WIDTH, START_BUTTON_HEIGHT, button_color)
        pyxel.rect(START_BUTTON_X, TOGETHER_START_BUTTON_Y,
                   START_BUTTON_WIDTH, START_BUTTON_HEIGHT, button_color)
        pyxel.text(START_BUTTON_X + BLANK, ALONE_START_BUTTON_Y + BLANK, "Play Alone", pyxel.COLOR_PEACH)
        pyxel.text(START_BUTTON_X + BLANK, TOGETHER_START_BUTTON_Y + BLANK, "Play Together", pyxel.COLOR_PEACH)
    
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        grid_color = pyxel.COLOR_BLACK
        # 勝率バー
        if self.is_agent:
            min_blank = 2
            pyxel.rect(GRID_POS_X,  SCREEN_HEIGHT // 8 + BLANK + FONT_SIZE, SCREEN_GRID_SIZE, FONT_SIZE + min_blank * 2, pyxel.COLOR_GREEN)
            pyxel.rect(GRID_POS_X,  SCREEN_HEIGHT // 8 + BLANK + FONT_SIZE, SCREEN_GRID_SIZE * (1 - self.rate), FONT_SIZE + min_blank * 2, pyxel.COLOR_ORANGE)
            pyxel.text(GRID_POS_X + MIN_BLANK, SCREEN_HEIGHT // 8 + BLANK + min_blank + FONT_SIZE, "Com", pyxel.COLOR_WHITE)
            pyxel.text(GRID_POS_X + SCREEN_GRID_SIZE - FONT_SIZE * 3, SCREEN_HEIGHT // 8 + BLANK + min_blank + FONT_SIZE, "You", pyxel.COLOR_WHITE)

        # 盤面
        pyxel.rectb(GRID_POS_X, GRID_POS_Y, SCREEN_GRID_SIZE, SCREEN_GRID_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE, grid_color)
        pyxel.line(GRID_POS_X, GRID_POS_Y + SCREEN_CELL_SIZE * 2, GRID_POS_X + SCREEN_GRID_SIZE - 1, GRID_POS_Y + SCREEN_CELL_SIZE * 2, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)
        pyxel.line(GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y, GRID_POS_X + SCREEN_CELL_SIZE * 2, GRID_POS_Y + SCREEN_GRID_SIZE - 1, grid_color)

        for shape in self.board:
            if shape is not None:
                shape.draw()

        # 状態表示
        if self.is_agent:       
            if self.current_player == self.agent.turn and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Com Turn", pyxel.COLOR_PEACH)
            elif self.current_player != self.agent.turn and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Your Turn", pyxel.COLOR_PEACH)
        else:
            if self.current_player == ttt_rules.PLAYER_O and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "O Player", pyxel.COLOR_PEACH)
            elif self.current_player == ttt_rules.PLAYER_X and self.winner is None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "X Player", pyxel.COLOR_PEACH)

        if self.is_agent:
            if self.winner == self.agent.turn:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is Com !!!", pyxel.COLOR_YELLOW)
                if not self.is_rate_calc:
                    self.is_rate_calc = True
                    self.game_count += 1
                    self.rate = self.win_count / self.game_count
                if self.rate <= AGENT_CHANGE_RATE and isinstance(self.agent, oxagent.MinimaxAgent):
                    pyxel.text(GRID_POS_X - FONT_SIZE * 9, SCREEN_HEIGHT // 8 + BLANK + min_blank + FONT_SIZE, "Level down", pyxel.COLOR_YELLOW)
                elif self.rate > NO_HINT_RATE and self.game_mode == GAME_MODE_2:
                    pyxel.text(GRID_POS_X - FONT_SIZE * 9, GRID_POS_Y, "Hint on", pyxel.COLOR_YELLOW)
            elif self.winner == ttt_rules.PLAYER_NONE:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Draw !!!", pyxel.COLOR_YELLOW)
            elif self.winner is not None:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "You are the winner !!!", pyxel.COLOR_YELLOW)
                if not self.is_rate_calc:
                    self.is_rate_calc = True
                    self.win_count += 1
                    self.game_count += 1
                    self.rate = self.win_count / self.game_count
                if self.rate > AGENT_CHANGE_RATE and isinstance(self.agent, oxagent.MCTSAgent):
                    pyxel.text(GRID_POS_X - FONT_SIZE * 9, SCREEN_HEIGHT // 8 + BLANK + min_blank + FONT_SIZE, "Level up", pyxel.COLOR_YELLOW)
                elif self.rate > NO_HINT_RATE and self.game_mode == GAME_MODE_2:
                    pyxel.text(GRID_POS_X - FONT_SIZE * 9, GRID_POS_Y, "Hint off", pyxel.COLOR_YELLOW)
        else:
            if self.winner == ttt_rules.PLAYER_O:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is O Player !!!", pyxel.COLOR_YELLOW)
            elif self.winner == ttt_rules.PLAYER_X:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "The Winner is X Player !!!", pyxel.COLOR_YELLOW)
            elif self.winner == ttt_rules.PLAYER_NONE:
                pyxel.text(GRID_POS_X, SCREEN_HEIGHT // 8, "Draw !!!", pyxel.COLOR_YELLOW)

App()
