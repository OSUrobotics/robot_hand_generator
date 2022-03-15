Module test
===========
Test script that ensures the generator methods can reproduce models that have been checked by other means.

Functions
---------

    
`read_json(json_loc)`
:   Read a given json file in as a dictionary.
    
    Args:
            json_loc (str): path to the json file to be read in
    
    Returns:
            (dictionary): A dictionary of the json that was read in

    
`write_json(json_loc, json_data)`
:   Write contant into the json file.
    
    Args:
            json_loc (str): file location of the json file to write
            json_data (dictionary): dictionary containing test results.

Classes
-------

`TestGenerator()`
:   Class for testing the generator.py mesh creation.
    
    Initialize the TestGeneratory Class.

    ### Methods

    `check_output(self)`
    :   Check if the new values match the old values.

    `joint_pin_bottom(self)`
    :   Test pin joint bottom.

    `joint_pin_top(self)`
    :   Test pin joint top.

    `main(self, udate_json=False)`
    :   Call the test methods.
        
        Args:
                udate_json (bool, optional): Trigger to save a new json key or not. Defaults to False.

    `palm_cuboid_test(self)`
    :   Test generation of the cuboid palm.

    `palm_cylinder_test(self)`
    :   Test generation of the cylinder palm.

    `segment_distal(self)`
    :   Test distal segment generation.

    `segment_general(self)`
    :   Test general segment generation.