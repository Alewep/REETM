import os
from os import listdir
import csv

def getfilename(file):
    base = os.path.basename(file)
    return os.path.splitext(base)[0]

def getFiles(directory,fileExt):
    return [getfilename(f) for f in listdir(directory) if f.endswith(fileExt)]

def getFiles(directory):
    return listdir(directory)

def csv_to_dict(filename):
    with open(filename, 'rb') as csv_file: reader = csv.reader(csv_file)
    return dict(reader)