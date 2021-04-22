import pygame
from event.eventmanager import *
from beatTraitement.AutomaticBeats import AutomaticBeats
import tkinter
import tkinter.filedialog

TIMEADVENCE = 1000  # time of advance in second


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

    def getPosition(self):
        return self.position

    def getTime(self):
        return self.time

    def timeToArrive(self):
        return self.time - self.timeSend

    def speed(self):
        return self.distanceInPixel / self.timeToArrive()

    def updatePosition(self):
        actualTime = pygame.time.get_ticks()
        durationLife = actualTime - self.timeSend
        self.position = durationLife * self.speed()


pygame.font.init()


class Button(object):
    def __init__(self, left, top, width, height, callback, label=None, image=None,
                 legend=None, color=(255, 255, 255), colorLabel=(0, 0, 0), fontLabel=pygame.font.Font(None, 25),
                 fontLegend=pygame.font.SysFont('Arial', 25)):

        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.image = image
        self.callback = callback
        self.label = label
        self.legend = legend
        self.color = color
        self.colorLabel = colorLabel
        self.fontLabel = fontLabel
        self.fontLegend = fontLegend

    def surface(self):
        return pygame.Surface((self.width, self.height))

    def rectangle(self):
        return self.surface().get_rect(topleft=(self.top, self.left))

    def cliked(self, event):
        if isinstance(event, MouseClickEvent):
            if pygame.Rect.collidepoint(self.rectangle(), event.getPos()):
                if self.callback:
                    self.callback()

    def draw(self, screen):
        surfaceButton = self.surface()
        if self.image is not None:
            img = pygame.image.load(self.image).convert_alpha()
            pygame.transform.smoothscale(img, (self.width, self.height), dest_surface=surfaceButton)
        else:
            pygame.Surface.fill(surfaceButton, self.color)

        if self.label is not None:
            labelSurface = self.fontLabel.render(self.label, True, self.colorLabel)
            surfaceButton.blit(labelSurface, (self.width / 2, self.height / 2))

        screen.blit(surfaceButton, (self.top, self.width))


class GameEngine(object):

    def __init__(self, evManager):

        # variable for game state
        self.time_start = None
        self.file = None
        self.arrayBeat = None
        self.listBeat = None
        self.passTimeMusic = False
        self.buttonMenuPlay = Button(100, 100, 100, 100, self.buttonPlay, label="Play")

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

    def notify(self, event):

        self.buttonMenuPlay.cliked(event)
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

    def beatNow(self):  # envoie un beat
        if (len(self.listBeat) != 0) and (pygame.time.get_ticks() >= (self.listBeat[0] - TIMEADVENCE)):
            print("beat :", self.listBeat[0])
            print(self.listBeat)
            newBeatEvent = BeatEvent(Beat(self.listBeat[0]))
            self.evManager.Post(newBeatEvent)
            self.listBeat.pop(0)

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
            elif self.state.peek() == STATE_PLAY and self.file is not None:
                self.beatNow()
                if not self.passTimeMusic and pygame.time.get_ticks() >= TIMEADVENCE:
                    self.passTimeMusic = True
                    pygame.mixer.music.play()
            else:
                self.running = False

    def initialize(self):
        if self.state.peek() == STATE_MENU:
            pass
        elif self.state.peek() == STATE_LIBRARY:
            pass
        elif self.state.peek() == STATE_PLAY:
            self.arrayBeat = AutomaticBeats(self.file).getinstruments()['Snare'] * 1000 + TIMEADVENCE

            pygame.mixer.init()
            pygame.mixer.music.load(self.file)

            self.arrayBeat = self.arrayBeat + pygame.time.get_ticks()
            self.listBeat = self.arrayBeat.tolist()


# State machine constants for the StateMachine class below
STATE_MENU = 1
STATE_LIBRARY = 2
STATE_PLAY = 3


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
