import numpy as np
import librosa
import os
from spleeter.separator import Separator
from ADTLib import ADT
import csv

    # classe regroupant les fonctions d'analyse du signal sonore des musiques
class AutomaticBeats(object) :

# on construit l'objet avec le chemin du fichier audio
    def __init__(self, filepath):
        self.file = filepath

# crée les fichiers vocals.wav drums.wav bass.wav others.wav dans le sous dossier preprocessed/nom_de_la_musique
    def preprocess(self):
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(self.file, 'preprocessed')
        os.remove('preprocessed/' + self.getmusicname()+'/vocals.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/other.wav')
        os.remove('preprocessed/' + self.getmusicname() + '/bass.wav')

# renvoie le nom du fichier audio sous forme de chaîne de caractères
    def getmusicname(self):
        base = os.path.basename(self.file)
        return os.path.splitext(base)[0]

# renvoie l'estimation du tempo (float) et la durée (en secondes, float) du fichier audio,
# et un tableau des temps (en secondes) des beats du ficher "drums.wav" créé à partir du fichieraudio
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

#renvoie un dictionnaire de clé le nom des instruments (Kick, Hihat,Snare) et de valeur les localisations en secondes des "coups" des instruments
#et
    def getinstruments(self):
        self.preprocess()
        file = 'preprocessed/' + self.getmusicname() + '/drums.wav'
        drum_onsets = ADT([file])[0]
        with open('preprocessed/'+self.getmusicname()+'/instruments.csv', 'w') as f:
            writer = csv.writer(f)
            for k, v in drum_onsets.items():
                writer.writerow([k, v])
        return drum_onsets
