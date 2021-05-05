import numpy as np
import librosa
import os
from spleeter.separator import Separator
from addons.ADTLib import ADT
import json
from json import JSONEncoder
import shutil

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# class regrouping the analysis functions

class AutomaticBeats(object) :

    def __init__(self, filepath):
        self.file = filepath
        self.instruments_dictionary = None

#creates preprocessed/music_name/drums.wav
    def preprocess(self):
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(self.file, 'preprocessed')
        os.remove('preprocessed/' + self.getmusicname()+'/vocals.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/other.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/bass.wav')

    def getmusicname(self):
        base = os.path.basename(self.file)
        return os.path.splitext(base)[0]

#returns tempo,duration and beats of drums.wav
    def getbeats(self):
        self.preprocess()
        file = 'preprocessed/' + self.getmusicname()+'/drums.wav'
        y, sr = librosa.load(file)
        onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)  #array de frames du rythme
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
        times = librosa.times_like(pulse, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        duration = librosa.get_duration(y, sr)
        return tempo, duration, times[beats_plp]

    def getduration(self):
        file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
        if os.path.exists(file):
            y, sr = librosa.load(file)
            return librosa.get_duration(y,sr)
        else :
            return None

#returns a dictionnary instrument => array of floats
    def getinstruments(self):
        if self.instruments_dictionary is None:
            self.preprocess()
            file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
            self.instruments_dictionary = ADT([file])[0]
        return self.instruments_dictionary

    def savejson(self):
        with open('preprocessed/'+self.getmusicname()+'/instruments.json', 'w') as outfile:
            json.dump(self.instruments_dictionary,outfile, cls=NumpyArrayEncoder)

    def copy(self):
        src = self.file
        dest = "preprocessed/" + self.getmusicname() +"/" + self.getmusicname()+".wav"
        shutil.copyfile(src, dest)