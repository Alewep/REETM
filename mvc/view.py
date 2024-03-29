import tkinter.messagebox

import pygame.display

from mvc.eventmanager import *
import mvc.timer as timer
from mvc.model import *
from interface import pygameInterface
from interface import tkinterInterface
import tkinter
import tkinter.filedialog

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

        """

        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.screen = None
        self.clock = None
        self.imgMenu = None

        self.instruments_state = []

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
        self.last = timer.time()

        self.positions = self.positions_difficuly()

        self.video = None

        self.YOUTUBELINKTEXTBOX = None
        self.BUTTONYOUTUBELINK = None
        self.BUTTONRESET = None
        self.BUTTONPAUSE = None
        self.PANELPAUSE = None
        self.BUTTONPASTE = None

    # add a hit to the screen
    def resetplay(self):
        self.video = None
        self.instruments_state = []
        self.message = None

    def addInstrument(self, instrument, numberclass):
        if numberclass + 1 > len(self.instruments_state):
            for i in range(len(self.instruments_state), numberclass + 1):
                self.instruments_state.append([])
        _, height = pygame.display.get_surface().get_size()
        instrument.setDistanceInPixel(height - self.model.config["checkligne"])
        self.instruments_state[numberclass].append(instrument)

    def updateInstrument_state(self, liste_instrument):
        _, height = pygame.display.get_surface().get_size()
        for i in range(len(liste_instrument)):
            liste_instrument[i].updatePosition()
        liste_instrument[:] = [x for x in liste_instrument if x.position < height]

    def isexcellent(self, beat):
        return (beat.time < timer.time() + self.model.config["delta_excellent"]) and (
                beat.time > timer.time() - self.model.config["delta_meh"])

    def positions_difficuly(self):
        middle = screen_width / 2
        if self.model.config['difficulty'] == 1:
            return [middle]
        elif self.model.config['difficulty'] == 2:
            return [middle - 100, middle + 100]
        elif self.model.config['difficulty'] == 3:
            return [middle - 100, middle, middle + 100]

    # displays beats, their color depending on whether they are in the "excellent" range
    def drawInstruments(self):
        colors = [(166, 89, 89), (89, 89, 166), (166, 166, 89)]
        colorsExecellent = [(255, 0, 0), (0, 0, 255), (255, 255, 0)]

        for i in range(len(self.instruments_state)):
            for beat in self.instruments_state[i]:
                color = colors[i]
                if self.isexcellent(beat):
                    color = colorsExecellent[i]
                pygame.draw.circle(self.screen, color, (self.positions[i], beat.position), 25)

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

    def displayScore(self):
        police = pygame.font.Font(None, 72)
        score_txt = 'Score : ' + str(self.model.gamescore)
        score = police.render(score_txt, True, pygame.Color(255, 255, 255))
        self.screen.blit(score, [screen_width - score.get_width(), 5])

    def displayBestScore(self):
        police = pygame.font.Font(None, 50)
        best_score_txt = "Best Score : " + (str(self.model.bestscore) if self.model.bestscore is not None else "N/A")
        score = police.render(best_score_txt, True, pygame.Color(255, 255, 255))
        self.screen.blit(score, [screen_width - score.get_width(), 55])

    def displayDifficulty(self):
        if self.model.config['difficulty'] == 1:
            difficuly_txt = "Easy"
            color = pygame.Color(0, 255, 0)
        elif self.model.config['difficulty'] == 2:
            difficuly_txt = "Medium"
            color = pygame.Color(255, 127, 0)
        elif self.model.config['difficulty'] == 3:
            difficuly_txt = "Hard"
            color = pygame.Color(255, 0, 0)

        police = pygame.font.Font(None, 40)
        difficulty = police.render("Difficulty : " + difficuly_txt, True, color)
        self.screen.blit(difficulty, [5, 80])

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

        if isinstance(event, StateChangeEvent):
            if event.state == STATE_PLAY:
                self.video = None
        elif isinstance(event, TickEvent):
            currentstate = self.model.state.peek()
            if currentstate == STATE_MENU:
                self.rendermenu()
            if currentstate == STATE_PLAY:
                self.renderplay()
            if currentstate == STATE_LIBRARY:
                self.renderlibrary()
            if currentstate == STATE_ENDGAME:
                self.video = None
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
            self.addInstrument(event.instrument, event.num)
        elif isinstance(event, ScoreEvent):
            self.message = event.type_success
        elif isinstance(event, InputEvent):
            if event.classe == 0:
                self.a_pressed = event.pressed
            if event.classe == 1:
                self.z_pressed = event.pressed
            if event.classe == 2:
                self.e_pressed = event.pressed
        elif isinstance(event, newBestScoreEvent):
            self.rendernewbestscore(event.newbestscore)
        elif isinstance(event, StateChangeEvent) | isinstance(event, ResetPlayEvent):
            if (isinstance(event, ResetPlayEvent)) or (event.state == STATE_PLAY):
                self.initializeVideo()

    # displays the "check" circles, their outline becoming colored and thicker if you press the key corresponding to their instrument

    def drawCheckCircles(self, height):
        color = (135, 206, 235)

        if self.a_pressed:
            pygame.draw.circle(self.screen, pygame.color.Color(255, 0, 0),
                               [self.positions[0], height - self.model.config["checkligne"]], 31, 6)
        else:
            pygame.draw.circle(self.screen, color, [self.positions[0], height - self.model.config["checkligne"]], 25, 1)

        if self.model.config['difficulty'] in [2, 3]:
            if self.z_pressed:
                pygame.draw.circle(self.screen, pygame.color.Color(0, 0, 255),
                                   [self.positions[1], height - self.model.config["checkligne"]], 31, 6)
            else:
                pygame.draw.circle(self.screen, color, [self.positions[1], height - self.model.config["checkligne"]],
                                   25, 1)

            if self.model.config['difficulty'] == 3:
                if self.e_pressed:
                    pygame.draw.circle(self.screen, pygame.color.Color(255, 255, 0),
                                       [self.positions[2], height - self.model.config["checkligne"]], 31, 6)
                else:
                    pygame.draw.circle(self.screen, color,
                                       [self.positions[2], height - self.model.config["checkligne"]], 25, 1)

    def drawCheckLetters(self, height):
        color = (135, 206, 235)
        police = pygame.font.Font(None, 60)

        letter_a = police.render("A", True, pygame.Color(255, 0, 0))
        letter_z = police.render("Z", True, pygame.Color(0, 0, 255))
        letter_e = police.render("E", True, pygame.Color(255, 255, 0))

        self.screen.blit(letter_a, [self.positions[0] - 15, height - self.model.config["checkligne"] + 25])

        if self.model.config['difficulty'] in [2, 3]:
            self.screen.blit(letter_z, [self.positions[1] - 15, height - self.model.config["checkligne"] + 25])

            if self.model.config['difficulty'] == 3:
                self.screen.blit(letter_e, [self.positions[2] - 15, height - self.model.config["checkligne"] + 25])

    def renderplay(self):
        """
        Draw the current game state on screen.
        Does nothing if isinitialized == False (pygame.init failed)
        """
        self.screen.fill((0, 0, 0))
        if self.video is None:
            self.initializeVideo()
        else:
            self.video.update(time=timer.time() - self.model.config["timeadvence"])
            self.video.draw(self.screen)

        self.BUTTONPAUSE.draw(self.screen)
        self.drawCheckCircles(screen_height)
        self.drawCheckLetters(screen_height)

        if self.message is not None:
            self.displaySucces(self.message)

        if not self.model.pause:
            for instrument in self.instruments_state:
                self.updateInstrument_state(instrument)
            self.drawInstruments()
        else:
            self.drawInstruments()
            self.PANELPAUSE.draw(self.screen)

        self.displayScore()
        self.displayBestScore()

        # flip the display to show whatever we drew
        pygame.display.flip()

    def rendermenu(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))

        fontTitle = pygame.font.SysFont('arial', 200)

        title = fontTitle.render("Reetm", True, (133, 193, 233))

        self.screen.blit(title, (350, 150))

        self.YOUTUBELINKTEXTBOX.draw(self.screen)
        self.BUTTONYOUTUBELINK.draw(self.screen)
        self.BUTTONRESET.draw(self.screen)
        self.BUTTONPASTE.draw(self.screen)

        self.buttonMenuPlay.draw(self.screen)
        self.buttonLibrary.draw(self.screen)
        self.buttonEasy.draw(self.screen)
        self.buttonMedium.draw(self.screen)
        self.buttonHard.draw(self.screen)
        self.displayDifficulty()
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
        self.songs_list = tkinterInterface.ComboBox(folderPath=PATHOFLIBRARY, title="Library")
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
        infobox = tkinter.messagebox.showinfo(parent=window, title="Congrats !",
                                              message="New best score : " + str(score) + " !")
        window.destroy()

    def renderloading(self):

        fontTitle = pygame.font.SysFont('arial', 100)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.imgMenu, (0, 0))
        text = fontTitle.render("Loading", True, (255, 255, 255))
        if self.counter == 3:
            self.counter = 0

        now = timer.time()

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

    def initializeVideo(self):
        video_path = self.model.getMusicRessources('video')
        if video_path is not None:
            self.video = pygame.sprite.Group()
            self.video.add(pygameInterface.VideoSprite(self.screen.get_rect(), video_path))

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
                                                     placeHolder=pygameInterface.StyleButton(480, 650, 191, 64,
                                                                                             label="Choose file",
                                                                                             color=(0, 0, 0),
                                                                                             colorLabel=(255, 0, 0))
                                                     )
        self.PANELPAUSE = pygameInterface.PauseScreen(380, 250, 500, 150,
                                                      {
                                                          "buttonHome": pygameInterface.Button(50, 30, 100, 100,
                                                                                               image="assets/home.png",
                                                                                               placeHolder=pygameInterface.StyleButton(
                                                                                                   50, 30, 100, 100,
                                                                                                   image="assets/holdhome.png",
                                                                                               )),
                                                          "buttonPlay": pygameInterface.Button(50, 180, 100, 100,
                                                                                               image="assets/play.png",
                                                                                               placeHolder=pygameInterface.StyleButton(
                                                                                                   50, 180, 100, 100,
                                                                                                   image="assets/holdplay.png")),
                                                          "buttonRetry": pygameInterface.Button(50, 330, 100, 100,
                                                                                                image="assets/retry.png",
                                                                                                placeHolder=pygameInterface.StyleButton(
                                                                                                    50, 330, 100, 100,
                                                                                                    image="assets/holdretry.png"))
                                                      }
                                                      , image="assets/panel.png"

                                                      )

        self.buttonMenuReturn = pygameInterface.Button(600, 550, 191, 64,
                                                       label="Continue",
                                                       color=(255, 0, 0),
                                                       colorLabel=(0, 0, 0),
                                                       placeHolder=pygameInterface.StyleButton(600, 550, 191, 64,
                                                                                               label="Continue",
                                                                                               color=(0, 0, 0),
                                                                                               colorLabel=(255, 0, 0))
                                                       )

        self.buttonLibrary = pygameInterface.Button(480, 380, 191, 64,
                                                    label="Library",
                                                    color=(255, 0, 0),
                                                    colorLabel=(0, 0, 0),
                                                    placeHolder=pygameInterface.StyleButton(480, 380, 191, 64,
                                                                                            label="Library",
                                                                                            color=(0, 0, 0),
                                                                                            colorLabel=(255, 0, 0))
                                                    )

        self.buttonEasy = pygameInterface.Button(5, 10, 70, 70,
                                                 label="Easy",
                                                 color=(0, 255, 0),
                                                 colorLabel=(0, 0, 0),
                                                 placeHolder=pygameInterface.StyleButton(5, 10, 70, 70,
                                                                                         label="Easy",
                                                                                         color=(0, 0, 0),
                                                                                         colorLabel=(0, 255, 0))
                                                 )
        self.buttonMedium = pygameInterface.Button(5, 90, 70, 70,
                                                   label="Medium",
                                                   color=(255, 127, 0),
                                                   colorLabel=(0, 0, 0),
                                                   placeHolder=pygameInterface.StyleButton(5, 90, 70, 70,
                                                                                           label="Medium",
                                                                                           color=(0, 0, 0),
                                                                                           colorLabel=(255, 127, 0))
                                                   )
        self.buttonHard = pygameInterface.Button(5, 170, 70, 70,
                                                 label="Hard",
                                                 color=(255, 0, 0),
                                                 colorLabel=(0, 0, 0),
                                                 placeHolder=pygameInterface.StyleButton(5, 170, 70, 70,
                                                                                         label="Hard",
                                                                                         color=(0, 0, 0),
                                                                                         colorLabel=(255, 0, 0))
                                                 )

        self.YOUTUBELINKTEXTBOX = pygameInterface.Textbox(380, 380, 500, 50)

        self.BUTTONYOUTUBELINK = pygameInterface.Button(390, 900, 115, 30,
                                                        image="assets/DownloadButton.jpg",
                                                        placeHolder=pygameInterface.StyleButton(390, 900, 115, 30,
                                                                                                image="assets/DownloadButtonSelect.jpg"))

        self.BUTTONPASTE = pygameInterface.Button(377, 330, 41, 50,
                                                  image="assets/PasteButton.png",
                                                  placeHolder=pygameInterface.StyleButton(377, 330, 41, 50,
                                                                                          image="assets/PasteButton.png"))

        self.BUTTONRESET = pygameInterface.Button(390, 1025, 115, 30,
                                                  image="assets/ClearButton.jpg",
                                                  placeHolder=pygameInterface.StyleButton(390, 1025, 115, 30,
                                                                                          image="assets/ClearButtonSelect.jpg"))
        self.BUTTONPAUSE = pygameInterface.Button(600, 5, 104, 90, image="assets/pause.png",
                                                  placeHolder=pygameInterface.StyleButton(600, 5, 104, 90,
                                                                                          image="assets/holdpause.png"))

        self.isinitialized = True
