#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import std_msgs.msg
import nav_msgs.msg
import geometry_msgs.msg
import multi_robot.msg 


class Auctioner:

    def bidCallback(self,data):
        self.dict[data.robotName]=data.bidValue

        print(len(self.dict))
        if(len(self.dict)==4):
            temp=min(self.dict.values())
            print(temp)
            res = [key for key in self.dict if self.dict[key] == temp]

            winner = multi_robot.msg.TD_assignTask()
            winner.robotName=res[0]
            winner.task = RobotNode.taskList[0]

            self.taskAssign.publish(winner)

    def __init__(self, time):
        rospy.Subscriber("/bid", multi_robot.msg.TD_bid, self.bidCallback)

        self.auctionPub = rospy.Publisher("/auction", geometry_msgs.msg.PoseStamped, queue_size=10)
        self.taskAssign = rospy.Publisher("/assignTask", multi_robot.msg.TD_assignTask, queue_size=10)
        

        while rospy.get_time()-time<10 and not rospy.is_shutdown():
            print(RobotNode.getLock())
            if(not RobotNode.taskList):
                print("tasklist")
            if(RobotNode.getLock()):
                print("auctionLock")
            if rospy.get_time()-time<7 and RobotNode.taskList and not RobotNode.getLock():
                RobotNode.setLock(1)
                self.dict={}
                auctionItem=RobotNode.taskList[0]
                self.auctionPub.publish(auctionItem)
            rospy.sleep(0.5)
                


    def __del__(self):
        print("deleted auctioner")
        # nextAuctioner=(ROBOTNUMBER)%2+1
        # rospy.Publisher("/transfer", std_msgs.msg.String, queue_size=10).publish("robot"+nextAuctioner)
        


class RobotNode:
    AuctionLock=0

    taskList=[]
    robotSet={}
    @staticmethod
    def getLock():
        return RobotNode.AuctionLock
    @staticmethod
    def setLock(i):
        RobotNode.AuctionLock=i

    
    def doTask(self):
        if self.roboStatus==3 and self.roboTaskList:
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
        if data.robotName==ROBOTNAME:
            self.roboTaskList.append(data.task)
        
        # TODO ::::: self.taskList.remove(data.task)
        self.taskList.pop(0)
        
        RobotNode.setLock(0)
        print(ROBOTNAME, "self.AuctionLock", RobotNode.getLock())

        self.doTask()

    def odometryCallback(self,data):
        self.robotPose=data.pose.pose.position

    def taskCallback(self,data):
        self.taskList.append(data)
        print(ROBOTNAME, len(self.taskList))

    def auctionBid(self, data):
        task=data.pose.position

        bid=multi_robot.msg.TD_bid()
        bid.robotName=ROBOTNAME
        bid.bidValue=(((self.robotPose.x-task.x-3)**2)+((self.robotPose.y-task.y+1)**2))**0.5

        self.bidPublisher.publish(bid)

    def transferAuctioner(self,data):
        self.auctioner=data

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

        while not rospy.is_shutdown():
            
            if self.auctioner==ROBOTNAME:
                auc=Auctioner(rospy.get_time())
                del auc
            # print(ROBOTNAME, self.taskList)
            rospy.sleep(1)
                
            
                

        


if __name__ == '__main__':
    
    rospy.init_node('roboNode')
    ROBOTNUMBER = int(rospy.get_param('roboNode/mode')[-1])
    ROBOTNAME="robot"+str(ROBOTNUMBER)
    tfb = RobotNode()
    rospy.spin()