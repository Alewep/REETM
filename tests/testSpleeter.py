from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
import pygame
filename = '../amazonia.mp3'

separator = Separator('spleeter:4stems')

audio_loader = AudioAdapter.default()
sample_rate = 44100
waveform, _ = audio_loader.load(filename, sample_rate=sample_rate)

prediction = separator.separate(waveform)

