#!/usr/bin/env python3
import rospy
import actionlib_msgs.msg
import geometry_msgs.msg

if __name__ == '__main__':
    rospy.init_node('taskNode')
    # st=rospy.Time.now()
    st = rospy.get_rostime()


    while not rospy.is_shutdown():
        # print(rospy.Time.now()-st)
        print(rospy.get_rostime().secs-st.secs)

        rospy.sleep(1)
