#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import std_msgs.msg
import nav_msgs.msg
import geometry_msgs.msg
import multi_robot.msg 


class Auctioner:
    def bidCallback(self,data):
        # print(self.dict)
        if self.dict[data.robotName]==0:
            self.dict[data.robotName]=data.bidValue
            if(self.bidders==0):
                self.winner.robotName=data.robotName
            else:
                # print(data.robotNmae)
                self.winner.robotName=self.winner.robotName if self.dict[self.winner.robotName]<self.dict[data.robotName] else data.robotName
                # print(self.winner.robotName)
            # print(data.bidValue)
            
            self.bidders+=1

        # print("number of bids:", len(self.dict))
        if(self.bidders==len(RobotNode.robotSet)):
            self.taskAssign.publish(self.winner)
        
            

    def __init__(self, time):
        # try:
        #     print(RobotNode.getTaskList())
        # except:
        #     print("No Task")
        self.dict={}
        
        sub = rospy.Subscriber("/bid", multi_robot.msg.TD_bid, self.bidCallback)

        self.auctionPub = rospy.Publisher("/auction", geometry_msgs.msg.PoseStamped, queue_size=1)
        self.taskAssign = rospy.Publisher("/assignTask", multi_robot.msg.TD_assignTask, queue_size=1)
        

        while rospy.get_time()-time<10 and not rospy.is_shutdown():
            # print("Lock:", RobotNode.getLock())
            if(not RobotNode.taskList):
                print("No tasks to Auction")
            if(RobotNode.getLock()):
                print("Last Auction Not Yet Complete")
            if rospy.get_time()-time<8.5 and RobotNode.getTaskLen() and not RobotNode.getLock():
                print(ROBOTNAME+" Auctioning task")
                RobotNode.setLock(1)
                rospy.sleep(1)
                self.bidders=0
                self.dict={}
                for i in RobotNode.robotSet:
                    self.dict[i] = 0
                
                # print(self.dict)
                rospy.sleep(0.4)

                auctionItem=RobotNode.getTaskList()
                self.winner = multi_robot.msg.TD_assignTask()
                self.winner.task = auctionItem

                self.auctionPub.publish(auctionItem)

            rospy.sleep(1)
        rospy.sleep(1)
        self.auctionPub.unregister()
        self.taskAssign.unregister()
        sub.unregister()
                


    def __del__(self):

        
        tpub = rospy.Publisher("/transfer", std_msgs.msg.String, queue_size=10)
        rospy.sleep(0.5)
        
        nextAuctioner="robot"+str(ROBOTNUMBER+1)
        if nextAuctioner in RobotNode.robotSet:
            tpub.publish(nextAuctioner)
        else:
            tpub.publish('robot1')
        tpub.unregister()
        rospy.sleep(0.5)
        print("deleted auctioner")
        
        


class RobotNode:
    AuctionLock=0

    taskList=[]
    robotSet=set()
    @staticmethod
    def getLock():
        return RobotNode.AuctionLock
    @staticmethod
    def setLock(i):
        RobotNode.AuctionLock=i

    @staticmethod
    def getTaskList():
        return RobotNode.taskList[0]
    @staticmethod
    def addTask(task):
        RobotNode.taskList.append(task)
    @staticmethod
    def removeTask():
        RobotNode.taskList.pop(0)
        # RobotNode.taskList.remove(data)
    @staticmethod
    def getTaskLen():
        return len(RobotNode.taskList)

    def introCallBack(self, data):
        # print(data.data)
        self.robotSet.add(data.data)
        # print(self.robotSet)

    def introduceYourself(self):

        sub = rospy.Subscriber('/intro', std_msgs.msg.String, self.introCallBack)
        pub= rospy.Publisher("/intro", std_msgs.msg.String, queue_size=10)
        temp = std_msgs.msg.String()
        temp.data=ROBOTNAME

        rospy.sleep(0.5)    

        pub.publish(temp)



    def doTask(self):
        if self.roboStatus==3 and self.roboTaskList:
            # print(ROBOTNAME, "robo Task")
            self.roboStatus==1
            task = self.roboTaskList.pop(0)
            self.goalPub.publish(task)
            

    def callback(self,data):
        try:
            self.roboStatus = data.status_list[-1].status
            # print(self.roboStatus)
            
            self.doTask()
            
        except:
            # print("zero")
            pass

    def taskAssign(self, data):
        # print(data)
        # if RobotNode.getTaskLen():
        try:
            if data.robotName==ROBOTNAME:
                print(ROBOTNAME+" accepted task")
                self.roboTaskList.append(data.task)
            
            # TODO ::::: self.taskList.remove(data.task)
            # self.taskList.pop(0)
            # print(self.taskList)
            RobotNode.removeTask()
            
            RobotNode.setLock(0)
            # print(ROBOTNAME, "remove lock", RobotNode.getLock())

            self.doTask()
        except:
            print(ROBOTNAME, "ignore")

    def odometryCallback(self,data):
        self.robotPose=data.pose.pose.position

    def taskCallback(self,data):
        # self.taskList.append(data)
        RobotNode.addTask(data)
        # print(ROBOTNAME, len(self.taskList))

    def auctionBid(self, data):
        task=data.pose.position

        bid=multi_robot.msg.TD_bid()
        bid.robotName=ROBOTNAME
        bid.bidValue=(((self.robotPose.x-task.x+3)**2)+((self.robotPose.y-task.y-1)**2))**0.5

        self.bidPublisher.publish(bid)

    def transferAuctioner(self,data):
        self.auctioner=data.data

    def __init__(self):
        rospy.sleep(1)

        self.roboStatus=3
        self.roboTaskList=[]
        self.auctioner="robot1"
        self.robotPose=geometry_msgs.msg.Point()

        rospy.Subscriber("/"+ROBOTNAME+"/move_base/status", actionlib_msgs.msg.GoalStatusArray, self.callback)
        rospy.Subscriber("/"+ROBOTNAME+"/odom", nav_msgs.msg.Odometry, self.odometryCallback)
        rospy.Subscriber('/task', geometry_msgs.msg.PoseStamped, self.taskCallback)
        rospy.Subscriber('/auction', geometry_msgs.msg.PoseStamped, self.auctionBid)
        rospy.Subscriber('/transfer', std_msgs.msg.String, self.transferAuctioner)
        rospy.Subscriber('/assignTask', multi_robot.msg.TD_assignTask, self.taskAssign)

        self.bidPublisher= rospy.Publisher("/bid", multi_robot.msg.TD_bid, queue_size=10)
        self.goalPub=rospy.Publisher("/"+ROBOTNAME+"/move_base_simple/goal", geometry_msgs.msg.PoseStamped, queue_size=10)

        rospy.sleep(1)

        self.introduceYourself()
        print(ROBOTNAME, "Intro Done")


        while not rospy.is_shutdown():
            # print(ROBOTNAME, RobotNode.getTaskLen())
            if self.auctioner==ROBOTNAME:
                print("Auctioner Set to "+ROBOTNAME)
                auc=Auctioner(rospy.get_time())
                rospy.sleep(0.1)
                del auc
                
                # print("No active Auctioner")
                # rospy.sleep(5)
            # print(ROBOTNAME, self.taskList)
            else:
                rospy.sleep(1)
                
            
                

        


if __name__ == '__main__':
    
    rospy.init_node('roboNode')
    ROBOTNUMBER = int(rospy.get_param('roboNode/mode')[-1])
    ROBOTNAME="robot"+str(ROBOTNUMBER)
    tfb = RobotNode()
    rospy.spin()