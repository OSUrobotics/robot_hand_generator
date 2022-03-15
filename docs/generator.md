Module generator
================
Script ran with blender's provided python to generate custom robot manipulators to be used in simulators.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022

Functions
---------

    
`read_json(json_loc)`
:   Read a given json file in as a dictionary.
    
    Args:
            json_loc (str): path to the json file to be read in
    
    Returns:
            (dictionary): A dictionary of the json that was read in

Classes
-------

`FingerGenerator(finger_dict, run_trigger=False)`
:   Generate fingers for the hand.
    
    Intialize the FingerGenerator Class.
    
    Args:
            finger_dict (Dictionary): A dictionary that describes the finger to be generated
            run_trigger (bool, optional): Trigger that determines if the generator will auto-run or be manually called. Defaults to False.

    ### Methods

    `main(self)`
    :   Call the segment generator to generate the segments for the finger.

`FingerSegmentGenerator(segment_dict, run_trigger=True)`
:   Generate the finger segment.
    
    Initialize the FingerSegmentGenerator class.
    
    Args:
            segment_dict (Dictionary): A dictionary that describes the segment that is going to be generated
            run_trigger (bool, optional) : Trigger for auto run or manual run. Defaults to True

    ### Methods

    `distal_segment(self, generate_joints=True)`
    :   Generate the distal segment. This one uses two bezier curves, one describes the segment face profile the other describes the segment top profile.
        
        Args:
                generate_joints (bool, optional): Determines if the joints are generated as well, for testing. Defaults to True.

    `general_segment(self, generate_joints=True)`
    :   Generate the generaric segment mostly the proximal and intermediate segments.
        
        Args:
                generate_joints (bool, optional): Determines if the joints are generated, for testing. Defaults to True.

`HandGenerator(hand_dict, directory_dict)`
:   This class controls the process for generating a hand.
    
    Initialize method for HandGenerator class.
    
    Args:
            hand_dict (dictionary): A dictionary that describes the hand to be generated
            directory_dict (dictioanry): A dictionary that contains the paths to useful directories

    ### Methods

    `create_meshes(self)`
    :   Create and export the meshes for the hand components.

    `generate_urdf(self)`
    :   Generate the urdf for the hand.

    `main(self)`
    :   Call the Generator classes for the palm and fingers.

`JointGenerator(joint_dict, bottom_center_xyz, joint_bottom=True, run_trigger=False)`
:   Generate different joints.
    
    Initialize the JointGenerator Class.
    
    Args:
            joint_dict (Dictionary): A dictionary that describes the desired joint
            bottom_center_xyz ([x_val, y_val, z_val]): [x,y,z] location of the center bottom face of the joint 
            joint_bottom (bool, optional): Sets if the joint is located on the bottom or top of the finger segment. Defaults to True.
            run_trigger (bool, optional): A trigger te say if it runs automatically or will be called manually. Defaults to False.

    ### Methods

    `main_bottom(self)`
    :   Determine and call the method for the style of the bottom joint.

    `main_top(self)`
    :   Determine and call the method for the style of the top joint.

    `pin_joint_bottom(self, orientation=0.0)`
    :   Generate the bottom portion of the joint, ie for a pin joint the half cylinder portion.
        
        Args:
                orientation (float, optional): The angle(degrees) to rotate the joint about it's z-axis only for joints on the palm. Defaults to 0.0.

    `pin_joint_top(self, orientation=0.0)`
    :   Generate the top portion of the pin joint, ie the cuboid stem.
        
        Args:
                orientation (float, optional): The angle(degrees) for rotating the joint anbout it's z-axis. Defaults to 0.0.

`MainGenerator(directory_dict, project_dict)`
:   Main Class that calls the HandGenerator class and ObjectGenerator class.
    
    Initialize method for the MainGenerator.
    
    Args:
            directory_dict (dictionary): A dictionary containing the location of needed directories 
            project_dict (dictionary): A dictionary that describes the desired hand and objects to be generated

`ObjectGenerator(object_dict)`
:   Generate the objects.
    
    Initialize the ObjectGenerator class.
    
    Args:
            object_dict (Dictionary): A dictionary that describes the desired objects to be generated.

`PalmGenerator(palm_dict, run_trigger=False)`
:   Generator for the Palm.
    
    Initialize the PalmGenerator.
    
    Args:
            palm_dict (Dictionary): A dictionary that describes the palm to be generated
            run_trigger (bool, optional): A trigger that determines if the main method is ran or if they will be mannually called. Defaults to False.

    ### Methods

    `cuboid_palm(self)`
    :   Generate a cuboid style palm.

    `cylinder_palm(self)`
    :   Generate a Cylinder style palm.

    `main(self)`
    :   Call the method to generate the style of palm, and the joints that go with it.