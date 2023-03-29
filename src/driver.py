#!/usr/bin/env python3

import roslaunch
import rospy
import rospkg
import yaml


# Get Path for multi_robot Pkg and declare global variabel PARAMS
rospack = rospkg.RosPack()
rospy.init_node('driverNode')
PATH = rospack.get_path('multi_robot')

PARAMS = ""

# The function to write the vizualization file as per out current simulation
def rviz_write():
    global PATH
    global PARAMS

    read = open(PATH+"/rviz/part1", "r")
    w = open(PATH+"/rviz/temp2.rviz","w")
    temp = read.readlines()

    w.writelines(temp)
    read.close()

    read = open(PATH+"/rviz/temp.rviz", "r")
    temp = read.readlines()
    read.close()

    for robotType in PARAMS["types"]:
        for i in range (int(PARAMS[robotType]["count"])):
            for j in temp:
                k = j.replace("robot1", robotType+str(i))
                w.writelines(k)
    
    read = open(PATH+"/rviz/part2", "r")
    temp = read.readlines()  
    w.writelines(temp)
    read.close()
    w.close() 


def main():
    global PARAMS

    # Start an instance of ROSLAUNCH API 
    uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    roslaunch.configure_logging(uuid)

    # roslaunch hospitalMinimal.launch
    ## this starts our barebone environment
    cli_args1 = ['multi_robot', 'hospitalMinimal.launch']
    roslaunch_file1 = roslaunch.rlutil.resolve_launch_arguments(cli_args1)
    launch_files = [roslaunch_file1]
    roslaunch.parent.ROSLaunchParent(uuid, launch_files[0]).start()


    #Get simulation parameters
    with open(PATH+"/param/SIMULATION.yaml") as fp:
        PARAMS = yaml.full_load(fp)["td"]
    
    #Get Start Coordinates corresponding to positions
    with open(PATH+"/param/distance_params.yaml") as fp:
        DIST = yaml.full_load(fp)["world_nodes"]

    rviz_write() #Generate the appropriate rviz file
    rospy.sleep(1)

    AUC_ID = 0
    for robotType in PARAMS["types"]:
        for i in range (int(PARAMS[robotType]["count"])):
            x_pos =  DIST[PARAMS[robotType]["start"]]["x"]
            y_pos =  DIST[PARAMS[robotType]["start"]]["y"]

            cli_args2 = [PATH+'/launch/TD_roboLauncher.launch', 'tbName:='+robotType+str(i), 'x:='+str((i*0.5)+x_pos), 'y:='+str(y_pos)]
            print(cli_args2)
            roslaunch_file2 = roslaunch.rlutil.resolve_launch_arguments(cli_args2)[0]
            roslaunch_args2 = cli_args2[1:]
            launch_files.append([(roslaunch_file2, roslaunch_args2)])

            if(PARAMS[robotType]["isAuctioner"] == 1):
                rospy.set_param("/td/aucID/"+robotType+str(i), AUC_ID)
                AUC_ID+=1
    rospy.set_param("/td/auctioner_count", AUC_ID)
    parent = {}
    for id, val in enumerate(launch_files[1:]):
        print(val)
        parent[id] = roslaunch.parent.ROSLaunchParent(uuid, val)

        parent[id].start()


    print("\n\n\n\n\n\nLaunches Done\n\n\n\n\n\n")
    rospy.spin()


if __name__=='__main__':
    main()

