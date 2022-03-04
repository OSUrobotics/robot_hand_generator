from bpy import data, context
import bpy
import mathutils
import bmesh
import numpy as np
import os
import sys
import json
from math import sin, cos, tan, pi
# sys.path.append(bpy.path.abspath("//")+'/root/robot_manipulator_generator/src') # this lets me call other scripts that I made

# from helper_functions import HelperFunctions
# from urdf_creator import UrdfGenerator

# func = bpy.data.texts["helper_functions.py"].as_module()


class MainGenerator():
    def __init__(self, directory_dict, project_dict):
        self.directory_dict = directory_dict
        self.project_dict = project_dict
        
        HF.delete_all()

        HnadGenerator(hand_dict=self.project_dict['hand'])


class HnadGenerator():
    def __init__(self, hand_dict):
        self.hand_dict = hand_dict
    
    def main(self):
        palm = PalmGenerator(self.hand_dict["palm"], run_trigger=True)

        finger_list = []

        for finger_number in range(self.hand_dict["palm"]["finger_qty"]):
            finger_list.append(FingerGenerator(self.hand_dict[f'finger_{finger_number}'], run_trigger=True))
            
        
        

class PalmGenerator():
    def __init__(self, palm_dict, run_trigger=False):
        self.palm_dict = palm_dict
        if run_trigger == True:
            self.main()
            
    def main(self):
        if self.palm_dict["palm_style"] == "cylinder":
            verts, faces = self.cylinder_palm()
        elif self.palm_dict["palm_style"] == "cuboid":
            verts, faces = self.cuboid_palm()
        HF.blender_make_mesh(verts=verts, faces=faces, mesh_name="palm")
        
        joint_list = []
        for joint_number in range(self.palm_dict["finger_qty"]):
            distance, angle, _ = self.palm_dict[f'finger_{joint_number}']["joint_pose"]
            bottom_center_xyz = [distance * cos(angle*pi/180), distance * sin(angle*pi/180), 0]
            joint_list.append(JointGenerator(self.palm_dict[f'finger_{joint_number}'], bottom_center_xyz=bottom_center_xyz, joint_bottom=True, run_trigger=True))
        
    
    def cuboid_palm(self, center_location=[0,0,0]):
        dimensions = self.palm_dict["palm_dimensions"]
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

    def cylinder_palm(self, center_location=[0,0,0]):
        dimensions = self.palm_dict["palm_dimensions"]
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


class JointGenerator():
    def __init__(self, joint_dict, bottom_center_xyz, joint_bottom=True, run_trigger=False): # joint_bottom is bottom of the joint not the bottom of the segment
        self.joint_dict = joint_dict
        self.bottom_center_xyz = bottom_center_xyz

        if joint_bottom == True and run_trigger ==True:
            self.main_bottom()
        elif joint_bottom == False and run_trigger == True:
            self.main_top()
    
    def main(self):
        pass

    def main_bottom(self):
        if self.joint_dict.has_key("joint_pose"):
            orientation = self.joint_dict["joint_pose"][-1]
        else:
            orientation = 0
        
        if self.joint_dict["style"] == "pin":
            self.pin_joint_bottom(orientation=orientation)  
            

    def main_top(self):
        pass
        
    def pin_joint_bottom(self, orientation=0):
        width, depth, length = self.joint_dict["joint_dimensions"]
        


    def pin_joint_top(self, bottom_center_xyz=[0,0,0]):
        pass


class FingerGenerator():
    def __init__(self, finger_dict, run_trigger=False):
        self.finger_dict = finger_dict


class FingerSegmentGenerator():
    def __init__(self, segment_dict, functions):
        self.segment_dict = segment_dict
        self.functions = functions
    
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