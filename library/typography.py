import pygame


class Typography:
    fonts = {
        'def_bold': './res/fonts/Cloude_Regular_Bold_1.02.ttf',
        'def_normal': './res/fonts/Cloude_Regular_1.02.ttf',
        'large': './res/fonts/NimbusRomNo9L-Med.otf'
    }

    def __init__(self, pygame_settings, caption, xy, font, size, color, bg_color, h_align, v_align, max_width,
                 max_height, shadow=False):
        self.font = font
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.caption = caption  # .replace('_', ' ')
        self.max_width = round(max_width)
        # self.max_height = round(max_height * pygame_settings.APP_SCALE)

        self.visible = True
        self.shadow = shadow
        self.sh_dist_x = 1
        self.sh_dist_y = 1

        pygame.freetype.set_default_resolution(96)
        self.text_font = pygame.freetype.Font(self.fonts[self.font], self.size)
        self.space_size = self.text_font.get_rect(' ')

        # self.line_spacing = self.text_font.get_sized_height(self.size)
        self.line_height = self.text_font.get_rect('O').height
        self.line_spacing = round(self.line_height * 1.5)
        self.actual_width, self.max_height = self.get_text_height()

        self.x, self.y = xy
        self.h_align = h_align
        self.v_align = v_align
        self.rendered_text = None
        self.rendered_rect = None
        self.render()

    def get_text_height(self):
        text = self.caption.split()
        x, y = 0, round(self.line_height / 2)
        max_x = 0
        for text_word in text:
            if text_word == '$n':
                x, y = 0, y + self.line_spacing
                continue
            word_bounds = self.text_font.get_rect(text_word)
            if x + word_bounds.width + self.space_size.width + word_bounds.x >= self.max_width:
                x, y = 0, y + self.line_spacing
            x = x + word_bounds.width + self.space_size.width + word_bounds.x
            max_x = max(x, max_x)
        text_height = y + self.line_spacing
        return max_x + self.sh_dist_x, text_height + self.sh_dist_y

    def align(self, h_align, v_align, rect):
        rect.left = self.x
        rect.top = self.y
        if h_align == 'center':
            rect.centerx = self.x
        elif h_align == 'right':
            rect.right = self.x
        if v_align == 'middle':
            rect.centery = self.y
        elif v_align == 'bottom':
            rect.bottom = self.y

    def render(self):
        txt_image = self.blit_text(self.caption, self.color, 0, 0)
        txt_rect = txt_image.get_rect()
        self.rendered_text = pygame.Surface((self.max_width, self.max_height)).convert()
        self.rendered_text.fill(self.bg_color)
        colorkey = self.rendered_text.get_at((0, 0))
        self.rendered_text.set_colorkey(colorkey, pygame.RLEACCEL)
        self.rendered_rect = self.rendered_text.get_rect()
        self.align(self.h_align, self.v_align, self.rendered_rect)

        if self.shadow:
            txt_shadow = self.blit_text(self.caption, (1, 1, 1), 0, 0)
            rect_shadow = txt_shadow.get_rect()
            rect_shadow.left += self.sh_dist_x
            rect_shadow.top += self.sh_dist_y
            self.rendered_text.blit(txt_shadow, rect_shadow)

        self.rendered_text.blit(txt_image, txt_rect)

    def blit_text(self, text, color, offset_x, offset_y):
        text_canvas = pygame.Surface((self.max_width, self.max_height)).convert()
        text_canvas.fill(self.bg_color)
        colorkey = text_canvas.get_at((0, 0))
        text_canvas.set_colorkey(colorkey, pygame.RLEACCEL)
        self.text_font.origin = True

        lined_text = self.split_text(text)
        y = self.line_spacing
        for i in range(0, len(lined_text)):
            line_bounds = self.text_font.get_rect(lined_text[i])
            # line_bounds.left = self.space_size.width
            if self.h_align == 'center':
                line_bounds.centerx = round(self.max_width / 2)
            elif self.h_align == 'right':
                line_bounds.right = self.max_width - self.space_size.width
            # line_bounds.top = (self.line_spacing * 0.96) * (i + 1)
            self.text_font.render_to(text_canvas, (line_bounds.left, y // 1) , None, color)
            y += max(line_bounds.height, self.line_spacing)
        return text_canvas

    def split_text(self, text):
        splitted_text = text.split()
        x = 0
        lined_text = []
        text_line = []
        for text_word in splitted_text:
            if text_word == '$n':
                x = 0
                merged_line = ' '.join(text_line)
                lined_text.append(merged_line)
                text_line.clear()
                continue
            word_bounds = self.text_font.get_rect(text_word)
            if x + word_bounds.width + self.space_size.width * 4 + word_bounds.x >= self.max_width:
                x = 0
                merged_line = ' '.join(text_line)
                lined_text.append(merged_line)
                text_line.clear()
            x = x + word_bounds.width + self.space_size.width + word_bounds.x
            text_line.append(text_word)
        if len(text_line) > 0:
            merged_line = ' '.join(text_line)
            lined_text.append(merged_line)
            text_line.clear()
        return lined_text

    def draw(self, surface, offset=None):
        # Draw the piece at its current location.
        if offset is None:
            offset = (0, 0)
        off_x, off_y = offset
        surface.blit(self.rendered_text, (self.rendered_rect.x + off_x, self.rendered_rect.y + off_y))
