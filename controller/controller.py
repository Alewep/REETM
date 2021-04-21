import pygame
from event.eventmanager import *

# keys used ingame
KeysList = [pygame.K_a, pygame.K_z, pygame.K_e]

class Keyboard(object):
    """
    Handles keyboard input.
    """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, TickEvent):
            # Called for each game tick. We check our keyboard presses here.
            for event in pygame.event.get():
                # handle window manager closing our window
                if event.type == pygame.QUIT:
                    self.evManager.Post(QuitEvent())
                # handle key down events, initialize (depending on which key is pressed) an instance of InputEvent with an integer 0=first instrument, etc
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.evManager.Post(QuitEvent())
                    if event.key in KeysList:
                        newInputEvent = InputEvent(KeysList.index(event.key),True)
                        self.evManager.Post(newInputEvent)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.evManager.Post(QuitEvent())
                    if event.key in KeysList:
                        newInputEvent = InputEvent(KeysList.index(event.key),False)
                        self.evManager.Post(newInputEvent)
