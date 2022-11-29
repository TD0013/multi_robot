#!/usr/bin/env python3

import roslaunch
import rospy

def rviz_write(z):
    read = open("/home/alpha3/catkin_ws/src/multi_robot/rviz/part1", "r")
    w = open("/home/alpha3/catkin_ws/src/multi_robot/rviz/temp2.rviz","w")
    temp = read.readlines()

    w.writelines(temp)
    read.close()

    read = open("/home/alpha3/catkin_ws/src/multi_robot/rviz/temp.rviz", "r")
    temp = read.readlines()
    read.close()

    for i in range(1,z+1):
        for j in temp:
            k = j.replace("robot1", "robot"+str(i))
            w.writelines(k)
    
    read = open("/home/alpha3/catkin_ws/src/multi_robot/rviz/part2", "r")
    temp = read.readlines()  
    w.writelines(temp)
    read.close()
    w.close()  


z = 5
rviz_write(z)
rospy.sleep(1)

uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
roslaunch.configure_logging(uuid)

cli_args1 = ['multi_robot', 'TD_minimal.launch']


roslaunch_file1 = roslaunch.rlutil.resolve_launch_arguments(cli_args1)

launch_files = [roslaunch_file1]


for i in range(1,z+1):
    cli_args2 = ['/home/alpha3/catkin_ws/src/multi_robot/launch/TD_roboLauncher.launch', 'tbName:=robot'+str(i), 'x:='+str(-4), 'y:='+str(i*0.5+1)]
    print(cli_args2)
    roslaunch_file2 = roslaunch.rlutil.resolve_launch_arguments(cli_args2)[0]
    roslaunch_args2 = cli_args2[1:]
    launch_files.append([(roslaunch_file2, roslaunch_args2)])

parent = {}
for id, val in enumerate(launch_files):
    print(val)
    parent[id] = roslaunch.parent.ROSLaunchParent(uuid, val)

    parent[id].start()


print("\n\n\n\n\n\nLaunches Done\n\n\n\n\n\n")


while not rospy.is_shutdown():
    
    # print("asd")
    # if(rospy.is_shutdown):
    #     break
    rospy.sleep(1)


  

# parent.shutdown()

