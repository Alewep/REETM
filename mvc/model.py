from mvc.eventmanager import *
import mvc.timer as timer
from addons.AutomaticBeats import AutomaticBeats
from addons.AutomaticBeats import simplification
from addons import library

import threading
import copy
import pygame
import numpy as np
import os
import json
import wget
import subprocess
from pytube import YouTube
import youtube_dl

PATHOFLIBRARY = "Library"
PREPROCESSEDPATH = "preprocessed"


class Beat(object):
    def __init__(self, time):
        self.time = time
        self.timeSend = timer.time()
        self.distanceInPixel = 0
        self.position = 0

    def setDistanceInPixel(self, distanceInPixel):
        self.distanceInPixel = distanceInPixel

    def setTimeSend(self):
        self.timeSend = timer.time()

    def timeToArrive(self):
        return self.time - self.timeSend

    def speed(self):
        return self.distanceInPixel / self.timeToArrive()

    def updatePosition(self):
        actualTime = timer.time()
        durationLife = actualTime - self.timeSend
        self.position = durationLife * self.speed()


def mp4ToWav(pathtosource, pathtosave):
    command = "ffmpeg -y -i \"" + pathtosource + "\" -ab 160k -ac 2 -ar 44100 -vn \"" + pathtosave + "\""
    subprocess.call(command, shell=True)


class Music(object):
    def __init__(self, libraryPath, musicName):
        self.libraryPath = libraryPath
        self.musicName = musicName
        self.videoFileName = "video"
        self.musicFileName = "music"
        self.thumbnailFileName = "thumbnail"
        self.dataFileName = "data"
        self.dataFileNameWithoutSpleeter = "dataWithoutSpleeter"
        self.bestScoreFileName = "bestScore"

    def pathOfMusicFolder(self):
        return self.libraryPath + "/" + self.musicName

    def videoPath(self):
        extension = ".mp4"
        return self.pathOfMusicFolder() + "/" + self.videoFileName + extension

    def musicPath(self):
        extension = ".wav"
        return self.pathOfMusicFolder() + "/" + self.musicFileName + extension

    def thumbnailPath(self):
        extension = ".jpg"
        return self.pathOfMusicFolder() + "/" + self.thumbnailFileName + extension

    def jsonPath(self, spleeter=True):
        if spleeter:
            fileName = self.dataFileName
        else:
            fileName = self.dataFileNameWithoutSpleeter

        return self.pathOfMusicFolder() + "/" + fileName + ".json"

    def bestScorePath(self):
        return self.pathOfMusicFolder() + "/" + self.bestScoreFileName + ".csv"


class GameEngine(object):

    def __init__(self, evManager):

        # config

        with open('config.json') as json_data:
            self.config = json.load(json_data)

        # variable for game state

        self.time_start = None
        self.music = None

        self.arrayInstruments = None
        self.listInstruments = None
        self.saveArrayInstruments = None
        self.saveListInstruments = None
        self.gamescore = 0

        self.passTimeMusic = False
        self.duration = None
        self.file = None
        self.bestscore = None

        self.pause = False

        self.timeVideoCheckPoint = timer.time()
        self.passVideo = False

        # general
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()

    def getMusicRessources(self, key):
        path = None
        if key == "video":
            path = self.music.videoPath()
        elif key == "music":
            path = self.music.musicPath()
        elif key == "thumbnail":
            path = self.music.thumbnailPath()

        if os.path.exists(path):
            return path
        return None

    # fait tout à partir du link (nom de méthode à modifier)
    def youtubeProcess(self, yt_link):
        try:
            yt = YouTube(yt_link)

            # create a song folder if it doesn't exist yet
            os.makedirs(PATHOFLIBRARY, exist_ok=True)

            # replace some characters that will cause some issues in the video title
            yt.title = yt.title.replace("|", "-")
            yt.title = yt.title.replace(":", "")
            yt.title = yt.title.replace("/", "")
            # create a folder from the song title if it doesn't exist yet in the song folder
            self.music = Music(PATHOFLIBRARY, yt.title)

            os.makedirs(self.music.pathOfMusicFolder(), exist_ok=True)
            wget.download(yt.thumbnail_url, out=self.music.thumbnailPath())

            # Download a youtube video in mp4 format from a youtube link without sound
            yt.streams.filter().first().download(output_path=self.music.pathOfMusicFolder(),
                                                 filename=self.music.videoFileName)
            mp4ToWav(self.music.videoPath(), self.music.musicPath())
            self.charginMusic()

        except:

            try:
                ydl_opts = {
                    'format': 'mp4',
                    'outtmpl': PATHOFLIBRARY + "/%(title)s/video.mp4",
                    'noplaylist': True,
                }
                # download the youtube video
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    video = ydl.extract_info(yt_link, download=True)
                # replace some characters that will cause some issues in the video title
                video["title"] = video["title"].replace("|", "_")
                video["title"] = video["title"].replace(":", " -")
                video["title"] = video["title"].replace("/", "_")

                # to get the link of the jpg format of the thumbnail instead of the webp format
                video["thumbnail"] = video["thumbnail"].replace("_webp", "")
                video["thumbnail"] = video["thumbnail"].replace("webp", "jpg")

                self.music = Music(PATHOFLIBRARY, video["title"])
                mp4ToWav(self.music.videoPath(), self.music.musicPath())

                # download the thumbnail
                wget.download(video["thumbnail"], out=self.music.thumbnailPath())
                self.charginMusic()
            except:
                self.evManager.Post(StateChangeEvent(STATE_MENU))

    def loading(self, target, args=[]):
        self.state.push(STATE_LOADING)
        threading.Thread(target=target, args=args).start()

    def buttonReturn(self):
        self.evManager.Post(StateChangeEvent(STATE_MENU))
        self.gamescore = 0

    def notify(self, event):

        if isinstance(event, QuitEvent):
            self.running = False
        elif isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)
                self.initialize()
        elif isinstance(event, InputEvent):
            if event.pressed:
                newScoreEvent = ScoreEvent(self.inputVerifBeat(event.time, event.classe), self.gamescore)
                self.evManager.Post(newScoreEvent)

        elif isinstance(event, FileChooseListEvent):
            self.file = None
            self.music = Music(PATHOFLIBRARY, event.file)
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

        elif isinstance(event, FileChooseEvent):
            self.file = event.file
            self.musicnamelist = None
            self.evManager.Post(StateChangeEvent(STATE_PLAY))

    def start_pause(self):
        timer.pause()
        self.pause = True
        pygame.mixer.music.pause()

    def end_pause(self):
        if self.pause:
            timer.unpause()
            pygame.mixer.music.unpause()
        self.pause = False

    def home(self, ):
        self.end_pause()
        self.evManager.Post(StateChangeEvent(STATE_MENU))
        pygame.mixer.music.stop()

    def play(self):
        self.end_pause()

    def retry(self):
        pygame.mixer.music.stop()
        self.end_pause()
        self.passTimeMusic = False
        self.arrayInstruments = copy.deepcopy(self.saveArrayInstruments)
        self.listInstruments = copy.deepcopy(self.saveListInstruments)
        self.evManager.Post(ResetPlayEvent())
        timer.reset()

    def instrumentNow(self, liste_beat, num_classe):

        if (len(liste_beat) > 0) and (timer.time() >= (liste_beat[0] - self.config["timeadvence"])):
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
        bestscorefilepath = self.music.bestScorePath()
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
        with open('config.json', 'w') as config:
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
                pass
            elif self.state.peek() == STATE_CHOOSEFILE:
                pass
            elif self.state.peek() == STATE_FILENOTFOUND:
                pass
            elif self.state.peek() == STATE_PLAY:
                if not self.pause:
                    for i in range(len(self.listInstruments)):
                        self.instrumentNow(self.listInstruments[i], i)
                    if not self.passTimeMusic and timer.time() >= self.config[
                        "timeadvence"]:
                        self.passTimeMusic = True
                        pygame.mixer.music.play()
                    if timer.time() >= self.duration + self.config["timeadvence"]:
                        self.evManager.Post(StateChangeEvent(STATE_ENDGAME))
            elif self.state.peek() == STATE_LOADING:
                pass
            else:
                self.running = False

    def charginMusic(self):
        try:
            self.passTimeMusic = False
            if self.file is not None:
                # place music to a other directory into Library
                name, ext = os.path.splitext(os.path.basename(self.file))
                self.music = Music(PATHOFLIBRARY, name)
                library.placeInLibrary(self.file, self.music.musicPath())
                musicfile = AutomaticBeats(self.music.musicPath(), preprocessPath=PREPROCESSEDPATH,
                                           spleeter=self.config["spleeter"])
                dictInstruments = musicfile.getinstruments()
                musicfile.savejson(self.music.jsonPath())

            elif self.music is not None:
                musicfile = AutomaticBeats(self.music.musicPath(), preprocessPath=PREPROCESSEDPATH,
                                           spleeter=self.config["spleeter"])

                if not os.path.exists(self.music.jsonPath(spleeter=self.config["spleeter"])):
                    dictInstruments = musicfile.getinstruments()
                    musicfile.savejson(self.music.jsonPath())
                else:
                    dictInstruments = library.json_to_dict(self.music.jsonPath(spleeter=self.config["spleeter"]))

            self.arrayInstruments = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                     dictInstruments.items()]

            if self.config['difficulty'] == 3:
                self.arrayInstruments = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                         dictInstruments.items()]

            elif self.config['difficulty'] == 2:

                arraykicksnare = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                  dictInstruments.items() if (instrument[0] in ['Kick', 'Snare'])]
                arraykicksnare = np.concatenate([arraykicksnare[0], arraykicksnare[1]])

                self.arrayInstruments = [np.sort(arraykicksnare)] + [(instrument[1] * 1000 + self.config["timeadvence"])
                                                                     for
                                                                     instrument in
                                                                     dictInstruments.items() if
                                                                     (instrument[0] == 'Hihat')]
            elif self.config['difficulty'] == 1:
                arrayallinstruments = [(instrument[1] * 1000 + self.config["timeadvence"]) for instrument in
                                       dictInstruments.items()]
                arrayallinstruments = np.concatenate(
                    [arrayallinstruments[0], arrayallinstruments[1], arrayallinstruments[2]])
                self.arrayInstruments = [np.sort(arrayallinstruments)]

            if self.config["simplification"]:
                self.arrayInstruments = simplification(self.arrayInstruments,
                                                       timerange=self.config["timeRangeForSimplification"])

            self.saveArrayInstruments = copy.deepcopy(self.arrayInstruments)
            if os.path.exists(self.music.bestScorePath()):
                self.bestscore = np.loadtxt(self.music.bestScorePath())
            pygame.mixer.init()

            pygame.mixer.music.load(self.music.musicPath())

            self.duration = musicfile.getduration() * 1000  # ms
            self.gamescore = 0
            self.listInstruments = [instrument.tolist() for instrument in self.arrayInstruments]
            self.saveListInstruments = copy.deepcopy(self.listInstruments)
            self.state.push(STATE_PLAY)
            timer.reset()
            self.timeVideoCheckPoint = timer.time()
            self.passVideo = False
        except:
            self.state.push(STATE_MENU)

    def initialize(self):

        if self.state.peek() == STATE_MENU:
            pass
        elif self.state.peek() == STATE_LIBRARY:
            pass
        elif self.state.peek() == STATE_ENDGAME:
            self.savebestscore()
        elif self.state.peek() == STATE_CHOOSEFILE:
            pass
        elif self.state.peek() == STATE_EMPTYLIBRARY:
            pass
        elif self.state.peek() == STATE_FILENOTFOUND:
            pass
        elif self.state.peek() == STATE_PLAY:
            self.loading(target=self.charginMusic)



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
