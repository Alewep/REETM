import numpy as np
import librosa
import os
from spleeter.separator import Separator
from addons.ADTLib import ADT
import json
import copy
from json import JSONEncoder
import shutil


def simplification(instruments, timerange=150):
    # time in milliseconds
    instruments = copy.deepcopy(instruments)
    print(instruments)
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

    def __init__(self, filepath, spleeter=True, simplification=True):
        self.file = filepath
        self.spleeter = spleeter
        self.simplification = simplification
        self.instruments_dictionary = None

    # creates preprocessed/music_name/drums.wav
    def preprocess(self):
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(self.file, 'preprocessed')
        os.remove('preprocessed/' + self.getmusicname() + '/vocals.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/other.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/bass.wav')

    def getmusicname(self):
        base = os.path.basename(self.file)
        return os.path.splitext(base)[0]

    # returns tempo,duration and beats of drums.wav
    def getbeats(self):
        self.preprocess()
        file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
        y, sr = librosa.load(file)
        onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)  # array de frames du rythme
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
        times = librosa.times_like(pulse, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        duration = librosa.get_duration(y, sr)
        return tempo, duration, times[beats_plp]

    def getduration(self):
        if self.spleeter:
            file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
            if os.path.exists(file):
                y, sr = librosa.load(file)
                return librosa.get_duration(y, sr)
            else:
                return None
        else:
            y, sr = librosa.load(self.file)
            return librosa.get_duration(y, sr)

    # returns a dictionnary instrument => array of floats
    def getinstruments(self):

        if self.instruments_dictionary is None:
            # spleeter mode
            if self.spleeter:
                self.preprocess()
                file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
            else:
                file = self.file
            self.instruments_dictionary = ADT([file])[0]
            # simplifaction mode

            if self.simplification:
                for _, instrument in self.instruments_dictionary.items():
                    for time in instrument:
                        mask = (time - 1 <= instrument) & (instrument <= time + 1)
                        moyenne = instrument[mask].mean()
                        instrument = np.append(instrument[np.logical_not(mask)], moyenne)
        return self.instruments_dictionary

    def savejson(self):
        if self.spleeter:
            with open('preprocessed/' + self.getmusicname() + '/instrumentswithspleeter.json', 'w') as outfile:
                json.dump(self.instruments_dictionary, outfile, cls=NumpyArrayEncoder)
        else:
            if not os.path.isdir("preprocessed"):
                os.mkdir("preprocessed")
            if not os.path.isdir("preprocessed/" + self.getmusicname()):
                os.mkdir("preprocessed/" + self.getmusicname())
            with open('preprocessed/' + self.getmusicname() + '/instrumentswithoutspleeter.json', 'w') as outfile:
                json.dump(self.instruments_dictionary, outfile, cls=NumpyArrayEncoder)

    def copy(self):
        src = self.file
        dest = "preprocessed/" + self.getmusicname() + "/" + self.getmusicname() + ".wav"
        shutil.copyfile(src, dest)
