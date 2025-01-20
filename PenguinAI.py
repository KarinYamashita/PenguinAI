# from kogi_canvas import Canvas
import math
import random
import time

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


class PenguinAI(object):
    def face(self):
        return "🐧"

    def place(self, board, stone):
        """
        最も良い手を選択する（次のターンの相手の手を考慮し、コーナーを重視）
        """
        best_x, best_y = -1, -1
        best_score = float("-inf")

        opponent = 3 - stone  # 相手の石
        board_size = len(board)

        # コーナーの座標リスト
        corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]

        for y in range(board_size):
            for x in range(board_size):
                if not can_place_x_y(board, stone, x, y):
                    continue

                # 仮の盤面で石を置く
                simulated_board = copy(board)
                move_stone(simulated_board, stone, x, y)

                # 自分の石の数を計算
                my_black, my_white = count_stone(simulated_board)
                my_score = my_black if stone == BLACK else my_white

                # 次のターンで相手が取れる最大の石の数を計算
                opponent_best_score = float("-inf")
                for oy in range(board_size):
                    for ox in range(board_size):
                        if not can_place_x_y(simulated_board, opponent, ox, oy):
                            continue
                        opponent_simulated_board = copy(simulated_board)
                        move_stone(opponent_simulated_board, opponent, ox, oy)
                        opp_black, opp_white = count_stone(opponent_simulated_board)
                        opp_score = opp_black if opponent == BLACK else opp_white
                        opponent_best_score = max(opponent_best_score, opp_score)

                # スコアの評価: 自分のスコア - 次のターンで相手が得られるスコア
                final_score = my_score - opponent_best_score

                # コーナーなら優先度を大幅に上げる
                if (x, y) in corners:
                    final_score += 100

                # 最善手を更新
                if final_score > best_score:
                    best_score = final_score
                    best_x, best_y = x, y

        return best_x, best_y
    
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
