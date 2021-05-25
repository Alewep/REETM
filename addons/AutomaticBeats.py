import numpy as np
import librosa
import os
from spleeter.separator import Separator
from addons.ADTLib import ADT
import json
import copy
from json import JSONEncoder


def simplification(instruments, timerange=150):
    # time in milliseconds
    instruments = copy.deepcopy(instruments)
    i = 0
    for instrument in instruments:
        simp = []
        term = False
        timeref = instrument[0]
        iteration = 1
        sum = timeref
        for time in instrument[1:]:
            if time > timeref + timerange:
                simp.append(sum / iteration)
                timeref = time
                sum = time
                iteration = 1
                term = True
            else:
                term = False
                sum += time
                iteration += 1
        if term:
            simp.append(sum / iteration)
        instruments[i] = np.array(simp)
        i += 1
    return instruments


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


# class regrouping the analysis functions

class AutomaticBeats(object):

    def __init__(self, filepath, preprocessPath="preprocessed", spleeter=True, simplification=True):

        self.file = filepath
        self.preprocessPath = preprocessPath
        self.spleeter = spleeter
        self.simplification = simplification
        self.instruments_dictionary = None

    # creates preprocessed/music_name/drums.wav
    def preprocess(self):
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(self.file,self.preprocessPath)
        os.remove(self.preprocessPath + "/music/vocals.wav")
        os.remove(self.preprocessPath + "/music/other.wav")
        os.remove(self.preprocessPath + "/music/bass.wav")

    def getmusicname(self):
        base = os.path.basename(self.file)
        return os.path.splitext(base)[0]

    # returns tempo,duration and beats of drums.wav
    def getbeats(self):
        self.preprocess()
        file = self.preprocessPath + "/music/drums.wav"
        y, sr = librosa.load(file)
        onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)  # array de frames du rythme
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
        times = librosa.times_like(pulse, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        duration = librosa.get_duration(y, sr)
        return tempo, duration, times[beats_plp]

    def getduration(self):
        y, sr = librosa.load(self.file)
        return librosa.get_duration(y, sr)

    # returns a dictionnary instrument => array of floats
    def getinstruments(self):

        if self.instruments_dictionary is None:
            # spleeter mode
            if self.spleeter:
                self.preprocess()
                file = self.preprocessPath + "/music/drums.wav"
            else:
                file = self.file
            self.instruments_dictionary = ADT([file])[0]
        return self.instruments_dictionary

    def savejson(self, savePath):
        if self.spleeter:
            with open(savePath, 'w') as outfile:
                json.dump(self.instruments_dictionary, outfile, cls=NumpyArrayEncoder)
        else:
            if not os.path.isdir(savePath):
                os.mkdir(savePath)
            with open(savePath, 'w') as outfile:
                json.dump(self.instruments_dictionary, outfile, cls=NumpyArrayEncoder)
