import pygame
from beatTraitement.AutomaticBeats import *
from event.eventmanager import *

TIMEADVENCE = 1000 # time of advance in second
delta_fail = 150 #ms
delta_meh = 100 #ms
delta_good = 50 #ms
delta_excellent = 25 #ms

#score depending on result

score_fail = 0
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

    def __init__(self, evManager):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        
        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        tempo (int) : tempo in bpm of the music
        duration (int) :  duration in seconds of the music
        """
        self.instruments = AutomaticBeats('/home/adrien/TER/REETM/amazonia.wav').getinstruments()
        self.arrayKick = self.instruments['Kick'] * 1000 + TIMEADVENCE
        self.arraySnare = self.instruments['Snare'] * 1000 + TIMEADVENCE
        self.arrayHihat = self.instruments['Hihat'] * 1000 + TIMEADVENCE
        file = '/home/adrien/TER/REETM/amazonia.wav'
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        self.passTime = False

        self.listKick = self.arrayKick.tolist()
        self.listSnare = self.arraySnare.tolist()
        self.listHihat = self.arrayHihat.tolist()
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.gamescore = 0

    def getScore(self):
        return self.gamescore

    def notify(self, event):
        """
        Called by an event in the message queue.
        """
        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, InputEvent):
            newScoreEvent = ScoreEvent(self.inputVerifBeat(event.getTime(), event.getClasseInstrument()), self.gamescore)
            self.evManager.Post(newScoreEvent)

    def instrumentNow(self, liste_beat, num_classe):
        if (len(liste_beat) != 0) and (pygame.time.get_ticks() >= (liste_beat[0] - TIMEADVENCE)):
            newBeatEvent = BeatEvent(Beat(liste_beat[0]),num_classe)
            self.evManager.Post(newBeatEvent)
            liste_beat.pop(0)

    def inputVerifBeat(self, beat_time,instrument_class): #update score depending and returns the type of success (fail, bad, meh, good, excellent)

        # margin time to determine score for a beat

        #determine the list we work on (kicks list, snare list... )depending on the key pressed
        if instrument_class == 0:
            work_list = self.arrayKick
        if instrument_class == 1:
            work_list = self.arraySnare
        if instrument_class == 2:
            work_list = self.arrayHihat

        list_fail = work_list[(work_list > beat_time - delta_fail) & (work_list < beat_time + delta_fail)]
        success_class = 'fail'
        score_to_add = score_fail
        if len(list_fail) > 0:
            list_meh = work_list[(work_list > beat_time - delta_meh ) & (work_list < beat_time + delta_meh)]
            success_class = 'bad'
            score_to_add = score_bad
            if len(list_meh) > 0:
                list_good = work_list[(work_list > beat_time - delta_good) & (work_list < beat_time + delta_good)]
                success_class = 'meh'
                score_to_add = score_meh
                if len(list_good) > 0:
                    list_excellent = work_list[(work_list > beat_time - delta_excellent) & (work_list < beat_time + delta_excellent)]
                    success_class = 'good'
                    score_to_add = score_good
                    if len(list_excellent) > 0:
                        success_class = 'excellent'
                        score_to_add = score_excellent

        self.gamescore += score_to_add
        print("Succès :" + success_class)
        print("Score actuel :" + str(self.gamescore))
        return success_class

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
            self.instrumentNow(self.listKick,0)
            self.instrumentNow(self.listSnare,1)
            self.instrumentNow(self.listHihat,2)
            if not self.passTime and pygame.time.get_ticks() >= TIMEADVENCE:
                pygame.mixer.music.unpause()
                self.passTime = True

