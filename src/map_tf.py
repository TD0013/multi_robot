#!/usr/bin/env python

import rospy
import tf
import tf.msg
import geometry_msgs.msg
import gazebo_msgs.msg
import math

        

class DynamicTFBroadcaster:
    def callback(self,data):
        if(self.i==1):
            self.index = data.name.index(self.robotName)
            # self.index = 2
            i = 0
        # self.pub_tf.sendTransform([data.pose[self.index].position.x, data.pose[self.index].position.y, data.pose[self.index].position.z], [data.pose[self.index].orientation.x, data.pose[self.index].orientation.y, data.pose[self.index].orientation.z, data.pose[self.index].orientation.w], rospy.Time.now(), self.robotName+"/base_footprint", "/map")
        self.pub_tf.sendTransform([data.pose[self.index].position.x, data.pose[self.index].position.y, data.pose[self.index].position.z], [data.pose[self.index].orientation.x, data.pose[self.index].orientation.y, data.pose[self.index].orientation.z, data.pose[self.index].orientation.w], rospy.Time.now(), self.robotName+"/base_footprint", self.robotName+"/odom")



    def __init__(self):
        rospy.sleep(5)
        self.i = 1
        self.pub_tf = tf.TransformBroadcaster()
        self.robotName = rospy.get_param("~robotName")
        
        rospy.Subscriber("/gazebo/model_states", gazebo_msgs.msg.ModelStates, self.callback)


if __name__ == '__main__':
    rospy.init_node('my_tf_broadcaster')
    tfb = DynamicTFBroadcaster()
    rospy.spin()