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

    def addInstrument(self, instrument, liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        instrument.setDistanceInPixel(height - CHECKLIGNE)
        liste_instrument.append(instrument)

    def updateInstrument_state(self,liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        for i in range(len(liste_instrument)):
            liste_instrument[i].updatePosition()
            # print(self.beats_state[i].getPosition())
        listTemp = liste_instrument.copy()
        for i in range(len(listTemp)):
            if listTemp[i].getPosition() > height:
                liste_instrument.pop(i)

    def drawInstrument(self):
        for b in self.kick_state:
            color = (255, 0, 0)
            pygame.draw.circle(self.surface, color, (100, b.getPosition()), 25)
        for b in self.snare_state:
            color = (0, 0, 255)
            pygame.draw.circle(self.surface, color, (200, b.getPosition()), 25)
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
        elif isinstance(event, BeatEvent):
            if event.getNum() == 0:
                self.addInstrument(event.getInstrument(),self.kick_state)
            if event.getNum() == 1:
                self.addInstrument(event.getInstrument(),self.snare_state)
            if event.getNum() == 2:
                self.addInstrument(event.getInstrument(),self.hihat_state)

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
        self.updateInstrument_state(self.kick_state)
        self.updateInstrument_state(self.snare_state)
        self.updateInstrument_state(self.hihat_state)
        self.drawInstrument()
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
