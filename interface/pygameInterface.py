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
                 fontLegend=pygame.font.SysFont('Arial', 25), placeHolder=None,decalLeft=0, decalTop=0):

        super().__init__(left, top, width, height, label, image, legend, color, colorLabel, fontLabel, fontLegend)
        self.placeHolder = placeHolder
        self.decalLeft = decalLeft
        self.decalTop = decalTop

    def __rectangle(self):
        return self._surface().get_rect(topleft=(self.top + self.decalTop, self.left + self.decalLeft))

    def clicked(self, pygameEventListener):
        for event in pygameEventListener:
            if event.type == pygame.MOUSEBUTTONUP:
                return pygame.Rect.collidepoint(self.__rectangle(), pygame.mouse.get_pos())
        return False

    def draw(self, screen, ):
        if self.placeHolder is not None and pygame.Rect.collidepoint(self.__rectangle(), pygame.mouse.get_pos()):
            self.placeHolder.draw(screen)
        else:
            super().draw(screen)


class Textbox(object):
    def __init__(self, x, y, width, height, fontLabel=pygame.font.Font(None, 30)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fontLabel = fontLabel
        self.text = ''
        self.target = 0
        self.fontLabel = pygame.font.Font(None, 25)
        self.count = 0

    def text_typing(self, add):
        self.text += add

    def text_backspace(self):
        if(self.text != ''):
            self.text = self.text[:-1]

    def reset(self):
        self.text = ''

    def draw(self, screen):
        surface = self._surface()
        img = pygame.image.load("./assets/textcursor.png")
        if(self.text == '' and self.target == 0):
            labelSurface = self.fontLabel.render("Enter the youtube link here", True, (150, 150, 150))
        else:
            labelSurface = self.fontLabel.render(self.text, True, (255, 255, 255))
        labelSurface_rect = labelSurface.get_rect(center=(self.width / 2, self.height / 2))
        surface.blit(labelSurface, labelSurface_rect)

        screen.blit(surface, (self.y, self.x))
        if(self.count < 10 and self.target == 1):
            screen.blit(img, (((self.y+(self.y+self.width))/2)-6+(labelSurface.get_size()[0]/2), self.x+3))

        self.count = self.count + 1
        if(self.count > 20):
            self.count = 0

    def _surface(self):
        return pygame.Surface((self.width, self.height))

    def _rectangle(self):
        return self._surface().get_rect(topleft=(self.x, self.y))

    def clicked(self, pygameEventListener):
        for event in pygameEventListener:
            if event.type == pygame.MOUSEBUTTONUP:
                return pygame.Rect.collidepoint(self._rectangle(), pygame.mouse.get_pos())
        return False


class PauseScreen(object):
    def __init__(self, top, left, width, height, buttonDict={},
                 fontLabel=pygame.font.SysFont('Arial', 25), image=None):
        self.top = top
        self.left = left
        self.width = width
        self.height = height

        self.buttonDict = buttonDict

        self.fontLabel = fontLabel

        self.display = False

        self.image = image

    def _surface(self):
        return pygame.Surface((self.width, self.height))

    def _rectangle(self):
        return self._surface().get_rect(topleft=(self.x, self.y))

    def homeClicked(self, pygameEventListener):
        return self.buttonHome.clicked(pygameEventListener)

    def retryClicked(self, pygameEventListener):
        return self.buttonRetry.clicked(pygameEventListener)

    def playClicked(self, pygameEventListener):
        return self.buttonPlay.clicked(pygameEventListener)

    def draw(self, screen):
        surfacePause = self._surface()

        if self.image is not None:
            surfacePause = pygame.image.load(self.image).convert_alpha()
        else:
            pygame.Surface.fill(surfacePause, self.color)

        width, height = size = surfacePause.get_width(), surfacePause.get_height()

        for button in self.buttonDict.items():
            button[1].decalTop = self.top
            button[1].decalLeft = self.left
            button[1].draw(surfacePause)

        labelSurface = self.fontLabel.render("Pause", True, (255, 255, 255))

        labelSurface_rect = labelSurface.get_rect(center=(width / 2, 0))
        labelSurface_rect.top = 0
        surfacePause.blit(labelSurface, labelSurface_rect)
        screen.blit(surfacePause, (self.top, self.left))
