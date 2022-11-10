#!/usr/bin/env python

import roslaunch
import rospy

uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
roslaunch.configure_logging(uuid)

cli_args1 = ['multi_robot', 'TD_minimal.launch']


roslaunch_file1 = roslaunch.rlutil.resolve_launch_arguments(cli_args1)

launch_files = [roslaunch_file1]

z = 5

for i in range(1,z):
    cli_args2 = ['/home/td0013/catkin_ws/src/multi_robot/launch/TD_roboLauncher.launch', 'tbName:=robot'+str(i), 'x:='+str(i+2), 'y:='+str(i+2)]
    print(cli_args2)
    roslaunch_file2 = roslaunch.rlutil.resolve_launch_arguments(cli_args2)[0]
    roslaunch_args2 = cli_args2[1:]
    launch_files.append([(roslaunch_file2, roslaunch_args2)])

parent = {}
for id, val in enumerate(launch_files):
    print(val)
    parent[id] = roslaunch.parent.ROSLaunchParent(uuid, val)

    parent[id].start()

while not rospy.is_shutdown():
    
    # print("asd")
    # if(rospy.is_shutdown):
    #     break
    rospy.sleep(1)


  

# parent.shutdown()
