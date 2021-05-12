import tkinter.messagebox

import pygame.time

from mvc.eventmanager import *
from mvc.model import *
from interface import pygameInterface
from interface import tkinterInterface
import tkinter
import tkinter.filedialog

CHECKLIGNE = 150

screen_height = 720
screen_width = 1280

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

        self.buttonMenuPlay = None
        self.buttonMenuReturn = None
        self.fileSelected = None
        self.songs_list = None
        self.counter = 0
        self.cooldown = 1000
        self.last = pygame.time.get_ticks()

        self.YOUTUBELINKTEXTBOX = None
        self.BUTTONYOUTUBELINK = None
        self.BUTTONRESET = None

    # add a hit to the screen
    def resetInstrument(self):
        self.kick_state = []
        self.snare_state = []
        self.hihat_state = []

    def addInstrument(self, instrument, liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        instrument.setDistanceInPixel(height - self.model.config["checkligne"])
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
        return (beat.time < pygame.time.get_ticks() + self.model.config["delta_excellent"]) & (
                beat.time > pygame.time.get_ticks() - self.model.config["delta_meh"])

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
            if currentstate == STATE_MENU:
                self.rendermenu()
            if currentstate == STATE_PLAY:
                self.renderplay()
            if currentstate == STATE_LIBRARY:
                self.renderlibrary()
            if currentstate == STATE_ENDGAME:
                self.resetInstrument()
                self.renderendgame()
            if currentstate == STATE_CHOOSEFILE:
                self.renderChooseFile()
            if currentstate == STATE_EMPTYLIBRARY:
                self.renderemptylibrary()
            if currentstate == STATE_FILENOTFOUND:
                self.renderfilenotfound()
            if currentstate == STATE_LOADING:
                self.renderloading()
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
        elif isinstance(event,newBestScoreEvent):
            self.rendernewbestscore(event.newbestscore)
    # displays the "check" circles, their outline becoming colored and thicker if you press the key corresponding to their instrument

    def drawCheckCircles(self, height):
        color = (135, 206, 235)

        if self.a_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(255, 0, 0), [400, height - self.model.config["checkligne"]], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [400, height - self.model.config["checkligne"]], 25, 1)
        if self.z_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(0, 0, 255), [500, height - self.model.config["checkligne"]], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [500, height - self.model.config["checkligne"]], 25, 1)
        if self.e_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(255, 255, 0), [600, height - self.model.config["checkligne"]], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [600, height - self.model.config["checkligne"]], 25, 1)

    def drawCheckLetters(self, height):
        color = (135, 206, 235)
        police = pygame.font.Font(None, 60)

        letter_a = police.render("A", True, pygame.Color(255, 0, 0))
        letter_z = police.render("Z", True, pygame.Color(0, 0, 255))
        letter_e = police.render("E", True, pygame.Color(255, 255, 0))

        self.screen.blit(letter_a, [385, height - self.model.config["checkligne"] + 25])
        self.screen.blit(letter_z, [485, height - self.model.config["checkligne"] + 25])
        self.screen.blit(letter_e, [585, height - self.model.config["checkligne"] + 25])

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
        self.drawCheckLetters(screen_height)
        # flip the display to show whatever we drew
        pygame.display.flip()

    def rendermenu(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))

        fontTitle = pygame.font.SysFont('arial', 200)

        title = fontTitle.render("Reetm", True, (133, 193, 233))

        self.screen.blit(title, (350, 150))

        self.buttonMenuPlay.draw(self.screen)
        self.buttonLibrary.draw(self.screen)

        self.YOUTUBELINKTEXTBOX.draw(self.screen)
        self.BUTTONYOUTUBELINK.draw(self.screen)
        self.BUTTONRESET.draw(self.screen)
        pygame.display.flip()

    def renderChooseFile(self):
        top = tkinter.Tk()
        top.withdraw()  # hide window
        self.fileSelected = tkinter.filedialog.askopenfilename(parent=top, title="Select a Music in wav format",
                                                               filetypes=(("wav files",
                                                                           "*.wav*"),
                                                                          ("all files",
                                                                           "*.*")))
        top.destroy()

    def renderlibrary(self):
        self.songs_list = tkinterInterface.ComboBox(title="Library")
        self.songs_list.window.mainloop()

    def renderemptylibrary(self):
        window = tkinter.Tk()
        w = 300  # width for the Tk root
        h = 400
        ws = window.winfo_screenwidth()  # width of the screen
        hs = window.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        window.withdraw()
        infobox = tkinter.messagebox.showinfo(parent=window, title="Error",
                                              message="The library is empty ! Please select a song via \"Start\" Button first")
        window.destroy()

    def renderfilenotfound(self):
        window = tkinter.Tk()
        w = 300  # width for the Tk root
        h = 400
        ws = window.winfo_screenwidth()  # width of the screen
        hs = window.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        window.withdraw()
        infobox = tkinter.messagebox.showinfo(parent=window, title="Error",
                                              message="File not found !")
        window.destroy()

    def renderendgame(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))
        self.message = None

        fontTitle = pygame.font.SysFont('arial', 100)

        final_score = fontTitle.render("Score : " + str(self.model.gamescore) + "!", True, (133, 193, 233))
        self.screen.blit(final_score, (375, 300))

        self.buttonMenuReturn.draw(self.screen)
        pygame.display.flip()

    def rendernewbestscore(self, score):
        window = tkinter.Tk()
        w = 300  # width for the Tk root
        h = 400
        ws = window.winfo_screenwidth()  # width of the screen
        hs = window.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        window.withdraw()
        infobox = tkinter.messagebox.showinfo(parent=window, title="Congrats !", message="New best score : " + str(score) +" !")
        window.destroy()

    def renderloading(self):

        fontTitle = pygame.font.SysFont('arial', 100)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))
        text = fontTitle.render("Loading", True, (133, 193, 233))
        if self.counter == 3:
            self.counter =0

        now = pygame.time.get_ticks()

        if now - self.last >= self.cooldown:
            self.last = now
            self.counter += 1
        if self.counter == 0:
            text = fontTitle.render("Loading.", True, (133, 193, 233))
        elif self.counter == 1:
            text = fontTitle.render("Loading..", True, (133, 193, 233))
        elif self.counter == 2:
            text = fontTitle.render("Loading...", True, (133, 193, 233))

        self.screen.blit(text, (375, 300))


        pygame.display.flip()






    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """
        self.imgMenu = pygame.image.load("assets/reetm.jpg")
        pygame.font.init()
        pygame.display.set_caption('Reetm')
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.buttonMenuPlay = pygameInterface.Button(480, 650, 191, 64,
                                                     label="Choose file",
                                                     color=(255, 0, 0),
                                                     colorLabel=(0, 0, 0),
                                                     placeHolder= pygameInterface.StyleButton(480, 650, 191, 64, label="Choose file", color=(0, 0, 0),
                                                                                              colorLabel=(255, 0, 0))
                                                     )

        self.buttonMenuReturn = pygameInterface.Button(600, 550, 191, 64,
                                                       label="Continue",
                                                       color=(255, 0, 0),
                                                       colorLabel=(0, 0, 0),
                                                       placeHolder= pygameInterface.StyleButton(600, 550, 191, 64, label="Continue", color=(0, 0, 0),
                                                                                                colorLabel=(255, 0, 0))
                                                       )

        self.buttonLibrary = pygameInterface.Button(480,380, 191, 64,
                                       label="Library",
                                       color=(255, 0, 0),
                                       colorLabel=(0, 0, 0),
                                       placeHolder=pygameInterface.StyleButton(480,380, 191, 64, label="Library", color=(0, 0, 0),
                                                               colorLabel=(255, 0, 0))
                                       )

        self.YOUTUBELINKTEXTBOX = pygameInterface.Textbox(380, 380, 500, 50)

        self.BUTTONYOUTUBELINK = pygameInterface.Button(390, 900, 115, 30,
                                   image="assets/DownloadButton.jpg",
                                   placeHolder=pygameInterface.StyleButton(390, 900, 115, 30, image="assets/DownloadButtonSelect.jpg"))

        self.BUTTONRESET = pygameInterface.Button(390, 1025, 115, 30,
                             image="assets/ClearButton.jpg",
                             placeHolder=pygameInterface.StyleButton(390, 1025, 115, 30, image="assets/ClearButtonSelect.jpg"))

        # print(self.clock)
        self.smallfont = pygame.font.Font(None, 40)
        self.isinitialized = True
