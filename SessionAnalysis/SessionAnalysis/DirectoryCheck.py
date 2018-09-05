import os, io, re
from datetime import datetime
from datetime import timedelta
from functools import reduce


# Constants
path = 'C:\\Users\\timregan\\Microsoft\\ProjectTorino - Logs from Trialists\\'

subDirs = next(os.walk(path))[1]

for subDir in subDirs:
    subSubDirs = next(os.walk(path + subDir))[1]
    for subSubDir in subSubDirs:
        print(path + subDir + '\\' + subSubDir)
    files = [name for name in os.listdir(path + subDir) if os.path.isfile(path + subDir + '\\' + name)]
    print(len(files))
    if len(files) > 0:
        os.mkdir(path + subDir + '\\Logs')
        for fileName in files:
            existingPath = path + subDir + '\\' + fileName
            newPath = path + subDir + '\\Logs\\' + fileName
            os.rename(existingPath, newPath)