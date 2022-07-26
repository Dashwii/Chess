from Movement import *


PREVIOUS_GAME_STATES = []


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
        self.last_move = None
        self.white_to_move = True
        self.w_king_square = get_king_square("w", self.board)
        self.b_king_square = get_king_square("b", self.board)

        self.castle_rights = {"w_queen_castle": True, "w_king_castle": True,
                              "b_queen_castle": True, "b_king_castle": True}
        self.in_check = False
        self.next_turn_check = False
        self.checkmate = False
        self.stalemate = False
        self.pawn_promotion = False

        self.current_valid_moves = []  # Initiate an empty list for our deepcopy to recall to while generating first moves.
        self.current_valid_moves = self.get_valid_moves()

    def next_turn_work(self):
        self.white_to_move = not self.white_to_move

        if self.next_turn_check:
            self.in_check = True
            self.next_turn_check = False

        self.current_valid_moves = self.get_valid_moves()

        if len(self.current_valid_moves) == 0 and self.in_check:
            self.checkmate = True
        elif len(self.current_valid_moves) == 0 and not self.in_check:
            self.stalemate = True

    def do_move(self, move, move_eval=False):
        PREVIOUS_GAME_STATES.append(self.copy())
        self.last_move = move
        if move.en_passant is not None:
            self.board[move.en_passant[0]][move.en_passant[1]] = "--"
        if move.piece_moved[1] == "K":
            if self.white_to_move:
                self.w_king_square = move.end_sq
            else:
                self.b_king_square = move.end_sq
            self.update_castling(move)
        elif move.piece_moved[1] == "R":
            self.update_castling(move)

        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved

        if move.piece_moved[1] == "P" and move.end_row == 0:
            self.pawn_promotion = True
            return
        elif move.piece_moved[1] == "P" and move.end_row == 7:
            self.pawn_promotion = True
            return
        if not move_eval:
            self.next_turn_work()

    def undo_move(self, ai_vs=False):
        if ai_vs and len(PREVIOUS_GAME_STATES) >= 2:
            PREVIOUS_GAME_STATES.pop()  # Get rid of one ply of state
            state = PREVIOUS_GAME_STATES.pop()
        elif len(PREVIOUS_GAME_STATES) > 0:
            state = PREVIOUS_GAME_STATES.pop()
        else:
            return
        self.board = state.board
        self.last_move = state.last_move
        self.white_to_move = state.white_to_move
        self.w_king_square = state.w_king_square
        self.b_king_square = state.b_king_square
        self.castle_rights = state.castle_rights
        self.in_check = state.in_check
        self.checkmate = state.checkmate
        self.stalemate = state.stalemate
        self.pawn_promotion = state.pawn_promotion
        if not hasattr(state, "current_valid_moves"):
            self.current_valid_moves = []
        else:
            self.current_valid_moves = state.current_valid_moves

    def get_valid_moves(self):
        possible_moves = self.get_possible_moves()
        enemy_king_sq = self.b_king_square if self.white_to_move else self.w_king_square

        for i, move in enumerate(possible_moves[::-1]):
            if move.end_sq == enemy_king_sq:
                self.next_turn_check = True
                possible_moves.remove(move)
            else:
                self.do_move(move, move_eval=True)
                if not self.is_valid_move(move):
                    possible_moves.remove(move)
                self.undo_move()
        return possible_moves

    def is_valid_move(self, move):
        turn = "w" if self.white_to_move else "b"
        square = self.w_king_square if self.white_to_move else self.b_king_square
        if move.castle is not None:
            # Handle castling
            if self.in_check:
                return False
            if self.white_to_move:
                if move.end_sq == (7, 6):  # King side
                    for k_square in [(7, 5), (7, 6)]:
                        if self.check_if_square_attacked(turn, k_square):
                            return False
                else:  # Queen Side
                    for q_square in [(7, 3), (7, 2)]:
                        if self.check_if_square_attacked(turn, q_square):
                            return False
            else:
                if move.end_sq == (0, 6):  # King side
                    for k_square in [(0, 5), (0, 6)]:
                        if self.check_if_square_attacked(turn, k_square):
                            return False
                else:  # Queen Side
                    for q_square in [(0, 3), (0, 2)]:
                        if self.check_if_square_attacked(turn, q_square):
                            return False
            return True
        else:
            # Move current turn king on every square that a piece can move to. (Rook, Bishop, Knight, Pawn, Queen, King)
            # We will use each move function (Diagonal, Horizontal, Knight, King, Pawn) [Queen is just combined diagonal and horizontal)
            # If current turn king captures an enemy piece that corresponds with their move function. The move is not legal.
            if self.check_if_square_attacked(turn, square):
                return False
            return True

    def check_if_square_attacked(self, turn, square):
        if check_king_pawn_check(turn, square, self.board):  # Working for white side at least. Did not test black.
            return True
        if check_king_horizontal_check(turn, square, self.board):
            return True
        if check_king_vertical_check(turn, square, self.board):
            return True
        if check_king_diagonal_check(turn, square, self.board):
            return True
        if check_king_knight_check(turn, square, self.board):
            return True
        return False

    def get_possible_moves(self):
        moves = []
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                piece = self.board[i][j]
                if (piece[0] == "w" and self.white_to_move) or (piece[0] == "b" and not self.white_to_move):
                    if piece[1] == "P":
                        moves.extend(get_pawn_moves(i, j, self.board, self.last_move))
                    elif piece[1] == "R":
                        moves.extend(get_rook_moves(i, j, self.board))
                    elif piece[1] == "B":
                        moves.extend(get_bishop_moves(i, j, self.board))
                    elif piece[1] == "N":
                        moves.extend(get_knight_moves(i, j, self.board))
                    elif piece[1] == "Q":
                        moves.extend(get_queen_moves(i, j, self.board))
                    else:
                        moves.extend(get_king_moves(i, j, piece[0], self.board, self.castle_rights))
        return moves

    def promote(self, wanted_piece):
        sq = self.last_move.end_sq
        color = self.last_move.piece_moved[0]
        self.board[sq[0]][sq[1]] = color + wanted_piece
        self.pawn_promotion = False
        print("Piece promoted.")

    def update_castling(self, move):
        if move.piece_moved[1] == "R":
            if self.white_to_move:
                if move.start_sq == (7, 7):
                    self.castle_rights["w_king_castle"] = False
                elif move.start_sq == (7, 0):
                    self.castle_rights["w_queen_castle"] = False
            else:
                if move.start_sq == (0, 7):
                    self.castle_rights["b_king_castle"] = False
                elif move.start_sq == (7, 0):
                    self.castle_rights["b_queen_castle"] = False
        else:
            if move.castle is not None:
                self.board[move.castle[0][0]][move.castle[0][1]] = "--"
                self.board[move.castle[1][0]][move.castle[1][1]] = move.piece_captured
            if self.white_to_move:
                self.castle_rights["w_king_castle"] = False
                self.castle_rights["w_queen_castle"] = False
            else:
                self.castle_rights["b_king_castle"] = False
                self.castle_rights["b_queen_castle"] = False

    def determine_valid_castle(self, move, enemy_move): # noqa
        if move.end_col - move.start_col == 2:  # King Side
            for direction in KING_SIDE_VECTOR_SCANS:
                if enemy_move.end_sq == (move.start_row + direction[0], move.start_col + direction[1]):
                    return False
            else:
                return True
        if move.end_col - move.start_col == -2:  # Queen Side
            for direction in QUEEN_SIDE_VECTOR_SCANS:
                if enemy_move.end_sq == (move.start_row + direction[0], move.start_col + direction[1]):
                    return False
            else:
                return True

    def copy(self):
        state = ChessEngine.__new__(ChessEngine)
        state.board = [[col for col in row] for row in self.board]
        state.last_move = self.last_move
        state.white_to_move = self.white_to_move
        state.w_king_square = self.w_king_square
        state.b_king_square = self.b_king_square
        state.castle_rights = {key: value for key, value in self.castle_rights.items()}
        state.in_check = self.in_check
        state.checkmate = self.checkmate
        state.stalemate = self.stalemate
        state.pawn_promotion = self.pawn_promotion
        state.current_valid_moves = self.current_valid_moves
        return state

    def reset_state(self):
        global PREVIOUS_GAME_STATES
        state = PREVIOUS_GAME_STATES.pop(0)
        PREVIOUS_GAME_STATES = []
        self.board = state.board
        self.last_move = state.last_move
        self.white_to_move = state.white_to_move
        self.w_king_square = state.w_king_square
        self.b_king_square = state.b_king_square
        self.castle_rights = state.castle_rights
        self.in_check = state.in_check
        self.checkmate = state.checkmate
        self.stalemate = state.stalemate
        self.pawn_promotion = state.pawn_promotion
        self.current_valid_moves = self.get_valid_moves()


def get_king_square(color, board):
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if board[i][j] == color + "K":
                return i, j
