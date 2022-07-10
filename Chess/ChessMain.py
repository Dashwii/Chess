import pygame as p
from ChessEngine import ChessEngine, Move, copy

"""
New branch Optimization_and_Refactors

Trying to clean up code on this branch before I implement AI/add other minor features. (That'll probably be the last thing I add)

Things I wanted refactored:
    - Rewrite main() into a class. Will make function arguments cleaner/make communication between pawn promotion and game over states cleaner.
    - Simplify animations. They work well. Just don't like the amount of arguments being passed around and conditionals to prevent issues like flicking in pawn promotion state. 
    - Reverse animations for previous moves. 
    - Add chess notation for moves made on side.
    - Allow resizing to I can test and play the game on my laptop. 
    - Add move timer info on side.
"""

p.init()
p.mixer.init()
move_sound = p.mixer.Sound("move_sound.mp3")
WIDTH, HEIGHT = 1920, 1080
BOARD_WIDTH = BOARD_HEIGHT = 1024
SQ_SIZE = 128
FPS = 60
CLOCK = p.time.Clock()
IMAGES = {}
SCREEN = p.display.set_mode((WIDTH, HEIGHT))


alpha_sq_surface = p.Surface((SQ_SIZE, SQ_SIZE))
alpha_sq_surface.set_alpha(150)
alpha_sq_surface.fill("yellow")


class Game:
    def __init__(self):
        self.program_running = True
        self.game_over = False
        self.screen = SCREEN
        self.click_start_sq = ()
        self.game_state = ChessEngine()
        self.mouse_button_held_down = False
        self.board_flipping_on = True
        self.toggle_board_flipping_back_on = False
        self.player_clicks = []

    def game_loop(self):
        while self.program_running:
            CLOCK.tick(FPS)
            events = p.event.get()
            self.handle_events(events)

            if self.player_clicks == 2 and not self.mouse_button_held_down:
                self.click_start_sq = ()
                self.player_clicks = 0

            self.rendering()

    def rendering(self):
        self.screen.fill((64, 64, 64))
        self.draw_board()
        self.draw_pieces()
        p.display.flip()


    def draw_board(self):
        # When were drawing the board's squares. If the board is flipped, and we don't mirror the squares. The opposite square will draw
        # over black's highlighted red square. There's two solutions. One option is sticking more conditionals to flip the board's
        # squares to achieve the same effect but not draw over black's highlighted squares. The other option is to do another
        # nested for loop to draw all highlighted squares and forget about the problem. For now, I've done the double nested for loop option.
        for i, r in enumerate(self.game_state.board):
            for j, c in enumerate(r):
                if (i + j) % 2 == 0:
                    if not self.board_flipping_on or self.game_state.white_to_move:
                        p.draw.rect(self.screen, "white", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                    elif self.board_flipping_on and not self.game_state.white_to_move:
                        p.draw.rect(self.screen, "white", p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), (BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                else:
                    p.draw.rect(self.screen, "dark green", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))

        # TODO: MAKE FLIP LOGIC OCCUR IN ONE FUNCTION. FUNCTION WILL CONSTANTLY CHECK IF BOARD IS FLIPPED AND INVERT ALL NECESSARY VARIABLES
        # Player click_start_sq highlight
        if len(self.click_start_sq) == 2:
            # click_start_sq rendering
            row = self.click_start_sq[0]
            col = self.click_start_sq[1]
            if not self.board_flipping_on or self.game_state.white_to_move:
                p.draw.rect(self.screen, "red", p.Rect(BOARD_X + (col * SQ_SIZE), BOARD_Y + (row * SQ_SIZE), SQ_SIZE, SQ_SIZE))
            elif self.board_flipping_on or not self.game_state:  # <---- Try reducing to just "else"
                p.draw.rect(self.screen, "red", p.Rect(BOARD_X + (opposite_flipped_index(col) * SQ_SIZE), BOARD_Y + (opposite_flipped_index(row) * SQ_SIZE), SQ_SIZE, SQ_SIZE))
            # Last move rendering
            if len(self.game_state.move_log) > 0:
                if not self.board_flipping_on or self.game_state.white_to_move:
                    # Start sq render
                    self.screen.blit(alpha_sq_surface, (BOARD_X + (self.game_state.move_log[-1].start_sq * SQ_SIZE), BOARD_Y + (self.game_state.move_log[-1].start_sq * SQ_SIZE)))

                    # End sq render
                    self.screen.blit(alpha_sq_surface, (BOARD_X + (self.game_state.move_log[-1].end_sq * SQ_SIZE), BOARD_Y + (self.game_state.move_log[-1].end_sq * SQ_SIZE)))
                elif self.board_flipping_on and not self.game_state.white_to_move:
                    # Start sq render
                    self.screen.blit(alpha_sq_surface, (BOARD_X + (opposite_flipped_index(self.game_state.move_log[-1].start_sq) * SQ_SIZE),
                                                        BOARD_Y + (opposite_flipped_index(self.game_state.move_log[-1].start_sq) * SQ_SIZE)))

                    # End sq render
                    self.screen.blit(alpha_sq_surface, (BOARD_X + (opposite_flipped_index(self.game_state.move_log[-1].end_sq) * SQ_SIZE),
                                                        BOARD_Y + (opposite_flipped_index(self.game_state.move_log[-1].end_sq) * SQ_SIZE)))

        # Blue square mouse dragging highlight
        if len(self.click_start_sq) == 2:
            square_highlight_pos = mouse_sq_coordinates(self.board_flipping_on, self.game_state.white_to_move)
            # We do this so if the player lets go of a piece and moves their mouse outside the board's space.
            # The blue square highlight returns to the pieces spot. The code directly below makes sure that if the piece
            # is dragged off board, the blue square highlights way off the screen.
            if len(square_highlight_pos) == 0 and self.mouse_button_held_down:
                square_highlight_pos = (1000, 1000)  # Make the blue highlight off-screen
            if not self.board_flipping_on or self.game_state.white_to_move:
                p.draw.rect(self.screen, "blue", p.Rect(BOARD_X + (square_highlight_pos[1] if self.mouse_button_held_down else self.click_start_sq[1]) * SQ_SIZE,
                            BOARD_Y + (square_highlight_pos[0] if self.mouse_button_held_down else self.click_start_sq[0]) * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6)
            else:
                p.draw.rect(self.screen, "blue", p.Rect(BOARD_X + (opposite_flipped_index(square_highlight_pos[1]) if self.mouse_button_held_down else opposite_flipped_index(self.click_start_sq[1])) * SQ_SIZE,
                            BOARD_Y + (opposite_flipped_index(square_highlight_pos[0]) if self.mouse_button_held_down else opposite_flipped_index(self.click_start_sq[0])) * SQ_SIZE,
                            SQ_SIZE, SQ_SIZE), 6)


    def draw_pieces(self):
        """
        Loop through a list of all saved positions of pieces on the board and render those pieces.
        If the piece's square is currently highlighted. We will also render the squares that piece attacks.
        :return:
        """
        saved_positions_of_all_pieces = [] # <-- Fake list. This will be implemented into game_state later
        # Render pieces
        for piece in saved_positions_of_all_pieces:
            _piece = piece[0]
            square = piece[1]
            squares_attacked = piece[2]
            if not self.board_flipping_on or self.game_state.white_to_move:
                if not (square == self.click_start_sq and self.mouse_button_held_down):  # Only render if the player hasn't selected this square and is holding their mouse button down.
                    self.screen.blit(IMAGES[_piece], p.Rect((BOARD_X + (square[1] * SQ_SIZE)), BOARD_Y + (square[0] * SQ_SIZE)))
                if square == self.click_start_sq:
                    for square_attacked in squares_attacked:
                        if self.game_state.board[square_attacked[0]][square_attacked[1]] == "--":
                            p.draw.circle(self.screen, "dark gray",
                                          (SQ_SIZE // 2 + BOARD_X + (square_attacked[1] * SQ_SIZE),
                                           SQ_SIZE // 2 + BOARD_Y + (square_attacked[0] * SQ_SIZE)), 20)
                        else:
                            p.draw.circle(self.screen, "dark gray",
                                          (SQ_SIZE // 2 + BOARD_X + (square_attacked[1] * SQ_SIZE),
                                           SQ_SIZE // 2 + BOARD_Y + (square_attacked[0] * SQ_SIZE)), 20)

            else:
                if not (square == self.click_start_sq and self.mouse_button_held_down):  # Only render if the player hasn't selected this square and is holding their mouse button down.
                    self.screen.blit(IMAGES[_piece], p.Rect((BOARD_X + (opposite_flipped_index(square[1]) * SQ_SIZE)), BOARD_Y + (opposite_flipped_index(square[0]) * SQ_SIZE)))
                if square == self.click_start_sq:
                    for square_attacked in squares_attacked:
                        if self.game_state.board[square_attacked[0]][square_attacked[1]] == "--":
                            p.draw.circle(self.screen, "dark gray",
                                          (SQ_SIZE // 2 + BOARD_X + (opposite_flipped_index(square_attacked[1]) * SQ_SIZE),
                                           SQ_SIZE // 2 + BOARD_Y + (opposite_flipped_index(square_attacked[0]) * SQ_SIZE)), 20)
                        else:
                            p.draw.circle(self.screen, "dark gray",
                                          (SQ_SIZE // 2 + BOARD_X + (opposite_flipped_index(square_attacked[1]) * SQ_SIZE),
                                           SQ_SIZE // 2 + BOARD_Y + (opposite_flipped_index(square_attacked[0]) * SQ_SIZE)), 20)

        # Render dragging
        if self.click_start_sq and self.mouse_button_held_down:
            mouse_pos = p.mouse.get_pos()
            drag_piece = self.game_state.board[self.click_start_sq[0]][self.click_start_sq[1]]
            self.screen.blit(IMAGES[drag_piece], p.Rect(mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))



    def handle_events(self, events):
        for e in events:
            if e.type == p.QUIT:
                self.game_over = False
                self.program_running = False
                p.display.quit()
            if e.type == p.MOUSEBUTTONDOWN:
                if not self.game_over:  # May stick "not gs.pawn_promote" here too
                    self.handle_player_click_mouse_button_down()
            if e.type == p.MOUSEBUTTONUP:
                if not self.game_over:
                    self.handle_player_click_mouse_button_up()
            if e.type == p.KEYDOWN:
                if e.key == p.K_z and len(self.click_start_sq) == 0:
                    self.game_state.undo_move()
                if e.key == p.K_f and len(self.click_start_sq) == 0:
                    # Think we can allow board flipping even if a piece is selected. Just flip self.click_start_sq's coordinates
                    if self.board_flipping_on:
                        print("Board flipping toggled off.")
                    else:
                        print("Board flipping toggled on.")
                    self.board_flipping_on = not self.board_flipping_on
                if e.key == p.K_p:
                    # Will have a cleanup function here. To reset all variables that need to be reset.
                    self.game_state = ChessEngine()

    def handle_player_click_mouse_button_down(self):
        """
        Rewrite of old click logic. Gonna test more later
        :return: None
        """
        self.mouse_button_held_down = True
        position_clicked = mouse_sq_coordinates(self.board_flipping_on, self.game_state.white_to_move)
        if len(position_clicked) == 2:
            # Make sure we are clicking on a valid piece for our turn or were clicking on a square we want to move to.
            if len(self.click_start_sq) == 2 and len(position_clicked) == 2:
                self.handle_move()
                if clicked_on_turn_piece(position_clicked, self.game_state) and self.click_start_sq != position_clicked:
                    self.click_start_sq = position_clicked
                elif position_clicked == self.click_start_sq:
                    self.player_clicks += 1
                else:
                    self.click_start_sq = ()
                    self.player_clicks = 0
            else:
                self.click_start_sq = position_clicked

    def handle_player_click_mouse_button_up(self):
        pass

    def handle_move(self):
        pass




BOARD_X = WIDTH // 2 - BOARD_WIDTH // 2
BOARD_Y = HEIGHT // 2 - BOARD_HEIGHT // 2

font = p.font.SysFont("Comic Sans MS", 50)
current_turn_text = font.render("Current Turn:", True, "white")
white_text = font.render("White", True, "white")
black_text = font.render("Black", True, "white")

def load_images():
    # Load images once into a dictionary for later access.
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


class PawnPromoteSelect:
    def __init__(self):
        self.padding = 50
        self.queen_box = p.Rect(1600, self.padding + 100, 128, 128)
        self.rook_box = p.Rect(1600, self.padding * 2 + 228, 128, 128)
        self.knight_box = p.Rect(1600, self.padding * 3 + 356, 128, 128)
        self.bishop_box = p.Rect(1600, self.padding * 4 + 484, 128, 128)
        self.selected_promotion = None

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

    def game_loop(self, screen, white_to_move, events):
        for event in events:
            if event.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                if self.queen_box.collidepoint(pos):
                    self.selected_promotion = "Q"
                elif self.rook_box.collidepoint(pos):
                    self.selected_promotion = "R"
                elif self.knight_box.collidepoint(pos):
                    self.selected_promotion = "N"
                elif self.bishop_box.collidepoint(pos):
                    self.selected_promotion = "B"
        self.render_images(screen, white_to_move)
        return None


class GameOver:
    def __init__(self):
        self.font = font
        self.black_win = self.font.render("Black won the game!", True, "white")
        self.white_win = self.font.render("White won the game!", True, "white")
        self.stalemate = self.font.render("Stalemate", True, "white")
        self.restart = False
        self.mouse_down_event_count = 0

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

    def game_loop(self, screen, gs, events):
        for event in events:
            if event.type == p.QUIT:
                p.display.quit()
            if event.type == p.MOUSEBUTTONDOWN:
                self.mouse_down_event_count += 1
                if self.mouse_down_event_count == 2:
                    self.mouse_down_event_count = 0
                    self.restart = True
        if gs.winner == "Black":
            self.draw_text(screen, "Black_Win")
        elif gs.winner == "White":
            self.draw_text(screen, "White_Win")
        else:
            self.draw_text(screen, "Stalemate")





def main():
    load_images()
    running = True
    screen = p.display.set_mode((WIDTH, HEIGHT))
    start_sq = ()
    gs = ChessEngine()
    game_over = GameOver()
    pawn_promote = PawnPromoteSelect()
    animations = AnimationHandler()
    mouse_button_held_down = False
    board_flipping = True
    board_flipping_was_on = False
    clicks = 0
    while running:
        CLOCK.tick(FPS)
        events = p.event.get()
        for e in events:
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_button_held_down = True
                end_pos_click = mouse_sq_coordinates(board_flipping, gs.white_to_move)
                if len(end_pos_click) == 2 and len(gs.current_valid_moves) > 0 and not gs.pawn_promote:
                    # Make sure were clicking on a valid piece for our turn.
                    if clicked_on_turn_piece(end_pos_click, gs) or len(start_sq) == 2:
                        if len(start_sq) == 2 and len(end_pos_click) == 2:  # Our ending click is on a valid move for the piece
                            handle_move(start_sq, end_pos_click, gs, animations)
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
                    valid = handle_move(start_sq, end_pos_click, gs, None)
                    if valid:  # Make sure if the move went through we de-highlight our start_sq (Stops blue highlight from rendering into next turn)
                        start_sq = ()
                        clicks = 0  # Reset clicks for next turn.
                    else:
                        clicks = 0
                elif len(end_pos_click) == 0:  # If user drags a piece off the board or on an unplayable square. Keep the square highlighted.
                    clicks = 0
            if e.type == p.KEYDOWN:
                if e.key == p.K_z and len(start_sq) == 0 and not gs.pawn_promote:  # Prevent while dragging a piece and while promoting a piece
                    gs.undo_move()
                if e.key == p.K_f and len(start_sq) == 0 and not gs.pawn_promote:  # Prevent while dragging a piece and while promoting a piece
                    if board_flipping:
                        print("Board flipping off.")
                    else:
                        print("Board flipping on.")
                    board_flipping = not board_flipping
                if e.key == p.K_p and len(start_sq) == 0 and not gs.pawn_promote:
                    gs = ChessEngine()
                    print("Board reset.")

        # This code makes clicks feel more responsive for de-highlighting a piece that was selected again.
        # It allows us to drop a highlighted piece. But then pick it up again and drag if we want to make a move. Or let go again to de-highlight.
        if clicks == 2 and not mouse_button_held_down:
            start_sq = ()
            clicks = 0

        screen.fill((64, 64, 64))

        draw_board(screen, gs, start_sq, board_flipping, gs.white_to_move, gs.move_log)
        draw_pieces(screen, gs, start_sq, board_flipping, gs.white_to_move, mouse_button_held_down, animations)
        screen.blit(current_turn_text, p.Rect(0, 40, 30, 30))

        animations.update_animations(screen, board_flipping, gs.white_to_move)

        # Draw current turn
        if gs.white_to_move:
            screen.blit(white_text, p.Rect(0, 120, 30, 30))
        else:
            screen.blit(black_text, p.Rect(0, 120, 30, 30))

        if gs.pawn_promote:
            pawn_promote.game_loop(screen, gs.white_to_move, events)
            if pawn_promote.selected_promotion:
                gs.promote(gs.move_log[-1].end_sq, pawn_promote.selected_promotion)
                pawn_promote.selected_promotion = None
                gs.next_turn_work()
                if board_flipping_was_on:
                    board_flipping = True
                    board_flipping_was_on = False

        if gs.checkmate or gs.stalemate:
            game_over.game_loop(screen, gs, events)
            if game_over.restart:
                gs = ChessEngine()  # Once game_over.game_loop() returns, restart the game.
                game_over.restart = False

        p.display.flip()


def clicked_on_turn_piece(click, gs):
    if gs.board[click[0]][click[1]][0] == "w" and gs.white_to_move:
        return True
    elif gs.board[click[0]][click[1]][0] == "b" and not gs.white_to_move:
        return True
    return False


def handle_move(start_sq, click, gs, animations):
    move = Move(start_sq, click, gs.board)
    for valid_move in gs.current_valid_moves:
        if move.id == valid_move.id:
            if animations is not None:
                animations.add_animation(move)
            else:
                move_sound.play()  # move_sound.play() now here for when a piece is dragged and placed instead of an animation.
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


def draw_board(screen, gs, start_sq, board_flipping, white_to_move, move_log):
    # When were drawing the board's squares. If the board is flipped, and we don't mirror the squares. The opposite square will draw
    # over black's highlighted red square. There's two solutions. One option is sticking more conditionals to flip the board's
    # squares to achieve the same effect but not draw over black's highlighted squares. The other option is to do another
    # nested for loop to draw all highlighted squares and forget about the problem. For now, I've done the double nested for loop option.
    for i, r in enumerate(gs.board):
        for j, c in enumerate(r):
            if (i + j) % 2 == 0:
                if not board_flipping or white_to_move:
                    p.draw.rect(screen, "white", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                elif board_flipping and not white_to_move:
                    p.draw.rect(screen, "white",
                                p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), (BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, "dark green", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))

    # Last move squares. Get a transparent surface for us to render
    alpha_sq_surface = p.Surface((SQ_SIZE, SQ_SIZE))
    alpha_sq_surface.set_alpha(150)
    alpha_sq_surface.fill("yellow")

    # Square highlighting
    for i, r in enumerate(gs.board):
        for j, c in enumerate(r):
            # Start square highlighting
            if len(start_sq) == 2:
                if i == start_sq[0] and j == start_sq[1] and gs.board[start_sq[0]][start_sq[1]] != "--" and not gs.pawn_promote:  # Prevents final move highlighting in pawn promotion state from appearing as orange.
                    if not board_flipping or white_to_move:                                                                       # Stops red highlight from quickly flickering in pawn_promote state if we keep the conditional here as well.
                        p.draw.rect(screen, "red",
                                    p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                    elif board_flipping and not white_to_move:
                        p.draw.rect(screen, "red",
                                    p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), (BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            # Last move highlighting
            if len(move_log) > 0:
                if not board_flipping or white_to_move:
                    if (i, j) == move_log[-1].start_sq:
                        screen.blit(alpha_sq_surface, (BOARD_X + j * SQ_SIZE, BOARD_Y + i * SQ_SIZE))
                    elif (i, j) == move_log[-1].end_sq:
                        screen.blit(alpha_sq_surface, (BOARD_X + j * SQ_SIZE, BOARD_Y + i * SQ_SIZE))
                elif board_flipping and not white_to_move:
                    if (i, j) == move_log[-1].start_sq:
                        screen.blit(alpha_sq_surface, (BOARD_X + opposite_flipped_index(j) * SQ_SIZE,
                                                       BOARD_Y + opposite_flipped_index(i) * SQ_SIZE))
                    elif (i, j) == move_log[-1].end_sq:
                        screen.blit(alpha_sq_surface, (BOARD_X + opposite_flipped_index(j) * SQ_SIZE,
                                                       BOARD_Y + opposite_flipped_index(i) * SQ_SIZE))


def draw_pieces(screen, gs, start_sq, board_flipping, white_to_move, mouse_button_held_down, animations):
    # gs.pawn_promote is plugged into some conditionals to prevent flicking issues with pieces and square highlighting when entering the pawn promotion state.

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
                sq_animation_response = animations.is_sq_in_end_sq_animation((i, j))
                if len(start_sq) == 2 and i == start_sq[0] and j == start_sq[1] and mouse_button_held_down and not gs.pawn_promote: # Don't render piece if it's supposed to be being dragged.
                    pass
                elif sq_animation_response:  # Keep enemy pieces in a capture animation rendered until the animation completes.
                    if sq_animation_response != "--":
                        screen.blit(IMAGES[sq_animation_response], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))
                else:
                    if piece != "--":  # Render piece on board normally
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))
    elif board_flipping and not white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                piece = gs.board[i][j]
                sq_animation_response = animations.is_sq_in_end_sq_animation((i, j))
                if len(start_sq) == 2 and i == start_sq[0] and j == start_sq[1] and mouse_button_held_down and not gs.pawn_promote:  # Don't render piece if it's supposed to be being dragged.
                    pass
                elif sq_animation_response:  # Keep enemy pieces in a capture animation rendered until the animation completes.
                    if sq_animation_response != "--":
                        screen.blit(IMAGES[sq_animation_response], p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE), SQ_SIZE, SQ_SIZE))
                else:
                    if piece != "--":  # Render piece on board normally
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (opposite_flipped_index(j) * SQ_SIZE), BOARD_Y + (opposite_flipped_index(i) * SQ_SIZE), SQ_SIZE, SQ_SIZE))

    # Blue highlight
    if len(start_sq) == 2:
        square_highlight_pos = mouse_sq_coordinates(board_flipping, gs.white_to_move)
        # We do this so if the player lets go of a piece and moves their mouse outside the board's space.
        # The blue square highlight returns to the pieces spot. The code directly below makes sure that if the piece
        # is dragged off board, the blue square highlights way off the screen.
        if len(square_highlight_pos) == 0 and mouse_button_held_down:
            square_highlight_pos = (1000, 1000)  # Make the blue highlight off-screen
        if not board_flipping or white_to_move and not gs.pawn_promote:
            p.draw.rect(screen, "blue",
                        p.Rect(BOARD_X + (square_highlight_pos[1] if mouse_button_held_down else start_sq[1]) * SQ_SIZE,
                               BOARD_Y + (square_highlight_pos[0] if mouse_button_held_down else start_sq[0]) * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6)  # Invert row and columns to get actual screen representation of highlight position.
        elif board_flipping and not white_to_move and not gs.pawn_promote:
            p.draw.rect(screen, "blue", p.Rect(BOARD_X + (opposite_flipped_index(square_highlight_pos[1]) if mouse_button_held_down else opposite_flipped_index(start_sq[1])) * SQ_SIZE,
                                               BOARD_Y + (opposite_flipped_index(square_highlight_pos[0]) if mouse_button_held_down else opposite_flipped_index(start_sq[0])) * SQ_SIZE,
                                               SQ_SIZE, SQ_SIZE), 6)
    # Drag piece render
    if start_sq and mouse_button_held_down and not gs.pawn_promote:
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


class AnimationHandler:
    def __init__(self):
        self.in_progress_animations = []
        self.past_animations = []

    def update_animations(self, screen, board_flipping, white_to_move):
        animations_still_in_progress = []
        for animation in self.in_progress_animations:
            animation.animate(screen, board_flipping, white_to_move)
            if not animation.animation_done:
                animations_still_in_progress.append(animation)
            else:
                self.past_animations.append(animation)
        self.in_progress_animations = animations_still_in_progress

    def add_animation(self, move):
        self.in_progress_animations.append(MoveAnimation(move))

    def return_animation_end_squares(self):
        return [animation.move.end_sq for animation in self.in_progress_animations]

    def return_animation_start_squares(self):
        return [animation.move.start_sq for animation in self.in_progress_animations]

    def is_sq_in_end_sq_animation(self, sq):
        for animation in self.in_progress_animations:
            if sq == animation.move.end_sq:
                return animation.move.piece_captured
        return False


class MoveAnimation:
    def __init__(self, move):
        self.move = move
        self.dx = (self.move.end_sq[1] - self.move.start_sq[1])
        self.dy = (self.move.end_sq[0] - self.move.start_sq[0])
        self.end_x = BOARD_X + self.move.end_sq[1] * SQ_SIZE
        self.end_y = BOARD_Y + self.move.end_sq[0] * SQ_SIZE
        self.rect = p.Rect(BOARD_X + self.move.start_sq[1]*SQ_SIZE, BOARD_Y + self.move.start_sq[0]*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        self.speed = 20

        self.image = IMAGES[self.move.piece_moved]
        self.animation_done = False

    def update_position(self):
        x_speed = (self.speed * self.dx)
        y_speed = (self.speed * self.dy)
        self.rect.x += x_speed
        self.rect.y += y_speed

        if x_speed > 0:
            if self.rect.x > self.end_x:
                self.rect.x = self.end_x
        elif x_speed < 0:
            if self.rect.x < self.end_x:
                self.rect.x = self.end_x
        if y_speed > 0:
            if self.rect.y > self.end_y:
                self.rect.y = self.end_y
        elif y_speed < 0:
            if self.rect.y < self.end_y:
                self.rect.y = self.end_y

    def reverse_animation(self):
        pass

    def animate(self, screen, board_flipping, white_to_move):
        if not board_flipping or white_to_move:
            screen.blit(self.image, self.rect)
        elif board_flipping and not white_to_move:
            temp_rect = copy.deepcopy(self.rect)
            temp_rect.x = (WIDTH - self.rect.x) - SQ_SIZE  # Subtract SQ_SIZE from the reflection calculation because squares aren't centered in their position. So we need to subtract for the reflection to not extend by 1 square.
            temp_rect.y = (HEIGHT - self.rect.y) - SQ_SIZE  # Subtract SQ_SIZE from the reflection calculation because squares aren't centered in their position. So we need to subtract for the reflection to not extend by 1 square.
            screen.blit(self.image,temp_rect)
        self.update_position()
        if self.rect.x == self.end_x and self.rect.y == self.end_y:
            move_sound.play()
            self.animation_done = True
            pass


if __name__ == "__main__":
    #load_images()
    #game = Game()
    #game.game_loop()
    main()
