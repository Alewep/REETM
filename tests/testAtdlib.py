
import numpy as np
import librosa
import os
from spleeter.separator import Separator
from ADTLib import ADT


class AutomaticBeats(object) :

    def __init__(self, filename):
        self.filename = filename

    def preprocess(self):
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(self.filename, 'preprocessed')

    def getmusicname(self):
        base = os.path.basename(self.filename)
        return os.path.splitext(base)[0]

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

    def getinstruments(self):
        self.preprocess()
        file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
        drum_onsets = ADT([file])[0]
        return drum_onsets

amazonia = AutomaticBeats('/home/adrien/TER/amazonia.mp3')