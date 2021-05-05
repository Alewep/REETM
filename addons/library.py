import os
from os import listdir
import json
import numpy as np

def getfilename(file):
    base = os.path.basename(file)
    return os.path.splitext(base)[0]

def getFiles(directory,fileExt):
    return [getfilename(f) for f in listdir(directory) if f.endswith(fileExt)]

def getFiles(directory):
    return listdir(directory)

def json_to_dict(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    for key in data.keys():
        newvalue = np.array(data[key])
        data[key]=newvalue
    return data
