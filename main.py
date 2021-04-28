from event import eventmanager
from model import model
from view import view
from controller import controller
import pygame



def run():

    evManager = eventmanager.EventManager()
    gamemodel = model.GameEngine(evManager)
    graphics = view.GraphicalView(evManager, gamemodel)
    keyboard = controller.Keyboard(evManager, gamemodel, graphics)

    gamemodel.run()
--
if __name__ == '__main__':
    run()
