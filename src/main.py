
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

        subprocess.run(f'{self.directory_dict["blender_location"]} --background --python generator.py {json_name}', shell=True) # --background

    def get_files_from_queue(self):
        
        for file in glob.glob(f'{self.directory_dict["hand_json_queue"]}*.json'):
            self.run_blender(json_name=file) #f'{self.directory_dict["hand_json_queue"]}
            self.move_json(file)

    def move_json(self, file_loc):
        json_data = self.read_json(file_loc)
        _, file_name = os.path.split(file_loc) 
        with open(f'{self.directory_dict["hand_model_output"]}{json_data["hand"]["hand_name"]}/{file_name}', 'w') as file:
            json.dump(json_data, file, indent=4)
        
        with open(f'{self.directory_dict["hand_json_archive"]}{file_name}', 'w') as file:
            json.dump(json_data, file, indent=4)
        
        os.remove(file_loc)


    def read_json(self, user_info_loc="./.user_info.json"):

        with open(user_info_loc, "r") as read_file:
            location = json.load(read_file)
        return location


if __name__ == '__main__':
    MainScript()
