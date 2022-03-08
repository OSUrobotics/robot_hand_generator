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
	def __init__(self, directory_dict, project_dict):
		self.directory_dict = directory_dict
		self.project_dict = project_dict
		
		HF.delete_all()

		HandGenerator(hand_dict=self.project_dict['hand'])


class HandGenerator():
	def __init__(self, hand_dict):
		self.hand_dict = hand_dict
		self.mesh_queue = {}
		self.main()
	
	def main(self):
		self.mesh_queue["palm"] = PalmGenerator(self.hand_dict["palm"], run_trigger=True)

		finger_list = []

		for finger_number in range(self.hand_dict["palm"]["finger_qty"]):
			finger_list.append(FingerGenerator(self.hand_dict[f'finger_{finger_number}'], run_trigger=True))
		self.mesh_queue["fingers"] = finger_list
		self.create_meshes()
		
	def create_meshes(self):
		names = []
		HF.blender_make_mesh(self.mesh_queue["palm"].verts, self.mesh_queue["palm"].faces, "palm_base")
		names.append("palm_base")
		for i, joint in enumerate(self.mesh_queue["palm"].joint_list):
			print(i, joint.verts)
			print('\n')
			HF.blender_make_mesh(joint.verts, joint.faces, f"palm_joint_{i}")
			names.append(f"palm_joint_{i}")
		HF.join_parts(names, "palm")
		HF.export_part("palm", "./")
		HF.delete_all()
		
		segment = self.mesh_queue["fingers"][0].segments[0]
		
		# for finger_number
		HF.blender_make_mesh(segment.verts, segment.faces, "segment")
		HF.blender_make_mesh(segment.segment_joint[0].verts, segment.segment_joint[0].faces, "bottom")
		HF.blender_make_mesh(segment.segment_joint[1].verts, segment.segment_joint[1].faces, "top")
		HF.join_parts(["bottom", "top", "segment"], "finger")
		HF.export_part("finger", "./")


class PalmGenerator():
	def __init__(self, palm_dict, run_trigger=False):
		self.palm_dict = palm_dict
		self.verts = []
		self.faces = []
		self.joint_list = []
		self.bottom_center_xyz = [0,0,0]
		if run_trigger == True:
			self.main()
			
	def main(self):
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
		# return verts, faces

	def cylinder_palm(self, bottom_center_xyz=[0,0,0]):
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

		# return verts, faces


class JointGenerator():
	def __init__(self, joint_dict, bottom_center_xyz, joint_bottom=True, run_trigger=False): # joint_bottom is bottom of the joint not the bottom of the segment
		self.joint_dict = joint_dict
		self.bottom_center_xyz = bottom_center_xyz
		self.verts = []
		self.faces = []

		if joint_bottom == True and run_trigger ==True:
			self.main_bottom()
		elif joint_bottom == False and run_trigger == True:
			self.main_top()
	
	def main(self):
		pass

	def main_bottom(self):
		if self.joint_dict.__contains__("joint_pose"):
			orientation = self.joint_dict["joint_pose"][-1]
		else:
			orientation = 0
		
		if self.joint_dict["joint_style"] == "pin":
			self.pin_joint_bottom(orientation=orientation)  
			

	def main_top(self):
		if self.joint_dict.__contains__("joint_pose"):
			orientation = self.joint_dict["joint_pose"][-1]
		else:
			orientation = 0
		
		if self.joint_dict["joint_style"] == "pin":
			self.pin_joint_top(orientation=orientation)
		
	def pin_joint_bottom(self, orientation=0): # This is the bottom of the joint, so for a pin joint it is the half cylinder 
		width, depth, length = self.joint_dict["joint_dimensions"]
		
		start_stop_verts = {}
		# verts = []
		# faces = []

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
		
		bottom_face = [(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1]+1, start_stop_verts['back_verts'][1]+1, start_stop_verts['back_verts'][0])]

		self.faces += front_face
		self.faces += back_face
		self.faces += top_faces
		self.faces += bottom_face

		# print(f"\n\n\n {verts} \n\n\n")

		translation = Matrix.Translation(Vector(self.bottom_center_xyz))

		rotation = Matrix.Rotation(orientation * pi/180.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(self.verts)):
			self.verts[i] = translation @ rotation @ self.verts[i]


		# return verts, faces


	def pin_joint_top(self, orientation=0):
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
		# faces = []
		self.faces += bottom_face
		self.faces += side_faces
		rotation = Matrix.Rotation(orientation * pi / 180.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(self.verts)):
			self.verts[i] = rotation @ self.verts[i]
		
		# return verts, faces


class FingerGenerator():
	def __init__(self, finger_dict, run_trigger=False):
		self.finger_dict = finger_dict
		self.segments = []
		for segment_number in range(self.finger_dict["segment_qty"]):
			self.segments.append(FingerSegmentGenerator(self.finger_dict[f"segment_{segment_number}"]))

	
	def main(self):
		pass


class FingerSegmentGenerator():
	def __init__(self, segment_dict):
		self.segment_dict = segment_dict
		self.segment_joint = []
		self.verts = []
		self.faces = []
		if len(self.segment_dict["segment_profile"]) == 2:
			self.general_segment()
		elif len(self.segment_dict["segment_profile"]) == 4:
			self.distal_segment()
	
	def general_segment(self):
		start_stop_verts = {}
		width, depth, length = self.segment_dict["segment_dimensions"]
		bottom_joint_length = self.segment_dict["segment_bottom_joint"]["joint_dimensions"][2]
		self.top_length = length + bottom_joint_length
		# self.segment_joint.append(JointGenerator(self.segment_dict["segment_bottom_joint"], [0.0,0.0,0.0], joint_bottom=False, run_trigger=True))
		# self.segment_joint.append(JointGenerator(self.segment_dict["segment_top_joint"], [0.0,0.0, self.top_length], joint_bottom=True, run_trigger=True))
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
		
		# self.segment_dict["segment_top_joint"]["joint_dimensions"][1] = remaining_depth
		self.segment_joint.append(JointGenerator(self.segment_dict["segment_bottom_joint"], [0.0,0.0,0.0], joint_bottom=False, run_trigger=True))
		self.segment_joint.append(JointGenerator(self.segment_dict["segment_top_joint"], [0.0,0.0, self.top_length], joint_bottom=True, run_trigger=True))
		


	def distal_segment(self):
		pass
	
class ObjectGenerator():
	def __init__(self, object_dict, functions):
		self.object_dict = object_dict
		self.functions = functions

def read_json(json_loc):

		with open(json_loc, "r") as read_file:
			dictionary = json.load(read_file)
		return dictionary


if __name__ == '__main__':
	# # functions = func.functions()
	# functions.delete_all()

	directory_dict = read_json('./.user_info.json')
	
	sys.path.append(bpy.path.abspath("//")+directory_dict['src']) # this lets me import the other scripts that I made

	import helper_functions as HF
	from urdf_creator import UrdfGenerator
	
	# test = HelperFunctions()
	# test.delete_all()
	json_file_name = sys.argv[-1]
	# print('\n\n\n')
	# print(json_file_name)
	# print('\n\n\n')
	hand_dict = read_json(json_file_name)
	# print(hand_dict)
	# print('\n\n\n')
	MainGenerator(directory_dict=directory_dict, project_dict=hand_dict)