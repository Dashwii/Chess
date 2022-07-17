import pygame as p

p.init()
p.mixer.init()
move_sound = p.mixer.Sound("move_sound.mp3")
WIDTH, HEIGHT = 1280, 720
BOARD_WIDTH = BOARD_HEIGHT = 640
SQ_SIZE = 80
FPS = 60
CLOCK = p.time.Clock()
IMAGES = {}
SCREEN = p.display.set_mode((WIDTH, HEIGHT))


alpha_sq_surface = p.Surface((SQ_SIZE, SQ_SIZE))
alpha_sq_surface.set_alpha(150)
alpha_sq_surface.fill((215, 202, 68))
alpha_circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
alpha_circle_surface.set_alpha(175)


BOARD_X = WIDTH // 2 - BOARD_WIDTH // 2
BOARD_Y = HEIGHT // 2 - BOARD_HEIGHT // 2

font = p.font.SysFont("Comic Sans MS", 40)
current_turn_text = font.render("Current Turn:", True, "white")
white_text = font.render("White", True, "white")
black_text = font.render("Black", True, "white")
coordinate_font = p.font.SysFont("arial", 18)

LIGHT_SQ = (238, 238, 210)
DARK_SQ = (118, 150, 86)
CHESS_BOARDER = (238, 238, 210)
