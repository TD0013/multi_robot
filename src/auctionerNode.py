#!/usr/bin/env python3
import rospy
import multi_robot.msg

AUCTION_TIME = 2

def auction():
    global tasksToAuction
    global bestBid
    global rejectionCount
    

    newAuction = tasksToAuction.pop(0)

    bestBid = multi_robot.msg.TD_STN_bid()
    bestBid.penalty = 10e9
    bestBid.robotName = ""
    bestBid.time = 10e9
    bestBid.eff = 10
    bestBid.taskID = newAuction.taskID
    
    auctionPub.publish(newAuction)

    rospy.sleep(AUCTION_TIME)               # wait for robots to bid

    if(bestBid.penalty >= 10e6):            # if no appropriate winner
        if(newAuction.timeconstraint ==1):  # if task hard, reject
            rejectionCount+=1
        else:                               # if task soft, add task to back of queue
            tasksToAuction.append(newAuction)   
            
    else:                                   # else assign task to winner
        bidWinner = multi_robot.msg.TD_STN_assignTask()
        bidWinner.robotName = bestBid.robotName
        bidWinner.task = newAuction
        # print(bidWinner.robotName)
        taskAssign.publish(bidWinner)




def bidCallback(data):
    global bestBid

    if(data.taskID==bestBid.taskID):
        if data.penalty<bestBid.penalty:            # lower penalty wins!!
            bestBid = data
        elif(data.penalty == bestBid.penalty):      # less efficient robot wins if equal penalty 
            if(data.eff>bestBid.eff):
                bestBid = data
            elif(data.eff==bestBid.eff):
                if(data.time < bestBid.time):       # better time wins amongst slow robots
                    bestBid = data


def newTask_cb(data):
    global tasksToAuction

    # TODO: improve this
    # if(1):
    if (data.taskID)%2==(int(robotID[1])%2):
        tasksToAuction.append(data)

if __name__ == '__main__':
    
    rospy.init_node('auctioner')                        # init ROS Node
    robotID = rospy.get_param('auctionerNode/name')     # get which robot this node if for
    rospy.loginfo_once(robotID)

    # init Subscribers and Publishers
    tasksToAuction = list()
    bestBid = multi_robot.msg.TD_STN_bid()
    rejectionCount = 0

    rospy.Subscriber('/task', multi_robot.msg.TD_task, newTask_cb)
    rospy.Subscriber("/bid", multi_robot.msg.TD_STN_bid, bidCallback)


    auctionPub = rospy.Publisher("/auction", multi_robot.msg.TD_task, queue_size=1)
    taskAssign = rospy.Publisher("/assignTask", multi_robot.msg.TD_STN_assignTask, queue_size=1)

    while not rospy.is_shutdown():
        if len(tasksToAuction)!=0:
            auction()
        
        rospy.sleep(0.5)
    
    

