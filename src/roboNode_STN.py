#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import geometry_msgs.msg
import nav_msgs.msg
import multi_robot.msg
import numpy as np
import yaml


with open("/home/alpha3/catkin_ws/src/multi_robot/param/distance_params.yaml", 'r') as file1:
    points= yaml.safe_load(file1)
    points = points["world_nodes"]

dist= np.loadtxt('/home/alpha3/catkin_ws/src/multi_robot/param/dist.txt', usecols=range(22))
dist = np.round(dist, decimals=3)
places = {}
z=0
for i in points:
    places[i] = z
    z+=1


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
            minTT = min(minTT, currList[-1][1])
        # retList.append(t)
        # print(retList)
        
    else:
        for i in taskI:
            # print(currList)
            if(i in started):   # Has the task been picked up
                timecpy = time+(dist[places[pos]][places[nodes[i].destination]])/velocity  #Current Time Update
                enRem = energyRem-(0.5*(mass+capacity-capacityRem)*velocity**2)*((dist[places[pos]][places[nodes[i].destination]])/velocity) #Current energy remaining update
                # print("enRem", enRem)
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
                # print(cap, velocity)
                tt = time+enRem/(0.5*(mass+cap)*velocity**2)                     # possible total travel time with new capacity

                if((timecpy+getNearestDock(pos)/velocity)>tt):              # Does robot run out of energy before reaching nearest dock
                    # print("energy over")
                    tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                else:
                    currList.append([pos, timecpy, i])                           
                    taskIcpy = taskI.copy()
                    taskIcpy.remove(i)            # remove curr task from task list as it has been delivered
                    tempSTN(nodes, timecpy, pos, taskIcpy, enRem, started, capacityRem, currList, tempPen)   #Recursion with current time, current pos, current energy rem
                    currList.pop()

            else:       # if task not picked up
                timecpy = time+(dist[places[pos]][places[nodes[i].pickup]])/velocity #Current Time Update
                enRem = energyRem-(0.5*(mass+capacity-capacityRem)*velocity**2)*((dist[places[pos]][places[nodes[i].pickup]])/velocity) #Current energy remaining update
                # print("enRem", enRem)

                pos = nodes[i].pickup   #current pos

                if(nodes[i].startTime>timecpy): # Basically wait for task to start
                    timecpy = nodes[i].startTime
            
                currList.append([pos, timecpy, i])
                startedCpy = started.copy()
                startedCpy.add(i)

                capacityRem = capacityRem-nodes[i].demand
                cap = capacity-capacityRem
                tt = time+enRem/(0.5*(mass+cap)*velocity**2)        # possible travel time with current capacity              
                
                # print(tt, getNearestDock(pos)/velocity)

                if((timecpy+getNearestDock(pos)/velocity)>tt): # Does robot run out of energy before reaching nearest dock
                    # print("energy over")
                    tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                else:
                    if(capacityRem<0):
                        tempSTN(nodes, time, pos, set(), enRem, started, capacity, currList, 10e9)
                    # print(str(i)+"start", time, nodes[i].startTime, timecpy)
                    else:
                        tempSTN(nodes, timecpy, pos, taskI, enRem, startedCpy, capacityRem, currList, currPen)
                currList.pop()

def getSTN(tasks):
    # print(tasks)

    global retList 
    global minPen  
    global minTT
    global energy
    global currPos
    global startedTasks
    global capacity
    global currCarr


    retList = list()
    minPen = 10e9
    minTT = 10e9


    nodes = {}
    currNodes = set()
    for i in tasks:
        nodes[i.taskID] = i
        currNodes.add(i.taskID)

    currList = []
    tempSTN(nodes, rospy.Time.now().to_sec(), currPos[0], currNodes, energy, startedTasks, capacity-currCarr, currList, 0)

    return 

def doTask():
    # pass
    global roboStatus
    global plannedPath
    global assigendTasks
    global startedTasks
    global currPos

    if roboStatus==3 and len(plannedPath)>0:
        # print(ROBOTNAME, "robo Task")
        # roboStatus==1
        task = plannedPath.pop(0)
        if(task[1] not in startedTasks):
            startedTasks.add(task[1])
        else:
            startedTasks.remove(task[1])
        currPos = task
        # print("Next Goal: ", currPos, startedTasks, assigendTasks)
        goalToPub =  geometry_msgs.msg.PoseStamped()
        goalToPub.header.frame_id = "map"
        goalToPub.pose.position.x = points[currPos[0]]["x"]
        goalToPub.pose.position.y = points[currPos[0]]["y"]
        goalToPub.pose.orientation.w = 1


        goalPub.publish(goalToPub)

def statusCallback(data):
    global roboStatus
    global currCarr
    global startedTasks
    global currPos
    global assigendTasks
    global totalPen

    if len(data.status_list)==0:
        pass
    else:
        # print(data.status_list[-1].status)
        if roboStatus!=3 and data.status_list[-1].status==3:
            print("status changed")
            
            thisTask = multi_robot.msg.TD_task()
            for x in assigendTasks:
                if(x.taskID == currPos[1]):
                    thisTask = x

            if currPos[1] in startedTasks:              #Task start position reached
                while not rospy.Time.now().to_sec()>thisTask.startTime:     #wait for task to start
                    rospy.sleep(0.1)
                currCarr = currCarr+thisTask.demand     # Add demand to carrying

            else:                                       #Task completed
                if(rospy.Time.now().to_sec() > thisTask.finishTime):        # add penalty (if any)
                    totalPen+=totalPen+ 10e9 if thisTask.timeconstraint==0 else rospy.Time.now().to_sec() - thisTask.finishTime

                # print(thisTask, totalPen)
                currCarr = currCarr-thisTask.demand
                assigendTasks.remove(thisTask)
            roboStatus = data.status_list[-1].status
            doTask()
        else:
            roboStatus = data.status_list[-1].status
            
def auctionBid(data):
    global arrtibute
    global assigendTasks
    global BUFFER

    if len(assigendTasks)< BUFFER  and arrtibute[data.type]=="1": #Check if robot buffer has space and can accomplish task
        global minPen  
        global minTT
        global robotID
        global eff
        global bidPublisher

        task = assigendTasks.copy()
        task.append(data)

        getSTN(task)


        newBid = multi_robot.msg.TD_STN_bid()
        newBid.robotName = robotID
        newBid.eff = eff
        newBid.penalty = minPen
        newBid.time = minTT
        newBid.taskID = data.taskID

        bidPublisher.publish(newBid)


    # elif arrtibute[data.type]=="1":        #for debugging
    #     print(robotID, "buffer full")

    # else:                                   #for debugging
    #     print(robotID, "Incompatible")

def taskAssign(data):
    global robotID

    if(data.robotName==robotID):
        global retList 
        global plannedPath
        global assigendTasks
        # print("I won")
        assigendTasks.append(data.task)

        getSTN(assigendTasks)

        plannedPath = list()
        for i in retList:
            plannedPath.append([i[0], i[2]])

    doTask()

if __name__ == '__main__':
    
    rospy.init_node('sota')                     # init ROS node
    robotID = rospy.get_param('roboNode/name')  # get the info of which robot this node is for
    props = rospy.get_param('/td/'+ robotID[:2])# get properties of the type of robot
    rospy.loginfo_once(props)
    rospy.set_param("/move_base_"+robotID+"/TebLocalPlannerROS/max_vel_x",props["velocity"])    #set the max vel in the simulator from the read properties
    rospy.set_param("/move_base_"+robotID+"/TebLocalPlannerROS/max_global_plan_lookahead_dist",props["velocity"])    #set the max vel in the simulator from the read properties


    capacity = props["capacity"]
    mass = props["mass"]
    velocity = props["velocity"]
    energy = props["energy"]
    currPos = [props["start"],-1]
    currCarr = 0
    BUFFER = props["BUFFER"]
    arrtibute  = props["attribute"]

    eff=0
    for i in props["attribute"]:
        if i =="1":
            eff+=1
    eff = eff/len(props["attribute"])


    #Init global data
    totalPen = 0

    startedTasks = set()
    assigendTasks = list()
    plannedPath = list()

    retList = list()
    minPen = 10e9
    minTT = 10e9

    roboStatus=3
    robotPose=geometry_msgs.msg.Point()

    #Init publishers and Subscribers

    bidPublisher= rospy.Publisher("/bid", multi_robot.msg.TD_STN_bid, queue_size=10)
    goalPub=rospy.Publisher("/"+robotID+"/move_base_simple/goal", geometry_msgs.msg.PoseStamped, queue_size=10)

    rospy.Subscriber("/"+robotID+"/move_base/status", actionlib_msgs.msg.GoalStatusArray, statusCallback)
    # rospy.Subscriber("/"+robotID+"/odom", nav_msgs.msg.Odometry, odometryCallback)
    # rospy.Subscriber('/task', geometry_msgs.msg.PoseStamped, taskCallback)
    rospy.Subscriber('/auction', multi_robot.msg.TD_task, auctionBid)
    rospy.Subscriber('/assignTask', multi_robot.msg.TD_STN_assignTask, taskAssign)

    while not rospy.is_shutdown():
        # print(robotID+" "+str(rospy.Time.now().to_sec()))
        # print("Pos", currPos)
        # print("Started Tasks", startedTasks)
        # print("len of assigned tasks",len(assigendTasks))

        energy = energy-0.5*(mass+currCarr)*(velocity**2)
        rospy.sleep(1)


    # rospy.spin()
