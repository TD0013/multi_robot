import cv2
import matplotlib.pyplot as plt
import numpy as np
import yaml

with open("/home/td0013/catkin_ws/src/multi_robot/param/distance_params.yaml", 'r') as file1:
    points= yaml.safe_load(file1)

with open("/home/td0013/catkin_ws/src/multi_robot/map/hospital_map.yaml", 'r') as file2:
    map_desc = yaml.safe_load(file2)

img = cv2.imread("/home/td0013/catkin_ws/src/multi_robot/map/hospital_map.pgm")
asd = np.asarray(img)


nodes = {"origin":[asd.shape[0]+int(map_desc["origin"][1]/map_desc["resolution"]), asd.shape[1]+int(map_desc["origin"][0]/map_desc["resolution"])]}

for x in points["world_nodes"]:
    nodes[x] = [int(int(points["world_nodes"][str(x)]["x"])/map_desc["resolution"]),int(int(points["world_nodes"][str(x)]["y"])/map_desc["resolution"])]

# map=np.copy(asd)
# for i in range(-5,5):
#     for j in range(-5,5):
#         map[nodes["origin"][0]+i][nodes["origin"][1]+j] = [255,0,0]

# axis.imshow(map)

target = 2
z = 0
for x in nodes:
    if(z==target):
        map=np.copy(asd)
        for i in range(-10,10):
            for j in range(-10,10):
            # asd[nodes["origin"][0]+i][nodes["origin"][1]+j] = [255,0,0]
            # asd[nodes["origin"][0]-nodes["store_1"][1]+i][nodes["origin"][1]+nodes["store_1"][0]+j] = [255,0,0]
                try:
                    map[nodes["origin"][0]-nodes[str(x)][1]+i][nodes["origin"][1]+nodes[str(x)][0]+j] = [255,0,0]
                    plt.imshow(map)
                    plt.title(str(x))
                

                except:
                    print(x)

    else:
        z+=1
            # axis[z][0].set_title()

plt.show()

