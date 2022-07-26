import pygame as p

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


alpha_sq_surface_yellow = p.Surface((SQ_SIZE, SQ_SIZE))
alpha_sq_surface_yellow.set_alpha(150)
alpha_sq_surface_yellow.fill((215, 202, 68))
alpha_circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
alpha_circle_surface.set_alpha(150)


BOARD_X = WIDTH // 2 - BOARD_WIDTH // 2
BOARD_Y = HEIGHT // 2 - BOARD_HEIGHT // 2

font = p.font.SysFont("Comic Sans MS", 40)
current_turn_text = font.render("Current Turn:", True, "white")
white_text = font.render("White", True, "white")
black_text = font.render("Black", True, "white")
coordinate_font = p.font.SysFont("arial", 30)

LIGHT_SQ = (238, 238, 210)
DARK_SQ = (118, 150, 86)
CHESS_BOARDER = (238, 238, 210)


MOVE_CIRCLE_RADIUS = 18
MOVE_CAPTURE_RADIUS = 60
MOVE_CAPTURE_WIDTH = 12

ANIMATION_SPEED = 20
