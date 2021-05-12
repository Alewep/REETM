import pygame

pygame.init()
class StyleButton(object):
    def __init__(self, left, top, width, height, label=None, image=None,
                 legend=None, color=(255, 255, 255), colorLabel=(0, 0, 0), fontLabel=pygame.font.Font(None, 25),
                 fontLegend=pygame.font.SysFont('Arial', 25)):

        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.image = image
        self.label = label
        self.legend = legend
        self.color = color
        self.colorLabel = colorLabel
        self.fontLabel = fontLabel
        self.fontLegend = fontLegend

    def _surface(self):
        return pygame.Surface((self.width, self.height))

    def _rectangle(self):
        return self._surface().get_rect(topleft=(self.top, self.left))

    def draw(self, screen):
        surfaceButton = self._surface()
        if self.image is not None:
            surfaceButton = pygame.image.load(self.image).convert_alpha()
        else:
            pygame.Surface.fill(surfaceButton, self.color)

        if self.label is not None:
            labelSurface = self.fontLabel.render(self.label, True, self.colorLabel)
            labelSurface_rect = labelSurface.get_rect(center=(self.width / 2, self.height / 2))
            surfaceButton.blit(labelSurface, labelSurface_rect)

        screen.blit(surfaceButton, (self.top, self.left))


class Button(StyleButton):
    def __init__(self, left, top, width, height, label=None, image=None,
                 legend=None, color=(255, 255, 255), colorLabel=(0, 0, 0), fontLabel=pygame.font.Font(None, 25),
                 fontLegend=pygame.font.SysFont('Arial', 25), placeHolder=None):

        super().__init__(left, top, width, height, label, image, legend, color, colorLabel, fontLabel, fontLegend)
        self.placeHolder = placeHolder

    def cliked(self, pygameEventListener):
        for event in pygameEventListener:
            if event.type == pygame.MOUSEBUTTONUP:
                return pygame.Rect.collidepoint(self._rectangle(), pygame.mouse.get_pos())
        return False

    def draw(self, screen):
        if self.placeHolder is not None and pygame.Rect.collidepoint(self._rectangle(), pygame.mouse.get_pos()):
            self.placeHolder.draw(screen)
        else:
            super().draw(screen)


class Textbox():
    def __init__(self, x, y, width, height, fontLabel=pygame.font.Font(None, 30)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fontLabel = fontLabel
        self.text = ''
        self.target = 0
        self.fontLabel = pygame.font.Font(None, 25)

    def text_typing(self, add):
        self.text += add

    def text_backspace(self):
        self.text = self.text[:-1]

    def reset(self):
        self.text = ''

    def draw(self, screen):
        surface = self._surface()
        labelSurface = self.fontLabel.render(self.text, True, (255, 255, 255))
        labelSurface_rect = labelSurface.get_rect(center=(self.width / 2, self.height / 2))
        surface.blit(labelSurface, labelSurface_rect)

        screen.blit(surface, (self.y, self.x))

    def getText(self):
        return self.text

    def _surface(self):
        return pygame.Surface((self.width, self.height))

    def _rectangle(self):
        return self._surface().get_rect(topleft=(self.x, self.y))

    def clicked(self, pygameEventListener):
        for event in pygameEventListener:
            if event.type == pygame.MOUSEBUTTONUP:
                return pygame.Rect.collidepoint(self._rectangle(), pygame.mouse.get_pos())
        return False
