import pygame

import view.view
from event.eventmanager import *
from model import model
import pyperclip

# keys used ingame
KeysList = [pygame.K_a, pygame.K_z, pygame.K_e]


class Keyboard(object):
    """
    Handles keyboard input.
    """

    def __init__(self, evManager, model,view):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.view = view
        self.listEvent = None

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """
        if isinstance(event, TickEvent):
            # Called for each game tick. We check our keyboard presses here.
            self.listEvent = pygame.event.get()
            for event in self.listEvent:
                # handle window manager closing our window
                if event.type == pygame.QUIT:
                    self.evManager.Post(QuitEvent())
                else:
                    currentstate = self.model.state.peek()
                    if currentstate == model.STATE_MENU:
                        self.keydownlinkyoutube(event)
                        self.keydownmenu(event)
                    if currentstate == model.STATE_PLAY:
                        self.keydownplay(event)
                    if currentstate == model.STATE_LIBRARY:
                        self.keydownhelp(event)
                    if currentstate == model.STATE_ENDGAME:
                        self.keydownendgame(event)

    def keydownmenu(self, event):
        if view.view.BUTTONMENUPLAY.cliked(self.listEvent):
            self.evManager.Post(ButtonMenuPlayEvent())

    def keydownlinkyoutube(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                view.view.BUTTONMENULINKYOUTUBE.text_backspace()
            else:
                if event.key == pygame.K_LCTRL:
                    view.view.BUTTONMENULINKYOUTUBE.text_typing(pyperclip.paste())
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.model.process(view.view.BUTTONMENULINKYOUTUBE.getText())
                else:
                    view.view.BUTTONMENULINKYOUTUBE.text_typing(event.unicode)

    def keydownplay(self, event):
        # handle key down events, initialize (depending on which key is pressed) an instance of InputEvent with an integer 0=first instrument, etc
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.evManager.Post(QuitEvent())
            if event.key in KeysList:
                newInputEvent = InputEvent(KeysList.index(event.key), True)
                self.evManager.Post(newInputEvent)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.evManager.Post(QuitEvent())
            if event.key in KeysList:
                newInputEvent = InputEvent(KeysList.index(event.key), False)
                self.evManager.Post(newInputEvent)


    def keydownlibrary(self, event):
        pass
    def keydownendgame(self,event):
        if view.view.BUTTONMENURETURN.cliked(self.listEvent):
            self.evManager.Post(ButtonMenuReturnEvent())