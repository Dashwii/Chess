from constants import *


class CoordText:
    def __init__(self, text, color, font, size, pos):
        self.text = text
        self.color = color
        self.size = size
        self.font = font
        self.pos = pos

        self.t_render = self.font.render(self.text, True, self.color)

    def render(self, screen, subtract_self=False):
        if subtract_self:
            screen.blit(self.t_render, (self.pos[0] - self.t_render.get_width(),
                                        self.pos[1] - self.t_render.get_height()))
        else:
            screen.blit(self.t_render, (self.pos[0], self.pos[1]))
