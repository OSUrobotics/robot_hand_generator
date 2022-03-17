"""Test script that ensures the generator methods can reproduce models that have been checked by other means."""

# Author: Josh Campbell, campbjos@oregonstate.edu
# Date: 3-14-2022

#!~/software/blender-2.93/2.93/python/bin/python3.9

import sys, json
import bpy

class TestGenerator():
	"""Class for testing the generator.py mesh creation."""

	def __init__(self):
		"""Initialize the TestGeneratory Class."""
		self.test_results_location = "./test_results.json"
		self.test_key_dict = read_json(self.test_results_location)
		self.test_results_dict = {}
		self.results = {}
		self.name_list = ["palm_cuboid_test", "palm_cylinder_test", "joint_pin_bottom", "joint_pin_top", "segment_general", "segment_distal"]
	
	def main(self, udate_json=False):
		"""Call the test methods.

		Args:
			udate_json (bool, optional): Trigger to save a new json key or not. Defaults to False.
		"""
		self.palm_cuboid_test()
		self.palm_cylinder_test()
		self.joint_pin_bottom()
		self.joint_pin_top()
		self.segment_general()
		self.segment_distal()
		self.check_output()

		if udate_json == True:
			write_json(self.test_results_location, self.test_results_dict)


	def palm_cuboid_test(self): # 0
		"""Test generation of the cuboid palm."""
		palm_dict = {
				"palm_style" : "cuboid",
				"palm_dimensions" : [0.50,2.0,0.5]
		}
		palm_cubiod = generator.PalmGenerator(palm_dict=palm_dict)
		palm_cubiod.cuboid_palm()
		palm_cubiod_vert_data = []
		palm_cubiod_faces = []
		for vert in palm_cubiod.verts:
			palm_cubiod_vert_data.append([round(vert[0], 5), round(vert[1], 5), round(vert[2], 5)])
		for face in palm_cubiod.faces:
			palm_cubiod_faces.append(list(face))
		self.test_results_dict[self.name_list[0]] = {"verts" : palm_cubiod_vert_data, "faces" : palm_cubiod_faces} #palm_cubiod_face_data} 

	
	def palm_cylinder_test(self): # 1
		"""Test generation of the cylinder palm."""
		palm_dict = {
				"palm_style" : "cylinder",
				"palm_dimensions" : [0.50,2.0,0.5]
		}
		palm_cylinder = generator.PalmGenerator(palm_dict=palm_dict, run_trigger=False)
		palm_cylinder.cylinder_palm()
		palm_cylinder_vert_data = []
		palm_cylinder_faces = []
		for vert in palm_cylinder.verts:
			palm_cylinder_vert_data.append([round(vert[0], 5), round(vert[1], 5),round(vert[2], 5)])
		for face in palm_cylinder.faces:
			palm_cylinder_faces.append(list(face))
		self.test_results_dict[self.name_list[1]] = {"verts" : palm_cylinder_vert_data, "faces": palm_cylinder_faces}


	def joint_pin_bottom(self): # 2
		"""Test pin joint bottom."""
		joint_dict = {
                    "joint_style" : "pin",
                    "joint_dimensions" : [0.1 , 0.1, 0.1],
                    "joint_range" : [0,180],
                    "joint_friction" : "n/a"
                }
		joint_pin_bottom = generator.JointGenerator(joint_dict, [0,0,0])
		joint_pin_bottom.pin_joint_bottom(orientation=0.0)
		joint_pin_bottom_vert = []
		joint_pin_bottom_faces = []
		for vert in joint_pin_bottom.verts:
			joint_pin_bottom_vert.append([round(vert[0], 5), round(vert[1], 5), round(vert[2], 5)])
		for face in joint_pin_bottom.faces:
			joint_pin_bottom_faces.append(list(face))
		self.test_results_dict[self.name_list[2]] = {"verts": joint_pin_bottom_vert, "faces": joint_pin_bottom_faces}
		
	def joint_pin_top(self): # 3
		"""Test pin joint top."""
		joint_dict = {
                    "joint_style" : "pin",
                    "joint_dimensions" : [0.1 , 0.1, 0.1],
                    "joint_range" : [0,180],
                    "joint_friction" : "n/a"
                }
		joint_pin_top = generator.JointGenerator(joint_dict, [0,0,0])
		joint_pin_top.pin_joint_top(orientation=0.0)
		joint_pin_top_verts = []
		joint_pin_top_faces = []
		for vert in joint_pin_top.verts:
			joint_pin_top_verts.append([round(vert[0], 5), round(vert[1], 5), round(vert[2], 5)])
		for face in joint_pin_top.faces:
			joint_pin_top_faces.append(list(face))
		self.test_results_dict[self.name_list[3]] = {"verts": joint_pin_top_verts, "faces": joint_pin_top_faces}

	def segment_general(self): # 4
		"""Test general segment generation."""
		segment_dict = {
                "segment_profile" : [[0.0,0.05,0],[0,0.05,0]],
                "segment_dimensions" : [0.1 , 0.1, 0.5],
                "segment_bottom_joint" : {
                    "joint_style" : "pin",
                    "joint_dimensions" : [0.1 , 0.1, 0.1],
                    "joint_range" : [0,180],
                    "joint_friction" : "n/a"
                },
                "segment_top_joint" : {
                    "joint_style" : "pin",
                    "joint_dimensions" : [0.1 , 0.1, 0.1],
                    "joint_range" : [0,180],
                    "joint_friction" : "n/a"
                }
		}
		segment_general = generator.FingerSegmentGenerator(segment_dict=segment_dict, run_trigger=False)
		segment_general.general_segment(generate_joints=False)
		segment_general_verts = []
		segment_general_faces = []
		for vert in segment_general.verts:
			segment_general_verts.append([round(vert[0], 5), round(vert[1], 5), round(vert[2], 5)])
		for face in segment_general.faces:
			segment_general_faces.append(list(face))
		self.test_results_dict[self.name_list[4]] = {"verts": segment_general_verts, "faces": segment_general_faces}

	def segment_distal(self): # 5
		"""Test distal segment generation."""
		segment_distal_dict = {
                "segment_profile" : [[0,0.05,0],[0,0.05,0], [0.00,0.0,0.05], [0.00,0.0,0.05]],
                "segment_dimensions" : [0.1 , 0.1, 0.5],
                "segment_bottom_joint" : {
                    "joint_style" : "pin",
                    "joint_dimensions" : [0.1 , 0.1, 0.1],
                    "joint_range" : [0,180],
                    "joint_friction" : "n/a"
                }
            }
		segment_distal = generator.FingerSegmentGenerator(segment_dict=segment_distal_dict)
		segment_distal_verts = []
		segment_distal_faces = []
		for vert in segment_distal.verts:
			segment_distal_verts.append([round(vert[0], 5), round(vert[1], 5), round(vert[2], 5)])
		for face in segment_distal.faces:
			segment_distal_faces.append(list(face))	
		self.test_results_dict[self.name_list[5]] = {"verts": segment_distal_verts, "faces": segment_distal_faces}

	def check_output(self):
		"""Check if the new values match the old values."""
		print('\n')
		for name in self.name_list:
			if self.test_results_dict[name]["verts"] == self.test_key_dict[name]["verts"]:
				vertex_result = 'Passed'
			else:
				vertex_result = 'Failed'

			if  self.test_results_dict[name]["faces"] == self.test_key_dict[name]["faces"]:
				face_result = 'Passed'
			else:
				face_result = 'Failed'

			print(f'{name} vertex check:  {vertex_result},    face check: {face_result}')


def write_json(json_loc, json_data):
	"""Write contant into the json file.

	Args:
		json_loc (str): file location of the json file to write
		json_data (dictionary): dictionary containing test results.
	"""
	with open(json_loc,'w') as write_file:
		json.dump(json_data, write_file, indent=4)

def read_json(json_loc):
	"""Read a given json file in as a dictionary.

	Args:
		json_loc (str): path to the json file to be read in

	Returns:
		(dictionary): A dictionary of the json that was read in
	"""
	with open(json_loc, "r") as read_file:
		dictionary = json.load(read_file)
	return dictionary

if __name__ == '__main__':

	directory_dict = read_json('../src/.user_info.json') # relative path to json file that contains absolute paths to different directories.
	
	sys.path.append(bpy.path.abspath("//")+directory_dict['src']) # this lets me import the other scripts that I made

	import generator

	test = TestGenerator()
	test.main(False)