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
        self.move_log = []
        self.piece_moves_func = {"P": self.get_pawn_moves, "R": self.get_rook_moves,
                                 "K": self.get_king_moves, "N": self.get_knight_moves,
                                 "Q": self.get_queen_moves, "B": self.get_bishop_moves}
        self.current_valid_moves = self.get_valid_moves()

    """
    Takes a Move as a parameter and executes it (will not work for castling, pawn promotion, and en-passant"""
    def do_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        self.current_valid_moves = self.get_valid_moves()

    """
    Undo the last move made"""
    def undo_move(self):
        if len(self.move_log):
            last_move = self.move_log.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.white_to_move = not self.white_to_move
            self.current_valid_moves = self.get_valid_moves()

    """
    Promotes a pawn to the piece chosen"""
    def promote(self, pawn_sq, piece_wanted):
        turn = self.board[pawn_sq[0]][pawn_sq[1]][0]
        self.board[pawn_sq[0]][pawn_sq[1]] = turn + piece_wanted
        print("Piece promoted!")

    """
    Will determine all valid moves considering king check"""
    def get_valid_moves(self):
        # Function will simulate every single move returned from possible moves.
        # We will then get all moves from the next turn.
        # If any piece from the enemy puts the king in check. Filter out the move.
        moves = self.get_all_possible_moves(self.board, self.white_to_move)
        valid_moves = []
        if self.white_to_move:
            our_turn = "w"
        else:
            our_turn = "b"
        for move in moves:
            board = copy.deepcopy(self.board)
            board[move.start_row][move.start_col] = "--"
            board[move.end_row][move.end_col] = move.piece_moved
            current_king_sq = ()
            for i, row in enumerate(board):
                for j, col in enumerate(row):
                    if board[i][j] == our_turn + "K":
                        current_king_sq = (i, j)
            enemy_moves_next_turn = self.get_all_possible_moves(board, not self.white_to_move)
            for enemy_move in enemy_moves_next_turn:
                if enemy_move.end_row == current_king_sq[0] and enemy_move.end_col == current_king_sq[1]:
                    break
            else:
                valid_moves.append(move)
        return valid_moves  # Temporary. Will check and remove moves that put the king in check later.

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
        else:
            if r == 1 and board[r + 2][c] == "--":
                moves.append(Move((r, c), (r + 2, c), board))
            if r + 1 < len(board) and board[r + 1][c] == "--":  # Go down the column from whites perspective
                moves.append(Move((r, c), (r + 1, c), board))
            if (r + 1 < len(board) and 0 <= c - 1) and board[r + 1][c - 1] != "--" and board[r + 1][c - 1][0] == "w":
                moves.append(Move((r, c),(r + 1, c - 1), board))
            if (r + 1 < len(board) and c + 1 < len(board)) and board[r + 1][c + 1] != "--" and board[r + 1][c + 1][0] == "w":
                moves.append(Move((r, c), (r + 1, c + 1), board))
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

    def __init__(self, start_sq, end_sq, board):
        self.start_sq = start_sq
        self.end_sq = end_sq
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.id = str(self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col)

    def __eq__(self, other):
        if self.id == other.id:
            return True

    def get_chess_notation(self):
        return Move.col_to_file[self.start_col] + Move.row_to_rank[self.start_row] + Move.col_to_file[self.end_col] + Move.row_to_rank[self.end_row]
