def rviz_write(z):
    read = open("/home/td0013/catkin_ws/src/multi_robot/rviz/part1", "r")
    w = open("/home/td0013/catkin_ws/src/multi_robot/rviz/temp2.rviz","w")
    temp = read.readlines()

    w.writelines(temp)
    read.close()

    read = open("/home/td0013/catkin_ws/src/multi_robot/rviz/temp.rviz", "r")
    temp = read.readlines()
    read.close()

    for i in range(1,z+1):
        for j in temp:
            k = j.replace("robot1", "robot"+str(i))
            w.writelines(k)
    
    read = open("/home/td0013/catkin_ws/src/multi_robot/rviz/part2", "r")
    temp = read.readlines()  
    w.writelines(temp)
    read.close()
    w.close()

    

    
    

rviz_write(4)