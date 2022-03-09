from asyncio.constants import SENDFILE_FALLBACK_READBUFFER_SIZE
from tracemalloc import start
from bpy import data, context
import bpy
import mathutils
import bmesh
import numpy as np
import os
import sys


class ManipulatorGenerator:
    def __init__(self, json_file_location):

        self.functions = functions()
        save_loc_json = "./user_info.json"
        manipulator_parameters = self.json_reader(json_file_location=json_file_location)
        save_locations = self.json_reader(save_loc_json)
        self.main(manipulator_parameters=manipulator_parameters, save_locations=save_locations)


    def main(self, manipulator_parameters, save_locations):
        manipulator_description = {}
        palm = PalmGenerator(manipulator_parameters['palm'])
        manipulator_description['file_type'] = 'manipulator'
        
        for finger_number in range(manipulator_parameters['palm']['finger_number']):
            FingerGenerator(finger_segment_parameters=manipulator_parameters[f'finger_{finger_number}'], functions=self.functions)
        
        UrdfGenerator(manipulator_description, save_locations['manipulator_urdf'])
        
        for object_number in range(manipulator_parameters['objects']['object_number']):
            objects = ObjectGenerator(manipulator_parameters['objects'][f'object_{object_number}'])
            UrdfGenerator(objects.object_description, save_locations['object_urdf'])

    def json_writer(self):
        pass


    def json_reader(self, json_file_location):
        pass

class UrdfGenerator:
    def __init__(self, description_file, save_location):
        pass
    
    def manipulator_urdf(self):
        pass

    def object_urdf(self):
        pass


class PalmGenerator:
    def __init__(self, palm_parameters):
        if palm_parameters['palm_style'] == 'cylinder':
            verts, faces = self.cylinder_palm(dimensions=palm_parameters['palm_dimensions'])
        elif palm_parameters['palm_style'] == 'cube':
            verts, faces = self.square_palm(palm_parameters['palm_dimensions'])
        else:
            raise ValueError(f"The palm style <{palm_parameters['palm_style']}> does not exist")
        
        BlenderCreateMeshes(verts, faces, name='palm')


    def cylinder_palm(self, dimensions, center_location=[0,0,0]):
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
    
    def square_palm(self, dimensions, center_location=[0,0,0]):
        

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


class FingerGenerator:
    def __init__(self, finger_segment_parameters, functions, start_pose=[0,0,0]):
        
        self.functions = functions


class FingerSegmentGenerator:
    def __init__(self):
        pass


class JointGenerator:
    def __init__(self):
        pass

class ObjectGenerator:
    def __init__(self, object_parameters):
        self.object_description = {'file_type':'object'}
        self.object_description['file_name'] = object_parameters['name']

        if object_parameters['type'] == 'cylinder':
            verts, faces = self.cylinder_object(object_parameters['size'])
        elif object_parameters['type'] == 'cube':
            verts, faces = self.cube_object(object_parameters['size'])
        else:
            raise ValueError(f"The object type <{object_parameters['type']}> does not exist")

        BlenderCreateMeshes(verts, faces, name= object_parameters['name'])

    def cube_object(self, object_size):
        verts = []
        faces = []

        return verts, faces

    def cylinder_object(self, object_size):
        verts = []
        faces = []

        return verts, faces


class BlenderCreateMeshes:
    def __init__(self, verts, faces, name):
        pass


if __name__ == "__main__":
    
    json_file_location = sys.argv[1]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    ManipulatorGenerator(json_file_location)
