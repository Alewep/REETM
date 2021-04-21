import pygame
from event.eventmanager import *
from model import model

CHECKLIGNE = 100


class GraphicalView(object):
    """
    Draws the model state onto the screen.
    """
    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
                
        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.screen = None
        self.clock = None
        self.smallfont = None
        self.beats_state = []
    def addBeat(self, beat):
        _, height = pygame.display.get_surface().get_size()
        beat.setDistanceInPixel(height - CHECKLIGNE)
        self.beats_state.append(beat)

    def updateBeats_state(self):
        _, height = pygame.display.get_surface().get_size()

        for i in range(len(self.beats_state)):
            self.beats_state[i].updatePosition()
            print(self.beats_state[i].getPosition())
        listTemp = self.beats_state.copy()
        for i in range(len(self.beats_state)):
            print(listTemp)
            print(self.beats_state)
            print(i)
            if listTemp[i].getPosition() > height:
                self.beats_state.pop(i)

    def drawBeat(self):
        for b in self.beats_state:
            color = (255, 0, 0)
            pygame.draw.circle(self.screen, color, (100, b.getPosition()), 25)

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, BeatEvent):
            self.addBeat(event.getBeat())
            if not self.isinitialized:
                return
        elif isinstance(event, TickEvent):
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_LIBRARY:
                self.renderlibrary()
            self.clock.tick(30)

    def renderplay(self):
        """
        Draw the current game state on screen.
        Does nothing if isinitialized == False (pygame.init failed)
        """
        width, height = pygame.display.get_surface().get_size()
        # clear display
        self.screen.fill((0, 0, 0))
        # draw some words on the screen
        # Initializing surface
        print(pygame.time.get_ticks())
        print(pygame.time.Clock())
        self.updateBeats_state()
        self.drawBeat()
        color = (135, 206, 235)
        pygame.draw.line(self.screen, color, (0, height - CHECKLIGNE), (width, height - CHECKLIGNE))
        # flip the display to show whatever we drew
        pygame.display.flip()

    def rendermenu(self):
        self.model.buttonMenuPlay.draw(self.screen)
        pygame.display.flip()
    def renderlibrary(self):
        pass

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """
        pygame.display.set_caption('Reetm')
        self.screen = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        print(self.clock)
        self.smallfont = pygame.font.Font(None, 40)
        self.isinitialized = True


