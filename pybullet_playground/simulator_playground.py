"""Script for testing the generated robot manipulators in a simply pybullet enviroment."""

# Author: Josh Campbell, campbjos@oregonstate.edu
# Date: 3-14-2022

#!/usr/bin/python3

import pybullet as p
import time
import pybullet_data
import os
import json
import glob

class sim_tester():
    """Simulator class to test different hands in."""

    def __init__(self, gripper_name, gripper_loc):
        """Initialize the sim_tester class.

        Args:
            gripper_name (str): The name of the gripper to be pulled into the simulator enviroment
            gripper_loc (str): The location of the top hand directory in the output directory
        """
        self.gripper_name = gripper_name
        self.gripper_loc = gripper_loc
        
        self.directory = os.path.dirname(__file__)


    def main(self):
        """Run the simulator."""           
        physicsClient = p.connect(p.GUI)  # or p.DIRECT for non-graphical version
        p.setAdditionalSearchPath(pybullet_data.getDataPath())  # optionally
        p.setGravity(0, 0, -10)
        LinkId = []
        cubeStartPos = [0, 0, 1]
        cubeStartOrientation = p.getQuaternionFromEuler([0, 0, 0])

        boxId = p.loadURDF(f"{self.gripper_loc}hand/{self.gripper_name}.urdf", useFixedBase=1)

        gripper = boxId

        p.resetDebugVisualizerCamera(cameraDistance=.2, cameraYaw=180, cameraPitch=-91, cameraTargetPosition=[0, 0.1, 0.1])

        for i in range(0, p.getNumJoints(gripper)):
            
            p.setJointMotorControl2(gripper, i, p.POSITION_CONTROL, targetPosition=0, force=0)
            linkName = p.getJointInfo(gripper, i)[12].decode("ascii")
            if "sensor" in linkName:
                LinkId.append("skip")
            else:
                LinkId.append(p.addUserDebugParameter(linkName, -3.14, 3.14, 0))



        while p.isConnected():

            p.stepSimulation()
            time.sleep(1. / 240.)

            for i in range(0, len(LinkId)):
                if LinkId[i] != "skip":
                    linkPos = p.readUserDebugParameter(LinkId[i])
                    p.setJointMotorControl2(gripper, i, p.POSITION_CONTROL, targetPosition=linkPos)


        p.disconnect()
    
def read_json(file_loc):
    """Read contents of a given json file.

    Args:
        file_loc (str): Full path to the json file including the file name.

    Returns:
        dictionary: dictionary that contains the content from the json.
    """
    with open(file_loc, "r") as read_file:
        file_contents = json.load(read_file)
    return file_contents


if __name__ == '__main__':

    directory = os.getcwd()

    file_content = read_json("/root/robot_hand_generator/src/.user_info.json")
    folders = []
    hand_names = []
    for folder in glob.glob(f'{file_content["hand_model_output"]}*/'):
        folders.append(folder)


    for i, hand in enumerate(folders):
        temp_hand = hand.split('/')
        hand_names.append(temp_hand[-2])
        print(f'{i}:   {temp_hand[-2]}')

    input_num = input("Enter the number of the hand you want loaded:   ")
    num = int(input_num)

    hand_name = hand_names[num]
    hand_loc = folders[num]

    sim_test = sim_tester(hand_name, hand_loc)
    sim_test.main()
