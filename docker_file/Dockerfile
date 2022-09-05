FROM osrf/ros:melodic-desktop-full

RUN apt update
RUN apt install -y nano
RUN apt install -y usbutils
RUN apt install -y libxtst6
RUN apt install -y python-pip
RUN apt install -y wget
RUN /bin/bash -c 'mkdir ~/software; \
    cd ~/software; \
    wget https://oregonstate.box.com/shared/static/895kxxvztksqcbjmlzyq7jg1flslseru.xz; \
    tar xf 895kxxvztksqcbjmlzyq7jg1flslseru.xz;\
    mv blender-2.93.7-linux-x64 ./blender-2.93; \
    echo "alias blender="~/software/blender-2.93/blender"" >> ~/.bashrc; \
    source ~/.bashrc; \
    sudo apt update; sudo apt install -y python3-pip;\
    cd ~/ ; git clone https://github.com/OSUrobotics/robot_hand_generator.git;\
    cd ~/robot_hand_generator/; pip3 install -r requirements.txt;\
    pip3 install pybullet;\
    cd ~/software/; git clone https://github.com/bulletphysics/bullet3.git; cd ./bullet3/; python3 setup.py build; python3 setup.py install;\
    /root/software/blender-2.93/2.93/python/bin/python3.9 -m ensurepip;\
    /root/software/blender-2.93/2.93/python/bin/python3.9 -m pip install upgrade pip;\
    /root/software/blender-2.93/2.93/python/bin/python3.9 -m pip install numpy;\
    /root/software/blender-2.93/2.93/python/bin/python3.9 -m pip install pathlib;\
    cd /root/robot_hand_generator/; python3 first_run.py 0 /root/software/blender-2.93/blender;\
    '
    
# CMD ["python3" "/root/robot_manipulator_generator/first_dun.py 0 /root/software/blender-2.93/blender"]
