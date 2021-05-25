from tkinter import *
from tkinter.ttk import *
from addons import library


class ComboBox(object):

    def __init__(self,folderPath,title=""):
        self.window = Tk()  # create a Tk root window
        self.window.title(title)
        w = 300  # width for the Tk root
        h = 400  # height for the Tk root

        # get screen width and height
        ws = self.window.winfo_screenwidth()  # width of the screen
        hs = self.window.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.stockSongs = library.getFiles(folderPath)
        self.listeSongs = Combobox(self.window, values=self.stockSongs, state='readonly',width=w)
        self.listeSongs.pack()
        self.buttonconfirm = Button(text="confirmation")
        self.buttonconfirm.pack()
        self.buttonconfirm.config(command=self.confirmation)
        self.clicked = False
        self.clickedquit = False
        self.chosenfile = None

        self.window.protocol('WM_DELETE_WINDOW', self.quit)

    def quit(self):
        self.window.destroy()
        self.clickedquit = True

    def confirmation(self):
        self.chosenfile = self.listeSongs.get()
        self.clicked = True
        self.window.destroy()
