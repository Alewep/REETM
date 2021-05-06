import tkinter

import pygame

import addons.library
from mvc.eventmanager import *
from addons.AutomaticBeats import AutomaticBeats
from tkinter import *
from tkinter.ttk import *
import numpy as np
import os
TIMEADVENCE = 2000  # time of advance in second

# constants used to determine the score

DELTA_BAD = 150  # ms
DELTA_MEH = 100  # ms
DELTA_GOOD = 50  # ms
DELTA_EXCELLENT = 25  # ms

# score depending on result

SCORE_FAIL = -0.5
SCORE_BAD = 0.25
SCORE_MEH = 0.5
SCORE_GOOD = 0.75
SCORE_EXCELLENT = 1


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
        self.window = Tk()  # create a Tk root window

        w = 300  # width for the Tk root
        h = 400  # height for the Tk root

        # get screen width and height
        ws = self.window.winfo_screenwidth()  # width of the screen
        hs = self.window.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.stockSongs = addons.library.getFiles('preprocessed')
        self.listeSongs = Combobox(self.window, values = self.stockSongs, state='readonly')
        self.listeSongs.pack()
        self.buttonconfirm = tkinter.Button(text = "confirmation")
        self.buttonconfirm.pack()
        self.buttonconfirm.config(command = self.confirmation)
        self.clicked = False
        self.clikedquit = False
        self.chosenfile = None

        self.window.protocol('WM_DELETE_WINDOW', self.quit)  # root is your root window

    def quit(self):
        self.window.destroy()
        self.clikedquit = True


    def confirmation(self):
        self.chosenfile = self.listeSongs.get()
        self.clicked = True
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

        self.gamescore = 0

        self.passTimeMusic = False

        self.musicnamelist = None

        # general
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()

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

        if isinstance(event, FileChooseListEvent):
            self.file = None
            self.musicnamelist = event.file
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

        if isinstance(event, FileChooseEvent):
            self.file = event.file
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

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

        list_bad = work_list[(work_list > beat_time - DELTA_BAD) & (work_list < beat_time + DELTA_BAD)]
        success_class = 'fail'
        score_to_add = SCORE_FAIL
        if len(list_bad) > 0:
            list_meh = work_list[(work_list > beat_time - DELTA_MEH) & (work_list < beat_time + DELTA_MEH)]
            success_class = 'bad'
            score_to_add = SCORE_BAD
            beat_to_delete = list_bad[0]
            if len(list_meh) > 0:
                list_good = work_list[(work_list > beat_time - DELTA_GOOD) & (work_list < beat_time + DELTA_GOOD)]
                success_class = 'meh'
                score_to_add = SCORE_MEH
                beat_to_delete = list_meh[0]
                if len(list_good) > 0:
                    list_excellent = work_list[
                        (work_list > beat_time - DELTA_EXCELLENT) & (work_list < beat_time + DELTA_EXCELLENT)]
                    success_class = 'good'
                    score_to_add = SCORE_GOOD
                    beat_to_delete = list_good[0]
                    if len(list_excellent) > 0:
                        success_class = 'excellent'
                        score_to_add = SCORE_EXCELLENT
                        beat_to_delete = list_excellent[0]

        self.gamescore += score_to_add
        if beat_to_delete is not None:
            work_list = np.delete(work_list, np.where(work_list == beat_to_delete))
        return success_class

    def savebestscore(self):
        musicfile = AutomaticBeats(self.file)
        bestscorefilepath = "preprocessed/"+musicfile.getmusicname()+"/bestscore.csv"
        if not os.path.exists(bestscorefilepath):
            array_score = np.around(np.array([self.gamescore]),decimals=2)
            np.savetxt(bestscorefilepath, array_score)
            self.evManager.Post(newBestScoreEvent(self.gamescore))
        else:
            saved_score = np.loadtxt(bestscorefilepath)
            if self.gamescore > saved_score:
                array_score = np.around(np.array([self.gamescore]),decimals=2)
                np.savetxt(bestscorefilepath, array_score)
                self.evManager.Post(newBestScoreEvent(self.gamescore))


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
                self.savebestscore()
            elif self.state.peek() == STATE_CHOOSEFILE:
                pass
            elif self.state.peek() == STATE_PLAY:
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
        elif self.state.peek() == STATE_CHOOSEFILE:
            pass
        elif self.state.peek() == STATE_PLAY:
            if self.file is not None:
                self.passTimeMusic = False
                musicfile = AutomaticBeats(self.file)
                instruments = musicfile.getinstruments()
                musicfile.savejson()
                musicfile.copy()

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

            if self.musicnamelist is not None:
                self.passTimeMusic = False
                self.file = "preprocessed/"+self.musicnamelist+"/"+self.musicnamelist+".wav"
                musicfile = AutomaticBeats(self.file)
                instruments = "preprocessed/"+self.musicnamelist+"/instruments.json"
                dict = addons.library.json_to_dict(instruments)
                self.arrayKick = dict["Kick"] * 1000 + TIMEADVENCE
                self.arraySnare = dict["Snare"] * 1000 + TIMEADVENCE
                self.arrayHihat = dict["Hihat"] * 1000 + TIMEADVENCE

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
STATE_CHOOSEFILE = 5


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
