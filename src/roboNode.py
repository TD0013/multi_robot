#!/usr/bin/env python
import rospy
import actionlib_msgs.msg
tbNumber=0
class DynamicTFBroadcaster:
    def callback(self,data):
        print(data.status_list[-1].status)



    def __init__(self):
        # rospy.sleep(5)
        rospy.Subscriber("/robot"+tbNumber+"/move_base/status", actionlib_msgs.msg.GoalStatusArray, self.callback)

if __name__ == '__main__':
    tbNumber = int(rospy.get_param("/curr_tbNumber")[-1])
    rospy.init_node('/roboNode')
    
    # print(rospy.get_param('curr_tbNumber'))
    tfb = DynamicTFBroadcaster()
    rospy.spin()
