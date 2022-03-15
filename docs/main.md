Module main
===========
Main script to be ran by user, this will grab jsons from the queue and run an instance of generator.py passing the json in.

Author: Josh Campbell, campbjos@oregonstate.edu
Date: 3-14-2022

Classes
-------

`MainScript()`
:   MainScipt class that takes all the jsons in the queue and passes them on to generator.py.
    
    Initialize the MainScript class.

    ### Methods

    `get_files_from_queue(self)`
    :   Get the json files in the queue and then call run_blender().

    `move_json(self, file_loc)`
    :   Move the json file to the archive directory and output folder with it's respective manipulator.
        
        Args:
            file_loc (str): The full path to the json file in the queue directory

    `read_json(self, user_info_loc='./.user_info.json')`
    :   Read in the content of a give json file.
        
        Args:
            user_info_loc (str, optional): path to the desired json file to read in. Defaults to "./.user_info.json".
        
        Returns:
            dictionary : A dictionary containing the contents of the json file.

    `run_blender(self, json_name)`
    :   Run an instance of generator.py using blender's python for a given json file.
        
        Args:
            json_name (str): cantains the absolute path to the json file.