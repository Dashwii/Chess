from constants import *
from coordtext import CoordText
from ChessEngine import ChessEngine, Move, copy


def load_images():
    # Load images once into a dictionary for later access.
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


class AnimationHandler:
    def __init__(self, game):
        self.game = game
        self.in_progress_animations = []
        self.past_animations = []

    def update_animations(self):
        animations_still_in_progress = []
        for animation in self.in_progress_animations:
            animation.animate(self.game.screen, self.game.board_flipping, self.game.gs.white_to_move)
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
        self.speed = 10  #  Used to be 20

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


class Highlighting:
    """Class that will hold some extra information highlighted squares, movement, etc.
    Intended to increase performance by storing some info instead of looping and searching all the time."""
    def __init__(self, game):
        self.game = game
        self.mouse_button_down = self.game.mouse_button_down
        self.start_sq = self.game.start_sq
        self.previous_start_sq = None
        self.screen = self.game.screen
        self.current_piece_sq_moves = []

    def render(self):
        self.render_red_highlight()
        self.render_last_move()
        self.render_piece_move_squares()
        self.render_blue_highlight()

    def render_last_move(self):
        if len(self.game.gs.move_log) > 0:
            start_sq = self.game.gs.move_log[-1].start_sq
            end_sq = self.game.gs.move_log[-1].end_sq
            self.screen.blit(alpha_sq_surface, (BOARD_X + self.game.index_adjustment(start_sq[1]) * SQ_SIZE, BOARD_Y + self.game.index_adjustment(start_sq[0]) * SQ_SIZE))
            self.screen.blit(alpha_sq_surface, (BOARD_X + self.game.index_adjustment(end_sq[1]) * SQ_SIZE, BOARD_Y + self.game.index_adjustment(end_sq[0]) * SQ_SIZE))

    def render_piece_move_squares(self):
        if len(self.game.start_sq) == 0:
            self.current_piece_sq_moves = []
            self.previous_start_sq = None

        if len(self.game.start_sq) > 0 and self.previous_start_sq != self.game.start_sq:
            self.current_piece_sq_moves = []
            for i, row in enumerate(self.game.gs.board):
                for j, col in enumerate(row):
                    if len(self.game.start_sq) and Move(self.game.start_sq, (i, j), self.game.gs.board).id in [d.id for d in self.game.gs.current_valid_moves]:
                        self.current_piece_sq_moves.append((i, j))
            self.previous_start_sq = self.game.start_sq

        for square in self.current_piece_sq_moves:
            if self.game.gs.board[square[0]][square[1]] == "--":
                alpha_circle_surface.fill(0)
                circle_radius = 12
                p.draw.circle(alpha_circle_surface, "dark gray", ((alpha_circle_surface.get_width() // 2), alpha_circle_surface.get_height() // 2), circle_radius)
                self.game.screen.blit(alpha_circle_surface, (BOARD_X + (self.game.index_adjustment(square[1]) * SQ_SIZE), BOARD_Y + (self.game.index_adjustment(square[0]) * SQ_SIZE)))
            else:
                alpha_circle_surface.fill(0) # This operation may be costly, I'm not sure. But if we don't clear the canvas. Capture circles will appear on empty squares. Due to the
                                             # same canvas being used for both blits.
                circle_radius = 40
                p.draw.circle(alpha_circle_surface, "dark gray",
                              ((alpha_circle_surface.get_width() // 2), alpha_circle_surface.get_height() // 2),
                              circle_radius, width=6)
                self.game.screen.blit(alpha_circle_surface,
                                 (BOARD_X + (self.game.index_adjustment(square[1]) * SQ_SIZE), BOARD_Y + (self.game.index_adjustment(square[0]) * SQ_SIZE)))

    def render_red_highlight(self):
        if len(self.game.start_sq) > 0:
            p.draw.rect(self.screen, "red", p.Rect(BOARD_X + (self.game.index_adjustment(self.game.start_sq[1]) * SQ_SIZE),
                        BOARD_Y + (self.game.index_adjustment(self.game.start_sq[0]) * SQ_SIZE),
                        SQ_SIZE, SQ_SIZE))

    def render_blue_highlight(self):
        if len(self.game.start_sq) > 0:
            square_highlight_pos = mouse_sq_coordinates(self.game.board_flipping, self.game.gs.white_to_move)
            if len(square_highlight_pos) == 0 and self.game.mouse_button_down:
                square_highlight_pos = (1000, 1000)  # Render square highlight off screen.
            if not self.game.gs.pawn_promote:
                p.draw.rect(self.screen, "blue",
                            p.Rect(BOARD_X + (self.game.index_adjustment(square_highlight_pos[1]) * SQ_SIZE if self.game.mouse_button_down else self.game.index_adjustment(self.game.start_sq[1]) * SQ_SIZE),
                                   BOARD_Y + (self.game.index_adjustment(square_highlight_pos[0]) * SQ_SIZE if self.game.mouse_button_down else self.game.index_adjustment(self.game.start_sq[0]) * SQ_SIZE),
                                   SQ_SIZE, SQ_SIZE), 5)


class Game:
    """Rewrite of main() to a class."""
    def __init__(self):
        self.running = True
        self.mouse_button_down = True
        self.board_flipping = True
        self.board_flipping_was_on = False
        self.start_sq = ()
        self.player_click_count = 0
        self.screen = SCREEN

        self.gs = ChessEngine()
        self.game_over = GameOver()
        self.pawn_promote = PawnPromoteSelect()
        self.highlights = Highlighting(self)
        self.animations = AnimationHandler(self)
        self.cords = coordinate_renders()

    def game_loop(self):
        while self.running:
            CLOCK.tick(FPS)
            events = p.event.get()
            for e in events:
                if e.type == p.QUIT:
                    self.running = False
                if e.type == p.MOUSEBUTTONDOWN:
                    self.mouse_button_down = True
                    end_pos_click = mouse_sq_coordinates(self.board_flipping, self.gs.white_to_move)
                    if len(self.start_sq) == 0 and len(end_pos_click) == 2:
                        if clicked_on_turn_piece(end_pos_click, self.gs):
                            self.start_sq = end_pos_click
                            self.player_click_count = 1
                    else:
                        if clicked_on_turn_piece(end_pos_click, self.gs) and self.start_sq != end_pos_click:
                            self.start_sq = end_pos_click
                            self.player_click_count = 1
                        elif self.start_sq == end_pos_click:
                            self.player_click_count += 1
                        else:
                            if len(end_pos_click) > 0:
                                self.handle_move(end_pos_click)
                            self.start_sq = ()
                            self.player_click_count = 0
                if e.type == p.MOUSEBUTTONUP:
                    self.mouse_button_down = False
                    end_pos_click = mouse_sq_coordinates(self.board_flipping, self.gs.white_to_move)
                    if len(self.start_sq) == 2 and len(end_pos_click) == 2 and end_pos_click != self.start_sq:
                        valid = self.handle_move(end_pos_click, dragged=True)
                        if valid:
                            self.start_sq = ()
                            self.player_click_count = 0
                        else:
                            self.player_click_count = 0
                    elif len(end_pos_click) == 0:
                        self.player_click_count = 0
                if e.type == p.KEYDOWN:
                    if e.key == p.K_f:
                        self.start_sq = ()
                        self.board_flipping = not self.board_flipping
                        if self.board_flipping:
                            print("Board flipping toggled on.")
                        else:
                            print("Board flipping toggled off.")
                    if e.key == p.K_z:
                        self.start_sq = ()
                        self.gs.undo_move()
            if self.player_click_count == 2 and not self.mouse_button_down:
                self.start_sq = ()
                self.player_click_count = 0
            self.screen.fill((64, 64, 64))
            self.draw_board()
            self.highlights.render()
            self.draw_pieces()
            self.animations.update_animations()
            p.display.flip()

    def index_adjustment(self, index):
        """Pass any index you need from the board into here. Will return a flipped or still index depending on if the board
        is flipped or not."""
        if not self.board_flipping or self.gs.white_to_move:
            return index
        else:
            return opposite_flipped_index(index)

    def draw_board(self):
        p.draw.rect(self.screen, (30, 30, 30), p.Rect(BOARD_X - 15, BOARD_Y - 15, BOARD_WIDTH + 30, BOARD_HEIGHT + 30))  # Boarder
        for i, r in enumerate(self.gs.board):
            for j, c in enumerate(r):
                if (i + j) % 2 == 0:
                    p.draw.rect(self.screen, LIGHT_SQ,
                                p.Rect(BOARD_X + (self.index_adjustment(j) * SQ_SIZE), (BOARD_Y + (self.index_adjustment(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                else:
                    p.draw.rect(self.screen, DARK_SQ,
                                p.Rect(BOARD_X + (self.index_adjustment(j) * SQ_SIZE), (BOARD_Y + (self.index_adjustment(i) * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
        for i in range(8):
            if self.gs.white_to_move or not self.board_flipping:
                self.cords[0][i][0].render(self.screen)
                self.cords[0][i][1].render(self.screen, subtract_self=True)
            elif not self.gs.white_to_move and self.board_flipping:
                self.cords[1][i][0].render(self.screen)
                self.cords[1][i][1].render(self.screen, subtract_self=True)

    def draw_pieces(self):
        for i, r in enumerate(self.gs.board):
            for j, c in enumerate(r):
                piece = self.gs.board[i][j]
                # In animation will either return False or a board square if our current square is "animating"
                in_animation = self.animations.is_sq_in_end_sq_animation((i, j))
                if in_animation:
                    if in_animation == "--":
                        pass
                    else:
                        self.screen.blit(IMAGES[in_animation], p.Rect(BOARD_X + (self.index_adjustment(j) * SQ_SIZE),
                                                                      BOARD_Y + (self.index_adjustment(i) * SQ_SIZE), SQ_SIZE, SQ_SIZE))
                elif piece != "--" and not ((i, j) == self.start_sq and self.mouse_button_down) and not self.gs.pawn_promote:
                    self.screen.blit(IMAGES[piece], p.Rect(BOARD_X + (self.index_adjustment(j) * SQ_SIZE),
                                                           BOARD_Y + (self.index_adjustment(i) * SQ_SIZE),
                                                           SQ_SIZE, SQ_SIZE))
        if self.start_sq and self.mouse_button_down and not self.gs.pawn_promote:
            pos = p.mouse.get_pos()
            render_piece = self.gs.board[self.start_sq[0]][self.start_sq[1]]
            if render_piece != "--":
                self.screen.blit(IMAGES[render_piece], p.Rect(pos[0] - SQ_SIZE // 2,
                                                              pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))

    def handle_move(self, end_square, dragged=False):
        move = Move(self.start_sq, end_square, self.gs.board)
        for valid_move in self.gs.current_valid_moves:
            if move.id == valid_move.id:
                if dragged:
                    move_sound.play()
                else:
                    self.animations.add_animation(move)
                self.gs.do_move(move)
                return True
        return False


def clicked_on_turn_piece(click, gs):
    if len(click) == 0:
        return
    if gs.board[click[0]][click[1]][0] == "w" and gs.white_to_move:
        return True
    elif gs.board[click[0]][click[1]][0] == "b" and not gs.white_to_move:
        return True
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


def coordinate_renders():
    nums = ["1", "2", "3", "4", "5", "6", "7", "8"]
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    white_text_render_objects = []
    black_text_render_objects = []
    for i, (num, letter) in enumerate(zip(nums, letters)):
        # White perspective
        w_rank = CoordText(num, DARK_SQ if i % 2 == 0 else "white", coordinate_font, None, (BOARD_X, BOARD_Y + (i * SQ_SIZE)))
        w_file = CoordText(letter, DARK_SQ if i % 2 == 1 else "white", coordinate_font, None, (BOARD_X + ((i + 1) * SQ_SIZE), BOARD_Y + (8 * SQ_SIZE)))
        # Black perspective
        b_rank = CoordText(nums[opposite_flipped_index(i)], DARK_SQ if i % 2 == 0 else LIGHT_SQ, coordinate_font, None, (BOARD_X, BOARD_Y + (i * SQ_SIZE)))
        b_file = CoordText(letters[opposite_flipped_index(i)], DARK_SQ if i % 2 == 1 else LIGHT_SQ, coordinate_font, None, (BOARD_X + ((i + 1) * SQ_SIZE), BOARD_Y + (8 * SQ_SIZE)))

        white_text_render_objects.append((w_rank, w_file))
        black_text_render_objects.append((b_rank, b_file))
    return [white_text_render_objects, black_text_render_objects]


def opposite_flipped_index(index):
    # 8 is the length of our board
    return 8 - index - 1


if __name__ == "__main__":
    load_images()
    game = Game()
    game.game_loop()
