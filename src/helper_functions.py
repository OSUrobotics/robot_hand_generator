"""Script containing custom functions to simplify blenders API."""

# Author: Josh Campbell, campbjos@oregonstate.edu
# Date: 3-14-2022

import bpy
from bpy import data, context
import bpy
import mathutils
from mathutils import Vector
import bmesh
import os
import json
import numpy as np
from pathlib import Path


def blender_make_mesh(verts, faces, mesh_name):
	"""Create the meshs using blenders tools.

	Args:
		verts (list): list of tuples, each tuple represents a vertex(x,y,z). 
		faces (list): list of tuples, each tuple represents a face and contains the index of the vertices used for a face. Follows right hand rule to get face normal.
		mesh_name (str): The name of the new mesh, make sure it is unique else blender will add .001 to the end if the name already exists.
	"""
	edges = [] # Only need edges or faces, we are using faces
	mesh_data = data.meshes.new(mesh_name)
	mesh_data.from_pydata(verts,edges,faces)
	bm = bmesh.new()
	bm.from_mesh(mesh_data)
	bm.to_mesh(mesh_data)
	bm.free()
	mesh_obj = data.objects.new(mesh_data.name, mesh_data)
	context.collection.objects.link(mesh_obj)

def directory_maker(location):
	"""Create a new directory.

	Args:
		location (str): path to new directory that needs to be made.
	"""
	if not os.path.isdir(location):
		Path(location).mkdir(parents=True, exist_ok=True)

def delete_all():
	"""Delete all objects in the blender enviroment."""
	bpy.ops.object.select_all(action='SELECT')  #deletes everything
	bpy.ops.object.delete(use_global=False)

def bezier_curve(p0, p1, p2, p3, resolution=0.01):
	"""Generate a bezier curve geiven the four points.

	Args:
		p0 (list): [x,y,z] of the first point
		p1 (list): [x,y,z] of the second point
		p2 (list): [x,y,z] of the third point
		p3 (list): [x,y,z] of the fourth point
		resolution (float, 0.01): The step size for "time" in the bezier curve, default is 0.01

	Returns:
		list: list of vectors which each point is a point on the bezier curve.
	"""
	points = []
	for t in np.arange(0.0, 1 + resolution, resolution):
		use_t = np.round(t,5)
		points.append(Vector([
		round((((1 - use_t) ** 3) * p0[0]) + (3*((1-use_t)**2) * use_t * p1[0]) + (3*(1-use_t) * (use_t ** 2) *p2[0]) + (use_t**3 * p3[0]),5),
		round((((1 - use_t) ** 3) * p0[1]) + (3*((1-use_t)**2) * use_t * p1[1]) + (3*(1-use_t) * (use_t ** 2) *p2[1]) + (use_t**3 * p3[1]),5),
		round((((1 - use_t) ** 3) * p0[2]) + (3*((1-use_t)**2) * use_t * p1[2]) + (3*(1-use_t) * (use_t ** 2) *p2[2]) + (use_t**3 * p3[2]),5)]))
	return points


def scale_part(name, scale):
	"""Scale a given object, (not used or tested in new format).
	
	Args: 
		name (str): object name
		scale (list): x,y,z values to scale object
	"""
	bpy.context.view_layer.objects.active = bpy.data.objects[name] 
	bpy.context.object.scale = scale

def join_parts(names, new_name):
	"""Combine multiple objects together.

	Args: 
		names (lsit): list of str, the names of the objects to be combined, the last object will be the cordniate frame the new mesh will have.
		new_name (str): Name of the new object.
	"""
	for i in range(len(names) - 1):
		bpy.data.objects[names[i]].select_set(True)
	
	bpy.context.view_layer.objects.active = bpy.data.objects[names[-1]]
	bpy.ops.object.join()
	bpy.context.selected_objects[0].name = new_name

def change_name(old_name, new_name):
	"""Change the name of an object.

	Args: 
		old_name (str): Current name of object you want to change
		new_name (str): New name you want the object to have
	"""
	bpy.context.view_layer.objects.active = bpy.data.objects[old_name]
	bpy.context.selected_objects[0].name = new_name

def export_part(name, export_directory):
	"""Export the object as an obj file.

	Arg: 
		name (str): The absolute path including the name of file object you wish to export.
	"""
	name += '.obj'
	target_file = os.path.join(export_directory, name)
	bpy.ops.export_scene.obj(filepath=target_file, use_triangles=True, path_mode='COPY', axis_forward="X", axis_up='Y')

def import_part(file_name, file_location, position=None, rotation=None):
	"""Import part from a seperate bledner file, (not used or tested in new format).

	Args:
		file_name (str): Blender file name
		file_location (str): path to the blender file
		position (list, optional): [x,y,z] of the objects location once it is imported. Defaults to None.
		rotation (list, optional): [r,p,y] of the objects oreintation once it is imported. Defaults to None.
	"""	
	part_name = file_name
	file_name += '.obj'
	# file_name += '.stl'
	target_file = os.path.join(file_location, file_name)
	bpy.ops.import_scene.obj(filepath=target_file)
	
	num_parts = len((bpy.context.selected_objects))
	if num_parts > 1:
		parts_list = []
		for i in range(num_parts):
			parts_list.append(bpy.context.selected_objects[i].name)
		join_parts(parts_list, part_name)
	else:
		change_name(bpy.context.selected_objects[-1].name, part_name)

	if position != None:
		translate_part(part_name, position)
	if rotation != None:
		rotate_part(part_name, rotation)

def rotate_part(part_name, rpy):
	"""Rotate a given part, (not used or tested in new format).

	Args:
		part_name (str): name of the object
		rpy (list): [r,p,y] amount to rotate the object by.
	"""
	bpy.context.view_layer.objects.active = bpy.data.objects[part_name]
	bpy.context.object.rotation_euler = rpy

def translate_part(part_name, xyz):
	"""Translate a given part, (not used or tested in new format).

	Args:
		part_name (str): name of the part to be translated.
		xyz (list): [x,y,z] amount to translate the object by.
	"""
	bpy.context.view_layer.objects.active = bpy.data.objects[part_name]
	bpy.context.object.location = xyz
