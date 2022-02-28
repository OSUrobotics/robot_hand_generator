#!/usr/bin/python3

import os
import json
import sys
import glob
from pathlib import Path
import shutil


class Setup():
    def __init__(self, input_val):
        self.current_directory = os.getcwd()

        if input_val == 0: # occures if it is being setup as a docker container using stand alone file structure
            self.stand_alone_file_structure()
        elif input_val == 1: # not a docker container using the mojo grasp file structure
            self.mojo_grasp_file_strucuture()

    def directory_maker(self, location):
        if not os.path.isdir(location):
            Path(location).mkdir(parents=True, exist_ok=True)

    def mojo_grasp_file_strucuture(self):
        self.top_directory, _ = os.path.split(self.current_directory)

    def stand_alone_file_structure(self):
        



if __name__ == '__main__':

    input_val = sys.argv[1:]
    if len(input_val) != 1:
        input_val = [1]
    elif int(input_val[0]) != 0:
        input_val = [1]

    print(int(input_val[0]))
    # Setup(input_val=input_val)

    