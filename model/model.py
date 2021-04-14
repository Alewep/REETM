import numpy as np
import pygame
from beatTraitement.AutomaticBeats import *
from event.eventmanager import *

TIMEADVENCE = 1000 # time of advance in second


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


class GameEngine(object):
    """
    Tracks the game state.
    """

    def __init__(self, evManager, tempo=180, duration=30):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        
        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        tempo (int) : tempo in bpm of the music
        duration (int) :  duration in seconds of the music
        """
        self.arrayBeat = AutomaticBeats('/home/etudiant/stage/amazonia.wav').getinstruments()['Snare'] * 1000 + TIMEADVENCE
        file = "/home/etudiant/stage/amazonia.wav"
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        self.passTime = False

        self.listBeat = self.arrayBeat.tolist()
        self.tempo = tempo
        self.duration = duration
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False

    def notify(self, event):
        """
        Called by an event in the message queue. 
        """

        if isinstance(event, QuitEvent):
            self.running = False

    def beatNow(self):  # envoie un beat
        if (len(self.listBeat) != 0) and (pygame.time.get_ticks() >= (self.listBeat[0] - TIMEADVENCE)):
            print("beat :", self.listBeat[0])
            print(self.listBeat)
            newBeatEvent = BeatEvent(Beat(self.listBeat[0]))
            self.evManager.Post(newBeatEvent)
            self.listBeat.pop(0)

    def run(self):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        while self.running:
            newTick = TickEvent()
            self.evManager.Post(newTick)
            self.beatNow()
            if not self.passTime and pygame.time.get_ticks() >= TIMEADVENCE:
                pygame.mixer.music.unpause()
                self.passTime = True
