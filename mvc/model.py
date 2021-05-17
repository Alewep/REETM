from mvc.eventmanager import *
from addons.AutomaticBeats import AutomaticBeats
from addons.AutomaticBeats import simplification
from addons import library

import pygame
import numpy as np
import os
import json
import wget
import subprocess
from pytube import YouTube


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


class GameEngine(object):

    def __init__(self, evManager):

        # config

        with open('config.json') as json_data:
            self.config = json.load(json_data)

        # variable for game state

        self.time_start = None
        self.file = None

        self.arrayInstruments = None
        self.listInstruments = None

        self.gamescore = 0

        self.passTimeMusic = False

        self.musicnamelist = None
        self.bestscore = None

        # general
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()

    # Download a youtube video in mp4 format from a youtube link
    def DL_mp4(self, yt):
        yt.streams.filter().first().download(output_path="song/" + yt.title + "/", filename=yt.title)

    # Download a youtube video in mp4 format from a youtube link without sound
    def DL_mp4_nosound(self, yt):
        yt.streams.filter(only_video=True).first().download(output_path="song/" + yt.title + "/",
                                                            filename=yt.title + "nosound")

    # Mp4 file format to wav file format
    def mp4ToWav(self, yt):
        command = "ffmpeg -y -i \"song/" + yt.title + "/" + yt.title + ".mp4\" -ab 160k -ac 2 -ar 44100 -vn \"song/" + yt.title + "/" + yt.title + ".wav\""
        subprocess.call(command, shell=True)

    # fait tout à partir du link (nom de méthode à modifier)
    def process(self, yt_link):
        try:
            yt = YouTube(yt_link)

            # create a song folder if it doesn't exist yet
            os.makedirs("song", exist_ok=True)

            # replace some character that will cause some issues
            yt.title = yt.title.replace("|", "-")
            yt.title = yt.title.replace(":", "")
            yt.title = yt.title.replace("/", "")
            # create a folder from the song title if it doesn't exist yet in the song folder
            os.makedirs("song/" + yt.title, exist_ok=True)
            wget.download(yt.thumbnail_url, out="song/" + yt.title)

            self.DL_mp4(yt)
            self.DL_mp4_nosound(yt)
            self.mp4ToWav(yt)
            self.file = "song/" + yt.title + "/" + yt.title + ".wav"
            self.evManager.Post(StateChangeEvent(STATE_PLAY))
            self.gamescore = 0
        except:
            self.evManager.Post(StateChangeEvent(STATE_MENU))

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

        if isinstance(event, FileChooseListEvent):
            self.file = None
            self.musicnamelist = event.file
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

        if isinstance(event, FileChooseEvent):
            self.file = event.file
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

    def instrumentNow(self, liste_beat, num_classe):
        if (len(liste_beat) != 0) and (pygame.time.get_ticks() >= (liste_beat[0] - self.config["timeadvence"])):
            newBeatEvent = BeatEvent(Beat(liste_beat[0]), num_classe)
            self.evManager.Post(newBeatEvent)
            liste_beat.pop(0)

    def inputVerifBeat(self, beat_time,
                       instrument_class):  # update score depending and returns the type of success (fail, bad, meh, good, excellent)

        work_list = self.arrayInstruments[instrument_class]

        beat_to_delete = None

        list_bad = work_list[
            (work_list > beat_time - self.config["delta_bad"]) & (work_list < beat_time + self.config["delta_bad"])]
        success_class = 'fail'
        score_to_add = self.config["score_fail"]
        if len(list_bad) > 0:
            list_meh = work_list[
                (work_list > beat_time - self.config["delta_meh"]) & (work_list < beat_time + self.config["delta_meh"])]
            success_class = 'bad'
            score_to_add = self.config["score_bad"]
            beat_to_delete = list_bad[0]
            if len(list_meh) > 0:
                list_good = work_list[(work_list > beat_time - self.config["delta_good"]) & (
                        work_list < beat_time + self.config["delta_good"])]
                success_class = 'meh'
                score_to_add = self.config["score_meh"]
                beat_to_delete = list_meh[0]
                if len(list_good) > 0:
                    list_excellent = work_list[
                        (work_list > beat_time - self.config["delta_excellent"]) & (
                                work_list < beat_time + self.config["delta_excellent"])]
                    success_class = 'good'
                    score_to_add = self.config["score_good"]
                    beat_to_delete = list_good[0]
                    if len(list_excellent) > 0:
                        success_class = 'excellent'
                        score_to_add = self.config["score_excellent"]
                        beat_to_delete = list_excellent[0]

        self.gamescore += score_to_add

        if beat_to_delete is not None:
            work_list = np.delete(work_list, np.where(work_list == beat_to_delete))
        return success_class

    def savebestscore(self):
        musicfile = AutomaticBeats(self.file, self.config["spleeter"])
        bestscorefilepath = "preprocessed/" + musicfile.getmusicname() + "/bestscore.csv"
        if not os.path.exists(bestscorefilepath):
            array_score = np.around(np.array([self.gamescore]), decimals=2)
            np.savetxt(bestscorefilepath, array_score)
            self.evManager.Post(newBestScoreEvent(self.gamescore))
        else:
            saved_score = np.loadtxt(bestscorefilepath)
            if self.gamescore > saved_score:
                array_score = np.around(np.array([self.gamescore]), decimals=2)
                np.savetxt(bestscorefilepath, array_score)
                self.evManager.Post(newBestScoreEvent(self.gamescore))

    def modifDifficulty(self, level):
        self.config['difficulty'] = level
        with open('config.json','w') as config:
            json.dump(self.config, config, indent=4)

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
            elif self.state.peek() == STATE_EMPTYLIBRARY:
                pass
            elif self.state.peek() == STATE_ENDGAME:
                self.savebestscore()
            elif self.state.peek() == STATE_CHOOSEFILE:
                pass
            elif self.state.peek() == STATE_FILENOTFOUND:
                pass
            elif self.state.peek() == STATE_PLAY:
                for i in range(len(self.listInstruments)):
                    self.instrumentNow(self.listInstruments[i], i)
                if not self.passTimeMusic and pygame.time.get_ticks() >= self.config["timeadvence"] + self.time_start:
                    self.passTimeMusic = True
                    pygame.mixer.music.play()
                if pygame.time.get_ticks() >= self.duration + self.time_start + self.config["timeadvence"]:
                    self.evManager.Post(StateChangeEvent(STATE_ENDGAME))
            elif self.state.peek() == STATE_LOADING:
                pass
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
        elif self.state.peek() == STATE_EMPTYLIBRARY:
            pass
        elif self.state.peek() == STATE_FILENOTFOUND:
            pass
        elif self.state.peek() == STATE_PLAY:
            if self.file is not None:
                self.passTimeMusic = False
                musicfile = AutomaticBeats(self.file, self.config["spleeter"])
                dictInstruments = musicfile.getinstruments()
                musicfile.savejson()
                musicfile.copy()
                if os.path.exists("preprocessed/" + musicfile.getmusicname() + "/bestscore.csv"):
                    self.bestscore = np.loadtxt("preprocessed/" + musicfile.getmusicname() + "/bestscore.csv")

            if self.musicnamelist is not None:
                self.passTimeMusic = False
                self.file = "preprocessed/" + self.musicnamelist + "/" + self.musicnamelist + ".wav"
                musicfile = AutomaticBeats(self.file, self.config["spleeter"])
                if os.path.exists("preprocessed/" + self.musicnamelist + "/bestscore.csv"):
                    self.bestscore = np.loadtxt("preprocessed/" + self.musicnamelist + "/bestscore.csv")
                if self.config["spleeter"]:
                    path = "preprocessed/" + self.musicnamelist + "/instrumentswithspleeter.json"
                    if os.path.exists(path):
                        instruments = path
                    else:
                        self.evManager.Post(StateChangeEvent(STATE_FILENOTFOUND))
                        return
                else:
                    path = "preprocessed/" + self.musicnamelist + "/instrumentswithoutspleeter.json"
                    if os.path.exists(path):
                        instruments = path
                    else:
                        self.evManager.Post(StateChangeEvent(STATE_FILENOTFOUND))
                        return
                dictInstruments = library.json_to_dict(instruments)

            if self.config["simplification"]:
                dictInstruments = simplification(dictInstruments)


            if self.config['difficulty'] == 3 :
                self.arrayInstruments = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                         dictInstruments.items()]

            elif self.config['difficulty'] == 2:

                arraykicksnare = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                  dictInstruments.items() if (instrument[0] in ['Kick','Snare'])]
                arraykicksnare = np.concatenate([arraykicksnare[0],arraykicksnare[1]])

                self.arrayInstruments = [np.sort(arraykicksnare)] + [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                  dictInstruments.items() if (instrument[0] == 'Hihat')]

            elif self.config['difficulty'] == 1:
                arrayallinstruments = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                         dictInstruments.items()]
                arrayallinstruments = np.concatenate([arrayallinstruments[0],arrayallinstruments[1],arrayallinstruments[2]])
                self.arrayInstruments = [np.sort(arrayallinstruments)]

            pygame.mixer.init()
            pygame.mixer.music.load(self.file)
            self.duration = musicfile.getduration() * 1000  # ms
            self.gamescore = 0
            self.time_start = pygame.time.get_ticks()
            self.arrayInstruments = [(instrument + pygame.time.get_ticks()) for instrument in self.arrayInstruments]
            self.listInstruments = [instrument.tolist() for instrument in self.arrayInstruments]


# State machine constants for the StateMachine class below
STATE_MENU = 1
STATE_LIBRARY = 2
STATE_PLAY = 3
STATE_ENDGAME = 4
STATE_CHOOSEFILE = 5
STATE_EMPTYLIBRARY = 6
STATE_FILENOTFOUND = 7
STATE_LOADING = 8


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
