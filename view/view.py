import pygame
from event.eventmanager import *

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
        self.surface = pygame.display.set_mode((400, 300))
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.screen = None
        self.clock = None
        self.smallfont = None
        self.kick_state = []
        self.snare_state = []
        self.hihat_state = []

    def addKick(self, kick):
        _, height = pygame.display.get_surface().get_size()
        kick.setDistanceInPixel(height - CHECKLIGNE)
        self.kick_state.append(kick)

    def addSnare(self, snare):
        _, height = pygame.display.get_surface().get_size()
        snare.setDistanceInPixel(height - CHECKLIGNE)
        self.snare_state.append(snare)

    def addHihat(self, hihat):
        _, height = pygame.display.get_surface().get_size()
        hihat.setDistanceInPixel(height - CHECKLIGNE)
        self.hihat_state.append(hihat)

    def updateKick_state(self):
        _, height = pygame.display.get_surface().get_size()

        for i in range(len(self.kick_state)):
            self.kick_state[i].updatePosition()
            #print(self.beats_state[i].getPosition())
        listTemp = self.kick_state.copy()
        for i in range(len(listTemp)):
            if listTemp[i].getPosition() > height:
                self.kick_state.pop(i)

    def updateSnare_state(self):
        _, height = pygame.display.get_surface().get_size()

        for i in range(len(self.snare_state)):
            self.snare_state[i].updatePosition()
            #print(self.beats_state[i].getPosition())
        listTemp = self.snare_state.copy()
        for i in range(len(listTemp)):
            if listTemp[i].getPosition() > height:
                self.snare_state.pop(i)

    def updateHihat_state(self):
        _, height = pygame.display.get_surface().get_size()

        for i in range(len(self.hihat_state)):
            self.hihat_state[i].updatePosition()
            #print(self.beats_state[i].getPosition())
        listTemp = self.hihat_state.copy()
        for i in range(len(listTemp)):
            if listTemp[i].getPosition() > height:
                self.hihat_state.pop(i)

    def drawKick(self):
        for b in self.kick_state:
            color = (255, 0, 0)
            pygame.draw.circle(self.surface, color, (100, b.getPosition()), 25)

    def drawSnare(self):
        for b in self.snare_state:
            color = (0, 0, 255)
            pygame.draw.circle(self.surface, color, (200, b.getPosition()), 25)

    def drawHihat(self):
        for b in self.hihat_state:
            color = (255, 255, 0)
            pygame.draw.circle(self.surface, color, (300, b.getPosition()), 25)

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
        elif isinstance(event, TickEvent):
            self.renderall()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(30)
        elif isinstance(event, KickEvent):
            self.addKick(event.getKick())
        elif isinstance(event, SnareEvent):
            self.addSnare(event.getSnare())
        elif isinstance(event, HihatEvent):
            self.addHihat(event.getHihat())

    def renderall(self):
        """
        Draw the current game state on screen.
        Does nothing if isinitialized == False (pygame.init failed)
        """
        height = 600
        width = 1000
        if not self.isinitialized:
            return
        # clear display
        self.screen.fill((0, 0, 0))
        # draw some words on the screen
        # Initializing surface
        #print(pygame.time.get_ticks())
        #print(pygame.time.Clock())
        self.surface = pygame.display.set_mode((width, height))
        self.updateKick_state()
        self.drawKick()
        self.updateSnare_state()
        self.drawSnare()
        self.updateHihat_state()
        self.drawHihat()
        color = (135, 206, 235)
        pygame.draw.line(self.surface, color,(0,height - CHECKLIGNE),(width,height - CHECKLIGNE))
        # flip the display to show whatever we drew
        pygame.display.flip()

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        result = pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Reetm')
        self.screen = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        #print(self.clock)
        self.smallfont = pygame.font.Font(None, 40)
        self.isinitialized = True
