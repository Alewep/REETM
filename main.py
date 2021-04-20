from event import eventmanager
from model import model
from view import view
from controller import controller




def run():
    evManager = eventmanager.EventManager()
    gamemodel = model.GameEngine(evManager)
    keyboard = controller.Keyboard(evManager, gamemodel)
    graphics = view.GraphicalView(evManager, gamemodel)
    gamemodel.run()
if __name__ == '__main__':
    run()
