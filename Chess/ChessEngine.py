import copy


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
        self.king_side_vector_scans = [(0, 1), (0, 2)]
        self.queen_side_vector_scans = [(0, -1), (0, -2), (0, -3)]
        self.move_log = []
        self.piece_moves_func = {"P": self.get_pawn_moves, "R": self.get_rook_moves,
                                 "K": self.get_king_moves, "N": self.get_knight_moves,
                                 "Q": self.get_queen_moves, "B": self.get_bishop_moves}
        self.check_mate = False
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
        if move.piece_moved[1] == "P" and move.end_row == 0 and self.white_to_move:  # White pawn promote
            self.pawn_promote = True
            return
        elif move.piece_moved[1] == "P" and move.end_row == 7 and not self.white_to_move:  # Black pawn promote
            self.pawn_promote = True
            return

        self.white_to_move = not self.white_to_move
        self.current_valid_moves = self.get_valid_moves()
        if len(self.current_valid_moves) == 0:  # When a pawn promotes test to make sure check works properly and doesn't break
            self.check_mate = True


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

            self.current_valid_moves = self.get_valid_moves()

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
            for vector in self.king_side_vector_scans:
                if enemy_move.end_sq == (move.start_row + vector[0], move.start_col + vector[1]):
                    return False
            else:
                return True
        elif move.end_col - move.start_col == -2:  # Queen side
            for vector in self.queen_side_vector_scans:
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

        def get_king_square(turn, board):
            for i, row in enumerate(board):
                for j, col in enumerate(row):
                    if board[i][j] == turn + "K":
                        return i, j

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
        for enemy_move in self.get_all_possible_moves(self.board, not self.white_to_move):
            if enemy_move.end_sq == current_king_sq:
                currently_in_check = True
                break
        else:
            currently_in_check = False

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
                    piece = board[i][j][1]
                    moves.extend(self.piece_moves_func[piece](i, j, board))
        return moves

    """
    Returns all moves for the pawn piece in the row and column. Will search for diagonal captures and vertical movement."""
    def get_pawn_moves(self, r, c, board):
        moves = []
        turn = board[r][c][0]

        def en_passant_check(turn, move_log):
            if len(move_log) == 0:
                return

            if turn == "w":
                if move_log[-1].end_row == 3 and move_log[-1].start_row == 1:
                    return True
                else:
                    return False
            else:
                if move_log[-1].end_row == 4 and move_log[-1].start_row == 6:
                    return True
                else:
                    return False

        # Search for every column above the pawn. If nothing is blocking then it's a valid move.
        if turn == "w":  # Go up the column from whites perspective
            if r == 6 and board[r - 2][c] == "--":
                moves.append(Move((r, c), (r - 2, c), board))
            if 0 <= r - 1 and board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), board))
            if (0 <= r - 1 and 0 <= c - 1) and board[r - 1][c - 1][0] == "b":
                moves.append(Move((r, c),(r - 1, c - 1), board))
            if (0 <= r - 1 and c + 1 < len(board)) and board[r - 1][c + 1][0] == "b":
                moves.append(Move((r, c), (r - 1, c + 1), board))
            # En passant
            if 0 <= c - 1 and board[r][c - 1] == "bP":
                if en_passant_check("w", self.move_log):
                    moves.append(Move((r, c), (r - 1, c - 1), board, en_passant=(r, c - 1)))
            if c + 1 < len(board) and board[r][c + 1] == "bP":
                if en_passant_check("w", self.move_log):
                    moves.append(Move((r, c), (r - 1, c + 1), board, en_passant=(r, c + 1)))

        else:
            if r == 1 and board[r + 2][c] == "--":
                moves.append(Move((r, c), (r + 2, c), board))
            if r + 1 < len(board) and board[r + 1][c] == "--":  # Go down the column from whites perspective
                moves.append(Move((r, c), (r + 1, c), board))
            if (r + 1 < len(board) and 0 <= c - 1) and board[r + 1][c - 1] != "--" and board[r + 1][c - 1][0] == "w":
                moves.append(Move((r, c),(r + 1, c - 1), board))
            if (r + 1 < len(board) and c + 1 < len(board)) and board[r + 1][c + 1] != "--" and board[r + 1][c + 1][0] == "w":
                moves.append(Move((r, c), (r + 1, c + 1), board))
            # En passant
            if 0 <= c - 1 and board[r][c - 1] == "wP":
                if en_passant_check("b", self.move_log):
                    moves.append(Move((r, c), (r + 1, c - 1), board, en_passant=(r, c - 1)))
            if c + 1 < len(board) and board[r][c + 1] == "wP":
                if en_passant_check("b", self.move_log):
                    moves.append(Move((r, c), (r + 1, c + 1), board, en_passant=(r, c + 1)))
        return moves

    """
    Returns all possible moves for the rook. Will search vertically and horizontally."""
    def get_rook_moves(self, r, c, board):
        moves = []
        moves.extend(self.horizontal_scan(r, c, board))
        moves.extend(self.horizontal_scan(r, c, board, reverse=True))
        return moves

    def get_king_moves(self, r, c, board):
        moves = []
        vectors = [(-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, -1), (1, 1)]
        for direction in vectors:
            dx = c + direction[1]
            dy = r + direction[0]
            if 0 <= dx < len(board) and 0 <= dy < len(board):
                sq_occupy = self.check_if_square_has_enemy_piece((r, c), (dy, dx), board)
                if sq_occupy == "EMPTY" or sq_occupy == "ENEMY":
                    moves.append(Move((r, c), (dy, dx), board))
                else:
                    pass

        # Castling
        # TODO: When doing future moves. Castling needs to be taken into account, seeing the ending position of the enemy king/enemy rooks
        if self.white_to_move:
            if self.castling["W_King_Side"]:
                for vector in self.king_side_vector_scans:
                    if c + vector[1] < len(board):
                        if board[r + vector[0]][c + vector[1]] != "--":
                            break
                    else:
                        break
                else:
                    moves.append(Move((r, c), (r, c + 2), board, castle=[(r, 7), (r, 5)]))
            if self.castling["W_Queen_Side"]:
                for vector in self.queen_side_vector_scans:
                    if board[r + vector[0]][c + vector[1]] != "--":
                        break
                else:
                    moves.append(Move((r, c), (r, c - 2), board, castle=[(r, 0), (r, 3)]))
        else:
            if self.castling["B_King_Side"]:
                for vector in self.king_side_vector_scans:
                    if c + vector[1] < len(board):
                        if board[r + vector[0]][c + vector[1]] != "--":
                            break
                    else:
                        break
                else:
                    moves.append(Move((r, c), (r, c + 2), board, castle=[(r, 7), (r, 5)]))
            if self.castling["B_Queen_Side"]:
                for vector in self.queen_side_vector_scans:
                    if board[r + vector[0]][c + vector[1]] != "--":
                        break
                else:
                    moves.append(Move((r, c), (r, c - 2), board, castle=[(r, 0), (r, 3)]))

        return moves

    def get_queen_moves(self, r, c, board):
        moves = []
        moves.extend(self.diagonal_scan(r, c, board))
        moves.extend(self.horizontal_scan(r, c, board))
        moves.extend(self.horizontal_scan(r, c, board, reverse=True))
        return moves

    def get_knight_moves(self, r, c, board):
        moves = []

        def column_knight_check(current_r, comparing_r, r_abs_dist, c, board):
            _moves = []
            if c + 1 < len(board):
                if c + 2 < len(board):
                    if self.check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 2), board) != "FRIENDLY" and r_abs_dist == 1:
                        _moves.append(Move((current_r, c), (comparing_r, c + 2), board))
                if self.check_if_square_has_enemy_piece((current_r, c), (comparing_r, c + 1), board) != "FRIENDLY" and r_abs_dist == 2:
                    _moves.append(Move((current_r, c), (comparing_r, c + 1), board))

            if c - 1 >= 0:
                if c - 2 >= 0:
                    if self.check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 2), board) != "FRIENDLY" and r_abs_dist == 1:
                        _moves.append(Move((current_r, c), (comparing_r, c - 2), board))
                if self.check_if_square_has_enemy_piece((current_r, c), (comparing_r, c - 1), board) != "FRIENDLY" and r_abs_dist == 2:
                    _moves.append(Move((current_r, c), (comparing_r, c - 1), board))
            return _moves

        if r - 1 >= 0:
            if r - 2 >= 0:
                moves.extend(column_knight_check(r, r - 2, 2, c, board))
            moves.extend(column_knight_check(r, r - 1, 1, c, board))
        if r + 1 < len(board):
            if r + 2 < len(board):
                moves.extend(column_knight_check(r, r + 2, 2, c, board))
            moves.extend(column_knight_check(r, r + 1, 1, c, board))
        return moves


    def get_bishop_moves(self, r, c, board):
        return self.diagonal_scan(r, c, board)

    def diagonal_scan(self, r, c, board):
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

    def horizontal_scan(self, r, c, board, reverse=False):
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


    def check_if_square_has_enemy_piece(self, start_sq, end_sq, board):
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
        if castle is not None:
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
