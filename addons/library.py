import os
from os import listdir
import csv
import numpy as np

def getfilename(file):
    base = os.path.basename(file)
    return os.path.splitext(base)[0]

def getFiles(directory,fileExt):
    return [getfilename(f) for f in listdir(directory) if f.endswith(fileExt)]

def getFiles(directory):
    return listdir(directory)

def csv_to_dict(filename):
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {rows[0]: rows[1] for rows in reader}
        for key in mydict.keys():
            mydict[key] = mydict[key].split('\n')
            mydict[key] = " ".join(mydict[key])
            mydict[key] = mydict[key].split('[')
            mydict[key] = " ".join(mydict[key])
            mydict[key] = mydict[key].split(']')
            mydict[key] = " ".join(mydict[key])
            mydict[key] = mydict[key].split(' ')
            for element in mydict[key]:
                if element == '':
                    mydict[key].remove(element)
            list_of_floats = [float(item) for item in mydict[key]]
            array_of_floats = np.array(list_of_floats)
            mydict[key] = array_of_floats
    return mydict
