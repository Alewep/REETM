from mvc import model, controller, view, eventmanager
import pygame


def run():
    pygame.font.init()
    evManager = eventmanager.EventManager()
    gamemodel = model.GameEngine(evManager)
    graphics = view.GraphicalView(evManager, gamemodel)
    keyboard = controller.Keyboard(evManager, gamemodel, graphics)

    gamemodel.run()


if __name__ == '__main__':
    run()
