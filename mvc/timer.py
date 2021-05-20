import pygame
import sys

this = sys.modules[__name__]

this.startTime = pygame.time.get_ticks()
this.timeStartPause = None
this.timeDecalagePause = 0


def reset():
    this.startTime = pygame.time.get_ticks()
    this.timeDecalagePause = 0


def time():
    return (pygame.time.get_ticks() - this.startTime) - actualDecalageTime()


def pause():
    this.timeStartPause = pygame.time.get_ticks()


def unpause():
    if this.timeStartPause is not None:
        this.timeDecalagePause += pygame.time.get_ticks() - this.timeStartPause
    else:
        raise NameError('Timer was not in pause')

    this.timeStartPause = None


def actualDecalageTime():
    if this.timeStartPause is not None:
        return (pygame.time.get_ticks() - this.timeStartPause) + this.timeDecalagePause
    return this.timeDecalagePause


def inpause():
    return this.timeStartPause is not None
