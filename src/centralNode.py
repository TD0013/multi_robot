#!/usr/bin/env python
import rospy
import actionlib_msgs.msg

class DynamicTFBroadcaster:
    def callback(self,data):
        print(data.status_list[-1].status)



    def __init__(self):
        # rospy.sleep(5)
        rospy.Subscriber("/robot1/move_base/status", actionlib_msgs.msg.GoalStatusArray, self.callback)

if __name__ == '__main__':
    rospy.init_node('my_tf_broadcaster')
    tfb = DynamicTFBroadcaster()
    rospy.spin()