"""Script for setting up the file structure and placing the examples.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022
"""



#!/usr/bin/python3

import os
import json
import sys
import glob
from pathlib import Path
import shutil



class Setup():
	"""Setup class."""
	
	def __init__(self, input_val, blender_loc= ' '):
		"""Initialize the setup class.

		Args:
			input_val (int): 0 -> stand alone file structure, 1 -> mojograsp file structure.
			blender_loc (str, optional): Allows for the path to blender be passed as an argument, if not the script will ask. Defaults to ' '.
		"""
		self.current_directory = os.getcwd()
		
		self.blender_loc = blender_loc
		if input_val == 0: # occures if it is being setup as a docker container using stand alone file structure
			self.stand_alone_file_structure()
		elif input_val == 1: # not a docker container using the mojo grasp file structure
			self.mojo_grasp_file_strucuture()

	def directory_maker(self, location):
		"""Create a new directory.

		Args:
			location (str): absolute path to the directory that you want created
		"""
		if not os.path.isdir(location):
			Path(location).mkdir(parents=True, exist_ok=True)

	def mojo_grasp_file_strucuture(self): # adding later
		"""Create the file structure specific to mojo-grasp."""
		self.top_directory, _ = os.path.split(self.current_directory)

	def stand_alone_file_structure(self):
		"""Create the file structure for stand alone install."""
		directory_dict = {
			'hand_model_output' : f'{self.current_directory}/output/',
			'hand_json_queue': f'{self.current_directory}/hand_json_files/hand_queue_json/',
			'hand_json_archive': f'{self.current_directory}/hand_json_files/hand_archive_json/',
			'hand_examples' : f'{self.current_directory}/hand_json_files/example_hand_json/',
			'src' : f'{self.current_directory}/src'
		}

		for directory_name in directory_dict.keys():
			self.directory_maker(directory_dict[directory_name])

		directory_dict['src'] = f'{self.current_directory}/src/'
		if self.blender_loc == ' ':
			blender_location = input('Enter the path to blender:    ')
			directory_dict['blender_location'] = blender_location
		else:
			directory_dict['blender_location'] = self.blender_loc

		with open(f'{self.current_directory}/src/.user_info.json','w') as write_file:
			json.dump(directory_dict, write_file, indent=4)
		
		self.setup_examples(dict = directory_dict)

	def setup_examples(self, dict):
		"""Move the example jsons to the hand_json_queue to be built when main.py is ran.

		Args:
			dict (dictionary): A dictionary containing needed directories
		"""
		example_loc = dict['hand_examples']
		hand_json_queue = dict['hand_json_queue']

		for json_file in glob.glob(f'{example_loc}*.json'):
			shutil.copy2(json_file, hand_json_queue)


if __name__ == '__main__':

	input_val = sys.argv[1:] 

	if len(input_val) == 2: # checks if the trigger and blender location is passed
		if int(input_val[0]) != 0:
			input_value = 1
			blender_loc = input_val[1]
		else:
			input_value = 0
			blender_loc = input_val[1]
	elif len(input_val) != 1:
		input_value = 1
		blender_loc=' '
		
	elif int(input_val[0]) != 0:
		input_value = 1
		blender_loc=' '
	else:
		input_value = int(input_val[0])
		blender_loc=' '
		
	Setup(input_val=input_value, blender_loc=blender_loc)

	
