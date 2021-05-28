import librosa
import matplotlib.pyplot as plt
import numpy as np

import spleeter

filename = 'amazonia.mp3'

y, sr = librosa.load(filename, duration=30)  # import, duration en secondes

onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)  # force du signal (?)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)  # estimation du tempo, array de frames du rythme


## si on ne spécifie pas units=time
hop_length = 512
times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)
print(times[beats])
plt.plot(times, librosa.util.normalize(onset_env), label='Onset strength')
plt.vlines(times[beats], 0, 1, alpha=0.5, color='r', linestyle='--', label='Beats')
plt.legend()

plt.show()
