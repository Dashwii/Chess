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
    pawn_promote = PawnPromoteSelect()
    board_flipping = True
    board_flipping_was_on = False
    while running:
        CLOCK.tick(FPS)
        events = p.event.get()
        for e in events:
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                if not gs.pawn_promote:
                    start_sq = (click_sq_coordinates(board_flipping, gs.white_to_move))
            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                if not gs.pawn_promote:
                    end_sq = (click_sq_coordinates(board_flipping, gs.white_to_move))
                    if end_sq == start_sq or end_sq is None or gs.board[start_sq[0]][start_sq[1]] == "--":
                        start_sq = ()
                    else:
                        if board_flipping and not gs.white_to_move:
                            start_sq = (opposite_flipped_index(start_sq[0]), opposite_flipped_index(start_sq[1]))
                            end_sq = (opposite_flipped_index(end_sq[0]), opposite_flipped_index(end_sq[1]))
                        move = Move(start_sq, end_sq, gs.board)
                        for i in gs.current_valid_moves:
                            if move.id == i.id:
                                move_sound.play()
                                gs.do_move(move)
                                start_sq = ()
                                break
                            else:
                                start_sq = ()
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z and len(start_sq) == 0:  # Prevent while dragging a piece
                    gs.undo_move()
                if e.key == p.K_f and len(start_sq) == 0:  # Prevent while dragging a piece
                    board_flipping = not board_flipping
                    print("Board flipping toggled.")

        screen.fill((64, 64, 64))
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


        draw_board(screen, gs.board, start_sq, board_flipping, gs.white_to_move)
        draw_pieces(screen, gs, start_sq, board_flipping, gs.white_to_move)
        screen.blit(current_turn_text, p.Rect(0, 40, 30, 30))
        if gs.white_to_move:
            screen.blit(white_text, p.Rect(0, 120, 30, 30))
        else:
            screen.blit(black_text, p.Rect(0, 120, 30, 30))
        p.display.flip()


def click_sq_coordinates(board_flipping, white_to_move):
    click_pos = p.mouse.get_pos()
    if BOARD_X < click_pos[0] < BOARD_X + BOARD_WIDTH:
        if BOARD_Y < click_pos[1] < BOARD_Y + BOARD_HEIGHT:  # Check if area player clicked is in the chess board
            if not board_flipping or white_to_move:
                row_clicked = (click_pos[1] - BOARD_Y) // SQ_SIZE
                col_clicked = (click_pos[0] - BOARD_X) // SQ_SIZE
            elif board_flipping and not white_to_move:
                row_clicked = (BOARD_Y - click_pos[1]) // SQ_SIZE
                col_clicked = (BOARD_X - click_pos[0]) // SQ_SIZE
            return row_clicked, col_clicked
    else:
        return ()


def draw_board(screen, chess_board, start_sq, board_flipping, white_to_move):
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            if (i + j) % 2 == 0:
                p.draw.rect(screen, "white", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, "dark green", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            if len(start_sq) > 0:
                if not board_flipping or white_to_move:
                    if i == start_sq[0] and j == start_sq[1] and chess_board[start_sq[0]][start_sq[1]] != "--":
                        p.draw.rect(screen, "red",
                                    p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
                elif board_flipping and not white_to_move:
                    new_start_sq = (-1 * start_sq[0] - 1, -1 * start_sq[1] - 1)
                    if i == new_start_sq[0] and j == new_start_sq[1] and chess_board[opposite_flipped_index(new_start_sq[0], neg_flip=False)][opposite_flipped_index(new_start_sq[1], neg_flip=False)] != "--":
                        p.draw.rect(screen, "red", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, gs, start_sq, board_flipping, white_to_move):
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
        reversed_board = [list(reversed(row)) for row in reversed(gs.board)]
        for i, r in enumerate(reversed_board):
            for j, c in enumerate(r):
                if len(start_sq) and Move((opposite_flipped_index(start_sq[0]), opposite_flipped_index(start_sq[1])), (opposite_flipped_index(i, neg_flip=False), opposite_flipped_index(j, neg_flip=False)), reversed_board).id in [d.id for d in gs.current_valid_moves]:
                    if reversed_board[i][j] == "--":
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 20)
                    else:
                        p.draw.circle(screen, "dark gray",
                                      (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 60, width=12)

    # Render pieces on the board
    if not board_flipping or white_to_move:
        for i, r in enumerate(gs.board):
            for j, c in enumerate(r):
                piece = gs.board[i][j]
                if len(start_sq) > 0 and i == start_sq[0] and j == start_sq[1]:
                    pass
                else:
                    if piece != "--":
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))
    elif board_flipping and not white_to_move:
        reversed_board = [list(reversed(row)) for row in reversed(gs.board)]
        for i, r in enumerate(reversed_board):
            for j, c in enumerate(r):
                piece = reversed_board[i][j]
                if len(start_sq) > 0 and i == (-1 * start_sq[0] - 1) and j == (-1 * start_sq[1] - 1):
                    pass
                else:
                    if piece != "--":
                        screen.blit(IMAGES[piece], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))

    # Drag piece render
    if start_sq:
        if not board_flipping or white_to_move:
            piece = gs.board[start_sq[0]][start_sq[1]]  # Reverse column and row to get the actual piece we clicked on.
        elif board_flipping and not white_to_move:
            piece = gs.board[start_sq[0]][start_sq[1]]
        if piece != "--":
            mouse_pos = p.mouse.get_pos()
            square_highlight_pos = click_sq_coordinates(board_flipping, gs.white_to_move)
            if len(square_highlight_pos) > 0:
                if not board_flipping or white_to_move:
                    p.draw.rect(screen, "blue", p.Rect(BOARD_X + square_highlight_pos[1] * SQ_SIZE, BOARD_Y + square_highlight_pos[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6) # Invert row and columns to get actual screen representation of highlight position.
                elif board_flipping and not white_to_move:
                    # Add 1 to square_highlight_pos[0] due to the negative integers not being 0 index based. Adding 1 reduces the negative integer by 1. Which we'll multiply by -1 to make positive.
                    p.draw.rect(screen, "blue", p.Rect(BOARD_X + (-1 * (square_highlight_pos[1] + 1)) * SQ_SIZE, BOARD_Y + (-1 * (square_highlight_pos[0] + 1)) * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6)
            screen.blit(IMAGES[piece], p.Rect(mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))


def render_all_moves(screen, gs):
    # Renders all possible moves at the current game state
    for move in gs.current_valid_moves:
        p.draw.circle(screen, "dark gray",
                      (SQ_SIZE // 2 + BOARD_X + (move.end_col * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (move.end_row * SQ_SIZE)), 20)


def opposite_flipped_index(index, neg_flip=True):
    if neg_flip:
        # Convert negative flipped index to 0 base indexing.  Ex. -8 -> -7
        index += 1

        index *= -1

    # 8 is the length of our board
    return 8 - index - 1


if __name__ == "__main__":
    main()