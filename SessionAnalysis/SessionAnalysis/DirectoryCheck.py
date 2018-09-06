import os, io, re
from datetime import datetime
from datetime import timedelta
from functools import reduce


# Constants
path = 'C:\\Users\\timregan\\Microsoft\\ProjectTorino - Logs from Trialists\\'

#sub_dirs = next(os.walk(path))[1]

def move_to_log(sub_dirs):
    files = [name for name in os.listdir(path + sub_dir) if os.path.isfile(path + sub_dir + '\\' + name)]
    if len(files) > 0:
        print(len(files))
        logs_path = path + sub_dir + '\\Logs'
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        for file_name in files:
            existing_path = path + sub_dir + '\\' + file_name
            new_path = path + sub_dir + '\\Logs\\' + file_name
            os.rename(existing_path, new_path)

def print_sub_sub_dirs(sub_dirs):
    for sub_dir in sub_dirs:
        sub_sub_dirs = next(os.walk(path + sub_dir))[1]
        for sub_sub_dir in sub_sub_dirs:
            print(path + sub_dir + '\\' + sub_sub_dir)

def directory_overlap(sub_dirs):
    files = {}
    for sub_dir in sub_dirs:
        files[sub_dir] = [name for name in os.listdir(path + sub_dir + '\\Logs\\') if os.path.isfile(path + sub_dir + '\\Logs\\' + name)]
    
