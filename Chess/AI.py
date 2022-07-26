from random import shuffle

PIECE_POINTS = {"Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
next_move = None


def find_best_move(gs):
    global next_move
    shuffle(gs.current_valid_moves)
    nega_max_move_finder(gs, DEPTH, 1 if gs.white_to_move else -1)
    return next_move


def nega_max_move_finder(gs, depth, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)
    max_score = -CHECKMATE
    for move in gs.current_valid_moves:
        gs.do_move(move)
        score = -nega_max_move_finder(gs, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def score_board(gs):
    # Positive score is good for white, negative score is good for black
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    if gs.stalemate:
        return STALEMATE
    score = 0
    board = gs.board
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if board[i][j][1] == "K":
                continue
            elif board[i][j][0] == "w":
                score += PIECE_POINTS[board[i][j][1]]
            elif board[i][j][0] == "b":
                score -= PIECE_POINTS[board[i][j][1]]
    return score

