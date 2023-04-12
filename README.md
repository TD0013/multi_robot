# multi_robot

This repo contains the a framework for multi-robot simulation on ubuntu using ROS noetic and gazebo.

## Table of Contents
  * [Installation](#installation)
  * [How to use](#how-to-use)


## Installation 
Pre-requisites: [ROS Noetic](http://wiki.ros.org/noetic), [Teb Local Planner](http://wiki.ros.org/teb_local_planner), [Turtlebot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/) and [Aws Hospital](https://github.com/aws-robotics/aws-robomaker-hospital-world).

After you are done with installing the pre-reqs, move to the src directory of your workspace and clone this repo and run catkin_make. Else, if you dont have a workspace, run 
```
mkdir catkin_ws/src
cd catkin_ws/src
git clone https://github.com/TD0013/multi_robot.git
cd ..
catkin_make
```
This sould successfully build the repo on your local device.

## How To Use
The main piece of code that runs everything is the "driver.py" file in the "src" folder [driver.py]
