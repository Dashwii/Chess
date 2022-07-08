class Move:
    def __init__(self, start_sq, end_sq, board):
        self.start_sq = start_sq
        self.end_sq = end_sq
        self.board = board
        self.piece_moved = board[start_sq[0]][start_sq[1]]
        self.piece_captured = board[end_sq[0]][end_sq[1]]
        self.id = str(self.start_sq[0] * 1000 + self.start_sq[1] * 100 + self.end_sq[0] * 10 + self.end_sq[1])


    def __eq__(self, other):
        return self.id == other.id


class EnPassant(Move):
    def __init__(self, start_sq, end_sq, board, en_passant):
        super().__init__(start_sq, end_sq, board)
        self.en_passant = en_passant


class Castle(Move):
    def __init__(self, start_sq, end_sq, board, castle):
        super().__init__(start_sq, end_sq, board)
        self.castle = castle


def return_piece_moves(piece, occupied_square, board, move_log, castle_rights):
    turn = piece[0]
    piece_type = piece[1]

    if piece_type == "P":
        return get_pawn_moves(turn, occupied_square, board, move_log)
    elif piece_type == "R":
        return get_rook_moves(turn, occupied_square, board)
    elif piece_type == "B":
        return get_bishop_moves(turn, occupied_square, board)
    elif piece_type == "N":
        return get_knight_moves(turn, occupied_square, board)
    elif piece_type == "Q":
        return get_queen_moves(turn, occupied_square, board)
    elif piece_type == "K":
        return get_king_moves(turn, occupied_square, board)


def en_passant_check(turn, enemy_square, move_log):
    if turn == "w":
        if move_log[-1].end_row == 3 and move_log[-1].start_row == 1 and enemy_square == move_log[-1].end_sq:
            return True
        else:
            return False
    else:
        if move_log[-1].end_row == 4 and move_log[-1].start_row == 6 and enemy_square == move_log[-1].end_sq:
            return True
        else:
            return False


def get_pawn_moves(turn, occupied_square, board, move_log):
    moves = []
    r, c = occupied_square

    if turn == "w":
        if r == 6 and board[r - 1][c] == "--" and board[r - 2][c] == "--":
            moves.append(Move((r, c), (r - 2, c), board))  # Double space move
        if 0 <= r - 1 and board[r-1][c] == "--":
            moves.append(Move((r, c), (r - 1, c), board))  # Single square move
        if (0 <= r - 1 and 0 <= c - 1) and board[r - 1][c - 1][0] == "b":  # Capture left
            moves.append(Move((r, c), (r - 1, c - 1), board))
        if (0 <= r - 1 and c + 1 < len(board)) and board[r - 1][c + 1][0] == "b":  # Capture right
            moves.append(Move((r, c), (r - 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "bP":
            if en_passant_check("w", (r, c - 1), move_log):
                moves.append(EnPassant((r, c), (r - 1), board, (r, c - 1)))  # Left en passant
        if c + 1 < len(board) and board[r][c + 1] == "bP":
            if en_passant_check("w", (r, c + 1), move_log):
                moves.append(EnPassant((r, c), (r + 1), board, (r, c + 1)))  # Right en passant
    else:
        # Double space move
        if r == 1 and board[r + 1][c] == "--" and board[r + 2][c] == "--":  # Double space move
            moves.append(Move((r, c), (r + 2, c), board))
        if r + 1 < len(board) - 1 and board[r + 1][c] == "--":  # Single space move
            moves.append(Move((r, c), (r + 1, c), board))
        if (r + 1 < len(board) - 1 and 0 <= c - 1) and board[r + 1][c - 1][0] == "b":  # Capture left
            moves.append(Move((r, c), (r + 1, c - 1), board))
        if (r + 1 < len(board) - 1 and c + 1 < len(board) - 1) and board[r + 1][c + 1][0] == "b":  # Capture right
            moves.append(Move((r, c), (r + 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "wP":
            if en_passant_check("b", (r, c - 1), move_log):
                moves.append(EnPassant((r, c), (r + 1), board, (r, c - 1)))  # Left en passant
        if c + 1 < len(board) and board[r][c + 1] == "wP":
            if en_passant_check("b", (r, c + 1), move_log):
                moves.append(EnPassant((r, c), (r + 1), board, (r, c + 1)))  # Right en passant



def get_rook_moves(turn, occupied_square, board):
    return straight_line_scan(turn, occupied_square, board)


def get_bishop_moves(turn, occupied_square, board):
    pass


def get_knight_moves(turn, occupied_square, board):
    pass


def get_queen_moves(turn, occupied_square, board):
    pass


def get_king_moves(turn, occupied_square, board, castle_rights):
    pass


def straight_line_scan(turn, occupied_square, board):
    squares = []

    # Row scan
    temp_squares = []
    #current_row = board[occupied_square[0]]
    current_row = board
    for i, square in enumerate(current_row):
        if i == occupied_square[1]:  # If the current column equals our occupied_square column
            pass

        elif square != "--" and square[0] == turn:
            if i < occupied_square[1]:
                temp_squares = []

            if i > occupied_square[1]:
                break

        elif square == "--":
            temp_squares.append((occupied_square, (occupied_square[0], i)))

        elif square != "--" and square[0] != turn:
            if i < occupied_square[1]:
                temp_squares = []

            temp_squares.append((occupied_square, (occupied_square[0], i)))

            if i > occupied_square[1]:
                break
    squares.extend(temp_squares)


    return squares



def test_straight_line():
    test1 = ["bP", "bP", "bP", "--", "bN", "--", "--", "bR"]
    test2 = ["bP", "wP", "bP", "--", "bN", "--", "--", "bR"]
    test3 = ["bP", "--", "wP", "bP", "--", "bR", "wP", "wP"]
    print(straight_line_scan("b", (0, 7), test1))
    print(straight_line_scan("b", (0, 7), test2))
    print(straight_line_scan("b", (0, 5), test3))


test_straight_line()