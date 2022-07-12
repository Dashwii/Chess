import copy
from Movement import *

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


class PieceLog:
    def __init__(self, piece, row, column):
        self.piece = piece
        self.turn = piece[0]
        self.type = piece[1]
        self.row = row
        self.column = column
        self.attacking_squares = []


class BoardData:
    """
    Class will save extra tidbits of data from a board to make things efficient while utilizing the easy design of
    a 2d array board with simple 2 character strings to set up and move pieces.
    """
    def __init__(self):
        self.piece_logs = []
        self.removed_pieces = []
        self.move_log = []
        self.current_turn_move_pieces = []
        self.board_state_history = []

    def gather_piece_log(self, board):
        """One time function run at init to keep track of piece positions on the board, their turn, their type,
        and what squares they attack. This function will mainly be useful for ChessMain for now."""
        for i, row in enumerate(board):
            for j, col in enumerate(row):
                if board[i][j] != "--":
                    self.piece_logs.append(PieceLog(board[i][j], i, j))

    def undo_history(self):
        self.piece_logs.append(self.removed_pieces.pop())
        self.move_log.pop()
        #self.update_current_turn_move_pieces()


class ChessEngine:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "--"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "wP"],
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
        self.checkmate = False
        self.stalemate = False
        self.winner = None
        self.board_data = BoardData()
        self.board_data.gather_piece_log(self.board)
        self.move_log = self.board_data.move_log
        self.current_valid_moves = self.get_valid_moves()

    def do_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        if move.en_passant is not None:
            self.board[move.en_passant[0]][move.en_passant[1]] = "--"
        if move.piece_moved[1] in ("K", "R"):
            self.castling_work(move)
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board_data.move_log.append(move)

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
        if len(self.board_data.move_log) > 0:
            last_move = self.board_data.move_log.pop()
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
            check = check_if_king_in_check(get_king_square("w", self.board), self.get_all_possible_moves(self.board, not self.white_to_move))
        else:
            check = check_if_king_in_check(get_king_square("b", self.board), self.get_all_possible_moves(self.board, not self.white_to_move))
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
                    if self.castling["W_King_Side_Regain_Castle"] is not None and len(self.board_data.move_log) <= self.castling["W_King_Side_Regain_Castle"] and self.castling["W_Undo_Regain_Castle"] is None:
                        self.castling["W_King_Side"] = True
                    if self.castling["W_Queen_Side_Regain_Castle"] is not None and len(self.board_data.move_log) <= self.castling["W_Queen_Side_Regain_Castle"] and self.castling["W_Undo_Regain_Castle"] is None:
                        self.castling["W_Queen_Side"] = True
                else:
                    if self.castling["B_King_Side_Regain_Castle"] is not None and len(self.board_data.move_log) <= self.castling["B_King_Side_Regain_Castle"] and self.castling["B_Undo_Regain_Castle"] is None:
                        self.castling["B_King_Side"] = True
                    if self.castling["B_Queen_Side_Regain_Castle"] is not None and len(self.board_data.move_log) <= self.castling["B_Queen_Side_Regain_Castle"] and self.castling["B_Undo_Regain_Castle"] is None:
                        self.castling["B_Queen_Side"] = True
            else:
                if self.white_to_move:
                    if move.start_sq == (7, 7):
                        self.castling["W_King_Side"] = False
                        self.castling["W_King_Side_Regain_Castle"] = len(self.board_data.move_log)
                    elif move.start_sq == (7, 0):
                        self.castling["W_Queen_Side"] = False
                        self.castling["W_Queen_Side_Regain_Castle"] = len(self.board_data.move_log)
                else:
                    if move.start_sq == (0, 7):
                        self.castling["B_King_Side"] = False
                        self.castling["B_King_Side_Regain_Castle"] = len(self.board_data.move_log)
                    elif move.start_sq == (0, 0):
                        self.castling["B_Queen_Side"] = False
                        self.castling["B_Queen_Side_Regain_Castle"] = len(self.board_data.move_log)

        elif move.piece_moved[1] == "K":
            if move.castle is None:  # If king moved, and it's not a castle type move we need to disable castling for that color.
                if undo:
                    if self.white_to_move:
                        if len(self.board_data.move_log) == self.castling["W_Undo_Regain_Castle"]:  # To regain the right to castle with an undo move. The player needs to undo the first move that their king moved on.
                            self.castling["W_King_Side"] = True
                            self.castling["W_Queen_Side"] = True
                    else:
                        if len(self.board_data.move_log) == self.castling["B_Undo_Regain_Castle"]:
                            self.castling["B_King_Side"] = True
                            self.castling["B_Queen_Side"] = True
                else:
                    if self.white_to_move:
                        self.castling["W_King_Side"] = False
                        self.castling["W_Queen_Side"] = False
                        if self.castling["W_Undo_Regain_Castle"] is None:  # We set this variables so a player can't undo a king move at any point of the game to regain castling.
                            self.castling["W_Undo_Regain_Castle"] = len(self.board_data.move_log)
                    else:
                        self.castling["B_King_Side"] = False
                        self.castling["B_Queen_Side"] = False
                        if self.castling["B_Undo_Regain_Castle"] is None:
                            self.castling["B_Undo_Regain_Castle"] = len(self.board_data.move_log)
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
        filtered_non_self_check_moves = []

        if self.white_to_move:
            our_turn = "w"
            opposing_turn = "b"
        else:
            our_turn = "b"
            opposing_turn = "w"

        current_king_sq = get_king_square(our_turn, self.board)
        currently_in_check = check_if_king_in_check(current_king_sq, self.get_all_possible_moves(self.board, not self.white_to_move))
        true_board_state = []
        for move in possible_moves:  # Clear out moves that will put current turn's king in check
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
                filtered_non_self_check_moves.append(move)
        return filtered_non_self_check_moves

    """
    Will determine all possible moves not considering king check"""
    def get_all_possible_moves(self, board, white_to_move):
        """
        Will give back all possible moves for each piece on the board"""
        moves = []
        for piece in self.board_data.piece_logs:
            if (piece.turn == "w" and white_to_move) or (piece.turn == "b" and not white_to_move):
                if piece.type == "P":
                    moves.extend(get_pawn_moves(piece.row, piece.column, board, self.board_data.move_log))
                elif piece.type == "R":
                    moves.extend(get_rook_moves(piece.row, piece.column, board))
                elif piece.type == "B":
                    moves.extend(get_bishop_moves(piece.row, piece.column, board))
                elif piece.type == "N":
                    moves.extend(get_knight_moves(piece.row, piece.column, board))
                elif piece.type == "Q":
                    moves.extend(get_queen_moves(piece.row, piece.column, board))
                else:
                    moves.extend(get_king_moves(piece.turn, piece.row, piece.column, board, self.castling))
        return moves


def determine_valid_castle(move, enemy_move, currently_in_check):
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
