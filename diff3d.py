## @author Ricardo Ortiz
#  @date April 19th, 2019
#

import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

## Rotate matrix about x
#  @param m Matrix to be rotated
#  @param radians The desired rotation in radians
#  @return matrix Returns the transformed matrix
#
def rotateX (m, radians):
    # Rotation matrix about X axis as defined by Wolfram [2]
    rotationMatrix = np.array([[ 1, 0, 0],
                                [0, math.cos(radians), math.sin(radians)],
                                [0, -math.sin(radians), math.cos(radians)] ])

    # For each coordinate, transform according to rotation matrix
    for i in range(len(m)):
        m[i,:] = (rotationMatrix*(np.matrix(m[i,:])).transpose()).transpose()[0]
    
    return m

if __name__=='__main__':

    fig = plt.figure() #[1]
    ax = fig.add_subplot(111, projection='3d')# [1]

    pyramid_vert = np.array([[1,1,-1],
                            [-1,1,-1],
                            [-1,-1,-1],
                            [1,-1,-1],
                            [0,0,1]])
                            
    pyramid_vert_2 = rotateX(pyramid_vert, math.pi)
    
    ax.scatter3D(pyramid_vert[:,0], pyramid_vert[:,1], pyramid_vert[:,2])
    ax.scatter3D(pyramid_vert_2[:,0], pyramid_vert_2[:,1], pyramid_vert_2[:,2])

    plt.show()

## Resources
#
#1.   From matplot lib tutorials https://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html
#2.   Wolfram Math World http://mathworld.wolfram.com/RotationMatrix.html
#3.   