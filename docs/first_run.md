Module first_run
================
Script for setting up the file structure and placing the examples.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022

Classes
-------

`Setup(input_val, blender_loc=' ')`
:   Setup class.
    
    Initialize the setup class.
    
    Args:
            input_val (int): 0 -> stand alone file structure, 1 -> mojograsp file structure.
            blender_loc (str, optional): Allows for the path to blender be passed as an argument, if not the script will ask. Defaults to ' '.

    ### Methods

    `directory_maker(self, location)`
    :   Create a new directory.
        
        Args:
                location (str): absolute path to the directory that you want created

    `mojo_grasp_file_strucuture(self)`
    :   Create the file structure specific to mojo-grasp.

    `setup_examples(self, dict)`
    :   Move the example jsons to the hand_json_queue to be built when main.py is ran.
        
        Args:
                dict (dictionary): A dictionary containing needed directories

    `stand_alone_file_structure(self)`
    :   Create the file structure for stand alone install.