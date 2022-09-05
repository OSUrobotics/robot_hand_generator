[![DOI](https://zenodo.org/badge/449414021.svg)](https://zenodo.org/badge/latestdoi/449414021)
# robot_hand_generator
A tool to help in the creation of simplified robot hands to be used in simulation. Primarily for use with mojo grasp.


## Requirements:

- If using docker(currently only officially support manner)
    - Need to use wslg on windows 11 or a linux system
    - If you want to vizualize the models, have your system setup so the docker container can display guis
    - All other requirements are taken care of by the docker image.
- Blender 2.93 (only version tested on possibly will work on newer versions)
- linux os (tested on ubuntu)
- PyBullet for simple visaulization and joint checking
- Python 3.6+


## Install and Setup(Docker on Linux host machine):
Docker with linux is the only supported manner wslg should be doable but requires you to download the repo to build the Dockerfile, as well as setup slightly differently.(Instructions will come later)

0. Here is some basic information to get going with docker: https://github.com/OSUrobotics/infrastructure-packages/blob/new_file_structure/docker_setup.md

1. Once docker is setup along with enabling visualization run the following commands:
    (If you added user to docker group you don't need sudo infront of the docker commands)

    ```console
    sudo docker build -t robot_hand_generator https://github.com/OSUrobotics/robot_hand_generator.git#main:docker_file
    ```
    ```console
    DOCKER_COMMON_ARGS="--gpus all --env=NVIDIA_VISIBLE_DEVICES=all --env=NVIDIA_DRIVER_CAPABILITIES=all --env=DISPLAY --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw"
    ```
    ```console
    sudo docker run -it -d --net=host --privileged $DOCKER_COMMON_ARGS --name hand_generator robot_hand_generator 
    ```

    * This will create a docker image called robot_hand_generator and a container based off that image called hand_generator.
    
    * If you get errors related to device drivers not being selected run this instead: 
     (Everything will still function, except for you wont be able to use the PyBullet simulation enviroment to check the hand)
    ```console
    sudo docker run -it -d --net=host --privileged --name hand_genertor robot_hand_generator
    ```
    
2. To start the container run the following:
    ```console
    sudo docker start hand_generator
    ```

3. Attach to the docker container by running:
    ```console
    sudo docker exec -it hand_generator bash
    ```
    Now you are in the container and the manipulator is already setup ready for you to use it.

4. Navigate to the root directory of the repo and do a git pull to ensure the files are up to date:
    ```console
    cd ~/robot_hand_generator/
    ```
    ```console
    git pull
    ```


## How to Use:
Documentation on the different scripts is provided in the /docs directory.
Assuming that you have started and are in the docker container the follow is the typical actions you'll want to do:

1. Navigate to the src directory in robot_manipulator_generator:
    ```console
    cd ~/robot_hand_generator/src/
    ```

2. Run main.py, which will generate a hand for all json files in the hand_json_queue directory:
    * On a fresh docker container there will be an example hand's json in the queue ready to go.
    ```console
    python3 main.py
    ```
    The output files will be located in folder named after the hand name located in here:
    ```console
    cd ~/robot_hand_generator/output/
    ```

3. To visualize the hands generated navigate the pybullet_playground and run the simulator:
    * Assuming that you have gui support setup for the docker container.
    ```console
    cd ~/robot_hand_generator/pybullet_playground
    ```
    ```console
    python3 simulator_playground.py
    ```
    The simulator will list the available manipulators enter the number associated with the one you want to view.

4. If you want to create your own custom hand navigate to the hand_json_queue directory and add a new json in this directory(A tool to help json creation is in developement).
    ```console
    cd ~/robot_hand_generator/hand_json_files/hand_queue_json/
    ```
    The example hand_json can be used as a reference and is found here:
    ```console
    ~/robot_hand_generator/hand_json_files/example_hand_json/test_hand.json
    ```
    An additional script that will simplify the json creation is in the works.


## Testing:

1. Navigate to test_code.
    ```console
    cd ~/robot_hand_generator/test_code/
    ```
2. Run the test code.
    ```console
    blender -b --python test.py
    ```


## Todo:

- Fix the test code to work with the recent updates.
- Create instruction specific for wslg
- Create instructions for non-docker install
