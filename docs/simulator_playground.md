Module simulator_playground
===========================
Script for testing the generated robot manipulators in a simply pybullet enviroment.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022

Functions
---------

    
`read_json(file_loc)`
:   Read contents of a given json file.
    
    Args:
        file_loc (str): Full path to the json file including the file name.
    
    Returns:
        dictionary: dictionary that contains the content from the json.

Classes
-------

`sim_tester(gripper_name, gripper_loc)`
:   Simulator class to test different hands in.
    
    Initialize the sim_tester class.
    
    Args:
        gripper_name (str): The name of the gripper to be pulled into the simulator enviroment
        gripper_loc (str): The location of the top hand directory in the output directory

    ### Methods

    `main(self)`
    :   Run the simulator.