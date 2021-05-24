import pygame
import os
import pyperclip
from mvc.eventmanager import *
from mvc import model




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
        # keys used ingame
        KeysListold = self.model.config["keyslist"]
        self.KeysList = []
        for elem in KeysListold:
            self.KeysList.append(eval(elem))
        self.KeysList = self.KeysList[0:self.model.config['difficulty']]

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
                    if currentstate == model.STATE_FILENOTFOUND:
                        self.keydownfilenotfound(event)


    def keydownmenu(self, event):
        if self.view.buttonMenuPlay.clicked(self.listEvent):
            self.evManager.Post(StateChangeEvent(model.STATE_CHOOSEFILE))
        if self.view.buttonLibrary.clicked(self.listEvent):
            if os.path.isdir('preprocessed'):
                self.evManager.Post(StateChangeEvent(model.STATE_LIBRARY))
            else:
                self.evManager.Post(StateChangeEvent(model.STATE_EMPTYLIBRARY))

        if self.view.buttonEasy.clicked(self.listEvent):
            self.model.modifDifficulty(1)
        if self.view.buttonMedium.clicked(self.listEvent):
            self.model.modifDifficulty(2)
        if self.view.buttonHard.clicked(self.listEvent):
            self.model.modifDifficulty(3)

    def keydownyoutubelink(self, event):
        # not optimized way, will modify later

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.view.YOUTUBELINKTEXTBOX.target = 0

        if self.view.YOUTUBELINKTEXTBOX.clicked(self.listEvent):
            self.view.YOUTUBELINKTEXTBOX.target = 1

        if self.view.BUTTONPASTE.clicked(self.listEvent):
            self.view.YOUTUBELINKTEXTBOX.text_typing(pyperclip.paste())

        if self.view.YOUTUBELINKTEXTBOX.target == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.view.YOUTUBELINKTEXTBOX.text_backspace()
                else:
                    if pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_v]:
                        self.view.YOUTUBELINKTEXTBOX.text_typing(pyperclip.paste())
                    else:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            self.model.process(self.view.YOUTUBELINKTEXTBOX.getText())
                        else:
                            self.view.YOUTUBELINKTEXTBOX.text_typing(event.unicode)

        if self.view.BUTTONYOUTUBELINK.clicked(self.listEvent):
            self.model.process(self.view.YOUTUBELINKTEXTBOX.text)
        if self.view.BUTTONRESET.clicked(self.listEvent):
            self.view.YOUTUBELINKTEXTBOX.reset()


    def keydownplay(self, event):
        # handle key down events, initialize (depending on which key is pressed) an instance of InputEvent with an integer 0=first instrument, etc
        if not self.model.pause:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.model.start_pause()
                if event.key in self.KeysList:
                    newInputEvent = InputEvent(self.KeysList.index(event.key), True)
                    self.evManager.Post(newInputEvent)
            if event.type == pygame.KEYUP:
                if event.key in self.KeysList:
                    newInputEvent = InputEvent(self.KeysList.index(event.key), False)
                    self.evManager.Post(newInputEvent)
            if self.view.BUTTONPAUSE.clicked(self.listEvent):
                self.model.start_pause()
        else:
            if self.view.PANELPAUSE.buttonDict['buttonHome'].clicked(self.listEvent):
                self.model.home()
            elif self.view.PANELPAUSE.buttonDict['buttonPlay'].clicked(self.listEvent):
                self.model.play()
            elif self.view.PANELPAUSE.buttonDict['buttonRetry'].clicked(self.listEvent):
                self.model.retry()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.model.play()

    def keydownchoosefile(self, event):
        if self.view.fileSelected is not None:
            if not self.view.fileSelected == ():
                self.evManager.Post(FileChooseEvent(self.view.fileSelected))
            else:
                self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownlibrary(self, event):
        if self.view.songs_list is not None:
            if self.view.songs_list.clicked:
                if not self.view.songs_list.chosenfile == '':
                    self.evManager.Post(FileChooseListEvent(self.view.songs_list.chosenfile))
                else:
                    self.evManager.Post(StateChangeEvent(model.STATE_MENU))
            if self.view.songs_list.clickedquit:
                self.evManager.Post(StateChangeEvent(model.STATE_MENU))
            self.view.songs_list = None

    def keydownemptylibrary(self, event):
        self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownfilenotfound(self, event):
        self.evManager.Post(StateChangeEvent(model.STATE_MENU))

    def keydownendgame(self, event):
        if self.view.buttonMenuReturn.clicked(self.listEvent):
            self.evManager.Post(StateChangeEvent(model.STATE_MENU))


