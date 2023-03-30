#!/usr/bin/env python3
import roslaunch
import rospy
import rospkg
import yaml


# Get Path for multi_robot Pkg and declare global variabel PARAMS
rospack = rospkg.RosPack()
rospy.init_node('driverNode')
PATH = rospack.get_path('multi_robot')

#Get simulation parameters
with open(PATH+"/param/SIMULATION.yaml") as fp:
    PARAMS = yaml.full_load(fp)["td"]

#Get Start Coordinates corresponding to positions
with open(PATH+"/param/distance_params.yaml") as fp:
    DIST = yaml.full_load(fp)["world_nodes"]

# The function to write the vizualization file as per out current simulation
def rviz_write():
    # Part 1: Write a non changing piece for an rviz file
    read = open(PATH+"/rviz/part1", "r")
    w = open(PATH+"/rviz/temp2.rviz","w")
    temp = read.readlines()

    w.writelines(temp)
    read.close()

    # Part 2: Read the part that we will change to visualize the number of robots we need
    read = open(PATH+"/rviz/temp.rviz", "r")
    temp = read.readlines()
    read.close()

    # Write for part 2
    for robotType in PARAMS["types"]:
        for i in range (int(PARAMS[robotType]["count"])):
            for j in temp:
                k = j.replace("robot1", robotType+str(i))
                w.writelines(k)
    
    # Part 3: Write some more constant lines for rviz files
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
    ## this starts our barebone environment and initilizes a list which stores all files we need to launch
    cli_args1 = ['multi_robot', 'hospitalMinimal.launch']
    roslaunch_file1 = roslaunch.rlutil.resolve_launch_arguments(cli_args1)
    launch_files = [roslaunch_file1]
    roslaunch.parent.ROSLaunchParent(uuid, launch_files[0]).start()

    rviz_write() #Generate the appropriate rviz file per the SIMULATION.yaml file
    rospy.sleep(1)

    AUC_ID = 0 # We will use this to assign unique auctioner IDs to robots that are able to become an auctioner

    for robotType in PARAMS["types"]: # For each type of robots
        for i in range (int(PARAMS[robotType]["count"])): # For each robot of that type (given by the count in SIMULATION.yaml)

            # Get coordinates for the start node of the robot
            x_pos =  DIST[PARAMS[robotType]["start"]]["x"]
            y_pos =  DIST[PARAMS[robotType]["start"]]["y"]

            # Add the launch file for that robot in the list and prepare for launch
            cli_args2 = [PATH+'/launch/TD_roboLauncher.launch', 'tbName:='+robotType+str(i), 'x:='+str((i*0.5)+x_pos), 'y:='+str(y_pos)]
            roslaunch_file2 = roslaunch.rlutil.resolve_launch_arguments(cli_args2)[0]
            roslaunch_args2 = cli_args2[1:]
            launch_files.append([(roslaunch_file2, roslaunch_args2)])
            
            # This assigns the next AUC_ID to the robot we are spawning right now
            if(PARAMS[robotType]["isAuctioner"] == 1):
                rospy.set_param("/td/aucID/"+robotType+str(i), AUC_ID)
                AUC_ID+=1
        
    # Get the total number of auctioners in the environment (is used when round robin auctioning)
    rospy.set_param("/td/auctioner_count", AUC_ID)

    # Finally launch all the commands we have in the list
    parent = {}
    for id, val in enumerate(launch_files[1:]):
        print(val)
        parent[id] = roslaunch.parent.ROSLaunchParent(uuid, val)
        parent[id].start()

    # If this node closes, everything shuts down, so we let it sleep instead
    rospy.spin() 


if __name__=='__main__':
    main()

