Module helper_functions
=======================
Script containing custom functions to simplify blenders API.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022

Functions
---------

    
`bezier_curve(p0, p1, p2, p3, resolution=0.01)`
:   Generate a bezier curve geiven the four points.
    
    Args:
            p0 (list): [x,y,z] of the first point
            p1 (list): [x,y,z] of the second point
            p2 (list): [x,y,z] of the third point
            p3 (list): [x,y,z] of the fourth point
            resolution (float, 0.01): The step size for "time" in the bezier curve, default is 0.01
    
    Returns:
            list: list of vectors which each point is a point on the bezier curve.

    
`blender_make_mesh(verts, faces, mesh_name)`
:   Create the meshs using blenders tools.
    
    Args:
            verts (list): list of tuples, each tuple represents a vertex(x,y,z). 
            faces (list): list of tuples, each tuple represents a face and contains the index of the vertices used for a face. Follows right hand rule to get face normal.
            mesh_name (str): The name of the new mesh, make sure it is unique else blender will add .001 to the end if the name already exists.

    
`change_name(old_name, new_name)`
:   Change the name of an object.
    
    Args: 
            old_name (str): Current name of object you want to change
            new_name (str): New name you want the object to have

    
`delete_all()`
:   Delete all objects in the blender enviroment.

    
`directory_maker(location)`
:   Create a new directory.
    
    Args:
            location (str): path to new directory that needs to be made.

    
`export_part(name, export_directory)`
:   Export the object as an obj file.
    
    Arg: 
            name (str): The absolute path including the name of file object you wish to export.

    
`import_part(file_name, file_location, position=None, rotation=None)`
:   Import part from a seperate bledner file, (not used or tested in new format).
    
    Args:
            file_name (str): Blender file name
            file_location (str): path to the blender file
            position (list, optional): [x,y,z] of the objects location once it is imported. Defaults to None.
            rotation (list, optional): [r,p,y] of the objects oreintation once it is imported. Defaults to None.

    
`join_parts(names, new_name)`
:   Combine multiple objects together.
    
    Args: 
            names (lsit): list of str, the names of the objects to be combined, the last object will be the cordniate frame the new mesh will have.
            new_name (str): Name of the new object.

    
`rotate_part(part_name, rpy)`
:   Rotate a given part, (not used or tested in new format).
    
    Args:
            part_name (str): name of the object
            rpy (list): [r,p,y] amount to rotate the object by.

    
`scale_part(name, scale)`
:   Scale a given object, (not used or tested in new format).
    
    Args: 
            name (str): object name
            scale (list): x,y,z values to scale object

    
`translate_part(part_name, xyz)`
:   Translate a given part, (not used or tested in new format).
    
    Args:
            part_name (str): name of the part to be translated.
            xyz (list): [x,y,z] amount to translate the object by.