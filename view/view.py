import pygame
from event.eventmanager import *
from model import model
from moviepy.editor import *

from model.model import *

CHECKLIGNE = 150

screen_height = 720
screen_width = 1280

BUTTONMENUPLAY = Button(600, 550, 191, 64,
                        image="tile000.png",
                        placeHolder=StyleButton(600, 550, 191, 64, image="tile002.png"))

BUTTONMENURETURN = Button(600, 550, 191, 64,
                          label="Continue",
                          color=(255, 0, 0),
                          colorLabel=(0, 0, 0),
                          placeHolder=StyleButton(600, 550, 191, 64, label="Continue", color=(0, 0, 0),
                                                  colorLabel=(255, 0, 0))
                          )


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
        self.imgMenu = None
        self.smallfont = None
        self.kick_state = []
        self.snare_state = []
        self.hihat_state = []
        self.message = None
        self.a_pressed = False
        self.z_pressed = False
        self.e_pressed = False

    # add a hit to the screen
    def resetInstrument(self):
        self.kick_state = []
        self.snare_state = []
        self.hihat_state = []

    def addInstrument(self, instrument, liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        instrument.setDistanceInPixel(height - CHECKLIGNE)
        liste_instrument.append(instrument)

    def updateInstrument_state(self, liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        for i in range(len(liste_instrument)):
            liste_instrument[i].updatePosition()
            # print(self.beats_state[i].getPosition())
        listTemp = liste_instrument.copy()
        for i in range(len(listTemp)):
            if listTemp[i].position > height:
                liste_instrument.pop(i)

    def isexcellent(self, beat):
        return (beat.time < pygame.time.get_ticks() + model.delta_excellent) & (
                beat.time > pygame.time.get_ticks() - model.delta_excellent)

    # displays beats, their color depending on whether they are in the "excellent" range
    def drawInstrument(self):
        for b in self.kick_state:
            color = (166, 89, 89)
            if self.isexcellent(b):
                color = (255, 0, 0)
            pygame.draw.circle(self.screen, color, (400, b.position), 25)
        for b in self.snare_state:
            color = (89, 89, 166)
            if self.isexcellent(b):
                color = (0, 0, 255)
            pygame.draw.circle(self.screen, color, (500, b.position), 25)
        for b in self.hihat_state:
            color = (166, 166, 89)
            if self.isexcellent(b):
                color = (255, 255, 0)
            pygame.draw.circle(self.screen, color, (600, b.position), 25)

    def displaySucces(self, succes):
        police = pygame.font.Font(None, 72)
        if succes == 'fail':
            texte = police.render("Fail !", True, pygame.Color(255, 0, 0))
        if succes == 'bad':
            texte = police.render("Bad !", True, pygame.Color(255, 140, 0))
        if succes == 'meh':
            texte = police.render("Meh !", True, pygame.Color(255, 165, 0))
        if succes == 'good':
            texte = police.render("Good !", True, pygame.Color(0, 128, 0))
        if succes == 'excellent':
            texte = police.render("Excellent !", True, pygame.Color(0, 255, 0))
        self.screen.blit(texte, [10, 5])
        pygame.display.flip()

    def displayScore(self):
        police = pygame.font.Font(None, 72)
        score_txt = 'Score : ' + str(self.model.gamescore)
        score = police.render(score_txt, True, pygame.Color(255, 255, 255))
        self.screen.blit(score, [screen_width - score.get_width(), 5])
        pygame.display.flip()

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
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_LIBRARY:
                self.renderlibrary()
            if currentstate == model.STATE_ENDGAME:
                self.resetInstrument()
                self.renderendgame()
            self.clock.tick(30)
        elif isinstance(event, BeatEvent):
            if event.num == 0:
                self.addInstrument(event.instrument, self.kick_state)
            if event.num == 1:
                self.addInstrument(event.instrument, self.snare_state)
            if event.num == 2:
                self.addInstrument(event.instrument, self.hihat_state)
        elif isinstance(event, ScoreEvent):
            self.message = event.type_success
        elif isinstance(event, InputEvent):
            if event.classe == 0:
                self.a_pressed = event.pressed
            if event.classe == 1:
                self.z_pressed = event.pressed
            if event.classe == 2:
                self.e_pressed = event.pressed

    # displays the "check" circles, their outline becoming colored and thicker if you press the key corresponding to their instrument

    def drawCheckCircles(self, height):
        color = (135, 206, 235)

        if self.a_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(255, 0, 0), [400, height - CHECKLIGNE], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [400, height - CHECKLIGNE], 25, 1)
        if self.z_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(0, 0, 255), [500, height - CHECKLIGNE], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [500, height - CHECKLIGNE], 25, 1)
        if self.e_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(255, 255, 0), [600, height - CHECKLIGNE], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [600, height - CHECKLIGNE], 25, 1)

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
        # print(pygame.time.get_ticks())
        # print(pygame.time.Clock())
        self.updateInstrument_state(self.kick_state)
        self.updateInstrument_state(self.snare_state)
        self.updateInstrument_state(self.hihat_state)
        self.drawInstrument()
        if self.message is not None:
            self.displaySucces(self.message)
        self.displayScore()
        self.drawCheckCircles(screen_height)
        # flip the display to show whatever we drew
        pygame.display.flip()

    def rendermenu(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))

        fontTitle = pygame.font.SysFont('arial', 200)

        title = fontTitle.render("Reetm", True, (133, 193, 233))
        self.screen.blit(title, (400, 150))

        BUTTONMENUPLAY.draw(self.screen)
        pygame.display.flip()

    def renderlibrary(self):
        pass

    def renderendgame(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))

        fontTitle = pygame.font.SysFont('arial', 100)

        final_score = fontTitle.render("Score : " + str(self.model.gamescore) + "!", True, (133, 193, 233))
        self.screen.blit(final_score, (375, 300))

        BUTTONMENURETURN.draw(self.screen)
        pygame.display.flip()

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """
        self.imgMenu = pygame.image.load("reetm.jpg")
        pygame.font.init()
        pygame.display.set_caption('Reetm')
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        # print(self.clock)
        self.smallfont = pygame.font.Font(None, 40)
        self.isinitialized = True
