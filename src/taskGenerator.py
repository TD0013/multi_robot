#!/usr/bin/env python3
import rospy
from multi_robot.msg import TD_task
from random import randint, choice
import yaml
import rospkg
import numpy as np

MIN_VEL = 0.5
TASKS_TO_GENERATE = 5

rospy.init_node('taskGen')                     # init ROS node

# Get Path for multi_robot Pkg and declare global variabel PARAMS    
rospack = rospkg.RosPack()
PATH = rospack.get_path('multi_robot')

with open(PATH+"/param/distance_params.yaml", 'r') as file1:
    points= yaml.safe_load(file1)
    points = points["world_nodes"]

dist= np.loadtxt(PATH+'/param/dist.txt', usecols=range(22))
dist = np.round(dist, decimals=3)

places = {}
z=0
for i in points:
    places[i] = z
    z+=1

if __name__ == '__main__':
    #Init publisher
    taskPub = rospy.Publisher('/task', TD_task, queue_size=1)

    step = 0

    rospy.sleep(1)

    while not rospy.is_shutdown() and step<TASKS_TO_GENERATE:
            task = TD_task()
            task.taskID= step
            task.arrivalTime = int(rospy.Time.now().to_sec())
            task.demand = randint(20, 100)
            
            task.pickup = choice(list(points.keys()))

            while task.pickup in ["dock_1", "dock_2", "dock_3"]:
                task.pickup = choice(list(points.keys()))

            task.destination = choice(list(points.keys()))
            while task.destination in ["dock_1", "dock_2", "dock_3", task.pickup]:
                task.destination = choice(list(points.keys()))
            task.startTime = task.arrivalTime+randint(0,10)
            task.finishTime = task.arrivalTime+int(dist[places[task.pickup]][places[task.destination]]/MIN_VEL)+randint(450,1000)
            task.timeconstraint = randint(0,1)
            task.type = randint(0,3)
            print(task)
            taskPub.publish(task)
            step+=1

            rospy.sleep(randint(1, 5))
