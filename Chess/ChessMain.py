import pygame as p
from ChessEngine import ChessEngine, Move

p.init()
p.mixer.init()
move_sound = p.mixer.Sound("move_sound.mp3")
WIDTH, HEIGHT = 1920, 1080
BOARD_WIDTH = BOARD_HEIGHT = 1024
SQ_SIZE = 128
FPS = 60
CLOCK = p.time.Clock()
IMAGES = {}

BOARD_X = WIDTH // 2 - BOARD_WIDTH // 2
BOARD_Y = HEIGHT // 2 - BOARD_HEIGHT // 2

font = p.font.SysFont("Comic Sans MS", 50)
current_turn_text = font.render("Current Turn:", True, "white")
white_text = font.render("White", True, "white")
black_text = font.render("Black", True, "white")


class PawnPromoteSelect:
    def __init__(self):
        self.padding = 50
        self.queen_box = p.Rect(1600, self.padding + 100, 128, 128)
        self.rook_box = p.Rect(1600, self.padding * 2 + 228, 128, 128)
        self.knight_box = p.Rect(1600, self.padding * 3 + 356, 128, 128)
        self.bishop_box = p.Rect(1600, self.padding * 4 + 484, 128, 128)

    def render_images(self, screen, white_to_move):
        if white_to_move:
            current_turn = "w"
        else:
            current_turn = "b"

        for box in [self.queen_box, self.rook_box, self.knight_box, self.bishop_box]:
            p.draw.rect(screen, "blue", box, 5)
        screen.blit(IMAGES[current_turn + "Q"], self.queen_box)
        screen.blit(IMAGES[current_turn + "R"], self.rook_box)
        screen.blit(IMAGES[current_turn + "N"], self.knight_box)
        screen.blit(IMAGES[current_turn + "B"], self.bishop_box)

    def get_input(self, events):
        for event in events:
            if event.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                if self.queen_box.collidepoint(pos):
                    return "Q"
                elif self.rook_box.collidepoint(pos):
                    return "R"
                elif self.knight_box.collidepoint(pos):
                    return "N"
                elif self.bishop_box.collidepoint(pos):
                    return "B"
        return None


class GameOver:
    def __init__(self):
        self.font = font
        self.black_win = self.font.render("Black won the game!", True, "white")
        self.white_win = self.font.render("White won the game!", True, "white")
        self.stalemate = self.font.render("Stalemate", True, "white")

    def draw_text(self, screen, condition):
        if condition == "Black_Win":
            x_align = WIDTH // 2 - self.black_win.get_width() // 2
            y_align = HEIGHT // 2 - self.black_win.get_height() // 2
            p.draw.rect(screen, "black", (x_align - 30, y_align - 30, self.black_win.get_width() + 60, self.black_win.get_height() + 60))
            screen.blit(self.black_win, (x_align, y_align))

        elif condition == "White_Win":
            x_align = WIDTH // 2 - self.white_win.get_width() // 2
            y_align = HEIGHT // 2 - self.white_win.get_height() // 2
            p.draw.rect(screen, "black", (x_align - 30, y_align - 30, self.white_win.get_width() + 60, self.white_win.get_height() + 60))
            screen.blit(self.white_win, (x_align, y_align))
        elif condition == "Stalemate":
            x_align = WIDTH // 2 - self.stalemate.get_width() // 2
            y_align = HEIGHT // 2 - self.stalemate.get_height() // 2
            p.draw.rect(screen, "black", (x_align - 30, y_align - 30, self.stalemate.get_width() + 60, self.stalemate.get_height() + 60))
            screen.blit(self.stalemate, (x_align, y_align))

        p.display.flip()

    def game_loop(self, screen, gs):
        while True:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.display.quit()
                if event.type == p.MOUSEBUTTONDOWN:
                    return

            if gs.winner == "Black":
                self.draw_text(screen, "Black_Win")
            elif gs.winner == "White":
                self.draw_text(screen, "White_Win")
            else:
                self.draw_text(screen, "Stalemate")


def load_images():
    # Load images once into a dictionary for later access.
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def main():
    load_images()
    running = True
    screen = p.display.set_mode((WIDTH, HEIGHT))
    start_sq = ()
    gs = ChessEngine()
    game_over = GameOver()
    pawn_promote = PawnPromoteSelect()
    mouse_button_held_down = False
    board_flipping = True
    board_flipping_was_on = False
    clicks = 0
    while running:
        CLOCK.tick(FPS)
        events = p.event.get()

        if gs.checkmate or gs.stalemate:
            game_over.game_loop(screen, gs)
            gs = ChessEngine()  # Once game_over.game_loop() returns, restart the game.

        for e in events:
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_button_held_down = True
                end_pos_click = mouse_sq_coordinates(board_flipping, gs.white_to_move)
                if len(end_pos_click) == 2 and len(gs.current_valid_moves) > 0:
                    # Make sure were clicking on a valid piece for our turn.
                    if clicked_on_turn_piece(end_pos_click, gs) or len(start_sq) == 2:
                        if len(start_sq) == 2 and len(end_pos_click) == 2:  # Our ending click is on a valid move for the piece
                            handle_move(start_sq, end_pos_click, gs)
                            if clicked_on_turn_piece(end_pos_click, gs) and start_sq != end_pos_click:  # In case user clicked on another piece of their turn
                                start_sq = end_pos_click
                            elif end_pos_click == start_sq:
                                clicks += 1
                            else:  # If user plays on an invalid playable square.
                                start_sq = ()
                                clicks = 0
                        elif len(start_sq) == 0:  # We click on the starting piece we want to move
                            start_sq = end_pos_click
                            clicks += 1
                else:
                    start_sq = ()
                    clicks = 0

            if e.type == p.MOUSEBUTTONUP:
                mouse_button_held_down = False
                end_pos_click = mouse_sq_coordinates(board_flipping, gs.white_to_move)
                if len(start_sq) == 2 and len(end_pos_click) == 2 and end_pos_click != start_sq:
                    valid = handle_move(start_sq, end_pos_click, gs)
                    if valid:  # Make sure if the move went through we de-highlight our start_sq (Stops blue highlight from rendering into next turn)
                        start_sq = ()
                        clicks = 0  # Reset clicks for next turn.
                    else:
                        clicks = 0
                elif len(end_pos_click) == 0:  # If user drags a piece off the board or on an unplayable square. Keep the square highlighted.
                    clicks = 0
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z and len(start_sq) == 0:  # Prevent while dragging a piece
                    gs.undo_move()
                if e.key == p.K_f and len(start_sq) == 0:  # Prevent while dragging a piece
                    board_flipping = not board_flipping
                    print("Board flipping toggled.")
                if e.key == p.K_p and len(start_sq) == 0:
                    gs = ChessEngine()
                    print("Board reset.")

        # This code makes clicks feel more responsive for de-highlighting a piece that was selected again.
        # It allows us to drop a highlighted piece. But then pick it up again and drag if we want to make a move. Or let go again to de-highlight.
        if clicks == 2 and not mouse_button_held_down:
            start_sq = ()
            clicks = 0

        if gs.pawn_promote:
            if board_flipping:
                board_flipping = False  # Set board flipping to false for a second. We need to wait until user input on the piece to promote to.
                board_flipping_was_on = True
            promote_turn = gs.white_to_move  # Get the opposite turn as that's the pawn belonging to the promotion. gs always flicked the next turn.
            pawn_promote.render_images(screen, promote_turn)
            promotion = pawn_promote.get_input(events)
            if promotion:
                pawn_sq = gs.move_log[-1].end_sq
                gs.promote(pawn_sq, promotion)
                gs.pawn_promote = False
                gs.white_to_move = not gs.white_to_move
                gs.current_valid_moves = gs.get_valid_moves()
                if board_flipping_was_on:
                    board_flipping = True
                    board_flipping_was_on = False

        screen.fill((64, 64, 64))
        draw_board(screen, gs.board, start_sq, board_flipping, gs.white_to_move)
        draw_pieces(screen, gs, start_sq, board_flipping, gs.white_to_move, mouse_button_held_down)
        screen.blit(current_turn_text, p.Rect(0, 40, 30, 30))

        if gs.white_to_move:
            screen.blit(white_text, p.Rect(0, 120, 30, 30))
        else:
            screen.blit(black_text, p.Rect(0, 120, 30, 30))

        p.display.flip()

def clicked_on_turn_piece(click, gs):
    if gs.board[click[0]][click[1]][0] == "w" and gs.white_to_move:
        return True
    elif gs.board[click[0]][click[1]][0] == "b" and not gs.white_to_move:
        return True
    return False


def handle_move(start_sq, click, gs):
    move = Move(start_sq, click, gs.board)
    for valid_move in gs.current_valid_moves:
        if move.id == valid_move.id:
            move_sound.play()
            gs.do_move(valid_move)  # Feed valid_move into do_move() so we can get en_passant and castling variables.
            return True
    else:
        return False


def mouse_sq_coordinates(board_flipping, white_to_move):
    click_pos = p.mouse.get_pos()
    if BOARD_X < click_pos[0] < BOARD_X + BOARD_WIDTH:
        if BOARD_Y < click_pos[1] < BOARD_Y + BOARD_HEIGHT:  # Check if area player clicked is in the chess board
            if not board_flipping or white_to_move:
                row_clicked = (click_pos[1] - BOARD_Y) // SQ_SIZE
                col_clicked = (click_pos[0] - BOARD_X) // SQ_SIZE
                return row_clicked, col_clicked
            elif board_flipping and not white_to_move:
                row_clicked = opposite_flipped_index((click_pos[1] - BOARD_Y) // SQ_SIZE)
                col_clicked = opposite_flipped_index((click_pos[0] - BOARD_X) // SQ_SIZE)
                return row_clicked, col_clicked
        else:
            return ()
    else:
        return ()


def draw_board(screen, chess_board, start_sq, board_flipping, white_to_move):
    # When were drawing the board's squares. If the board is flipped, and we don't mirror the squares. The opposite square will draw
    # over black's highlighted red square. There's two solutions. One option is sticking more conditionals to flip the board's
    # squares to achieve the same effect but not draw over black's highlighted squares. The other option is to do another
    # nested for loop to draw all highlighted squares and forget about the problem. For now, I've done the double nested for loop option.
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            if (i + j) % 2 == 0:
                if not board_flipping or white_to_move:
                    p.draw.rect(screen, "white", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                elif board_flipping and not white_to_move:
                    p.draw.rect(screen, "white",
                                p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), (BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, "dark green", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            if len(start_sq) == 2:
                if i == start_sq[0] and j == start_sq[1] and chess_board[start_sq[0]][start_sq[1]] != "--":
                    if not board_flipping or white_to_move:
                        p.draw.rect(screen, "red",
                                    p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                    elif board_flipping and not white_to_move:
                        p.draw.rect(screen, "red",
                                    p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), (BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, gs, start_sq, board_flipping, white_to_move, mouse_button_held_down):
    # Loop through every square in the board and see what square gives us a valid spot. Pretty bad algo but will work for now
    if not board_flipping or white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                if len(start_sq) and Move(start_sq, (i, j), gs.board).id in [d.id for d in gs.current_valid_moves]:
                    if gs.board[i][j] == "--":
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 20)
                    else:
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 60, width=12)

    elif board_flipping and not white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                if len(start_sq) and Move((start_sq[0], start_sq[1]), (i, j), gs.board).id in [d.id for d in gs.current_valid_moves]:
                    if gs.board[i][j] == "--":
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), 20)
                    else:
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), 60, width=12)

    # Render pieces on the board
    if not board_flipping or white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                piece = gs.board[i][j]
                if len(start_sq) == 2 and i == start_sq[0] and j == start_sq[1] and mouse_button_held_down:
                    pass
                else:
                    if piece != "--":
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))
    elif board_flipping and not white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                piece = gs.board[i][j]
                if len(start_sq) == 2 and i == start_sq[0] and j == start_sq[1] and mouse_button_held_down:
                    pass
                else:
                    if piece != "--":
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE), SQ_SIZE, SQ_SIZE))

    # Blue highlight
    if len(start_sq) == 2:
        square_highlight_pos = mouse_sq_coordinates(board_flipping, gs.white_to_move)
        # We do this so if the player lets go of a piece and moves their mouse outside the board's space.
        # The blue square highlight returns to the pieces spot. The code directly below makes sure that if the piece
        # is dragged off board, the blue square highlights way off the screen.
        if len(square_highlight_pos) == 0 and mouse_button_held_down:
            square_highlight_pos = (1000, 1000)  # Make the blue highlight off-screen
        if not board_flipping or white_to_move:
            p.draw.rect(screen, "blue",
                        p.Rect(BOARD_X + (square_highlight_pos[1] if mouse_button_held_down else start_sq[1]) * SQ_SIZE,
                               BOARD_Y + (square_highlight_pos[0] if mouse_button_held_down else start_sq[0]) * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6)  # Invert row and columns to get actual screen representation of highlight position.
        elif board_flipping and not white_to_move:
            p.draw.rect(screen, "blue", p.Rect(BOARD_X + (opposite_flipped_index(square_highlight_pos[1]) if mouse_button_held_down else opposite_flipped_index(start_sq[1])) * SQ_SIZE,
                                               BOARD_Y + (opposite_flipped_index(square_highlight_pos[0]) if mouse_button_held_down else opposite_flipped_index(start_sq[0])) * SQ_SIZE,
                                               SQ_SIZE, SQ_SIZE), 6)
    # Drag piece render
    if start_sq and mouse_button_held_down:
        mouse_pos = p.mouse.get_pos()
        piece = gs.board[start_sq[0]][start_sq[1]]
        if piece != "--":
            screen.blit(IMAGES[piece], p.Rect(mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))


def render_all_moves(screen, gs):
    """
    Not in use currently"""
    # Renders all possible moves at the current game state
    for move in gs.current_valid_moves:
        p.draw.circle(screen, "dark gray",
                      (SQ_SIZE // 2 + BOARD_X + (move.end_col * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (move.end_row * SQ_SIZE)), 20)


def opposite_flipped_index(index):
    # 8 is the length of our board
    return 8 - index - 1


if __name__ == "__main__":
    main()
