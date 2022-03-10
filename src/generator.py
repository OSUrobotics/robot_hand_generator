#!~/software/blender-2.93/2.93/python/bin/python3.9

from bpy import data, context
import bpy
import mathutils
from mathutils import Matrix, Vector
import bmesh
import numpy as np
import os
import sys
import json
from math import sin, cos, tan, pi


class MainGenerator():
	"""Main Class that calls the HandGenerator class and ObjectGenerator class."""

	def __init__(self, directory_dict, project_dict):
		"""Initialize method for the MainGenerator.

		Args:
			directory_dict (dictionary): A dictionary containing the location of needed directories 
			project_dict (dictionary): A dictionary that describes the desired hand and objects to be generated
		"""
		self.directory_dict = directory_dict
		self.project_dict = project_dict
		
		HF.delete_all()

		HandGenerator(hand_dict=self.project_dict['hand'], directory_dict=self.directory_dict)


class HandGenerator():
	"""This class controls the process for generating a hand."""

	def __init__(self, hand_dict, directory_dict):
		"""Initialize method for HandGenerator class.

		Args:
			hand_dict (dictionary): A dictionary that describes the hand to be generated
			directory_dict (dictioanry): A dictionary that contains the paths to useful directories
		"""
		self.hand_dict = hand_dict
		self.directory_dict = directory_dict
		self.hand_directory = f'{self.directory_dict["hand_model_output"]}{self.hand_dict["hand_name"]}/hand/'
		self.obj_files = f'{self.hand_directory}obj_files/'
		HF.directory_maker(self.hand_directory)
		HF.directory_maker(self.obj_files)
		self.mesh_queue = {}
		self.main()
	
	def main(self):
		"""Call the Generator classes for the palm and fingers."""
		self.mesh_queue["palm"] = PalmGenerator(self.hand_dict["palm"], run_trigger=True)

		finger_list = []

		for finger_number in range(self.hand_dict["palm"]["finger_qty"]):
			finger_list.append(FingerGenerator(self.hand_dict[f'finger_{finger_number}'], run_trigger=True))
		self.mesh_queue["fingers"] = finger_list
		self.create_meshes()
		self.generate_urdf()
		
	def create_meshes(self):
		"""Create and export the meshes for the hand components."""
		palm_names = []
		HF.blender_make_mesh(self.mesh_queue["palm"].verts, self.mesh_queue["palm"].faces, "palm_base")
		HF.export_part("palm_collision", self.obj_files)
		palm_names.append("palm_base")
		for i, joint in enumerate(self.mesh_queue["palm"].joint_list):
			# print(i, joint.verts)
			# print('\n')
			HF.blender_make_mesh(joint.verts, joint.faces, f"palm_joint_{i}")
			palm_names.append(f"palm_joint_{i}")
		HF.join_parts(palm_names, "palm")
		HF.export_part("palm", self.obj_files)
		HF.delete_all()
		
		for finger_number, finger in enumerate(self.mesh_queue["fingers"]):
			for segment_number, segment in enumerate(finger.segments):

				print(len(segment.verts), len(segment.faces))		
				HF.blender_make_mesh(segment.verts, segment.faces, f"finger{finger_number}_segment{segment_number}")
				HF.export_part(f"finger{finger_number}_segment{segment_number}_collision", self.obj_files)
				HF.blender_make_mesh(segment.segment_joint[0].verts, segment.segment_joint[0].faces, f"finger{finger_number}_segment{segment_number}_bottom")
				if segment_number == len(finger.segments) - 1:
					HF.join_parts([f"finger{finger_number}_segment{segment_number}_bottom", f"finger{finger_number}_segment{segment_number}"], f"finger{finger_number}_segment{segment_number}_combined")
				else:
					HF.blender_make_mesh(segment.segment_joint[1].verts, segment.segment_joint[1].faces, f"finger{finger_number}_segment{segment_number}_top")
					HF.join_parts([f"finger{finger_number}_segment{segment_number}_bottom", f"finger{finger_number}_segment{segment_number}_top", f"finger{finger_number}_segment{segment_number}"], f"finger_{finger_number}_segment{segment_number}_combined")
				
				HF.export_part(f"finger{finger_number}_segment{segment_number}", self.obj_files)
				HF.delete_all()

	def generate_urdf(self):
		"""Generate the urdf for the hand."""
		self.urdf = UrdfGenerator(f'{self.hand_directory}')

		self.urdf.start_file(self.hand_dict["hand_name"])

		self.urdf.link(name = "palm", pose=(0,0,0,0,0,0), model_name="palm")

		for finger_number in range(self.hand_dict["palm"]["finger_qty"]):
			finger = self.hand_dict[f"finger_{finger_number}"]
			initial_pose = finger["finger_pose"]
			segment0 = finger["segment_0"]
			previous_height = self.mesh_queue["fingers"][finger_number].segments[0].top_length
			self.urdf.link(f"finger{finger_number}_segment0")
			self.urdf.joint(f"finger{finger_number}_segment0_joint", "revolute", f"finger{finger_number}_segment0", "palm", (1,0,0), (0,0,(finger["finger_pose"][2]+180) * pi /180), (finger["finger_pose"][0] * sin(finger["finger_pose"][1]*pi/180), finger["finger_pose"][0] * cos(finger["finger_pose"][1]*pi/180), 0))
			for segment_number in range(1, finger[f"segment_qty"]):
				self.urdf.link(f"finger{finger_number}_segment{segment_number}")
				self.urdf.joint(f"finger{finger_number}_segment{segment_number}_joint", "revolute", f"finger{finger_number}_segment{segment_number}", f"finger{finger_number}_segment{segment_number-1}", (1,0,0), xyz_in=(0,0,previous_height))
				previous_height = self.mesh_queue["fingers"][finger_number].segments[segment_number].top_length
			
		self.urdf.end_file()
		self.urdf.write(filename=self.hand_dict["hand_name"])

class PalmGenerator():
	"""Generator for the Palm."""

	def __init__(self, palm_dict, run_trigger=False):
		"""Initialize the PalmGenerator.

		Args:
			palm_dict (Dictionary): A dictionary that describes the palm to be generated
			run_trigger (bool, optional): A trigger that determines if the main method is ran or if they will be mannually called. Defaults to False.
		"""
		self.palm_dict = palm_dict
		self.verts = []
		self.faces = []
		self.joint_list = []
		self.bottom_center_xyz = [0,0,0]
		if run_trigger == True:
			self.main()
			
	def main(self):
		"""Call the method to generate the style of palm, and the joints that go with it."""
		if self.palm_dict["palm_style"] == "cylinder":
			self.cylinder_palm()
		elif self.palm_dict["palm_style"] == "cuboid":
			self.cuboid_palm()
		# HF.blender_make_mesh(verts=verts, faces=faces, mesh_name="palm")
		
		# joint_list = []
		for joint_number in range(self.palm_dict["finger_qty"]):
			distance, angle, _ = self.palm_dict["palm_joints"][f'finger_{joint_number}']["joint_pose"]
			bottom_center_xyz = [distance * sin(angle*pi/180),distance * cos(angle*pi/180), 0]
			self.joint_list.append(JointGenerator(self.palm_dict["palm_joints"][f'finger_{joint_number}'], bottom_center_xyz=bottom_center_xyz, joint_bottom=True, run_trigger=True))
		
	
	def cuboid_palm(self):
		"""Generate a cuboid style palm."""
		dimensions = self.palm_dict["palm_dimensions"]
		start_stop_verts_dict = {}
		# verts = []

		top_verts = [
			Vector((-1*dimensions[0]/2,  dimensions[1]/2,    0)), 
			Vector((-1*dimensions[0]/2,  -1*dimensions[1]/2, 0)),
			Vector((dimensions[0]/2,     -1*dimensions[1]/2, 0)),
			Vector((dimensions[0]/2,     dimensions[1]/2,    0))]
		
		self.verts += top_verts
		start_stop_verts_dict['top_verts'] = (0, len(self.verts)-1)

		bottom_verts = [
			Vector(( -1*dimensions[0]/2,  dimensions[1]/2,    -1* dimensions[2])), 
			Vector(( -1*dimensions[0]/2,  -1*dimensions[1]/2, -1* dimensions[2])),
			Vector(( dimensions[0]/2,     -1*dimensions[1]/2, -1* dimensions[2])),
			Vector(( dimensions[0]/2,     dimensions[1]/2,    -1* dimensions[2]))]
		self.verts += bottom_verts
		
		start_stop_verts_dict['bottom_verts'] = (len(top_verts), len(self.verts)-1)
		
		top_face = [(0, 1, 2, 3)]
		bottom_face = [tuple(range(start_stop_verts_dict['bottom_verts'][1], start_stop_verts_dict['bottom_verts'][0]-1, -1))]

		top_vertex = range(start_stop_verts_dict['top_verts'][0], start_stop_verts_dict['top_verts'][1] + 1)
		bottom_vertex = range(start_stop_verts_dict['bottom_verts'][0], start_stop_verts_dict['bottom_verts'][1] + 1)
		side_faces = []
		for i in range(4):
			side_faces.append((
				top_vertex[i -1],
				bottom_vertex[i -1],
				bottom_vertex[i],
				top_vertex[i]))

		self.faces = top_face + bottom_face + side_faces
		translation = Matrix.Translation(Vector(self.bottom_center_xyz))
		rotation = Matrix.Rotation(0.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(self.verts)):
			self.verts[i] = translation @ rotation @ self.verts[i]

	def cylinder_palm(self):
		"""Generate a Cylinder style palm."""
		dimensions = self.palm_dict["palm_dimensions"]
		start_stop_verts = {}
		# verts = []
		faces = []
		top_verts = []
		top_negative_verts = []
		top_positive_verts = []
		bottom_negative_verts = []
		bottom_positive_verts = []
		step_size = 0.001
		for x in np.arange(-1.0* dimensions[0]/2.0, dimensions[0]/2.0 + step_size, step_size):
			rounded_x = round(x,3)

			y = ((dimensions[1]/2)**2 * (1 - ((rounded_x-self.bottom_center_xyz[0])**2)/(dimensions[0]/2)**2)) ** 0.5 + self.bottom_center_xyz[1]
			negative_y = -1 * y
			top_negative_verts.append(Vector((rounded_x, negative_y, self.bottom_center_xyz[2])))
			bottom_negative_verts.append(Vector((rounded_x, negative_y, self.bottom_center_xyz[2] - dimensions[2])))
			
			if -1 * dimensions[0]/2 < rounded_x < dimensions[0]/2: 
				top_positive_verts.insert(0, Vector((rounded_x, y, self.bottom_center_xyz[2])))
				bottom_positive_verts.insert(0, Vector((rounded_x, y, self.bottom_center_xyz[2] - dimensions[2])))
		
		self.verts += top_negative_verts
		self.verts += top_positive_verts
		start_stop_verts['top_verts'] = (0, len(self.verts)-1)
		self.verts += bottom_negative_verts
		self.verts += bottom_positive_verts
		start_stop_verts['bottom_verts'] = (start_stop_verts['top_verts'][1] + 1, len(self.verts) - 1)

		top_face = [tuple(range(start_stop_verts['top_verts'][0], start_stop_verts['top_verts'][1] + 1, 1))]
		bottom_face = [tuple(range(start_stop_verts['bottom_verts'][1], start_stop_verts['bottom_verts'][0] - 1, -1))]
		side_faces = []

		top_vertex = range(start_stop_verts['top_verts'][0], start_stop_verts['top_verts'][1] + 1)
		bottom_vertex = range(start_stop_verts['bottom_verts'][0], start_stop_verts['bottom_verts'][1] + 1)

		for vertex in range(start_stop_verts['top_verts'][1] + 1):
			side_faces.append((
				top_vertex[vertex-1],
				bottom_vertex[vertex-1],
				bottom_vertex[vertex],
				top_vertex[vertex]))
	
		self.faces += top_face
		self.faces += bottom_face
		self.faces += side_faces


class JointGenerator():
	"""Generate different joints."""

	def __init__(self, joint_dict, bottom_center_xyz, joint_bottom=True, run_trigger=False): # joint_bottom is bottom of the joint not the bottom of the segment
		"""Initialize the JointGenerator Class.

		Args:
			joint_dict (Dictionary): A dictionary that describes the desired joint
			bottom_center_xyz ([x_val, y_val, z_val]): [x,y,z] location of the center bottom face of the joint 
			joint_bottom (bool, optional): Sets if the joint is located on the bottom or top of the finger segment. Defaults to True.
			run_trigger (bool, optional): A trigger te say if it runs automatically or will be called manually. Defaults to False.
		"""
		self.joint_dict = joint_dict
		self.bottom_center_xyz = bottom_center_xyz
		self.verts = []
		self.faces = []

		if joint_bottom == True and run_trigger ==True:
			self.main_bottom()
		elif joint_bottom == False and run_trigger == True:
			self.main_top()

	def main_bottom(self):
		"""Determine and call the method for the style of the bottom joint."""
		if self.joint_dict.__contains__("joint_pose"):
			orientation = self.joint_dict["joint_pose"][-1]
		else:
			orientation = 0
		
		if self.joint_dict["joint_style"] == "pin":
			self.pin_joint_bottom(orientation=orientation)  
			

	def main_top(self):
		"""Determine and call the method for the style of the top joint."""
		if self.joint_dict.__contains__("joint_pose"):
			orientation = self.joint_dict["joint_pose"][-1]
		else:
			orientation = 0
		
		if self.joint_dict["joint_style"] == "pin":
			self.pin_joint_top(orientation=orientation)
		
	def pin_joint_bottom(self, orientation=0.0): # This is the bottom of the joint, so for a pin joint it is the half cylinder
		"""Generate the bottom portion of the joint, ie for a pin joint the half cylinder portion.

		Args:
			orientation (float, optional): The angle(degrees) to rotate the joint about it's z-axis only for joints on the palm. Defaults to 0.0.
		"""
		width, depth, length = self.joint_dict["joint_dimensions"]
		
		start_stop_verts = {}

		self.bottom_center_xyz = self.bottom_center_xyz

		front_verts = []
		back_verts = []
		joint_raduis = depth / 2  # blender y-axis
		half_joint_width = width / 2  # blender x-axis
		joint_length_half = length / 2 # blender z-axis
		front_verts.append(Vector((-1* half_joint_width, -1*joint_raduis, 0)))
		back_verts.append(Vector((half_joint_width, -1*joint_raduis, 0)))

		for y_loc in np.arange(-1*joint_raduis + 0.001, joint_raduis - 0.001, 0.001):
			y_loc_use = np.round(y_loc,3)
			
			# z_loc = (joint_raduis**2 - x_loc**2) ** 0.5 + self.bottom_center_xyz[2]
			z_loc = (joint_length_half**2 * (1 - (y_loc_use - 0)**2 / joint_raduis**2))**.5 + 0
			# print(f'y: {y_loc_use}, z: {z_loc}')
			# y = ((dimensions[1]/2)**2 * (1 - ((rounded_x-self.bottom_center_xyz[0])**2)/(dimensions[0]/2)**2)) ** 0.5 + self.bottom_center_xyz[1]

			front_verts.append(Vector(( -1* half_joint_width, y_loc_use, z_loc)))
			back_verts.append(Vector((half_joint_width, y_loc_use, z_loc)))

		front_verts.append(Vector((-1*half_joint_width, joint_raduis, 0)))
		back_verts.append(Vector((half_joint_width, joint_raduis, 0)))
		self.verts += front_verts
		start_stop_verts['front_verts'] = (0, len(self.verts)-1)
		
		self.verts += back_verts
		start_stop_verts['back_verts'] = (start_stop_verts['front_verts'][1]+1, len(self.verts)-1)

		back_face = [tuple(range(start_stop_verts['back_verts'][1], start_stop_verts['back_verts'][0] - 1, -1))]
		front_face = [tuple(range(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1] + 1, 1))]

		top_faces = []
		for loc in range(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1], 1):
			top_faces.append((start_stop_verts['front_verts'][0] + loc, start_stop_verts['back_verts'][0] + loc, start_stop_verts['back_verts'][0]+loc + 1, start_stop_verts['front_verts'][0] + loc + 1))
		
		bottom_face = [(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1], start_stop_verts['back_verts'][1], start_stop_verts['back_verts'][0])]

		self.faces += front_face
		self.faces += back_face
		self.faces += top_faces
		self.faces += bottom_face

		translation = Matrix.Translation(Vector(self.bottom_center_xyz))

		rotation = Matrix.Rotation(orientation * pi/180.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(self.verts)):
			self.verts[i] = translation @ rotation @ self.verts[i]


	def pin_joint_top(self, orientation=0.0):
		"""Generate the top portion of the pin joint, ie the cuboid stem.

		Args:
			orientation (float, optional): The angle(degrees) for rotating the joint anbout it's z-axis. Defaults to 0.0.
		"""
		width, depth, joint_length = self.joint_dict["joint_dimensions"]
		joint_width = width * 0.9
		joint_depth = depth * 0.4
		
		start_stop_verts_dict = {}
		
		top_verts = [
			Vector(( joint_width/2,    -1*joint_depth/2,    joint_length)), 
			Vector(( -1*joint_width/2, -1*joint_depth/2,    joint_length)),
			Vector(( -1*joint_width/2, joint_depth/2,       joint_length)),
			Vector(( joint_width/2,    joint_depth/2,       joint_length))]
		self.verts += top_verts
		start_stop_verts_dict['top_verts'] = (0, len(self.verts)-1)
		bottom_verts = [
			Vector(( joint_width/2,    -1*joint_depth/2,  0)), 
			Vector(( -1*joint_width/2, -1*joint_depth/2,  0)),
			Vector(( -1*joint_width/2, joint_depth/2,     0)),
			Vector(( joint_width/2,    joint_depth/2,     0))]
		
		self.verts += bottom_verts
		
		start_stop_verts_dict['bottom_verts'] = (len(top_verts), len(self.verts)-1)
		
		bottom_face = [tuple(range(start_stop_verts_dict['bottom_verts'][0], start_stop_verts_dict['bottom_verts'][1]+1, 1))]

		top_vertex = range(start_stop_verts_dict['top_verts'][0], start_stop_verts_dict['top_verts'][1] + 1)
		bottom_vertex = range(start_stop_verts_dict['bottom_verts'][0], start_stop_verts_dict['bottom_verts'][1] + 1)
		side_faces = []
		for i in range(4):
			side_faces.append((
				top_vertex[i -1],
				top_vertex[i],
				bottom_vertex[i],
				bottom_vertex[i -1]))
		self.faces += bottom_face
		self.faces += side_faces
		rotation = Matrix.Rotation(orientation * pi / 180.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(self.verts)):
			self.verts[i] = rotation @ self.verts[i]
		

class FingerGenerator():
	"""Generate fingers for the hand."""

	def __init__(self, finger_dict, run_trigger=False):
		"""Intialize the FingerGenerator Class.

		Args:
			finger_dict (Dictionary): A dictionary that describes the finger to be generated
			run_trigger (bool, optional): Trigger that determines if the generator will auto-run or be manually called. Defaults to False.
		"""
		self.finger_dict = finger_dict
		self.segments = []
		if run_trigger == True:
			self.main()

	
	def main(self):
		"""Call the segment generator to generate the segments for the finger."""
		for segment_number in range(self.finger_dict["segment_qty"]):
			self.segments.append(FingerSegmentGenerator(self.finger_dict[f"segment_{segment_number}"]))


class FingerSegmentGenerator():
	"""Generate the finger segment."""

	def __init__(self, segment_dict):
		"""Initialize the FingerSegmentGenerator class.

		Args:
			segment_dict (Dictionary): A dictionary that describes the segment that is going to be generated
		"""
		self.segment_dict = segment_dict
		self.segment_joint = []
		self.verts = []
		self.faces = []
		if len(self.segment_dict["segment_profile"]) == 2:
			self.general_segment()
		elif len(self.segment_dict["segment_profile"]) == 4:
			self.distal_segment()
	
	def general_segment(self):
		"""Generate the generaric segment mostly the proximal and intermediate segments."""
		start_stop_verts = {}
		width, depth, length = self.segment_dict["segment_dimensions"]
		bottom_joint_length = self.segment_dict["segment_bottom_joint"]["joint_dimensions"][2]
		self.top_length = length + bottom_joint_length
		segment_profiles = self.segment_dict["segment_profile"]
		bottom_bezier_verts = HF.bezier_curve([width/2, 0, 0],
												[width/2 + segment_profiles[0][0], segment_profiles[0][1], segment_profiles[0][2]],
												[-1*width/2 + segment_profiles[1][0], segment_profiles[1][1], segment_profiles[1][2]],
												[-1*width/2, 0, 0])
		self.verts += bottom_bezier_verts
		start_stop_verts["bottom_bezier_verts"] = (0, len(self.verts)-1)

		top_bezier_verts = HF.bezier_curve([width/2, 0, length],
											[segment_profiles[0][0], segment_profiles[0][1], segment_profiles[0][2] + length],
											[-1*segment_profiles[1][0], segment_profiles[1][1], segment_profiles[1][2] + length],
											[-1*width/2, 0, length])
		self.verts += top_bezier_verts
		start_stop_verts["top_bezier_verts"] = (start_stop_verts["bottom_bezier_verts"][0]+1, len(self.verts)-1)
		
		max_y_value = 0
		for vert in self.verts:
			if vert[1] > max_y_value:
				max_y_value = vert[1]
		remaining_depth = depth - max_y_value

		self.verts.append(Vector((width/2, -1*remaining_depth, length)))
		self.verts.append(Vector((-1*width/2, -1*remaining_depth, length)))
		self.verts.append(Vector((-1*width/2, -1*remaining_depth, 0)))
		self.verts.append(Vector((width/2, -1*remaining_depth, 0)))
		bottom_face = [tuple(range(start_stop_verts['bottom_bezier_verts'][1], start_stop_verts['bottom_bezier_verts'][0]-1, -1)) + (len(self.verts) - 1, len(self.verts) - 2)]
		top_face = [tuple(range(start_stop_verts['top_bezier_verts'][0], start_stop_verts['top_bezier_verts'][1]+1)) + (len(self.verts)-3, len(self.verts)-4)]
		side_faces = [(start_stop_verts['bottom_bezier_verts'][0], start_stop_verts['top_bezier_verts'][0], len(self.verts)-4, len(self.verts)-1),
						(start_stop_verts['bottom_bezier_verts'][1], len(self.verts)-2, len(self.verts)-3, start_stop_verts['top_bezier_verts'][1]),
						(len(self.verts)-4, len(self.verts)-3, len(self.verts)-2, len(self.verts)-1)]

		front_faces = []
		offset = start_stop_verts['bottom_bezier_verts'][1]
		for i in range(1,start_stop_verts['bottom_bezier_verts'][1]+1):
			front_faces.append((i, i+1, i+offset+1, i + offset))
		
		self.faces += bottom_face
		self.faces += top_face
		self.faces += side_faces
		self.faces += front_faces

		bezier_y_offset = depth/2 - max_y_value
		translate = Matrix.Translation(Vector((0.0, bezier_y_offset, bottom_joint_length)))
		for i in range(len(self.verts)):
			self.verts[i] = translate @ self.verts[i]
		
		# Calls the joint generator to create the top and bottom portions of the joint
		self.segment_joint.append(JointGenerator(self.segment_dict["segment_bottom_joint"], [0.0,0.0,0.0], joint_bottom=False, run_trigger=True))
		self.segment_joint.append(JointGenerator(self.segment_dict["segment_top_joint"], [0.0,0.0, self.top_length], joint_bottom=True, run_trigger=True))
		


	def distal_segment(self):
		"""Generate the distal segment. This one uses two bezier curves, one describes the segment face profile the other describes the segment top profile."""
		start_stop_verts = {}
		width, depth, length = self.segment_dict["segment_dimensions"]
		bottom_joint_length = self.segment_dict["segment_bottom_joint"]["joint_dimensions"][2]
		self.top_length = length + bottom_joint_length

		segment_profiles = self.segment_dict["segment_profile"]
		bottom_bezier_verts = HF.bezier_curve([width/2, 0, 0],
												[width/2 + segment_profiles[0][0], segment_profiles[0][1], segment_profiles[0][2]],
												[-1*width/2 + segment_profiles[1][0], segment_profiles[1][1], segment_profiles[1][2]],
												[-1*width/2, 0, 0])
		self.verts += bottom_bezier_verts
		start_stop_verts["bottom_bezier_verts"] = (0, len(self.verts)-1)

		top_bezier_verts = HF.bezier_curve([width/2, 0, length],
											[segment_profiles[0][0], segment_profiles[0][1], segment_profiles[0][2] + length],
											[-1*segment_profiles[1][0], segment_profiles[1][1], segment_profiles[1][2] + length],
											[-1*width/2, 0, length])
		self.verts += top_bezier_verts
		start_stop_verts["top_bezier_verts"] = (start_stop_verts["bottom_bezier_verts"][0]+1, len(self.verts)-1)
		
		max_y_value = 0
		for vert in self.verts:
			if vert[1] > max_y_value:
				max_y_value = vert[1]
		remaining_depth = depth - max_y_value

		top_bezier_point1 = self.segment_dict["segment_profile"][2]
		top_bezier_point2 = self.segment_dict["segment_profile"][3]
		top_verts = []
		for vertex in top_bezier_verts:
			top_verts.append(HF.bezier_curve(
				[vertex[0], vertex[1], vertex[2]],
				[vertex[0] + top_bezier_point1[0], vertex[1] + top_bezier_point1[1], vertex[2] + top_bezier_point1[2]],
				[vertex[0] + top_bezier_point2[0], top_bezier_point2[1] - remaining_depth, vertex[2] + top_bezier_point2[2]],
				[vertex[0], -remaining_depth, vertex[2]]
			))

		start_points = []
		end_points = []
		for vert_list in top_verts:
			start_points.append(len(self.verts))
			self.verts += vert_list
			end_points.append(len(self.verts)-1)
		
		self.verts.append(Vector((-1*width/2, -1*remaining_depth, 0)))
		self.verts.append(Vector((width/2, -1*remaining_depth, 0)))
		bottom_face = [tuple(range(start_stop_verts['bottom_bezier_verts'][1], start_stop_verts['bottom_bezier_verts'][0]-1, -1)) + (len(self.verts) - 1, len(self.verts) - 2)]

		back_face = [(len(self.verts)-2, len(self.verts)-1, end_points[0], end_points[-1])]
		side_face1 = [tuple(range(start_points[0], end_points[0] +1)) + (len(self.verts)-1,0)]
		side_face2 = [tuple(range(end_points[-1],start_points[-1] -1, -1)) + (len(bottom_bezier_verts)-1, len(self.verts)-2)]

		top_faces = []
		for i in range(len(top_verts)-1):
			for j in range(len(top_verts[i])-1):
				top_faces.append((j + start_points[i], j + start_points[i + 1], j + 1 + start_points[i + 1], j + 1 + start_points[i]))

		front_faces = []
		offset = start_stop_verts['bottom_bezier_verts'][1]
		for i in range(start_stop_verts['bottom_bezier_verts'][1] + 1):
			front_faces.append((i, i+1, i+offset+1, i + offset))
		
		self.faces += bottom_face
		self.faces += top_faces
		self.faces += side_face1
		self.faces += side_face2
		self.faces += front_faces
		self.faces += back_face

		bezier_y_offset = depth/2 - max_y_value
		translate = Matrix.Translation(Vector((0.0, bezier_y_offset, bottom_joint_length)))
		for i in range(len(self.verts)):
			self.verts[i] = translate @ self.verts[i]
		
		# Calls the joint generator to create the joint on the bottom of the segment
		self.segment_joint.append(JointGenerator(self.segment_dict["segment_bottom_joint"], [0.0,0.0,0.0], joint_bottom=False, run_trigger=True))
	
class ObjectGenerator():
	"""Generate the objects."""

	def __init__(self, object_dict):
		"""Initialize the ObjectGenerator class.

		Args:
			object_dict (Dictionary): A dictionary that describes the desired objects to be generated.
		"""
		self.object_dict = object_dict

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

	directory_dict = read_json('./.user_info.json') # relative path to json file that contains absolute paths to different directories.
	
	sys.path.append(bpy.path.abspath("//")+directory_dict['src']) # this lets me import the other scripts that I made

	# helper functions for blender generation and creating a urdf
	import helper_functions as HF 
	from urdf_creator import UrdfGenerator
	
	# this script is called using subprocess in the main.py and during the call the file name is passed in as an argument
	json_file_name = sys.argv[-1]

	hand_dict = read_json(json_file_name) # read in the json for the hand to be generated

	MainGenerator(directory_dict=directory_dict, project_dict=hand_dict) # start the generation process.