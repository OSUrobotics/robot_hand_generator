Module urdf_creator
===================
Contains the helper class for generating custom urdf files.

Classes
-------

`UrdfGenerator(file_location)`
:   Helps user to create a URDF file

    ### Methods

    `end_file(self)`
    :   adds the ending info of a urdf file

    `joint(self, name, Type, child, parent, axis=(0, 0, 0), rpy_in=(0, 0, 0), xyz_in=(0.0, 0.0, 0.0))`
    :   adds a joint to the urdf file
        Inputs: name: joint name
                Type: revolute, or fix for now more can be added later
                child: name of child link
                parent: name of parent link
                axis: (x,y,z) axis of rotation
                rpy_in: (r,p,y) rotation of child link relative to parent
                xyz_in: (x,y,z) location of child's origin relative to parents origin

    `link(self, name='', pose=(0, 0, 0, 0, 0, 0), scale=(1, 1, 1), mass=0.5, model_name='')`
    :   adds a link to the urdf file
        Inputs: name: name of the link
                pose: (x,y,z,r,p,y) of the link relative to the origin of it's parent link, typically this is taken
                    care of by the joint not the link
                scale: (x,y,z) scale factor in each direction
                mass: not currently used
                model_name: use if model name is different then link name

    `listConverter(self, pose)`
    :   converts a list into a string to be used in the urdf file

    `new_urdf(self)`
    :   makes the urdf file blank for a new file to be created

    `start_file(self, gripper_name='default')`
    :   called for starting a urdf, adding the initial info for the urdf file
        Input: gripper_name: name of the gripper the file is associated with

    `write(self, filename='urdf_Test')`
    :   Once all components for the urdf file are complete write the file
        Inputs: filename: name of the urdf file