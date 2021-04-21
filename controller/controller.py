import pygame
from event.eventmanager import *
from model import model


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
                # handle key down events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.evManager.Post(QuitEvent())
                else:
                    currentstate = self.model.state.peek()
                    if currentstate == model.STATE_MENU:
                        self.keydownmenu(event)
                    if currentstate == model.STATE_PLAY:
                        self.keydownplay(event)
                    if currentstate == model.STATE_LIBRARY:
                        self.keydownhelp(event)

    def keydownmenu(self, event):

        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            self.evManager.Post(MouseClickEvent(pos))
            print(pos)

    def keydownplay(self, event):
        pass

    def keydownlibrary(self, event):
        pass
