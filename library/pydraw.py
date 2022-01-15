# Draws visual elements with pygame
import pygame


def square(sq_xy, sq_size, sq_cols, sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=True, sq_image=None, same_surface=False):
    if same_surface:
        sq_surface = sq_image
    else:
        if sq_image is not None:
            sq_surface = pygame.Surface((sq_image.get_width(), sq_image.get_height())).convert()
        else:
            sq_surface = pygame.Surface(sq_size).convert()
        sq_surface.set_colorkey(sq_surface.get_at((0,0)))

    col_light, col_shadow, col_bg, col_outline = sq_cols

    if sq_ldir == 1:
        col_seq = (col_light, col_light, col_shadow, col_shadow)
    elif sq_ldir == 2:
        col_seq = (col_shadow, col_light, col_light, col_shadow)
    elif sq_ldir == 3:
        col_seq = (col_shadow, col_shadow, col_light, col_light)
    elif sq_ldir == 4:
        col_seq = (col_light, col_light, col_light, col_light)
    elif sq_ldir == 5:
        col_seq = (col_shadow, col_shadow, col_shadow, col_shadow)
    else:
        col_seq = (col_light, col_shadow, col_shadow, col_light)

    if sq_fill:
        sq_surface.fill(col_bg, (sq_xy, sq_size))
    if sq_image is not None and not same_surface:
        sq_surface.blit(sq_image, (0,0))

    left, top = sq_xy

    for i in range(0 + sq_outsize, sq_bsize + sq_outsize):
        pygame.draw.lines(sq_surface, col_seq[0], False, ((left + i, top + i), (left + sq_size[0] - (2 + i), top + i)))
        pygame.draw.lines(sq_surface, col_seq[1], False, ((left + sq_size[0] - (1 + i), top + 1 + i), (left + sq_size[0] - (1 + i), top + sq_size[1] - (1 + i))))
        pygame.draw.lines(sq_surface, col_seq[2], False, ((left + sq_size[0] - (1 + i), top + sq_size[1] - (1 + i)), (left + (1 + i), top + sq_size[1] - (1 + i))))
        pygame.draw.lines(sq_surface, col_seq[3], False, ((left + i, top + sq_size[1] - (2 + i)), (left + i, top + i)))

    for i in range(0, sq_outsize):
        pygame.draw.lines(sq_surface, col_outline, False, ((left + i, top + i), (left + sq_size[0] - (1 + i), top + i)))
        pygame.draw.lines(sq_surface, col_outline, False, ((left + sq_size[0] - (1 + i), top + 1 + i), (left + sq_size[0] - (1 + i), top + sq_size[1] - (1 + i))))
        pygame.draw.lines(sq_surface, col_outline, False, ((left + sq_size[0] - (1 + i), top + sq_size[1] - (1 + i)), (left + i, top + sq_size[1] - (1 + i))))
        pygame.draw.lines(sq_surface, col_outline, False, ((left + i, top + sq_size[1] - (1 + i)), (left + i, top + i)))

    return sq_surface