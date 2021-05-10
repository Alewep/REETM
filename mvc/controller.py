import pygame
import os
from mvc.eventmanager import *
from mvc import model

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

    def __init__(self, evManager, engine, graphic):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = engine
        self.view = graphic
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
                        self.keydownyoutubelink(event)
                        self.keydownmenu(event)
                    if currentstate == model.STATE_PLAY:
                        self.keydownplay(event)
                    if currentstate == model.STATE_LIBRARY:
                        self.keydownlibrary(event)
                    if currentstate == model.STATE_EMPTYLIBRARY:
                        self.keydownemptylibrary(event)
                    if currentstate == model.STATE_ENDGAME:
                        self.keydownendgame(event)
                    if currentstate == model.STATE_CHOOSEFILE:
                        self.keydownchoosefile(event)


    def keydownmenu(self, event):
        if self.view.buttonMenuPlay.cliked(self.listEvent):
            self.evManager.Post(StateChangeEvent(model.STATE_CHOOSEFILE))
        if self.view.buttonLibrary.cliked(self.listEvent):
            if os.path.isdir('preprocessed'):
                self.evManager.Post(StateChangeEvent(model.STATE_LIBRARY))
            else:
                self.evManager.Post(StateChangeEvent(model.STATE_EMPTYLIBRARY))


    def keydownyoutubelink(self, event):
        #not optimized way, will modify later
        if event.type == pygame.MOUSEBUTTONDOWN:
            view.view.YOUTUBELINKTEXTBOX.target = 0

        if view.view.YOUTUBELINKTEXTBOX.clicked(self.listEvent):
            view.view.YOUTUBELINKTEXTBOX.target = 1

        if(view.view.YOUTUBELINKTEXTBOX.target == 1):
            if event.type == pygame.KEYDOWN:
                #if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                if event.key == pygame.K_BACKSPACE:
                    view.view.YOUTUBELINKTEXTBOX.text_backspace()
                else:
                    if pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_v]:
                        view.view.YOUTUBELINKTEXTBOX.text_typing(pyperclip.paste())
                    else:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            self.model.process(view.view.YOUTUBELINKTEXTBOX.getText())
                        else:
                            view.view.YOUTUBELINKTEXTBOX.text_typing(event.unicode)

        if view.view.BUTTONYOUTUBELINK.cliked(self.listEvent):
            self.model.process(view.view.YOUTUBELINKTEXTBOX.getText())
        if view.view.BUTTONRESET.cliked(self.listEvent):
            view.view.YOUTUBELINKTEXTBOX.reset()

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

    def keydownchoosefile(self, event):
        if self.view.fileSelected is not None:
            if not self.view.fileSelected == ():
                self.evManager.Post(FileChooseEvent(self.view.fileSelected))
            else:
                self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownlibrary(self, event):
        if self.view.songs_list.clicked:
            if not self.view.songs_list.chosenfile == '':
                self.evManager.Post(FileChooseListEvent(self.view.songs_list.chosenfile))
            else:
                self.evManager.Post(StateChangeEvent(model.STATE_MENU))
        if self.view.songs_list.clikedquit:
            self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownemptylibrary(self,event):
        self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownendgame(self, event):
        if self.view.buttonMenuReturn.cliked(self.listEvent):
            self.evManager.Post(StateChangeEvent(model.STATE_MENU))
