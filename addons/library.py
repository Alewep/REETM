import os
from os import listdir

def getfilename(file):
    base = os.path.basename(file)
    return os.path.splitext(base)[0]

def getFiles(directory,fileExt):
    return [getfilename(f) for f in listdir(directory) if f.endswith(fileExt)]
