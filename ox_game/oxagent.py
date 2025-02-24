# oxagent.py
import random
from math import sqrt, log
from ttt_rules import check_winner
import ttt_rules

# Agent用定数
AGENT_THINK_TIME = 20

class BaseAgent:
    def __init__(self, turn=None):
        # turn が指定されなければランダムに決定
        if turn is None:
            turn = random.choice([ttt_rules.PLAYER_O, ttt_rules.PLAYER_X])
        self.turn = turn
        if self.turn == ttt_rules.PLAYER_O:
            self.agent_mark = 'O'
            self.human_mark = 'X'
        else:
            self.agent_mark = 'X'
            self.human_mark = 'O'
        self.reset()
    
    def reset(self):
        # 内部盤面は 3×3 の2次元リスト（初期状態は空白）
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.move = None
        self.think_time = AGENT_THINK_TIME

    def can_set(self):
        if self.think_time == 0:
            self.think_time = AGENT_THINK_TIME
            return True
        else:
            self.think_time -= 1
            return False

    def update_board(self, board):
        """GUI側で人間が入力した手 (x, y) を内部盤面に反映する。"""
        self.board = board

    def get_xy(self):
        """set_xy() で決定した手 (x, y) を返す。"""
        return self.move

# ────────────── ミニマックス法エージェント ──────────────
class MinimaxAgent(BaseAgent):
    def get_empty_cells(self, board):
        return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ' ']
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        if check_winner(board, self.agent_mark):
            return 10 - depth
        if check_winner(board, self.human_mark):
            return depth - 10
        if not self.get_empty_cells(board):
            return 0
        
        if is_maximizing:
            max_eval = -float("inf")
            for r, c in self.get_empty_cells(board):
                board[r][c] = self.agent_mark
                eval = self.minimax(board, depth + 1, False, alpha, beta)
                board[r][c] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for r, c in self.get_empty_cells(board):
                board[r][c] = self.human_mark
                eval = self.minimax(board, depth + 1, True, alpha, beta)
                board[r][c] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self):
        best_score = -float("inf")
        best_move = None
        board_copy = [row[:] for row in self.board]
        for r, c in self.get_empty_cells(board_copy):
            board_copy[r][c] = self.agent_mark
            move_score = self.minimax(board_copy, 0, False, -float("inf"), float("inf"))
            board_copy[r][c] = ' '
            if move_score > best_score:
                best_score = move_score
                # 内部盤面は board[y][x] 形式なので、(x, y) の順で返す
                best_moves = [(c, r)]  # 最良手リストをリセット
            elif move_score == best_score:
                best_moves.append((c, r))  # 同じ評価値の手を追加
            print(best_moves)
        return random.choice(best_moves) if best_moves else None

    def set_xy(self):
        if self.can_set():
            move = self.find_best_move()
            if move is not None:
                x, y = move
                self.board[y][x] = self.agent_mark
                self.move = move
            else:
                self.move = (None, None)
        else:
            self.move = (None, None)
            print("wait")

# ────────────── MCTS（モンテカルロ木探索）エージェント ──────────────
class MCTSNode:
    def __init__(self, board, parent, move, player):
        """
        board  : 3×3 の2次元リスト（状態）
        parent : 親ノード（rootの場合は None）
        move   : 親からこのノードへ遷移するために行われた手 (x, y)（rootは None）
        player : この状態で手番となるプレイヤー（PLAYER_O または PLAYER_X）
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.player = player
        self.visits = 0
        self.wins = 0
        self.children = []
        self.untried_moves = self.get_possible_moves(board)
    
    def get_possible_moves(self, board):
        moves = []
        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    moves.append((c, r))
        return moves

    def select_child(self):
        c_param = sqrt(2)
        best_child = None
        best_value = -float('inf')
        for child in self.children:
            value = (child.wins / child.visits) + c_param * sqrt(log(self.visits) / child.visits)
            if value > best_value:
                best_value = value
                best_child = child
        return best_child

    def add_child(self, move, board, next_player):
        child = MCTSNode([row[:] for row in board], parent=self, move=move, player=next_player)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

class MCTSAgent(BaseAgent):
    def __init__(self, turn=None, iterations=1000):
        self.iterations = iterations
        super().__init__(turn)
    
    def set_xy(self):
        root = MCTSNode(board=[row[:] for row in self.board], parent=None, move=None, player=self.turn)
        for _ in range(self.iterations):
            node = root
            state = [row[:] for row in self.board]
            # ① 選択: 完全に展開されているノードまで降下
            while node.untried_moves == [] and node.children:
                node = node.select_child()
                x, y = node.move
                mark = self.agent_mark if node.parent.player == self.turn else self.human_mark
                state[y][x] = mark
            # ② 拡張: 未展開の手があれば展開
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                x, y = move
                mark = self.agent_mark if node.player == self.turn else self.human_mark
                state[y][x] = mark
                next_player = ttt_rules.PLAYER_O if node.player == ttt_rules.PLAYER_X else ttt_rules.PLAYER_X
                node = node.add_child(move, state, next_player)
            # ③ シミュレーション: ランダムプレイアウト
            rollout_state = [row[:] for row in state]
            current_player = node.player
            while True:
                if check_winner(rollout_state, self.agent_mark):
                    outcome = 1
                    break
                if check_winner(rollout_state, self.human_mark):
                    outcome = 0
                    break
                possible_moves = [(c, r) for r in range(3) for c in range(3) if rollout_state[r][c] == ' ']
                if not possible_moves:
                    outcome = 0.5  # 引き分け
                    break
                move = random.choice(possible_moves)
                mark = self.agent_mark if current_player == self.turn else self.human_mark
                rollout_state[move[1]][move[0]] = mark
                current_player = ttt_rules.PLAYER_O if current_player == ttt_rules.PLAYER_X else ttt_rules.PLAYER_X
            # ④ 逆伝播: 結果を木全体に伝播（各層で結果を反転）
            result = outcome
            while node is not None:
                node.visits += 1
                if node.player == self.turn:
                    node.wins += result
                else:
                    node.wins += (1 - result)
                result = 1 - result
                node = node.parent
        if root.children:
            best_child = max(root.children, key=lambda c: c.visits)
            self.move = best_child.move
            x, y = self.move
            self.board[y][x] = self.agent_mark
        else:
            self.move = (None, None)