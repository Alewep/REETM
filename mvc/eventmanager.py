import pygame.time


class Event(object):
    """
    A superclass for any events that might be generated by an
    object and sent to the EventManager.
    """

    def __init__(self):
        self.name = "Generic event"

    def __str__(self):
        return self.name


class QuitEvent(Event):
    """
    Quit event.
    """

    def __init__(self):
        self.name = "Quit event"


class TickEvent(Event):
    """
    Tick event.
    """

    def __init__(self):
        self.name = "Tick event"


class BeatEvent(Event):
    def __init__(self, instrument, num_classe):
        self.name = "Beat event"
        self.instrument = instrument
        self.num = num_classe
        self.instrument.setTimeSend()


class MouseClickEvent(Event):
    def __init__(self, pos):
        self.pos = pos
        self.name = "Mouse click event"


class InputEvent(Event):
    """
    Keyboard input event.
    """

    def __init__(self, instrumentclass, pressed):  # instrumentclass is int
        self.name = "Input event"
        self.classe = instrumentclass
        self.time = pygame.time.get_ticks()
        self.pressed = pressed

class newBestScoreEvent(Event):
    def __init__(self, score):
        self.name = "Score event"
        self.newbestscore = score

class ScoreEvent(Event):
    def __init__(self, type_success, current_score):
        self.name = "Score event"
        self.type_success = type_success
        self.score = current_score


class FileChooseEvent(Event):
    def __init__(self, file):
        self.file = file


class FileChooseListEvent(Event):
    def __init__(self, file):
        self.file = file

class ButtonMenuPlayEvent(Event):
    def __init__(self):
        self.name = "Button menu play event"


class ButtonMenuReturnEvent(Event):
    def __init__(self):
        self.name = "Button menu return event"


class InitializeEvent(Event):
    """
    Tells all listeners to initialize themselves.
    This includes loading libraries and resources.
    
    Avoid initializing such things within listener __init__ calls 
    to minimize snafus (if some rely on others being yet created.)
    """

    def __init__(self):
        self.name = "Initialize event"


class StateChangeEvent(Event):
    """
    Change the model state machine.
    Given a None state will pop() instead of push.
    """

    def __init__(self, state):
        self.name = "State change event"
        self.state = state

    def __str__(self):
        if self.state:
            return '%s pushed %s' % (self.name, self.state)
        else:
            return '%s popped' % (self.name,)


class EventManager(object):
    """
    We coordinate communication between the Model, View, and Controller.
    """

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def RegisterListener(self, listener):
        """ 
        Adds a listener to our spam list. 
        It will receive Post()ed events through its notify(event) call.
        """

        self.listeners[listener] = 1

    def UnregisterListener(self, listener):
        """ 
        Remove a listener from our spam list.
        This is implemented but hardly used.
        Our weak ref spam list will auto remove any listeners who stop existing.
        """

        if listener in self.listeners.keys():
            del self.listeners[listener]

    def Post(self, event):
        """
        Post a new event to the message queue.
        It will be broadcast to all listeners.
        """

        for listener in self.listeners.keys():
            listener.notify(event)
