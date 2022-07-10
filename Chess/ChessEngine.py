import copy


"""
New branch Optimization_and_Refactors

Trying to clean up/refactor code as much as I can + comment and make everything clean before I implement AI.
ChessEngine is probably going to be rewritten a decent amount so the AI won't take years to look ahead and make moves.

Things I wanted refactored:
    - Simulating moves ahead
    - Some functions to be simplified
    - Remembering which pieces are on each squares to eliminate looking for them every turn.
    - Better check system and check filtering
    - Castling rewrite/simplification?
    - Making sure the game works in any board state. Some bugs I noticed like the king spawning in a corner allows it to move outside the board, crashing the game.
    - Insufficient material game over state, Repeated moves game over state.
    - Move timer.
"""


# Squares that will be checked for castling
KING_SIDE_VECTOR_SCANS = [(0, 1), (0, 2)]
QUEEN_SIDE_VECTOR_SCANS = [(0, -1), (0, -2), (0, -3)]


class ChessEngine:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.pawn_promote = False
        self.castling = {"W_Undo_Regain_Castle": None, "W_Queen_Side_Regain_Castle": None, "W_King_Side_Regain_Castle": None, "W_King_Side": True, "W_Queen_Side": True,
                         "B_Undo_Regain_Castle": None, "B_Queen_Side_Regain_Castle": None, "B_King_Side_Regain_Castle": None,"B_King_Side": True, "B_Queen_Side": True}
        # In these tuples the king's current row/column will be added in the respective indexes to see if the squares are clear.
        self.move_log = []
        self.checkmate = False
        self.stalemate = False
        self.winner = None
        self.current_valid_moves = self.get_valid_moves()

    """
    Takes a Move as a parameter and executes it"""
    def do_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        if move.en_passant is not None:
            self.board[move.en_passant[0]][move.en_passant[1]] = "--"
        if move.piece_moved[1] in ("K", "R"):
            self.castling_work(move)
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)

        # Pawn promotion
        # If a pawn_promotion is eligible return out early. Once we get input we'll update our moves and the turn. (May need to break this function up to check for checkmates as well after pawn_promotion)
        if move.piece_moved[1] == "P" and move.end_row == 0 and self.white_to_move:  # White pawn promote
            self.pawn_promote = True
            return
        elif move.piece_moved[1] == "P" and move.end_row == 7 and not self.white_to_move:  # Black pawn promote
            self.pawn_promote = True
            return

        self.next_turn_work()

    def undo_move(self):
        if len(self.move_log) > 0:
            last_move = self.move_log.pop()
            self.white_to_move = not self.white_to_move
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
            if last_move.en_passant is not None:
                self.board[last_move.en_passant[0]][last_move.en_passant[1]] = last_move.piece_captured
                self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured = "--"
            else:
                self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            if last_move.piece_moved[1] in ("K", "R"):
                self.castling_work(last_move, undo=True)

            # Reset state variables
            if self.checkmate:
                self.checkmate = False
            elif self.stalemate:
                self.stalemate = False

            self.current_valid_moves = self.get_valid_moves()

    """
    Work that needs to be done on a new turn."""
    def next_turn_work(self):
        if self.pawn_promote:
            self.pawn_promote = False

        self.white_to_move = not self.white_to_move
        self.current_valid_moves = self.get_valid_moves()

        # Determine if were in checkmate or game is a draw.
        if self.white_to_move:
            check = check_king_in_check(get_king_square("w", self.board), self.get_all_possible_moves(self.board, not self.white_to_move))
        else:
            check = check_king_in_check(get_king_square("b", self.board), self.get_all_possible_moves(self.board, not self.white_to_move))
        if len(self.current_valid_moves) == 0 and check:
            self.checkmate = True
            # Get previous turn before turns flipped.
            if self.white_to_move:
                self.winner = "Black"
            else:
                self.winner = "White"
        elif len(self.current_valid_moves) == 0 and not check:
            self.stalemate = True

    """
        Promotes a pawn to the piece chosen"""

    def promote(self, pawn_sq, piece_wanted):
        turn = self.board[pawn_sq[0]][pawn_sq[1]][0]
        self.board[pawn_sq[0]][pawn_sq[1]] = turn + piece_wanted
        print("Piece promoted!")


    def castling_work(self, move, undo=False):
        if move.piece_moved[1] == "R":  # Disable castling for a colors side if the rook moved.
            if undo:
                if self.white_to_move:
                    if self.castling["W_King_Side_Regain_Castle"] is not None and len(self.move_log) <= self.castling["W_King_Side_Regain_Castle"] and self.castling["W_Undo_Regain_Castle"] is None:
                        self.castling["W_King_Side"] = True
                    if self.castling["W_Queen_Side_Regain_Castle"] is not None and len(self.move_log) <= self.castling["W_Queen_Side_Regain_Castle"] and self.castling["W_Undo_Regain_Castle"] is None:
                        self.castling["W_Queen_Side"] = True
                else:
                    if self.castling["B_King_Side_Regain_Castle"] is not None and len(self.move_log) <= self.castling["B_King_Side_Regain_Castle"] and self.castling["B_Undo_Regain_Castle"] is None:
                        self.castling["B_King_Side"] = True
                    if self.castling["B_Queen_Side_Regain_Castle"] is not None and len(self.move_log) <= self.castling["B_Queen_Side_Regain_Castle"] and self.castling["B_Undo_Regain_Castle"] is None:
                        self.castling["B_Queen_Side"] = True
            else:
                if self.white_to_move:
                    if move.start_sq == (7, 7):
                        self.castling["W_King_Side"] = False
                        self.castling["W_King_Side_Regain_Castle"] = len(self.move_log)
                    elif move.start_sq == (7, 0):
                        self.castling["W_Queen_Side"] = False
                        self.castling["W_Queen_Side_Regain_Castle"] = len(self.move_log)
                else:
                    if move.start_sq == (0, 7):
                        self.castling["B_King_Side"] = False
                        self.castling["B_King_Side_Regain_Castle"] = len(self.move_log)
                    elif move.start_sq == (0, 0):
                        self.castling["B_Queen_Side"] = False
                        self.castling["B_Queen_Side_Regain_Castle"] = len(self.move_log)

        elif move.piece_moved[1] == "K":
            if move.castle is None:  # If king moved, and it's not a castle type move we need to disable castling for that color.
                if undo:
                    if self.white_to_move:
                        if len(self.move_log) == self.castling["W_Undo_Regain_Castle"]:  # To regain the right to castle with an undo move. The player needs to undo the first move that their king moved on.
                            self.castling["W_King_Side"] = True
                            self.castling["W_Queen_Side"] = True
                    else:
                        if len(self.move_log) == self.castling["B_Undo_Regain_Castle"]:
                            self.castling["B_King_Side"] = True
                            self.castling["B_Queen_Side"] = True
                else:
                    if self.white_to_move:
                        self.castling["W_King_Side"] = False
                        self.castling["W_Queen_Side"] = False
                        if self.castling["W_Undo_Regain_Castle"] is None:  # We set this variables so a player can't undo a king move at any point of the game to regain castling.
                            self.castling["W_Undo_Regain_Castle"] = len(self.move_log)
                    else:
                        self.castling["B_King_Side"] = False
                        self.castling["B_Queen_Side"] = False
                        if self.castling["B_Undo_Regain_Castle"] is None:
                            self.castling["B_Undo_Regain_Castle"] = len(self.move_log)
            else:  # If the king move was a castle.
                if undo:
                    self.board[move.rook_start_sq[0]][move.rook_start_sq[1]] = move.piece_captured
                    self.board[move.end_row][move.end_col] = "--"
                    self.board[move.rook_end_sq[0]][move.rook_end_sq[1]] = "--"
                    if self.white_to_move:
                        self.castling["W_King_Side"] = True
                        self.castling["W_Queen_Side"] = True
                    else:
                        self.castling["B_King_Side"] = True
                        self.castling["B_Queen_Side"] = True
                else:
                    self.board[move.castle[0][0]][move.castle[0][1]] = "--"
                    self.board[move.castle[1][0]][move.castle[1][1]] = move.piece_captured

                    if self.white_to_move:
                        self.castling["W_King_Side"] = False
                        self.castling["W_Queen_Side"] = False
                    else:
                        self.castling["B_King_Side"] = False
                        self.castling["B_Queen_Side"] = False

    def determine_valid_castle(self, move, enemy_move, currently_in_check):
        if currently_in_check:  # If we are in check immediately return False since the king cannot castle out of check.
            return False

        # Determine if the castle is queen side of king side
        if move.end_col - move.start_col == 2:  # King side
            for vector in KING_SIDE_VECTOR_SCANS:
                if enemy_move.end_sq == (move.start_row + vector[0], move.start_col + vector[1]):
                    return False
            else:
                return True
        elif move.end_col - move.start_col == -2:  # Queen side
            for vector in QUEEN_SIDE_VECTOR_SCANS:
                if enemy_move.end_sq == (move.start_row + vector[0], move.start_col + vector[1]):
                    return False
            else:
                return True

    """
    Will determine all valid moves considering king check"""
    def get_valid_moves(self):
        # Function will first filter moves that capture the enemy king.
        # Function will then simulate remaining moves and get opposing teams next turn moves.
        # If any piece from the enemy puts our king in check. Filter out the move.

        possible_moves = self.get_all_possible_moves(self.board, self.white_to_move)
        filtered_non_king_capture_moves = []
        filtered_self_check_moves = []

        if self.white_to_move:
            our_turn = "w"
            opposing_turn = "b"
        else:
            our_turn = "b"
            opposing_turn = "w"

        # Clear our possible_moves that capture opposing king
        opposing_king_sq = get_king_square(opposing_turn, self.board)
        for move in possible_moves:
            if move.end_row == opposing_king_sq[0] and move.end_col == opposing_king_sq[1]:
                pass
            else:
                filtered_non_king_capture_moves.append(move)

        current_king_sq = get_king_square(our_turn, self.board)
        currently_in_check = check_king_in_check(current_king_sq, self.get_all_possible_moves(self.board, not self.white_to_move))

        for move in filtered_non_king_capture_moves:  # Clear out moves that will put current turn's king in check
            board = copy.deepcopy(self.board)
            board[move.start_row][move.start_col] = "--"
            board[move.end_row][move.end_col] = move.piece_moved
            current_king_sq = get_king_square(our_turn, board)
            enemy_moves_next_turn = self.get_all_possible_moves(board, not self.white_to_move)
            for enemy_move in enemy_moves_next_turn:
                if enemy_move.end_row == current_king_sq[0] and enemy_move.end_col == current_king_sq[1]:
                    break
                if move.castle is not None:  # Check if our castle squares are occupied by this move.
                    if not self.determine_valid_castle(move, enemy_move, currently_in_check):
                        break
            else:
                filtered_self_check_moves.append(move)
        return filtered_self_check_moves

    """
    Will determine all possible moves not considering king check"""
    def get_all_possible_moves(self, board, white_to_move):
        # Passing an argument instead of accessing self so we can test moves for the turn ahead. Maybe white_to_move in this function should be 'turn'.
        moves = []
        for i, r in enumerate(board):  # Num of rows
            for j, c in enumerate(r):  # Num of columns
                turn = board[i][j][0]
                if (turn == "w" and white_to_move) or (turn == "b" and not white_to_move):
                    piece_type = board[i][j][1]
                    if piece_type == "P":
                        moves.extend(get_pawn_moves(i, j, board, self.move_log))
                    elif piece_type == "R":
                        moves.extend(get_rook_moves(i, j, board))
                    elif piece_type == "B":
                        moves.extend(get_bishop_moves(i, j, board))
                    elif piece_type == "N":
                        moves.extend(get_knight_moves(i, j, board))
                    elif piece_type == "Q":
                        moves.extend(get_queen_moves(i, j, board))
                    else:
                        moves.extend(get_king_moves(turn, i, j, board, self.castling))
        return moves



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
    moves.extend(horizontal_scan(r, c, board))
    moves.extend(horizontal_scan(r, c, board, reverse=True))
    return moves


def check_king_in_check(current_king_sq, enemy_moves):
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


# def return_piece_moves(piece, occupied_square, board, move_log, castle_rights):
#     turn = piece[0]
#     piece_type = piece[1]
#
#     if piece_type == "P":
#         return get_pawn_moves(turn, occupied_square, board, move_log)
#     elif piece_type == "R":
#         return get_rook_moves(turn, occupied_square, board)
#     elif piece_type == "B":
#         return get_bishop_moves(turn, occupied_square, board)
#     elif piece_type == "N":
#         return get_knight_moves(turn, occupied_square, board)
#     elif piece_type == "Q":
#         return get_queen_moves(turn, occupied_square, board)
#     elif piece_type == "K":
#         return get_king_moves(turn, occupied_square, board, castle_rights)


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
            moves.append(Move((r, c),(r - 1, c - 1), board))
        if (0 <= r - 1 and c + 1 < len(board)) and board[r - 1][c + 1][0] == "b":
            moves.append(Move((r, c), (r - 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "bP":
            if en_passant_check("w", (r, c-1), move_log):
                moves.append(Move((r, c), (r - 1, c - 1), board, en_passant=(r, c - 1)))  # Right scan
        if c + 1 < len(board) and board[r][c + 1] == "bP":
            if en_passant_check("w", (r, c+1), move_log):
                moves.append(Move((r, c), (r - 1, c + 1), board, en_passant=(r, c + 1)))  # Left scan

    else:
        # Two space move
        if r == 1 and board[r + 1][c] == "--" and board[r + 2][c] == "--":
            moves.append(Move((r, c), (r + 2, c), board))
        if r + 1 < len(board) and board[r + 1][c] == "--":  # Go down the column from whites perspective
            moves.append(Move((r, c), (r + 1, c), board))
        if (r + 1 < len(board) and 0 <= c - 1) and board[r + 1][c - 1] != "--" and board[r + 1][c - 1][0] == "w":
            moves.append(Move((r, c),(r + 1, c - 1), board))
        if (r + 1 < len(board) and c + 1 < len(board)) and board[r + 1][c + 1] != "--" and board[r + 1][c + 1][0] == "w":
            moves.append(Move((r, c), (r + 1, c + 1), board))
        # En passant
        if 0 <= c - 1 and board[r][c - 1] == "wP":
            if en_passant_check("b", (r, c-1), move_log):
                moves.append(Move((r, c), (r + 1, c - 1), board, en_passant=(r, c - 1)))
        if c + 1 < len(board) and board[r][c + 1] == "wP":
            if en_passant_check("b", (r, c+1), move_log):
                moves.append(Move((r, c), (r + 1, c + 1), board, en_passant=(r, c + 1)))
    return moves


def get_rook_moves(r, c, board):
    """
    Returns all possible moves for the rook. Will search vertically and horizontally."""
    moves = []
    moves.extend(horizontal_scan(r, c, board))
    moves.extend(horizontal_scan(r, c, board, reverse=True))
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
            if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 2), board) != "FRIENDLY" and r_abs_dist == 1:
                _moves.append(Move((current_r, c), (comparing_r, c + 2), board))
        if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 1), board) != "FRIENDLY" and r_abs_dist == 2:
            _moves.append(Move((current_r, c), (comparing_r, c + 1), board))

    if c - 1 >= 0:
        if c - 2 >= 0:
            if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 2), board) != "FRIENDLY" and r_abs_dist == 1:
                _moves.append(Move((current_r, c), (comparing_r, c - 2), board))
        if check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 1), board) != "FRIENDLY" and r_abs_dist == 2:
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


def horizontal_scan(r, c, board, reverse=False):
    _moves = []

    """
    Row check"""
    if not reverse:
        for i in range(len(board[r][c:])):  # Scanning right
            i += 1
            if 0 <= c + i < len(board):
                if board[r][c + i] == "--":
                    _moves.append(Move((r, c), (r, c + i), board))
                elif board[r][c + i] != "--":
                    our_turn = board[r][c][0]
                    other_turn = board[r][c + i][0]
                    if our_turn == other_turn:
                        break
                    else:
                        _moves.append(Move((r, c), (r, c + i), board))
                        break
            else:
                break
    else:
        for i in range(len(board[r][:c + 1])):  # Scanning left
            i += 1
            if 0 <= c - i < len(board):
                if board[r][c - i] == "--":
                    _moves.append(Move((r, c), (r, c - i), board))
                elif board[r][c - i] != "--":
                    our_turn = board[r][c][0]
                    other_turn = board[r][c - i][0]
                    if our_turn == other_turn:
                        break
                    else:
                        _moves.append(Move((r, c), (r, c - i), board))
                        break
            else:
                break

    """
    Column check"""
    if not reverse:
        for i in range(len(board[r:])):  # Scan down the column
            i += 1
            if 0 <= r + i < len(board):
                if board[r + i][c] == "--":
                    _moves.append(Move((r, c), (r + i, c), board))
                elif board[r + i][c] != "--":
                    our_turn = board[r][c][0]
                    other_turn = board[r + i][c][0]
                    if our_turn == other_turn:
                        break
                    else:
                        _moves.append(Move((r, c), (r + i, c), board))
                        break
            else:
                break
    else:
        for i in range(len(board[:r])):  # Scan up the column
            i += 1
            if 0 <= r - i < len(board):
                if board[r - i][c] == "--":
                    _moves.append(Move((r, c), (r - i, c), board))
                elif board[r - i][c] != "--":
                    our_turn = board[r][c][0]
                    other_turn = board[r - i][c][0]
                    if our_turn == other_turn:
                        break
                    else:
                        _moves.append(Move((r, c), (r - i, c), board))
                        break
    return _moves






class Move:
    # Computer notation to chess notation conversion
    rank_to_row = {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4,
                   "3": 5, "2": 6, "1": 7}
    row_to_rank = {v: k for k, v in rank_to_row.items()}
    file_to_col = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_file = {v: k for k, v in file_to_col.items()}

    def __init__(self, start_sq, end_sq, board, en_passant=None, castle=None):
        self.start_sq = start_sq
        self.end_sq = end_sq
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.en_passant = en_passant
        self.castle = castle

        self.piece_moved = board[self.start_row][self.start_col]
        if en_passant is not None:
            self.piece_captured = board[en_passant[0]][en_passant[1]]
        elif castle is not None:
            self.piece_captured = board[castle[0][0]][castle[0][1]]
            self.rook_start_sq = self.castle[0]
            self.rook_end_sq = self.castle[1]
        else:
            self.piece_captured = board[self.end_row][self.end_col]
        self.id = str(self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col)

    def __eq__(self, other):
        if self.id == other.id:
            return True

    def get_chess_notation(self):
        return Move.col_to_file[self.start_col] + Move.row_to_rank[self.start_row] + Move.col_to_file[self.end_col] + Move.row_to_rank[self.end_row]
