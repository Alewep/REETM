import numpy as np
import librosa
import os

from ADTLib import ADT

import soundfile as sf


class AutomaticBeats(object):

    def __init__(self, filename):
        self.filename = filename

    def getmusicname(self):
        return self.filename

    def getinstruments(self):
        drum_onsets = ADT([self.filename])[0]
        return drum_onsets


boris = AutomaticBeats('/home/etudiant/stage/tests/testsimple.wav')
y, sr = librosa.load(boris.getmusicname())
clicks = librosa.clicks(times=boris.getinstruments()['Kick'], sr=sr, length=len(y))

sf.write('boris.wav', y, sr)
sf.write('borismodif.wav', y + clicks, sr)
