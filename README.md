# robot_manipulator_generator
A tool to help in the creation of simplified robot manipulators to be used in simulation. Primarily for use with mojo grasp.


## Requirements:

- If using docker
    - Need to use wslg on windows 11 or a linux system
    - If you want to vizualize the models, have your system setup so the docker container can display guis
    - All other requirements are taken care of by the docker image.
- Blender 2.93 (only version tested on possibly will work on newer versions)
- linux os (tested on ubuntu)
- PyBullet for simple visaulization and joint checking
- Python 3.6+


## Install and Setup:
If you want to use this with mojo-grasp follow the instructions on that repo(will be added once this is integrate with it).

For using this package stand alone there are two options:

1. Use docker and either the provided docker image or dockerfile (Recommended)
2. Install blender on your system and then install this package.
    - Also install pybullet if you want viualize the full manipulator.
    - Instructions not currently available.


### Option 1: Docker

1. 

