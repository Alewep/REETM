import numpy as np
import librosa
import os
from spleeter.separator import Separator
from ADTLib import ADT
import csv

# class regrouping the analysis functions

class AutomaticBeats(object) :

    def __init__(self, filepath):
        self.file = filepath
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
        self.preprocess()
        file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
        drum_onsets = ADT([file])[0]
        with open('preprocessed/'+self.getmusicname()+'/instruments.csv', 'w') as f:
            writer = csv.writer(f)
            for k, v in drum_onsets.items():
                writer.writerow([k, v])
        return drum_onsets
