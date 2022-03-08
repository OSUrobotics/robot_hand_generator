import bpy
import os
from bpy import data, context
import bpy
import mathutils
from mathutils import Vector
import bmesh
import json
import numpy as np
from pathlib import Path

# class HelperFunctions():
#     """
#     Useful functions for creating multiple models in blender
#     """

    # def __init__(self, current_directory='', export_directory=''):
    #     pass
        # self.directory = current_directory
        # self.export_directory = export_directory
        # self.sim_dir = ''
        # self.obj_dir = ''

def blender_make_mesh(verts, faces, mesh_name):
    edges = []
    mesh_data = data.meshes.new(mesh_name)
    mesh_data.from_pydata(verts,edges,faces)
    bm = bmesh.new()
    bm.from_mesh(mesh_data)
    bm.to_mesh(mesh_data)
    bm.free()
    mesh_obj = data.objects.new(mesh_data.name, mesh_data)
    context.collection.objects.link(mesh_obj)

def directory_maker(location):
        if not os.path.isdir(location):
            Path(location).mkdir(parents=True, exist_ok=True)

def delete_all():
    """
    Deletes all objects in the blender enviroment
    """
    bpy.ops.object.select_all(action='SELECT')  #deletes everything
    bpy.ops.object.delete(use_global=False)

def bezier_curve(p0, p1, p2, p3):
	points = []
	for t in np.arange(0.0, 1.01, 0.01):
		points.append(Vector([
		(((1 - t) ** 3) * p0[0]) + (3*((1-t)**2) * t * p1[0]) + (3*(1-t) * (t ** 2) *p2[0]) + (t**3 * p3[0]),
		(((1 - t) ** 3) * p0[1]) + (3*((1-t)**2) * t * p1[1]) + (3*(1-t) * (t ** 2) *p2[1]) + (t**3 * p3[1]),
		(((1 - t) ** 3) * p0[2]) + (3*((1-t)**2) * t * p1[2]) + (3*(1-t) * (t ** 2) *p2[2]) + (t**3 * p3[2])]))
	return points


def scale_part(name, scale):
    """
    Scales a given object
    Inputs: name: object name
            scale: x,y,z values to scale object
    """
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
    bpy.context.object.scale = scale

def join_parts(names, new_name):
    """
    Combine multiple objects together
    Inputs: names: the names of the objects to be combined
            new_name: what to name the new object
    """

    for i in range(len(names) - 1):
        bpy.data.objects[names[i]].select_set(True)
    
    bpy.context.view_layer.objects.active = bpy.data.objects[names[-1]]
    bpy.ops.object.join()
    bpy.context.selected_objects[0].name = new_name

def change_name(old_name, new_name):
    """
    change the name of an object
    Inputs: old_name: name of object you want to change
            new_name: name you want the object to have
    """
    bpy.context.view_layer.objects.active = bpy.data.objects[old_name]
    bpy.context.selected_objects[0].name = new_name

def export_part(name, export_directory):
    """
    export the object as an obj file
    Input: name: name of object you wish to export
    """
    name += '.obj'
    target_file = os.path.join(export_directory, name)
    bpy.ops.export_scene.obj(filepath=target_file, use_triangles=True, path_mode='COPY')

def import_part(file_name, file_location, position=None, rotation=None):
    
    # if file_location == None:
    #     file_location = self.export_directory
    
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

    bpy.context.view_layer.objects.active = bpy.data.objects[part_name]
    bpy.context.object.rotation_euler = rpy

def translate_part(part_name, xyz):
    bpy.context.view_layer.objects.active = bpy.data.objects[part_name]
    bpy.context.object.location = xyz

def set_directories(sim='', obj=''):
    """
    Change directories
    Inputs: sim: simulator directory
            obj: object directory
    """

    sim_dir = sim
    obj_dir = obj