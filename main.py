from mvc import model, controller, view, eventmanager


def run():

    evManager = eventmanager.EventManager()
    gamemodel = model.GameEngine(evManager)
    graphics = view.GraphicalView(evManager, gamemodel)
    keyboard = controller.Keyboard(evManager, gamemodel, graphics)

    gamemodel.run()

if __name__ == '__main__':
    run()
