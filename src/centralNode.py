#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import geometry_msgs.msg

class RoundRobin:
    def assignTask(self):
        print("called Assign Task")
        Robot=self.robotList.pop(0)
        Task=self.taskList.pop(0)
        print(len(self.robotList))
        taskAssign = geometry_msgs.msg.PoseStamped()
        taskAssign.header.frame_id=Robot
        taskAssign.pose=Task.pose
        self.taskPub.publish(taskAssign)

    def statusCallback(self,data):
        # print(data)
        ID = data.text
        Status = data.status

        if(Status==3):
            print("added", ID, "to queue")
            self.robotList.append(ID)
            if(len(self.taskList)!=0):
                self.assignTask() 

    def taskCallback(self,data):
        self.taskList.append(data)
        if(len(self.robotList)!=0):
            self.assignTask()

    def __init__(self):
        rospy.sleep(2)
        self.robotList = []
        self.taskList = []

        self.taskPub = rospy.Publisher('/taskLine', geometry_msgs.msg.PoseStamped, queue_size=10)
        rospy.Subscriber("/statusLine", actionlib_msgs.msg.GoalStatus, self.statusCallback)
        rospy.Subscriber('/task', geometry_msgs.msg.PoseStamped, self.taskCallback)

        while not rospy.is_shutdown():
            print("Robots = ", len(self.robotList))
            print("Tasks  = ", len(self.taskList))
            rospy.sleep(1)


if __name__ == '__main__':
    rospy.init_node('my_tf_broadcaster')
    tfb = RoundRobin()
    rospy.spin()