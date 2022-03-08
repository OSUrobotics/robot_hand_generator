
from asyncio.constants import SENDFILE_FALLBACK_READBUFFER_SIZE
from tracemalloc import start
from bpy import data, context
import bpy
import mathutils
from mathutils import Matrix, Vector
import bmesh
import numpy as np
import os
from math import pi
#test

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def test_bezier():


	bottom_bezier_verts = bezier_curve([-1.0,0.0,0.0],[-1.0,1.0,0.0],[1.0,1.0,0.0],[1.0,0.0,0.0])

	faces1 = tuple(range(len(bottom_bezier_verts)))

	top_bezier_verts = bezier_curve([-1.0,0.0,1.0],[-1.0,1.0,1.0],[1.0,1.0,1.0],[1.0,0.0,1.0])

	#   verts3


	verts = bottom_bezier_verts + top_bezier_verts
	faces2 = tuple(range(len(bottom_bezier_verts),len(verts)))
	#   faces2 = tuple(range(len(verts)-1, len(bottom_bezier_verts)-1, -1))
	face_back = (0, len(bottom_bezier_verts)-1, len(verts)-1, len(bottom_bezier_verts))
	faces = [faces1, faces2,face_back]

	#   side_faces = [tuple(range(0, len(verts),1))]
	offset = len(bottom_bezier_verts)

	side_faces = []
	for i in range(len(bottom_bezier_verts) -1):
		side_faces.append((i+1, i, offset+i, offset + 1+i))
	#   
	faces += side_faces
	return  verts, faces

def triangle():

	verts = [(1,0,0), (.5,.75,0), (0,1,0), (-.5,.75,0), (-1,0,0),(-1,0,1), (-.5,.75,1), (0,1,1), (.5,.75,1), (1,0,1)]
	#    faces = [(0,1,2,3,4,5)]
	faces = [tuple(range(len(verts)))]
	return verts, faces


def export_part(name):
	"""
	export the object as an obj file
	Input: name: name of object you wish to export
	"""
	name += '.obj'
	target_file = os.path.join('./test_obj', name)
	bpy.ops.export_scene.obj(filepath=target_file, use_triangles=True, path_mode='COPY')

def translate_part(part_name, xyz):
		bpy.context.view_layer.objects.active = bpy.data.objects[part_name]
		bpy.context.object.location = xyz


class JointGenerator:
	def __init__(self):
		pass

	def pin_joint_top(self, center_location, joint_dimensions=[1,1,0.5], orientation=0):
		
		# This will be a half cylinder that the front will be deviate a little to match the bezier curve profile of the segment's top that it will attach to.
		#Initially this wont match the bezier curve
		

		start_stop_verts = {}
		verts = []
		faces = []

		front_verts = []
		back_verts = []
		joint_raduis = joint_dimensions[1] / 2
		half_joint_width = joint_dimensions[0] / 2
		joint_length_half = joint_dimensions[2] / 2
		for x_loc in np.arange(center_location[0] - joint_raduis, center_location[0] + joint_raduis + 0.001, 0.001 ):
			x_loc_use = np.round(x_loc,3)
			# z_loc = (joint_raduis**2 - x_loc**2) ** 0.5 + center_location[2]
			z_loc = (joint_length_half**2 * (1 - (x_loc_use - center_location[0])**2 / joint_raduis**2))**.5 + center_location[2]

			# y = ((dimensions[1]/2)**2 * (1 - ((rounded_x-center_location[0])**2)/(dimensions[0]/2)**2)) ** 0.5 + center_location[1]

			front_verts.append(Vector((x_loc_use, center_location[1] - half_joint_width, z_loc)))
			back_verts.append(Vector((x_loc_use, center_location[1] + half_joint_width, z_loc)))
		
		verts += front_verts
		start_stop_verts['front_verts'] = (0, len(verts)-1)
		
		verts += back_verts
		start_stop_verts['back_verts'] = (start_stop_verts['front_verts'][1]+1, len(verts)-1)

		back_face = [tuple(range(start_stop_verts['back_verts'][0], start_stop_verts['back_verts'][1] + 1, 1))]
		front_face = [tuple(range(start_stop_verts['front_verts'][1], start_stop_verts['front_verts'][0] - 1, -1))]

		top_faces = []
		for loc in range(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1], 1):
			top_faces.append((start_stop_verts['front_verts'][0] + loc, start_stop_verts['front_verts'][0] + loc + 1, start_stop_verts['back_verts'][0] + loc +1, start_stop_verts['back_verts'][0]+loc))
		
		bottom_face = [(start_stop_verts['front_verts'][0], start_stop_verts['front_verts'][1]+1, start_stop_verts['back_verts'][1]+1, start_stop_verts['back_verts'][0])]

		faces += front_face
		faces += back_face
		faces += top_faces
		# faces += bottom_face

		# print(f"\n\n\n {verts} \n\n\n")

		rotation = Matrix.Rotation(orientation * pi/180.0, 4, Vector((0.0,0.0,1.0)))
		for i in range(len(verts)):
			verts[i] = rotation @ verts[i]


		return verts, faces

	def pin_joint_bottom(self, center_location=[0,0,0], joint_dimensions=[1,1,0.5]):
		
		# This is the stem or the part of the joint that attaches to the bottom of the segment
		start_stop_verts_dict = {}
		verts = []
		
		top_verts = [
			(center_location[0] + -1*joint_dimensions[0]/2, center_location[1] + joint_dimensions[1]/2, center_location[2] + joint_dimensions[2]), 
			(center_location[0] + -1*joint_dimensions[0]/2, center_location[1] + -1*joint_dimensions[1]/2, center_location[2] + joint_dimensions[2]),
			(center_location[0] + joint_dimensions[0]/2, center_location[1] + -1*joint_dimensions[1]/2, center_location[2] + joint_dimensions[2]),
			(center_location[0] + joint_dimensions[0]/2, center_location[1] + joint_dimensions[1]/2, center_location[2] + joint_dimensions[2])]
		verts += top_verts
		start_stop_verts_dict['top_verts'] = (0, len(verts)-1)
		bottom_verts = [
			(center_location[0] + -1*joint_dimensions[0]/2, center_location[1]  + joint_dimensions[1]/2, center_location[2]), 
			(center_location[0] + -1*joint_dimensions[0]/2, center_location[1] + -1*joint_dimensions[1]/2, center_location[2]),
			(center_location[0] + joint_dimensions[0]/2, center_location[1] + -1*joint_dimensions[1]/2, center_location[2]),
			(center_location[0] + joint_dimensions[0]/2, center_location[1] + joint_dimensions[1]/2, center_location[2])]
		
		verts += bottom_verts
		
		start_stop_verts_dict['bottom_verts'] = (len(top_verts), len(verts)-1)
		
		# bottom_face = [(3,2,1,0)]
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
		faces = []
		faces += bottom_face
		faces += side_faces
		# faces += top_face
		return verts, faces


class FingerSegmentGenerator():
	def __init__(self):
		pass


	def finger_segment_generator(selfceneter_location=[0,0,0],
		front_bottom = [[-0.5, 0.0, 0.0], [-0.5, 0.2, 0.0] , [0.5, 0.2, 0.0], [0.5, 0.2, 0.0]], 
		front_top = [[-0.5, 0.0, 1.0], [-0.5, 0.2, 1.0] , [0.5, 0.2, 1.0], [0.5, 0.2, 1.0]]):
		
		start_stop_verts = {}
		verts = [(0.5,0.5,0), (-0.5, 0.5, 0), (-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5,0.5,1), (-0.5, 0.5, 1), (-0.5, -0.5, 1), (0.5, -0.5, 1)]
		faces = [(0,1,2,3), (4,5,6,7), (0,1,4,5), (1,2,5,6), (2,3,6,7), (3,0,7,4)]




		return verts, faces


	def distal_segment_generator(self,ceneter_location=[0,0,0],
		front_bottom = [[-0.5, 0.0, 0.0], [-0.5, 0.2, 0.0] , [0.5, 0.2, 0.0], [0.5, 0.2, 0.0]], 
		front_top = [[-0.5, 0.0, 1.0], [-0.5, 0.2, 1.0] , [0.5, 0.2, 1.0], [0.5, 0.2, 1.0]], 
		top = [[0.2, 0.2, 0.2], [0.2, 0.2, 0.2]],
		thickness = 1):

		start_stop_verts = {}
		# bottom_bezier_verts = bezier_curve([-1.0, 0.0, 0.0], [-1.0, front_bottom[0], 0.0], [1.0, front_bottom[1], 0.0], [1.0, 0.0, 0.0])
		# top_bezier_verts = bezier_curve([-1.0, 0.0, 1.0], [-1.0, front[0], 1.0], [1.0, front[1], 1.0], [1.0, 0.0, 1.0])

		verts = []

		bottom_bezier_verts = bezier_curve(front_bottom[0], front_bottom[1], front_bottom[2], front_bottom[3])
		verts += bottom_bezier_verts
		start_stop_verts['bottom_bezier_verts'] = (0, len(verts) - 1)
		
		top_bezier_verts = bezier_curve(front_top[0], front_top[1], front_top[2], front_top[3])
		verts += top_bezier_verts
		start_stop_verts['top_bezier_verts'] = (start_stop_verts['bottom_bezier_verts'][1] + 1, len(verts) - 1)
		# verts = bottom_bezier_verts + top_bezier_verts

		top_verts = []
		for i in top_bezier_verts:
			top_verts.append(bezier_curve(
				[i[0], i[1], i[2]], 
				[i[0] + top[0][0], i[1] + top[0][1], i[2] + top[0][2]], 
				[i[0] + top[1][0], -1.0 + top[1][1], i[2] + top[1][2]], 
				[i[0], -1.0, i[2]]))

		start_points = []
		end_points = []
		for vert_list in top_verts:
			start_points.append(len(verts))
			verts += vert_list
			end_points.append(len(verts)-1)

		start_stop_verts['top_verts'] = (start_stop_verts['top_bezier_verts'][1]+1, len(verts)-1)

		verts += [(front_bottom[0][0], -1 * thickness, front_bottom[0][-1]), (front_bottom[-1][0], -1 * thickness, front_bottom[-1][-1])]
		
		bottom_face = [tuple(range((len(bottom_bezier_verts)-1))) + (len(verts) - 1, len(verts) - 2)]

		side_face1 = tuple(range(end_points[0], start_points[0] -1, -1)) + (0, len(verts)-2)
		side_face2 = tuple(range(start_points[-1], end_points[-1]+1, 1)) + (len(verts) - 1, len(bottom_bezier_verts)-1)
		
		back_face = [(len(verts)-2, len(verts)-1, end_points[-1], end_points[0])]

		top_faces = []
		for i in range(len(top_verts)-1):
			for j in range(len(top_verts[i])-1):
				top_faces.append((j + start_points[i], j + 1 + start_points[i], j + 1 + start_points[i + 1], j + start_points[i + 1]))

		# faces = [faces1, faces2, face_back]

		#   side_faces = [tuple(range(0, len(verts),1))]
		offset = len(bottom_bezier_verts)

		front_faces = []
		for i in range(len(bottom_bezier_verts) -1):
			front_faces.append((i+1, i, offset+i, offset + 1+i))
		
		faces = []
		faces += front_faces
		faces += top_faces
		faces += bottom_face
		faces += [side_face1]
		faces += [side_face2]
		faces += back_face
		
		return  verts, faces

class PalmGenerator:
	def __init__(self):

		pass

	def cylinder_palm(self, center_location, dimensions):
		start_stop_verts = {}
		verts = []
		faces = []
		top_verts = []
		top_negative_verts = []
		top_positive_verts = []
		bottom_negative_verts = []
		bottom_positive_verts = []
		step_size = 0.001
		for x in np.arange(-1.0* dimensions[0]/2.0, dimensions[0]/2.0 + step_size, step_size):
			rounded_x = round(x,3)

			y = ((dimensions[1]/2)**2 * (1 - ((rounded_x-center_location[0])**2)/(dimensions[0]/2)**2)) ** 0.5 + center_location[1]
			negative_y = -1 * y
			top_negative_verts.append((rounded_x, negative_y, center_location[2]))
			bottom_negative_verts.append((rounded_x, negative_y, center_location[2] - dimensions[2]))
			
			if -1 * dimensions[0]/2 < rounded_x < dimensions[0]/2: 
				top_positive_verts.insert(0, (rounded_x, y, center_location[2]))
				bottom_positive_verts.insert(0, (rounded_x, y, center_location[2] - dimensions[2]))
		
		verts += top_negative_verts
		verts += top_positive_verts
		start_stop_verts['top_verts'] = (0, len(verts)-1)
		verts += bottom_negative_verts
		verts += bottom_positive_verts
		start_stop_verts['bottom_verts'] = (start_stop_verts['top_verts'][1] + 1, len(verts) - 1)


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
	
		faces += top_face
		faces += bottom_face
		faces += side_faces

		return verts, faces


		
	
	def square_palm(self, center_location, dimensions):
		

		start_stop_verts_dict = {}
		verts = []
		top_verts = [
			(center_location[0] + -1*dimensions[0]/2, center_location[1]  + dimensions[1]/2, center_location[2]), 
			(center_location[0] + -1*dimensions[0]/2, center_location[1] + -1*dimensions[1]/2, center_location[2]),
			(center_location[0] + dimensions[0]/2, center_location[1] + -1*dimensions[1]/2, center_location[2]),
			(center_location[0] + dimensions[0]/2, center_location[1] + dimensions[1]/2, center_location[2])]
		
		verts += top_verts
		start_stop_verts_dict['top_verts'] = (0, len(verts)-1)

		bottom_verts = [
			(center_location[0] + -1*dimensions[0]/2, center_location[1] + dimensions[1]/2, center_location[2] - dimensions[2]), 
			(center_location[0] + -1*dimensions[0]/2, center_location[1] + -1*dimensions[1]/2, center_location[2] - dimensions[2]),
			(center_location[0] + dimensions[0]/2, center_location[1] + -1*dimensions[1]/2, center_location[2] - dimensions[2]),
			(center_location[0] + dimensions[0]/2, center_location[1] + dimensions[1]/2, center_location[2] - dimensions[2])]
		verts += bottom_verts
		
		start_stop_verts_dict['bottom_verts'] = (len(top_verts), len(verts)-1)
		
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

		faces = top_face + bottom_face + side_faces
		return verts, faces


def bezier_curve(p1, p2, p3, p4):
	points = []
	for t in np.arange(0.0, 1.01, 0.01):
		points.append([
		(((1 - t) ** 3) * p1[0]) + (3*((1-t)**2) * t * p2[0]) + (3*(1-t) * (t ** 2) *p3[0]) + (t**3 * p4[0]),
		(((1 - t) ** 3) * p1[1]) + (3*((1-t)**2) * t * p2[1]) + (3*(1-t) * (t ** 2) *p3[1]) + (t**3 * p4[1]),
		(((1 - t) ** 3) * p1[2]) + (3*((1-t)**2) * t * p2[2]) + (3*(1-t) * (t ** 2) *p3[2]) + (t**3 * p4[2])])
	return points


# def test_bezier_top(
#     front_bottom = [[-0.5, 0.0, 0.0], [-0.5, 0.2, 0.0] , [0.5, 0.2, 0.0], [0.5, 0.2, 0.0]], 
#     front_top = [[-0.5, 0.0, 1.0], [-0.5, 0.2, 1.0] , [0.5, 0.2, 1.0], [0.5, 0.2, 1.0]], 
#     top = [0.2, 0.2],
#     thickness = 1):
	
#     # bottom_bezier_verts = bezier_curve([-1.0, 0.0, 0.0], [-1.0, front_bottom[0], 0.0], [1.0, front_bottom[1], 0.0], [1.0, 0.0, 0.0])
#     # top_bezier_verts = bezier_curve([-1.0, 0.0, 1.0], [-1.0, front[0], 1.0], [1.0, front[1], 1.0], [1.0, 0.0, 1.0])

#     bottom_bezier_verts = bezier_curve(front_bottom[0], front_bottom[1], front_bottom[2], front_bottom[3])
#     top_bezier_verts = bezier_curve(front_top[0], front_top[1], front_top[2], front_top[3])
#     verts = bottom_bezier_verts + top_bezier_verts

#     top_verts = []
#     for i in top_bezier_verts:
#         top_verts.append(bezier_curve([i[0], i[1], i[2]], [i[0], i[1], i[2] + top[0]], [i[0], -1.0, i[2] + top[1]], [i[0], -1.0, i[2]]))
	
#     start_points = []
#     end_points = []
#     for vert_list in top_verts:
#         start_points.append(len(verts))
#         verts += vert_list
#         end_points.append(len(verts)-1)

#     verts += [(front_bottom[0][0], -1 * thickness, front_bottom[0][-1]), (front_bottom[-1][0], -1 * thickness, front_bottom[-1][-1])]
	
#     bottom_face = [tuple(range((len(bottom_bezier_verts)-1))) + (len(verts) - 1, len(verts) - 2)]

#     side_face1 = tuple(range(end_points[0], start_points[0], -1)) + (0, len(verts)-2)
#     side_face2 = tuple(range(start_points[-1], end_points[-1],)) + (len(verts) - 1, len(bottom_bezier_verts)-1)
	
#     back_face = [(len(verts)-2, len(verts)-1, end_points[-1], end_points[0])]

#     top_faces = []
#     for i in range(len(top_verts)-1):
#         for j in range(len(top_verts[i])-1):
#             top_faces.append((j + start_points[i], j + 1 + start_points[i], j + 1 + start_points[i + 1], j + start_points[i + 1]))

#     # faces = [faces1, faces2, face_back]

#     #   side_faces = [tuple(range(0, len(verts),1))]
#     offset = len(bottom_bezier_verts)

#     front_faces = []
#     for i in range(len(bottom_bezier_verts) -1):
#         front_faces.append((i+1, i, offset+i, offset + 1+i))
	
#     faces = []
#     faces += front_faces
#     faces += top_faces
#     faces += bottom_face
#     faces += [side_face1]
#     faces += [side_face2]
#     faces += back_face
	
#     return  verts, faces

def join_parts(names, new_name):
	"""
	Combine multiple objects together
	Inputs: names: the names of the objects to be combined
			new_name: what to name the new object
	"""

	# for i in range(len(names) - 1):
	#     bpy.data.objects[names[i]].select_set(True)
	for name in names:
		bpy.data.objects[name].select_set(True)

	bpy.context.view_layer.objects.active = bpy.data.objects[names[-1]]
	bpy.ops.object.join()
	bpy.context.selected_objects[0].name = new_name

if __name__ == '__main__':

	# verts, faces = test_bezier()


	# verts, faces = test_bezier_top(
	# 	front_bottom = [[-0.5, 0.0, 0.0], [-0.5, 0.20, 0.0] , [0.5, 0.20, 0.0], [0.5, 0.0, 0.0]], 
	# 	front_top = [[-0.5, 0.0, 1.0], [-0.5, 0.20, 1.0] , [0.5, 0.20, 1.0], [0.5, 0.0, 1.0]], 
	# 	top = [2, 1],
	# 	thickness= 1)

	test = FingerSegmentGenerator()
	verts, faces = test.finger_segment_generator()
	verts, faces = test.distal_segment_generator(
	    front_bottom=[[-0.5, 0.0, 0.0], [-0.5, 0.20, 0.0] , [0.5, 0.20, 0.0], [0.5, 0.0, 0.0]], 
	    front_top = [[-0.5, 0.0, 1.0], [-0.5, 0.20, 1.0] , [0.5, 0.20, 1.0], [0.5, 0.0, 1.0]], 
	    top = [[0, 0, .4], [0, 0, .4]],
	    thickness= 1)

	# test = PalmGenerator()
	# verts, faces = test.square_palm([0,0,2.5], [1,1,2])  # not sure if I want the orgin to be on the top or bottom of the palm leaning towards the top

	# # verts,faces = test.cylinder_palm([0,0,0], [3,2,2])

	# # test_joint = JointGenerator()
	# # verts, faces = test_joint.pin_joint_top([0,0,0], {'width': 1, 'depth': 1})

	# #   verts, faces = triangle()
	edges = []
	mesh_name = "segment"
	mesh_data = data.meshes.new(mesh_name)
	mesh_data.from_pydata(verts,edges,faces)
	bm = bmesh.new()
	bm.from_mesh(mesh_data)
	bm.to_mesh(mesh_data)
	bm.free()
	mesh_obj = data.objects.new(mesh_data.name, mesh_data)
	context.collection.objects.link(mesh_obj)

	# test_joint = JointGenerator()
	# verts, faces = test_joint.pin_joint_top([0,0,2.5], [1, 1, 0.5], orientation=10.0)

	# edges = []
	# mesh_name = "top"
	# mesh_data = data.meshes.new(mesh_name)
	# mesh_data.from_pydata(verts,edges,faces)
	# bm = bmesh.new()
	# bm.from_mesh(mesh_data)
	# bm.to_mesh(mesh_data)
	# bm.free()
	# mesh_obj = data.objects.new(mesh_data.name, mesh_data)
	# context.collection.objects.link(mesh_obj)

	# test_joint = JointGenerator()
	# verts, faces = test_joint.pin_joint_bottom([0,0,0], [0.4, .9, 0.5])

	# edges = []
	# mesh_name = "bottom"
	# mesh_data = data.meshes.new(mesh_name)
	# mesh_data.from_pydata(verts,edges,faces)
	# bm = bmesh.new()
	# bm.from_mesh(mesh_data)
	# bm.to_mesh(mesh_data)
	# bm.free()
	# mesh_obj = data.objects.new(mesh_data.name, mesh_data)
	# context.collection.objects.link(mesh_obj)

	# join_parts(["segment", "top", "bottom"], "finger")
	# bpy.types.Mesh.calc_loop_triangles()

	# translate_part(mesh_name, (0,2,0))
	export_part('testing')
