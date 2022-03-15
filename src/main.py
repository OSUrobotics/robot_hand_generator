"""Main script to be ran by user, this will grab jsons from the queue and run an instance of generator.py passing the json in."""

# Author: Josh Campbell, campbjos@oregonstate.edu
# Date: 3-14-2022

#!/usr/bin/python3
import glob
import subprocess
import os
import sys
import json

class MainScript():
    """MainScipt class that takes all the jsons in the queue and passes them on to generator.py."""

    def __init__(self):
        """Initialize the MainScript class."""
        self.directory_dict = self.read_json()
        os.chdir(self.directory_dict['src'])
        self.get_files_from_queue()


    def run_blender(self, json_name):
        """Run an instance of generator.py using blender's python for a given json file.

        Args:
            json_name (str): cantains the absolute path to the json file.
        """
        subprocess.run(f'{self.directory_dict["blender_location"]} --background --python generator.py {json_name}', shell=True) # --background

    def get_files_from_queue(self):
        """Get the json files in the queue and then call run_blender()."""
        for file in glob.glob(f'{self.directory_dict["hand_json_queue"]}*.json'):
            self.run_blender(json_name=file) #f'{self.directory_dict["hand_json_queue"]}
            self.move_json(file)

    def move_json(self, file_loc):
        """Move the json file to the archive directory and output folder with it's respective manipulator.

        Args:
            file_loc (str): The full path to the json file in the queue directory
        """
        json_data = self.read_json(file_loc)
        _, file_name = os.path.split(file_loc) 
        with open(f'{self.directory_dict["hand_model_output"]}{json_data["hand"]["hand_name"]}/{file_name}', 'w') as file:
            json.dump(json_data, file, indent=4)
        
        with open(f'{self.directory_dict["hand_json_archive"]}{file_name}', 'w') as file:
            json.dump(json_data, file, indent=4)
        
        os.remove(file_loc)


    def read_json(self, user_info_loc="./.user_info.json"):
        """Read in the content of a give json file.

        Args:
            user_info_loc (str, optional): path to the desired json file to read in. Defaults to "./.user_info.json".

        Returns:
            dictionary : A dictionary containing the contents of the json file.
        """
        with open(user_info_loc, "r") as read_file:
            location = json.load(read_file)
        return location


if __name__ == '__main__':
    MainScript()
