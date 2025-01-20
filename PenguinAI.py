# from kogi_canvas import Canvas
import math
import random
import time
import copy

BLACK=1
WHITE=2

board = [
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,1,2,0,0],
        [0,0,2,1,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
]

def can_place_x_y(board, stone, x, y):
    """
    石を置けるかどうかを調べる関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return: 置けるなら True, 置けないなら False
    """
    if board[y][x] != 0:
        return False  # 既に石がある場合は置けない

    opponent = 3 - stone  # 相手の石 (1なら2、2なら1)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True  # 石を置ける条件を満たす

    return False

def can_place(board, stone):
    """
    石を置ける場所を調べる関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def random_place(board, stone):
    """
    石をランダムに置く関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    while True:
        x = random.randint(0, len(board[0]) - 1)
        y = random.randint(0, len(board) - 1)
        if can_place_x_y(board, stone, x, y):
            return x, y

def copy(board):
    """
    盤面をコピーする関数。
    board: 2次元配列のオセロボード
    """
    return [row[:] for row in board]


def move_stone(board, stone, x, y):
    """
    石を置き、ひっくり返す関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return:
    """
    moves = [copy(board)]*3
    if not can_place_x_y(board, stone, x, y):
        return moves  # 置けない場合は何もしない

    board[y][x] = stone  # 石を置く
    moves.append(copy(board))
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    flipped_count = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            for flip_x, flip_y in stones_to_flip:
                board[flip_y][flip_x] = stone
                moves.append(copy(board))
                flipped_count += 1

    return moves

def count_stone(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white

class PenguinAI:
    def face(self):
        return "🐧"

    def alpha_beta_score(self, state, stone, alpha, beta, depth):
        """
        Alpha-Beta法でスコアを計算
        """
        if depth == 0 or not can_place(state, stone):
            # 深さが0、または石を置けない場合は盤面スコアを返す
            return self.evaluate_state(state, stone)

        legal_actions = self.get_legal_actions(state, stone)
        for action in legal_actions:
            next_state = copy.deepcopy(state)
            move_stone(next_state, stone, action[0], action[1])  # 状態を進める
            score = -self.alpha_beta_score(next_state, 3 - stone, -beta, -alpha, depth - 1)
            if score > alpha:
                alpha = score
            if alpha >= beta:
                return alpha
        return alpha

    def alpha_beta_action(self, state, stone, depth):
        """
        Alpha-Beta法で最善手を決定
        """
        best_action = None
        alpha = -math.inf

        legal_actions = self.get_legal_actions(state, stone)
        for action in legal_actions:
            next_state = copy.deepcopy(state)
            move_stone(next_state, stone, action[0], action[1])  # 状態を進める
            score = -self.alpha_beta_score(next_state, 3 - stone, -math.inf, -alpha, depth - 1)
            if score > alpha:
                alpha = score
                best_action = action
        return best_action if best_action else None  # Noneを返す

    def get_legal_actions(self, state, stone):
        """
        石を置ける全ての合法手を取得
        """
        legal_actions = []
        for y in range(len(state)):
            for x in range(len(state[0])):
                if can_place_x_y(state, stone, x, y):
                    legal_actions.append((x, y))
        return legal_actions

    def evaluate_state(self, state, stone):
        """
        状態の評価関数: 盤面のスコアを計算
        """
        black, white = count_stone(state)
        return black - white if stone == BLACK else white - black

    def place(self, board, stone):
        """
        Alpha-Beta法で最善手を選択
        """
        action = self.alpha_beta_action(board, stone, depth=4)  # 深さは4で探索
        return action if action else (-1, -1)  # 最善手がない場合に備えた保険
    
def draw_board(canvas, board):
    ctx = canvas.getContext("2d")
    grid = width // len(board)
    for y, line in enumerate(board):
        for x, stone in enumerate(line):
            cx = x * grid + grid // 2
            cy = y * grid + grid // 2
            if stone != 0:
                ctx.beginPath()
                ctx.arc(cx, cy, grid//2, 0, 2 * math.pi) # 円の描画
                ctx.fillStyle = "black" if stone == 1 else "white"
                ctx.fill()

width=300

def draw_board_moves(canvas, moves):
    for board in moves:
        draw_board(canvas, board)
    
def run_othello(blackai=None, whiteai=None, board=None):
    if board is None:
        board = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,1,2,0,0],
            [0,0,2,1,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
        ]
    if blackai is None:
        blackai = PenguinAI()

    if whiteai is None:
        whiteai = PenguinAI()
        print(f'{whiteai.face()}が相手するよ！覚悟しな！')

    black_time = 0
    white_time = 0
    moved = True
    while moved and can_place(board, BLACK) and can_place(board, WHITE):
        moved = False
        if can_place(board, BLACK):
            start = time.time()
            x, y = blackai.place(copy(board), BLACK)
            black_time += time.time() - start
            if not can_place_x_y(board, BLACK, x, y):
                print(f'{blackai.face()}は、置けないところに置こうとしました', (x, y))
                print('反則負けです')
                return
            move_stone(board, BLACK, x, y)
            black, white = count_stone(board)
            print(f'{blackai.face()}は{(x, y)}におきました。黒: {black}, 白: {white}')
            moved = True
        else:
            print(f'{blackai.face()}は、どこにも置けないのでスキップします')

        if can_place(board, WHITE):
            start = time.time()
            x, y = whiteai.place(copy(board), WHITE)
            white_time += time.time() - start
            if not can_place_x_y(board, WHITE, x, y):
                print(f'{whiteai.face()}は、置けないところに置こうとしました', (x, y))
                print('反則負けです')
                return
            move_stone(board, WHITE, x, y)
            black, white = count_stone(board)
            print(f'{whiteai.face()}は{(x, y)}におきました。黒: {black}, 白: {white}')
            moved = True
        else:
            print(f'{whiteai.face()}は、どこにも置けないのでスキップします')

    black, white = count_stone(board)
    print(f'最終結果: 黒: {black}, 白: {white}', end=' ')
    if black > white:
        print(f'黒{blackai.face()}の勝ち')
    elif black < white:
        print(f'白{whiteai.face()}の勝ち')
    else:
        print('引き分け')
    print(f'思考時間: 黒: {black_time:.5f}秒, 白: {white_time:.5f}秒')
