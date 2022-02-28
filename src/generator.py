from bpy import data, context
import bpy
import mathutils
import bmesh
import numpy as np
import os
import sys

# sys.path.append(bpy.path.abspath("//")+'/root/robot_manipulator_generator/src') # this lets me call other scripts that I made

# from helper_functions import HelperFunctions
# from urdf_creator import UrdfGenerator

# func = bpy.data.texts["helper_functions.py"].as_module()


class MainGenerator():
    def __init__(self):
        test2 = HelperFunctions()
        test2.delete_all()
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)



if __name__ == '__main__':
    # # functions = func.functions()
    # functions.delete_all()
    
    sys.path.append(bpy.path.abspath("//")+'/root/robot_manipulator_generator/src') # this lets me import the other scripts that I made

    from helper_functions import HelperFunctions
    from urdf_creator import UrdfGenerator
    
    # test = HelperFunctions()
    # test.delete_all()
    sys.argv[1:]

    MainGenerator()