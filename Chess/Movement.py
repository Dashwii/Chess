



# Squares that will be checked for castling
KING_SIDE_VECTOR_SCANS = [(0, 1), (0, 2)]
QUEEN_SIDE_VECTOR_SCANS = [(0, -1), (0, -2), (0, -3)]


# class Move:
#     # Computer notation to chess notation conversion
#     rank_to_row = {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4,
#                    "3": 5, "2": 6, "1": 7}
#     row_to_rank = {v: k for k, v in rank_to_row.items()}
#     file_to_col = {"a": 0, "b": 1, "c": 2, "d": 3,
#                    "e": 4, "f": 5, "g": 6, "h": 7}
#     col_to_file = {v: k for k, v in file_to_col.items()}
#
#     def __init__(self, start_sq, end_sq, board, en_passant=None, castle=None):
#         self.start_sq = start_sq
#         self.end_sq = end_sq
#         self.start_row = start_sq[0]
#         self.start_col = start_sq[1]
#         self.end_row = end_sq[0]
#         self.end_col = end_sq[1]
#         self.en_passant = en_passant
#         self.castle = castle
#
#         self.piece_moved = board[self.start_row][self.start_col]
#         if en_passant is not None:
#             self.piece_captured = board[en_passant[0]][en_passant[1]]
#         elif castle is not None:
#             self.piece_captured = board[castle[0][0]][castle[0][1]]
#             self.rook_start_sq = self.castle[0]
#             self.rook_end_sq = self.castle[1]
#         else:
#             self.piece_captured = board[self.end_row][self.end_col]
#         self.id = str(self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col)
#
#     def __eq__(self, other):
#         if self.id == other.id:
#             return True
#
#     def get_chess_notation(self):
#         return Move.col_to_file[self.start_col] + Move.row_to_rank[self.start_row] + Move.col_to_file[self.end_col] + Move.row_to_rank[self.end_row]


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


def check_if_king_in_check(current_king_sq, enemy_moves):
    """
    Check if the king were searching for is in check"""
    for enemy_move in enemy_moves:
        if enemy_move.end_sq == current_king_sq:
            return True
    else:
        return False


def get_king_square(turn, board):
    """
    Get the current square the king were searching for is on"""
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if board[i][j] == turn + "K":
                return i, j


def get_king_moves(turn, r, c, board, castling_rights):
    moves = []
    vectors = [(-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, -1), (1, 1)]
    for direction in vectors:
        dx = c + direction[1]
        dy = r + direction[0]
        if 0 <= dx < len(board) and 0 <= dy < len(board):
            sq_occupy = check_if_square_has_enemy_piece((r, c), (dy, dx), board)
            if sq_occupy == "EMPTY" or sq_occupy == "ENEMY":
                moves.append(Move((r, c), (dy, dx), board))
            else:
                pass

    # Castling
    if turn == "w":
        if castling_rights["W_King_Side"]:
            for vector in KING_SIDE_VECTOR_SCANS:
                if c + vector[1] < len(board):
                    if board[r + vector[0]][c + vector[1]] != "--":
                        break
                else:
                    break
            else:
                moves.append(Move((r, c), (r, c + 2), board, castle=[(r, 7), (r, 5)]))
        if castling_rights["W_Queen_Side"]:
            for vector in QUEEN_SIDE_VECTOR_SCANS:
                if board[r + vector[0]][c + vector[1]] != "--":
                    break
            else:
                moves.append(Move((r, c), (r, c - 2), board, castle=[(r, 0), (r, 3)]))
    else:
        if castling_rights["B_King_Side"]:
            for vector in KING_SIDE_VECTOR_SCANS:
                if c + vector[1] < len(board):
                    if board[r + vector[0]][c + vector[1]] != "--":
                        break
                else:
                    break
            else:
                moves.append(Move((r, c), (r, c + 2), board, castle=[(r, 7), (r, 5)]))
        if castling_rights["B_Queen_Side"]:
            for vector in QUEEN_SIDE_VECTOR_SCANS:
                if board[r + vector[0]][c + vector[1]] != "--":
                    break
            else:
                moves.append(Move((r, c), (r, c - 2), board, castle=[(r, 0), (r, 3)]))

    return moves


def get_queen_moves(r, c, board):
    moves = []
    moves.extend(diagonal_scan(r, c, board))
    moves.extend(moves_in_col_or_row(board[r][c][0], r, c, board, vertical=False))
    moves.extend(moves_in_col_or_row(board[r][c][0], r, c, board, vertical=True))
    return moves


def en_passant_check(turn, enemy_r_c, move_log):
    if len(move_log) == 0:
        return

    if turn == "w":
        if move_log[-1].end_row == 3 and move_log[-1].start_row == 1 and enemy_r_c == move_log[-1].end_sq:
            return True
        else:
            return False
    else:
        if move_log[-1].end_row == 4 and move_log[-1].start_row == 6 and enemy_r_c == move_log[-1].end_sq:
            return True
        else:
            return False


def get_pawn_moves(r, c, board, move_log):
    """
    Returns all moves for the pawn piece in the row and column. Will search for diagonal captures and vertical movement."""

    moves = []
    turn = board[r][c][0]

    # Search for every column above the pawn. If nothing is blocking then it's a valid move.
    if turn == "w":  # Go up the column from whites perspective
        # Two space move
        if r == 6 and board[r - 1][c] == "--" and board[r - 2][c] == "--":
            moves.append(Move((r, c), (r - 2, c), board))
        if 0 <= r - 1 and board[r - 1][c] == "--":
            moves.append(Move((r, c), (r - 1, c), board))
        if (0 <= r - 1 and 0 <= c - 1) and board[r - 1][c - 1][0] == "b":
            moves.append(Move((r, c), (r - 1, c - 1), board))
        if (0 <= r - 1 and c + 1 < len(board)) and board[r - 1][c + 1][0] == "b":
            moves.append(Move((r, c), (r - 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "bP":
            if en_passant_check("w", (r, c - 1), move_log):
                moves.append(Move((r, c), (r - 1, c - 1), board, en_passant=(r, c - 1)))  # Right scan
        if c + 1 < len(board) and board[r][c + 1] == "bP":
            if en_passant_check("w", (r, c + 1), move_log):
                moves.append(Move((r, c), (r - 1, c + 1), board, en_passant=(r, c + 1)))  # Left scan

    else:
        # Two space move
        if r == 1 and board[r + 1][c] == "--" and board[r + 2][c] == "--":
            moves.append(Move((r, c), (r + 2, c), board))
        if r + 1 < len(board) and board[r + 1][c] == "--":  # Go down the column from whites perspective
            moves.append(Move((r, c), (r + 1, c), board))
        if (r + 1 < len(board) and 0 <= c - 1) and board[r + 1][c - 1] != "--" and board[r + 1][c - 1][0] == "w":
            moves.append(Move((r, c), (r + 1, c - 1), board))
        if (r + 1 < len(board) and c + 1 < len(board)) and board[r + 1][c + 1] != "--" and board[r + 1][c + 1][
            0] == "w":
            moves.append(Move((r, c), (r + 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "wP":
            if en_passant_check("b", (r, c - 1), move_log):
                moves.append(Move((r, c), (r + 1, c - 1), board, en_passant=(r, c - 1)))
        if c + 1 < len(board) and board[r][c + 1] == "wP":
            if en_passant_check("b", (r, c + 1), move_log):
                moves.append(Move((r, c), (r + 1, c + 1), board, en_passant=(r, c + 1)))
    return moves


def get_rook_moves(r, c, board):
    """
    Returns all possible moves for the rook. Will search vertically and horizontally."""
    moves = []
    moves.extend(moves_in_col_or_row(board[r][c][0], r, c, board, vertical=False))
    moves.extend(moves_in_col_or_row(board[r][c][0], r, c, board, vertical=True))
    return moves


def get_bishop_moves(r, c, board):
    return diagonal_scan(r, c, board)


def check_if_square_has_enemy_piece(start_sq, end_sq, board):
    # Function will soon acknowledge kings.
    start_r = start_sq[0]
    start_c = start_sq[1]
    end_r = end_sq[0]
    end_c = end_sq[1]

    our_turn = board[start_r][start_c][0]
    other_turn = board[end_r][end_c][0]

    if other_turn == "-":
        return "EMPTY"
    elif other_turn == our_turn:
        return "FRIENDLY"
    else:
        return "ENEMY"


def column_knight_check(current_r, comparing_r, r_abs_dist, c, board):
    _moves = []
    if c + 1 < len(board):
        if c + 2 < len(board):
            if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 2),
                                               board) != "FRIENDLY" and r_abs_dist == 1:
                _moves.append(Move((current_r, c), (comparing_r, c + 2), board))
        if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 1),
                                           board) != "FRIENDLY" and r_abs_dist == 2:
            _moves.append(Move((current_r, c), (comparing_r, c + 1), board))

    if c - 1 >= 0:
        if c - 2 >= 0:
            if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 2),
                                               board) != "FRIENDLY" and r_abs_dist == 1:
                _moves.append(Move((current_r, c), (comparing_r, c - 2), board))
        if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 1),
                                           board) != "FRIENDLY" and r_abs_dist == 2:
            _moves.append(Move((current_r, c), (comparing_r, c - 1), board))
    return _moves


def get_knight_moves(r, c, board):
    moves = []
    if r - 1 >= 0:
        if r - 2 >= 0:
            moves.extend(column_knight_check(r, r - 2, 2, c, board))
        moves.extend(column_knight_check(r, r - 1, 1, c, board))
    if r + 1 < len(board):
        if r + 2 < len(board):
            moves.extend(column_knight_check(r, r + 2, 2, c, board))
        moves.extend(column_knight_check(r, r + 1, 1, c, board))
    return moves


def diagonal_scan(r, c, board):
    moves = []
    vectors = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for direction in vectors:
        for i, row in enumerate(board[r]):
            i += 1
            dx = c + (i * direction[1])  # Column in list
            dy = r + (i * direction[0])  # Row in list
            if 0 <= dx < len(board) and 0 <= dy < len(board):
                if board[dy][dx] == "--":
                    moves.append(Move((r, c), (dy, dx), board))
                else:
                    our_turn = board[r][c][0]
                    other_turn = board[dy][dx][0]
                    if our_turn == other_turn:
                        break
                    else:
                        moves.append(Move((r, c), (dy, dx), board))
                        break
            else:
                break
    return moves


def moves_in_col_or_row(turn, r, c, board, vertical=False):
    moves = []
    if not vertical:
        for i, square in enumerate(board[r]):
            if i == c:
                pass
            elif square != "--" and square[0] == turn:
                if i < c:
                    moves = []
                if i > c:
                    break
            elif square == "--":
                moves.append(Move((r, c), (r, i), board))
            elif square != "--" and square[0] != turn:
                if i < c:
                    moves = []
                moves.append(Move((r, c), (r, i), board))
                if i > c:
                    break
    else:
        col_list = [r[c] for r in board]
        for i, square in enumerate(col_list):
            if i == r:
                pass
            elif square != "--" and square[0] == turn:
                if i < r:
                    moves = []
                if i > r:
                    break
            elif square == "--":
                moves.append(Move((r, c), (i, c), board))
            elif square != "--" and square[0] != turn:
                if i < r:
                    moves = []
                moves.append(Move((r, c), (i, c), board))
                if i > r:
                    break
    return moves

