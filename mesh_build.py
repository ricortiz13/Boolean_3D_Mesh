## @author Ricardo Ortiz
#  @date April 20th, 2019
#
from parser_mesh import Parser_Mesh, STL_Parser

import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

class Mesh(object):
    def __init__(self, stl_file=None):
        self.all_vert = []
        self.triangles = []
        self.bounding_box_max = []
        self.bounding_box_min = []
        self.vertex_dict = dict()
        if stl_file != None:
            self.get_mesh(stl_file)
    
    ## Parse an stl file and extract mesh (triangles and vertices)
    #  @param stl_file File used to extract geometry/triangle data
    def get_mesh(self, stl_file):
        par = Parser_Mesh(stl_file)
        counter = 0
        triangle = []
        vertex = []
        mesh = []
        for line in par.get_raw_data():
            line = line.split(" ")
            if line[0] == "vertex":
                vertex.append(float(line[1]))
                vertex.append(float(line[2]))
                vertex.append(float(line[3].split('\n')[0]))
                self.all_vert.append(tuple(vertex))
                triangle.append(vertex)
                vertex = []
                counter+=1
            if counter >= 3:       
                mesh.append(triangle)
                triangle = []
                counter = 0

        #from https://www.w3schools.com/python/python_howto_remove_duplicates.asp
        self.all_vert = list(dict.fromkeys(self.all_vert))
        self.vertex_dict = dict((token,False) for token in self.all_vert)
        self.all_vert = np.array(self.all_vert)
    
        self.triangles = np.array(mesh)

        self.bounding_box_max = (np.amax(self.all_vert[:,0]), np.amax(self.all_vert[:,1]), np.amax(self.all_vert[:,2]))
        self.bounding_box_min = (np.amin(self.all_vert[:,0]), np.amin(self.all_vert[:,1]), np.amin(self.all_vert[:,2]))

        return self.triangles


    ## According to [3], equation is given by: n=(V1-V0)-cross-(V2-V0)
    def calculate_triangle_normal(self, triangle):
        dir = np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0])
        return dir/len(dir)

    # n_dot_(P1-P0)=0
    #Point A - Starter, the point within the mesh
    #Point B - End, the point outside the mesh
    #return bool intersection detected
    #return coordinate of where along the triangle plance the intersection occured
    def __segment_intersects_plane(self, triangle, pointA, pointB):
        P_i = pointA
        intersection_detected = False
        normal = self.calculate_triangle_normal(triangle)
        denominator = np.dot(normal,pointB - pointA)
        numerator = np.dot(normal,triangle[0]-pointA)
        
        if (denominator) != 0: #when 0, no intersect or either end of segment is on plane
            r = numerator/denominator
            if r>=0:
                intersection_detected = True
                P_i = pointA + r*(pointB)
        return intersection_detected, P_i

    def __point_within_triangle(self, triangle, point):

        u = triangle[1] - triangle [0]#1-0
        v = triangle[2] - triangle[0] #2-0
        w = point - triangle[0]

        denominator = np.square(np.dot(u,v)) - np.dot(u,u)*np.dot(v,v)

        s = np.dot(u,v)*np.dot(w,v) - np.dot(v,v)*np.dot(w,u)
        s=s/denominator

        t = np.dot(u,v)*np.dot(w,u) - np.dot(u,u)*np.dot(w,v)
        t = t/denominator

        within_triangle = float(((s>=0) and (t>=0) and (s+t<=1)))
        if within_triangle and ((s == 0) or (t == 0) or (s+t == 1)):
            within_triangle = 1.0
        return within_triangle

    ## Make sure at least one vector is uneven to disqualify. Check +- along major axis (max pos 6 checks)
    ## Return true when a coordinate exists within or on the boundary of
    #  a 3D mesh
    # Resource: http://geomalgorithms.com/a06-_intersect-2.html
    ## TODO add check to remove vertices
    def __point_within_mesh(self, point):
        within_mesh = True

        offset = (abs(self.bounding_box_min[-1])+abs(self.bounding_box_max[-1]))*100

        pos_x_check = np.array([point[0]+offset,point[1],point[2]])
        pos_y_check = np.array([point[0],point[1]+offset,point[2]])
        pos_z_check = np.array([point[0],point[1],point[2]+offset]) 

        neg_x_check = np.array([point[0]-offset,point[1],point[2]])
        neg_y_check = np.array([point[0],point[1]-offset,point[2]])
        neg_z_check = np.array([point[0],point[1],point[2]-offset])

        test_vectors = [pos_x_check, neg_x_check, pos_y_check, neg_y_check, pos_z_check, neg_z_check]

        for vector in test_vectors:
            intersection_counter = 0.0
            for triangle in self.triangles:
                intersects_plane, P_i = self.__segment_intersects_plane(triangle, point, vector)
                if intersects_plane and self.vertex_dict.get(tuple(P_i), True):
                    #intersection_counter += self.__point_within_triangle_real(triangle, P_i)
                    inter = self.__point_within_triangle(triangle, P_i)
                    #if inter==0.5: #TODO Does this save time/iterations? Answer: No. This if statement is negatively impacting results when
                    #    return (within_mesh) #TODO this if statement is accepting points
                    intersection_counter+=inter
            odd_num_of_intersections = intersection_counter%2.0 != 0
            if odd_num_of_intersections:
                return within_mesh

        return not(within_mesh)

    ## TODO remove triangles from input mesh
    ## TODO consider returning a new mesh
    def diff_mesh_real(self,mesh):
        diff = []
        diff_mesh = Mesh()
        

        for point in mesh.all_vert:
            
            if (self.vertex_dict.get(tuple(point), True) and not(self.__point_within_mesh(point))):
                diff.append(point)
        diff_mesh.set_triangles(mesh.triangles)
        diff_mesh.set_vertices(diff)
        return diff_mesh #np.array(diff)

    ## set new vertices
    def set_vertices(self, vert):
        vert_1 = []
        for ver in vert:
            vert_1.append(tuple(ver))
        self.all_vert = list(dict.fromkeys(vert_1))
        self.vertex_dict = dict((token,False) for token in self.all_vert)
        self.all_vert = np.array(self.all_vert)

        self.bounding_box_max = (np.amax(self.all_vert[:,0]), np.amax(self.all_vert[:,1]), np.amax(self.all_vert[:,2]))
        self.bounding_box_min = (np.amin(self.all_vert[:,0]), np.amin(self.all_vert[:,1]), np.amin(self.all_vert[:,2]))
        
        #update triangles
        new_triangles = []
        for triangle in self.triangles:
            counter = 0
            for point in triangle:
                if self.vertex_dict.get(tuple(point), True):
                    break
                else:
                    counter+=1
            if counter >= 3:
                new_triangles.append(triangle)
        self.triangles = np.array(new_triangles)

    def set_triangles(self, triangles):
        self.triangles = np.array(triangles)

if __name__=='__main__':
    model = Mesh('model.stl')
    scan = Mesh('scan.stl')

    fig = plt.figure() #[1]
    ax = fig.add_subplot(111, projection='3d')# [1]

    #ax.scatter3D(model.all_vert[:,0], model.all_vert[:,1], model.all_vert[:,2])
    #ax.add_collection3d(Poly3DCollection(model.triangles,facecolors='cyan', edgecolors='b', alpha=.5))

    #$$$
    diff_mesh = model.diff_mesh_real(scan)
    all_vert = diff_mesh.all_vert
    if len(all_vert)>0:
        #ax.scatter3D(all_vert[:,0], all_vert[:,1], all_vert[:,2])
        ax.add_collection3d(Poly3DCollection(diff_mesh.triangles,facecolors='yellow', edgecolors='orange', alpha=.5))
    else:
        print("No vert")
    #$$$
    #ax.scatter3D(scan.all_vert[:,0], scan.all_vert[:,1], scan.all_vert[:,2])
    #ax.add_collection3d(Poly3DCollection(scan.triangles,facecolors='yellow', edgecolors='b', alpha=.5))

    limit = 20
    ax.set_xlim([-limit, limit])
    ax.set_ylim([-limit, limit])
    ax.set_zlim([-limit, limit])
    plt.show()
