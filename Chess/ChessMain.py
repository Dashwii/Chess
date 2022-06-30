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
    while running:
        CLOCK.tick(FPS)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                start_sq = (click_sq_coordinates())
            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                end_sq = (click_sq_coordinates())
                if end_sq == start_sq or end_sq is None or gs.board[start_sq[0]][start_sq[1]] == "--":
                    start_sq = ()
                else:
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
                if e.key == p.K_z:
                    gs.undo_move()
        screen.fill((64, 64, 64))
        draw_board(screen, gs.board, start_sq)
        draw_pieces(screen, gs.board, gs, start_sq)
        screen.blit(current_turn_text, p.Rect(0, 40, 30, 30))
        if gs.white_to_move:
            screen.blit(white_text, p.Rect(0, 120, 30, 30))
        else:
            screen.blit(black_text, p.Rect(0, 120, 30, 30))
        p.display.flip()


def click_sq_coordinates():
    click_pos = p.mouse.get_pos()
    if BOARD_X < click_pos[0] < BOARD_X + BOARD_WIDTH:
        if BOARD_Y < click_pos[1] < BOARD_Y + BOARD_HEIGHT:  # Check if area player clicked is in the chess board
            row_clicked = (click_pos[1] - BOARD_Y) // SQ_SIZE
            col_clicked = (click_pos[0] - BOARD_X) // SQ_SIZE
            return row_clicked, col_clicked


def draw_board(screen, chess_board, start_sq):
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            if (i + j) % 2 == 0:
                p.draw.rect(screen, "white", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, "dark green", p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))
            if start_sq and i == start_sq[0] and j == start_sq[1] and chess_board[start_sq[0]][start_sq[1]] != "--":
                p.draw.rect(screen, "red",
                            p.Rect(BOARD_X + (j * SQ_SIZE), (BOARD_Y + (i * SQ_SIZE)), SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, chess_board, gs, start_sq):
    # Loop through every square in the board and see what square gives us a valid spot. Pretty bad algo but will work for now
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            if len(start_sq) and Move(start_sq, (i, j), chess_board).id in [d.id for d in gs.current_valid_moves]:
                if chess_board[i][j] == "--":
                    p.draw.circle(screen, "dark gray",
                                  (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 20)
                else:
                    p.draw.circle(screen, "dark gray",
                                  (SQ_SIZE // 2 + BOARD_X + (j * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (i * SQ_SIZE)), 60, width=12)

    # Render pieces on the board
    for i, r in enumerate(chess_board):
        for j, c in enumerate(r):
            piece = chess_board[i][j]
            if start_sq is not None and len(start_sq) == 2 and i == start_sq[0] and j == start_sq[1]:
                pass
            else:
                if piece != "--":
                    screen.blit(IMAGES[piece], p.Rect(BOARD_X + (j * SQ_SIZE), BOARD_Y + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))

    # Drag piece render
    if start_sq:
        piece = chess_board[start_sq[0]][start_sq[1]]  # Reverse column and row to get the actual piece we clicked on.
        if piece != "--":
            mouse_pos = p.mouse.get_pos()
            square_highlight_pos = click_sq_coordinates()
            if square_highlight_pos is not None:
                p.draw.rect(screen, "blue", p.Rect(BOARD_X + square_highlight_pos[1] * SQ_SIZE, BOARD_Y + square_highlight_pos[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE), 6) # Invert row and columns to get actual screen representation of highlight position.
            screen.blit(IMAGES[piece], p.Rect(mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))


def render_all_moves(screen, gs):
    # Renders all possible moves at the current game state
    for move in gs.current_valid_moves:
        p.draw.circle(screen, "dark gray",
                      (SQ_SIZE // 2 + BOARD_X + (move.end_col * SQ_SIZE), SQ_SIZE // 2 + BOARD_Y + (move.end_row * SQ_SIZE)), 20)


if __name__ == "__main__":
    main()
