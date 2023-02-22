#!/usr/bin/env python3

import rospy
from multi_robot.msg import TD_task
import yaml
from random import randint, choice
import numpy as np

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

# print(choice(list(points.keys())))
# for i in dist:
#     print(i)
# print(dist[places["reception"]][places["reception"]])
print(np.matrix(dist).max())

# Robot Parameters
velocity = 0.1
capacity = 400
energy = 40000
mass = 10

startPos = choice(list(points.keys()))


def getNearestDock(pos):
    global dist
    asd = 10e9
    for i in ["dock_1", "dock_2", "dock_3"]:
        asd  = min(asd, dist[places[i]][places[pos]])
    
    return asd


def tempSTN(nodes, time, pos, taskI, energyRem, started, capacityRem, currList, currPen):
    global capacity
    global mass
    global velocity
    global retList
    global minPen
    global minTT
    if len(taskI)==0:
        # print(currList, currPen)
        if(currPen<minPen):
            minPen = currPen
            t = currList.copy()
            retList=t
            minTT = min(minTT, currList[-1][2])
        # retList.append(t)
        # print(retList)
        
    else:
        for i in taskI:
            # print(currList)
            if(i in started):   # Has the task been picked up
                timecpy = time+(dist[places[pos]][places[nodes[i].destination]])/velocity  #Current Time Update
                enRem = energyRem-(1/2*(mass+capacity-capacityRem)*velocity**2)*((dist[places[pos]][places[nodes[i].destination]])/velocity) #Current energy remaining update
                # print(enRem)
                pos = nodes[i].destination                                  #current Position
                # print(str(i)+"drop", timecpy)

                if(nodes[i].timeconstraint ==1):
                    tempPen = currPen+max(0, (timecpy-nodes[i].finishTime))   #penalty update for soft task
                else:                                                        #Hard task penalty update
                    if(timecpy-nodes[i].finishTime>0):
                        tempPen =currPen+10e6
                    else:
                        tempPen = currPen

                capacityRem = capacityRem+nodes[i].demand                   # New capacity

                cap = capacity-capacityRem
                tt = enRem/(1/2*(mass+cap)*velocity**2)                     # possible total travel time with new capacity

                if((timecpy+getNearestDock(pos)/velocity)>tt):              # Does robot run out of energy before reaching nearest dock
                    # print("energy over")
                    tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                else:
                    currList.append([str(i)+" End", pos, timecpy])                           
                    taskIcpy = taskI.copy()
                    taskIcpy.remove(i)            # remove curr task from task list as it has been delivered
                    tempSTN(nodes, timecpy, pos, taskIcpy, enRem, started, capacityRem, currList, tempPen)   #Recursion with current time, current pos, current energy rem
                    currList.pop()

            else:       # if task not picked up
                timecpy = time+(dist[places[pos]][places[nodes[i].pickup]])/velocity #Current Time Update
                enRem = energyRem-(1/2*(mass+capacity-capacityRem)*velocity**2)*((dist[places[pos]][places[nodes[i].pickup]])/velocity) #Current energy remaining update
                # print(enRem)
                pos = nodes[i].pickup   #current pos

                if(nodes[i].startTime>timecpy): # Basically wait for task to start
                    timecpy = nodes[i].startTime
            
                currList.append([str(i)+" start", pos, timecpy])
                startedCpy = started.copy()
                startedCpy.add(i)

                capacityRem = capacityRem-nodes[i].demand
                cap = capacity-capacityRem
                tt = enRem/(1/2*(mass+cap)*velocity**2)        # possible travel time with current capacity              

                if((timecpy+getNearestDock(pos)/velocity)>tt): # Does robot run out of energy before reaching nearest dock
                    print("energy over")
                    tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                else:
                    if(capacityRem<0):
                        tempSTN(nodes, time, pos, set(), enRem, started, capacity, currList, 10e9)
                    # print(str(i)+"start", time, nodes[i].startTime, timecpy)
                    else:
                        tempSTN(nodes, timecpy, pos, taskI, enRem, startedCpy, capacityRem, currList, currPen)
                currList.pop()


## Demo Tasks
taskQ = []

for i in range(2):
    task = TD_task()
    task.taskID= i
    task.arrivalTime = 0
    task.demand = randint(20, 100)
    task.destination = choice(list(points.keys()))
    task.finishTime = randint(20,40)
    task.pickup = choice(list(points.keys()))
    while task.pickup==task.destination:
        task.pickup = choice(list(points.keys()))
    task.startTime = randint(0,10)
    task.timeconstraint = randint(0,1)

    taskQ.append(task)

for i in taskQ:
    print(i)
    print()


def getSTN(tasks):
    nodes = {}
    currNodes = set()
    for i in tasks:
        nodes[i.taskID] = i
        currNodes.add(i.taskID)

    # generateSTN(0,startPos, currNodes, energy, set(), capacity)
    currList = []
    energyRem = energy
    tempSTN(nodes, 0,startPos, currNodes, energyRem, set(), capacity, currList, 0)



retList = list()

minPen = 10e9
minTT=10e9
getSTN(taskQ)


# pl1 = nodes[1].pickup
# pl2 = nodes[0].destination

# print(dist[places["dock_2"]][places["dock_1"]])
print(retList)
print(minPen)
# print(minTT)

# getNearestDock("dock_2")



