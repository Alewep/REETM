import pygame
from event.eventmanager import *
from beatTraitement.AutomaticBeats import AutomaticBeats
from library import library
import tkinter
import tkinter.filedialog
from tkinter.ttk import *
from tkinter import *
import numpy as np

TIMEADVENCE = 2000  # time of advance in second

# constants used to determine the score

delta_bad = 150  # ms
delta_meh = 100  # ms
delta_good = 50  # ms
delta_excellent = 25  # ms

# score depending on result

score_fail = -0.5
score_bad = 0.25
score_meh = 0.5
score_good = 0.75
score_excellent = 1


class Beat(object):
    def __init__(self, time):
        self.time = time
        self.timeSend = pygame.time.get_ticks()
        self.distanceInPixel = 0
        self.position = 0

    def setDistanceInPixel(self, distanceInPixel):
        self.distanceInPixel = distanceInPixel

    def setTimeSend(self):
        self.timeSend = pygame.time.get_ticks()

    def timeToArrive(self):
        return self.time - self.timeSend

    def speed(self):
        return self.distanceInPixel / self.timeToArrive()

    def updatePosition(self):
        actualTime = pygame.time.get_ticks()
        durationLife = actualTime - self.timeSend
        self.position = durationLife * self.speed()


pygame.font.init()


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


class ComboBox(object):

    def __init__(self):
        self.window = tkinter.Tk()

        w = 225  # width for the Tk root
        h = 300  # height for the Tk root
        ws = self.window.winfo_screenwidth()  # width of the screen
        hs = self.window.winfo_screenheight()  # height of the screen
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        Label(self.window, text="Choose a song to play !", foreground='black', font = ("Times New Roman", 15))
        Label(self.window, text="Select a song :",
                  font=("Times New Roman", 12)).grid(column=0,
                                                     row=5, padx=35, pady=25)
        self.songSelect = StringVar()
        self.stockSongs = library.getFiles(r'./tests','.wav')
        self.listeSongs = Combobox(self.window, textvariable=self.songSelect, values=self.stockSongs, state='readonly')
        self.listeSongs.grid(padx=35)
        self.listeSongs.bind('<<ComboboxSelected>>', self.songSelected)

    def songSelected(self,event):
        self.window.destroy()


class GameEngine(object):

    def __init__(self, evManager):

        # variable for game state
        self.time_start = None
        self.file = None
        self.arrayKick = None
        self.arraySnare = None
        self.arrayHihat = None

        self.listKick = None
        self.listSnare = None
        self.listHihat = None

        self.passTimeMusic = False

        # general
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()

    def buttonPlay(self):
        top = tkinter.Tk()
        top.withdraw()  # hide window
        self.file = tkinter.filedialog.askopenfilename(parent=top, title="Select a Music in wav format",
                                                       filetypes=(("wav files",
                                                                   "*.wav*"),
                                                                  ("all files",
                                                                   "*.*")))
        top.destroy()
        self.evManager.Post(StateChangeEvent(STATE_PLAY))
        self.gamescore = 0

    def buttonReturn(self):
        self.evManager.Post(StateChangeEvent(STATE_MENU))
        self.gamescore = 0

    def notify(self, event):

        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)
                self.initialize()
        if isinstance(event, InputEvent):
            if event.pressed:
                newScoreEvent = ScoreEvent(self.inputVerifBeat(event.time, event.classe), self.gamescore)
                self.evManager.Post(newScoreEvent)
        if isinstance(event, ButtonMenuPlayEvent):
            self.buttonPlay()
        if isinstance(event, ButtonMenuReturnEvent):
            self.buttonReturn()

    def instrumentNow(self, liste_beat, num_classe):
        if (len(liste_beat) != 0) and (pygame.time.get_ticks() >= (liste_beat[0] - TIMEADVENCE)):
            newBeatEvent = BeatEvent(Beat(liste_beat[0]), num_classe)
            self.evManager.Post(newBeatEvent)
            liste_beat.pop(0)

    def inputVerifBeat(self, beat_time,
                       instrument_class):  # update score depending and returns the type of success (fail, bad, meh, good, excellent)

        # margin time to determine score for a beat

        # determine the list we work on (kicks list, snare list... )depending on the key pressed
        if instrument_class == 0:
            work_list = self.arrayKick
        if instrument_class == 1:
            work_list = self.arraySnare
        if instrument_class == 2:
            work_list = self.arrayHihat

        beat_to_delete = None

        list_bad = work_list[(work_list > beat_time - delta_bad) & (work_list < beat_time + delta_bad)]
        success_class = 'fail'
        score_to_add = score_fail
        if len(list_bad) > 0:
            list_meh = work_list[(work_list > beat_time - delta_meh) & (work_list < beat_time + delta_meh)]
            success_class = 'bad'
            score_to_add = score_bad
            beat_to_delete = list_bad[0]
            if len(list_meh) > 0:
                list_good = work_list[(work_list > beat_time - delta_good) & (work_list < beat_time + delta_good)]
                success_class = 'meh'
                score_to_add = score_meh
                beat_to_delete = list_meh[0]
                if len(list_good) > 0:
                    list_excellent = work_list[
                        (work_list > beat_time - delta_excellent) & (work_list < beat_time + delta_excellent)]
                    success_class = 'good'
                    score_to_add = score_good
                    beat_to_delete = list_good[0]
                    if len(list_excellent) > 0:
                        success_class = 'excellent'
                        score_to_add = score_excellent
                        beat_to_delete = list_excellent[0]

        self.gamescore += score_to_add
        if beat_to_delete is not None:
            work_list = np.delete(work_list,np.where(work_list == beat_to_delete))
        # print("Succès :" + success_class)
        # print("Score actuel :" + str(self.gamescore))
        return success_class

    def run(self):

        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(STATE_MENU)
        while self.running:
            newTick = TickEvent()
            self.evManager.Post(newTick)
            if self.state.peek() == STATE_MENU:
                pass
            elif self.state.peek() == STATE_LIBRARY:
                pass
            elif self.state.peek() == STATE_ENDGAME:
                pass
            elif self.state.peek() == STATE_PLAY and self.file is not None:
                self.instrumentNow(self.listKick, 0)
                self.instrumentNow(self.listSnare, 1)
                self.instrumentNow(self.listHihat, 2)
                if not self.passTimeMusic and pygame.time.get_ticks() >= TIMEADVENCE + self.time_start:
                    self.passTimeMusic = True
                    pygame.mixer.music.play()
                if pygame.time.get_ticks() >= self.duration + self.time_start + TIMEADVENCE:
                    self.evManager.Post(StateChangeEvent(STATE_ENDGAME))
            else:
                self.running = False

    def initialize(self):
        if self.state.peek() == STATE_MENU:
            pass
        elif self.state.peek() == STATE_LIBRARY:
            pass
        elif self.state.peek() == STATE_ENDGAME:
            pass
        elif self.state.peek() == STATE_PLAY:
            self.passTimeMusic = False
            musicfile = AutomaticBeats(self.file)
            instruments = musicfile.getinstruments()
            self.arrayKick = instruments["Kick"] * 1000 + TIMEADVENCE
            self.arraySnare = instruments["Snare"] * 1000 + TIMEADVENCE
            self.arrayHihat = instruments["Hihat"] * 1000 + TIMEADVENCE

            pygame.mixer.init()
            pygame.mixer.music.load(self.file)
            self.duration = musicfile.getduration() * 1000  # ms
            self.gamescore = 0
            self.time_start = pygame.time.get_ticks()
            self.arrayKick = self.arrayKick + pygame.time.get_ticks()
            self.arraySnare = self.arraySnare + pygame.time.get_ticks()
            self.arrayHihat = self.arrayHihat + pygame.time.get_ticks()

            self.listKick = self.arrayKick.tolist()
            self.listSnare = self.arraySnare.tolist()
            self.listHihat = self.arrayHihat.tolist()


# State machine constants for the StateMachine class below
STATE_MENU = 1
STATE_LIBRARY = 2
STATE_PLAY = 3
STATE_ENDGAME = 4


class StateMachine(object):
    """
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    """

    def __init__(self):
        self.statestack = []

    def peek(self):
        """
        Returns the current state without altering the stack.
        Returns None if the stack is empty.
        """
        try:
            return self.statestack[-1]
        except IndexError:
            # empty stack
            return None

    def pop(self):
        """
        Returns the current state and remove it from the stack.
        Returns None if the stack is empty.
        """
        try:
            self.statestack.pop()
            return len(self.statestack) > 0
        except IndexError:
            # empty stack
            return None

    def push(self, state):
        """
        Push a new state onto the stack.
        Returns the pushed value.
        """
        self.statestack.append(state)
        return state
