#!/usr/bin/env python3
import rospy
from multi_robot.msg import TD_task
from random import randint, choice
import yaml
import numpy as np

MIN_VEL = 0.5


with open("/home/td0013/catkin_ws/src/multi_robot/param/distance_params.yaml", 'r') as file1:
    points= yaml.safe_load(file1)
    points = points["world_nodes"]

dist= np.loadtxt('/home/td0013/catkin_ws/src/multi_robot/param/dist.txt', usecols=range(22))
dist = np.round(dist, decimals=3)

places = {}
z=0
for i in points:
    places[i] = z
    z+=1

if __name__ == '__main__':
    
    rospy.init_node('taskGen')                     # init ROS node
    count = rospy.get_param('/td/task_count')

    #Init publisher
    taskPub = rospy.Publisher('/task', TD_task, queue_size=1)

    step = 0

    rospy.sleep(1)

    while not rospy.is_shutdown() and step<count:
            task = TD_task()
            task.taskID= step
            task.arrivalTime = int(rospy.Time.now().to_sec())
            task.demand = randint(20, 100)
            task.destination = choice(list(points.keys()))
            
            task.pickup = choice(list(points.keys()))

            while task.pickup in ["dock_1", "dock_2", "dock_3"]:
                task.pickup = choice(list(points.keys()))

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
