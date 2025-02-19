# ttt_rules.py

def check_winner(board, player):
    """
    3×3の2次元リスト board に対して、player（"O" または "X"）が勝利しているか判定する。
    """
    # 横方向
    for row in board:
        if all(cell == player for cell in row):
            return True
    # 縦方向
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # 斜め方向
    if all(board[i][i] == player for i in range(3)) or all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def convert_app_board(app_board, shape_O, shape_X):
    """
    Appモジュールで管理している盤面（長さ9のリスト）を、
    3×3の2次元リストに変換する関数。
    
    各セルには以下を返す：
      - 該当セルが shape_O のインスタンスなら "O"
      - 該当セルが shape_X のインスタンスなら "X"
      - None の場合は " "（空白）
    """
    board_2d = []
    for row in range(3):
        current = []
        for col in range(3):
            cell = app_board[row * 3 + col]
            if cell is None:
                current.append(" ")
            elif isinstance(cell, shape_O):
                current.append("O")
            elif isinstance(cell, shape_X):
                current.append("X")
            else:
                current.append(" ")
        board_2d.append(current)
    return board_2d
