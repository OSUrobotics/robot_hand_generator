#!/usr/bin/python3

import os
import json
import sys
import glob
from pathlib import Path
import shutil



class Setup():
    def __init__(self, input_val, blender_loc= ' '):
        self.current_directory = os.getcwd()
        print(self.current_directory)
        self.blender_loc = blender_loc
        if input_val == 0: # occures if it is being setup as a docker container using stand alone file structure
            self.stand_alone_file_structure()
        elif input_val == 1: # not a docker container using the mojo grasp file structure
            self.mojo_grasp_file_strucuture()

    def directory_maker(self, location):
        if not os.path.isdir(location):
            Path(location).mkdir(parents=True, exist_ok=True)

    def mojo_grasp_file_strucuture(self): # adding later
        self.top_directory, _ = os.path.split(self.current_directory)

    def stand_alone_file_structure(self):
        directory_dict = {
            'hand_model_output' : f'{self.current_directory}/output/',
            'hand_json_queue': f'{self.current_directory}/hand_json_files/hand_queue_json/',
            'hand_json_archive': f'{self.current_directory}/hand_json_files/hand_archive_json/',
            'hand_examples' : f'{self.current_directory}/hand_json_files/example_hand_json/',
            'src' : f'{self.current_directory}/src'
        }

        for directory_name in directory_dict.keys():
            # print(directory_name)
            self.directory_maker(directory_dict[directory_name])

        directory_dict['src'] = f'{self.current_directory}/src/'
        if self.blender_loc == ' ':
            blender_location = input('Enter the path to blender:    ')
            directory_dict['blender_location'] = blender_location
        else:
            directory_dict['blender_location'] = self.blender_loc

        with open(f'{self.current_directory}/src/.user_info.json','w') as write_file:
            json.dump(directory_dict, write_file, indent=4)
        
        # self.setup_examples(dict = directory_dict)

    def setup_examples(self, dict):
        example_loc = dict['hand_examples']
        hand_json_queue = dict['hand_json_queue']

        for json_file in glob.glob(f'{example_loc}*.json'):
            shutil.copy2(json_file, hand_json_queue)


if __name__ == '__main__':

    input_val = sys.argv[1:]
    if len(input_val) == 2:
        if int(input_val[0]) != 0:
            input_value = 1
            blender_loc = input_val[1]
        else:
            input_value = 0
            blender_loc = input_val[1]
    elif len(input_val) != 1:
        input_value = 1
        
    elif int(input_val[0]) != 0:
        input_value = 1
    else:
        input_value = int(input_val[0])

    # print(input_value, blender_loc)
    Setup(input_val=input_value)

    