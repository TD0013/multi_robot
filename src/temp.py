# %%
from random import randint, choice
from multi_robot.msg import TD_task
import yaml
import numpy as np

# %%
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

# %%
TIMETOCHARGE = 3000

class Robot:
    def getNearestDock(self, pos):
        global dist
        asd = 10e9
        for i in ["dock_1", "dock_2", "dock_3"]:
            asd  = min(asd, dist[places[i]][places[pos]])
        
        return asd

    def getCentralDock(self, start, next):
        global dist
        asd = 10e9
        for i in ["dock_1", "dock_2", "dock_3"]:
            asd  = min(asd, dist[places[i]][places[start]]+dist[places[i]][places[next]])
        
        return asd


    def tempSTN(self, nodes, time, pos, taskI, energyRem, started, capacityRem, currList, currPen, bufferSize):
        global dist
        global places
        if len(taskI)==0:
            # print(currList, currPen)
            if(currPen<self.minPen):
                self.minPen = currPen
                t = currList.copy()
                self.retList=t
                self.minTT = min(self.minTT, currList[-1][1])
            # retList.append(t)
            # print(retList)
            
        else:
            for i in taskI:
                # print(currList)
                if(i in started):   # Has the task been picked up
                    timecpy = time+(dist[places[pos]][places[nodes[i].destination]])/self.velocity  #Current Time Update
                    enRem = energyRem-(0.5*(self.mass+self.capacity-capacityRem)*self.velocity**2)*((dist[places[pos]][places[nodes[i].destination]])/self.velocity) #Current energy remaining update
                    # print(enRem)
                    prevPos = pos
                    pos = nodes[i].destination                                  #current Position
                    # print(str(i)+"drop", timecpy)


                    newcapacityRem = capacityRem+nodes[i].demand                   # New capacity
                    newBuff = bufferSize+1
                    cap = self.capacity-newcapacityRem
                    tt = (enRem*1.0)/(0.5*(self.mass+cap)*(self.velocity**2))                     # possible total travel time with new capacity
                    currList.append([pos, timecpy])                           
                    taskIcpy = taskI.copy()
                    taskIcpy.remove(i)            # remove curr task from task list as it has been delivered

                    if((timecpy+self.getNearestDock(pos)/self.velocity)>tt):              # Does robot run out of energy before reaching nearest dock
                        # print("energy over")
                        # tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                        timecpy = time + TIMETOCHARGE + (self.getCentralDock(prevPos, pos)/self.velocity)
                        if(nodes[i].timeconstraint ==1):
                            tempPen = currPen+max(0, (timecpy-nodes[i].finishTime))   #penalty update for soft task
                        else:                                                        #Hard task penalty update
                            if(timecpy-nodes[i].finishTime>0):
                                tempPen =currPen+10e6
                            else:
                                tempPen = currPen
                        self.tempSTN(nodes, timecpy, pos, taskIcpy, self.energy, started, newcapacityRem, currList, tempPen, newBuff)   #Recursion with current time, current pos, current energy rem

                    else:
                        if(nodes[i].timeconstraint ==1):
                            tempPen = currPen+max(0, (timecpy-nodes[i].finishTime))   #penalty update for soft task
                        else:                                                        #Hard task penalty update
                            if(timecpy-nodes[i].finishTime>0):
                                tempPen =currPen+10e6
                            else:
                                tempPen = currPen
                        self.tempSTN(nodes, timecpy, pos, taskIcpy, enRem, started, newcapacityRem, currList, tempPen, newBuff)   #Recursion with current time, current pos, current energy rem

                    currList.pop()


                else:       # if task not picked up
                    # print(pos)
                    # print(places[pos])
                    # print(dist[places[pos]][places[nodes[i].pickup]])
                    if(bufferSize>0):
                        timecpy = time+(dist[places[pos]][places[nodes[i].pickup]])/self.velocity #Current Time Update
                        enRem = energyRem-(0.5*(self.mass+self.capacity-capacityRem)*self.velocity**2)*((dist[places[pos]][places[nodes[i].pickup]])/self.velocity) #Current energy remaining update
                        # print(enRem)
                        prevPos = pos
                        pos = nodes[i].pickup   #current pos

                        if(nodes[i].startTime>timecpy): # Basically wait for task to start
                            timecpy = nodes[i].startTime
                    
                        currList.append([pos, timecpy])
                        startedCpy = started.copy()
                        startedCpy.add(i)

                        newcapacityRem = capacityRem-nodes[i].demand
                        cap = self.capacity-capacityRem
                        newBuff = bufferSize-1
                        if(newcapacityRem<=0):
                                self.tempSTN(nodes, time, pos, set(), enRem, started, self.capacity, currList, 10e9, newBuff)
                        else:
                            # print(0.5*(self.mass+cap)*(self.velocity**2))
                            tt = (enRem*1.0)/(0.5*(self.mass+cap)*(self.velocity**2))        # possible travel time with current capacity              

                            if((timecpy+self.getNearestDock(pos)/self.velocity)>tt): # Does robot run out of energy before reaching nearest dock
                                # print("energy over")
                                # tempSTN(nodes, time, pos, set(), energyRem, started, capacityRem, currList, 10e9)
                                timecpy = time + TIMETOCHARGE + (self.getCentralDock(prevPos, pos)/self.velocity)
                                self.tempSTN(nodes, timecpy, pos, taskI, self.energy, startedCpy, newcapacityRem, currList, currPen, newBuff)

                            else:
                                # print(str(i)+"start", time, nodes[i].startTime, timecpy)
                                    self.tempSTN(nodes, timecpy, pos, taskI, enRem, startedCpy, newcapacityRem, currList, currPen, newBuff)
                        currList.pop()


    def getSTN(self, task):
            # print(self.arrtibute, task.type)
        if(self.arrtibute[int(task.type)]=="1"):

            self.retList = list()
            self.minPen = 10e9
            self.minTT = 10e9

            temp  = self.tasks.copy()
            temp.append(task)
            nodes = {}
            currNodes = set()
            for i in temp:
                nodes[i.taskID] = i
                currNodes.add(i.taskID)

            # generateSTN(0,startPos, currNodes, energy, set(), capacity)
            currList = []
            energyRem = self.energy
            self.tempSTN(nodes, 0, self.currPos, currNodes, energyRem, set(), self.capacity, currList, 0, self.BUFFER)
            # print(self.retList)
            return self.minPen, self.minTT, self.eff
        else:
            return 10e9,10e9,self.eff
    
    def addTask(self, task):

        self.retList = list()
        self.minPen = 10e9
        self.minTT = 10e9

        self.tasks.append(task)

        nodes = {}
        currNodes = set()
        for i in self.tasks:
            nodes[i.taskID] = i
            currNodes.add(i.taskID)

        # generateSTN(0,startPos, currNodes, energy, set(), capacity)
        currList = []
        energyRem = self.energy
        self.tempSTN(nodes, 0,self.currPos, currNodes, energyRem, set(), self.capacity, currList, 0, self.BUFFER)

        self.finalList = self.retList.copy()
        self.finalPen = self.minPen
        self.finalTT = self.minTT

    def __init__(self, robotID) -> None:

        self.robotID = robotID

        with open('/home/alpha3/catkin_ws/src/multi_robot/param/graph.yaml') as f:
            props = yaml.load(f, Loader=yaml.SafeLoader)
            # print(data)
        # print(props["td"][self.robotID[:2]]["capacity"])
        props = props["td"][self.robotID[:2]]

        self.capacity = props["capacity"]
        self.mass = props["mass"]
        self.velocity = props["velocity"]
        self.energy = props["energy"]
        self.currPos = props["start"]
        self.currCarr = 0
        self.BUFFER = props["BUFFER"]
        self.arrtibute  = props["attribute"]

        self.eff=0
        for i in props["attribute"]:
            if i =="1":
                self.eff+=1
        self.eff = self.eff/len(props["attribute"])

        self.retList = list()
        self.minPen = 10e9
        self.minTT = 10e9

        self.tasks = list()

        self.finalList = list()
        self.finalPen = 0
        self.finalTT = 0


# %%
# make Robots
R1COUNT =  2
R2COUNT = 4
R3COUNT = 4

roboList = list()
SOTArobotList = list()

for i in range(R1COUNT):
    roboList.append(Robot("r1"+str(i)))
    SOTArobotList.append(Robot("r1"+str(i)))

for i in range(R2COUNT):
    roboList.append(Robot("r2"+str(i)))
    SOTArobotList.append(Robot("r2"+str(i)))

for i in range(R3COUNT):
    roboList.append(Robot("r3"+str(i)))
    SOTArobotList.append(Robot("r3"+str(i)))

print("asd")
for i in roboList:
    print(i.robotID)


# %%
## Demo Tasks
TASKCOUNT = 40


MIN_VEL = 0.5

taskQ = []

for i in range(TASKCOUNT):
    task = TD_task()
    task.taskID= i
    task.arrivalTime = 0
    task.demand = randint(10, 40)
    task.destination = choice(list(points.keys()))
    
    task.pickup = choice(list(points.keys()))

    while task.pickup in ["dock_1", "dock_2", "dock_3"]:
        task.pickup = choice(list(points.keys()))

    while task.destination in ["dock_1", "dock_2", "dock_3", task.pickup]:
        task.destination = choice(list(points.keys()))
    task.startTime = task.arrivalTime+randint(0,10)
    task.finishTime = task.arrivalTime+int(dist[places[task.pickup]][places[task.destination]]/MIN_VEL)

    task.timeconstraint = randint(0,1)
    task.type = randint(0,2)
    # if i>=0 and i<TASKCOUNT/2: 
    #     task.timeconstraint = 1
    #     task.type = (2)
    # else:
    #     task.timeconstraint = 1
    #     task.type = randint(0,1)
    # print(task)
    taskQ.append(task)

    
for i in taskQ:
    print(i)
    print()

# %%
totalRejected = 0
for i in taskQ:
    bestRobot = "asd"
    bestBid = [10e9,1,10e9]
    # print(roboList)
    for j in roboList:
        bid = j.getSTN(i)
        print(i.taskID,j.robotID)
        print(bid)
        #if (bestBid[0]>bid[0])or (bestBid[0]==bid[0] and bestBid[2]>bid[2]) or (bestBid[0]==bid[0] and bestBid[2] == bid[2] and bestBid[1]>bid[1]):
        if (bestBid[0]==bid[0] and bestBid[2]>bid[2]):  
            bestRobot = j
            bestBid = bid
        else:
            if(bestBid[0]>bid[0]): 
                bestRobot = j
                bestBid = bid
    # print(bestRobot.robotID)
    if(bestBid[0]>=10e6):
        # print("rej", bestBid[0])
        totalRejected+=1
    else:
        # print(bestBid[0])
        bestRobot.addTask(i)

SOTAtotalRejected = 0
for i in taskQ:
    SOTAbestRobot = "asd"
    SOTAbestBid = [10e9,1,10e9]
    # print(roboList)
    for j in SOTArobotList:
        SOTAbid = j.getSTN(i)
        print(i.taskID,j.robotID)
        print(SOTAbid)
        if (SOTAbestBid[0]>SOTAbid[0]):
            SOTAbestRobot = j
            SOTAbestBid = SOTAbid
            
    # print(bestRobot.robotID)
    if(SOTAbestBid[0]>=10e6):
        SOTAtotalRejected+=1
    else:
        SOTAbestRobot.addTask(i)

totalPen = 0
maxTT = 0
for i in roboList:
    print(i.robotID, len(i.finalList), i.finalPen)
    totalPen+=i.finalPen
    maxTT=max(i.finalTT, maxTT)
print("Our Algo")
print(totalPen, maxTT, totalRejected) 

SOTAtotalPen = 0
SOTAmaxTT = 0
for i in SOTArobotList:
    print(i.robotID, len(i.finalList), i.finalPen)
    SOTAtotalPen+=i.finalPen
    SOTAmaxTT=max(i.finalTT, SOTAmaxTT)
print("For SOTA")
print(SOTAtotalPen, SOTAmaxTT, SOTAtotalRejected) 




