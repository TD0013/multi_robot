#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import geometry_msgs.msg

class RobotNode:
    def callback(self,data):
        try:
            stat = data.status_list[-1].status
            # print(stat)
            if(stat!=self.Status.status):
                self.Status.status=stat
                self.statusPub.publish(self.Status)
        except:
            # print("zero")
            pass
    # def callback(self,data):
    #     print(data.status_list[-1].status)

    def doTask(self,data):
        if(data.header.frame_id=="robot"+str(tbNumber)):
            data.header.frame_id="map"
            self.goalPub.publish(data)

    def __init__(self):
        rospy.sleep(3)
        # print("asdfdsdgfhgjfhkgfdjgshfasgdhdfhg")
        self.Status=actionlib_msgs.msg.GoalStatus()
        self.Status.text="robot"+str(tbNumber)
        self.Status.status=3

        self.statusPub=rospy.Publisher("/statusLine", actionlib_msgs.msg.GoalStatus, queue_size=10)
        rospy.sleep(0.1)
        self.statusPub.publish(self.Status)

        self.goalPub=rospy.Publisher("/robot"+str(tbNumber)+"/move_base_simple/goal", geometry_msgs.msg.PoseStamped, queue_size=10)
        
        rospy.Subscriber("/robot"+str(tbNumber)+"/move_base/status", actionlib_msgs.msg.GoalStatusArray, self.callback)
        
        rospy.Subscriber('/taskLine', geometry_msgs.msg.PoseStamped, self.doTask)

        # while not rospy.is_shutdown():
        #     self.statusPub.publish(self.Status)
        #     rospy.sleep(1)

if __name__ == '__main__':
    
    rospy.init_node('roboNode')
    tbNumber = int(rospy.get_param('roboNode/mode')[-1])
    
    tbProp = rospy.get_param('/td/robot'+str(tbNumber))
    print("robot"+str(tbNumber), tbProp) 
    

    # while not rospy.is_shutdown():
        # print(tbNumber)
    tfb = RobotNode()
    rospy.spin()
