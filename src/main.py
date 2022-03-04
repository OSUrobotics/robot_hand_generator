
import glob

import subprocess
import os
import sys
import json

class MainScript():
    def __init__(self):
        self.directory_dict = self.read_json()
        os.chdir(self.directory_dict['src'])
        self.get_files_from_queue()


    def run_blender(self, json_name):

        subprocess.run(f'{self.directory_dict["blender_location"]} --background --python generator.py {json_name}', shell=True)

    def get_files_from_queue(self):
        
        for file in glob.glob(f'{self.directory_dict["hand_json_queue"]}*.json'):
            self.run_blender(json_name=file) #f'{self.directory_dict["hand_json_queue"]}
        

    def read_json(self, user_info_loc="./.user_info.json"):

        with open(user_info_loc, "r") as read_file:
            location = json.load(read_file)
        return location


if __name__ == '__main__':
    MainScript()
