#!/usr/bin/env python

import fastcluster as fc
from scipy.spatial.distance import pdist, squareform
import math
from swt_conv import swtt_state

def import_analize_modules():
    global numpy
    numpy      = __import__("numpy")
    global pylab
    pylab      = __import__("pylab")
    global pywt
    pywt       = __import__("pywt")
    global music
    music      = __import__("music")
    global wav_source
    wav_source = __import__("wav_source")
    global math
    math       = __import__("math")
    
class tree_entry:
    def __init__(self, x = None, left = None, right = None):
        self._left = left
        self._right = right
        self._parent = None;
        if x:
            self._xx = [x]
        else:
            self._xx = []
        
        if self._left:
            self._left._parent = self
            self._xx.extend(self._left._xx)
        if self._right:
            self._right._parent = self
            self._xx.extend(self._right._xx)
        self._average_x = numpy.mean(self._xx)
    def average_x(self):
        return self._average_x
    def left(self):
        return self._left
    def right(self):
        return self._right
    
class ClusterTree:
    def __init__(self, x_array, tree_matrix):
        leaf_arr = []
        for ii in range(x_array.shape[0]):
            leaf_arr.append(tree_entry(x = x_array[ii, 0]))
            
        for ii in range(tree_matrix.shape[0]):
            left_leaf = leaf_arr[int(tree_matrix[ii,0])]
            right_leaf = leaf_arr[int(tree_matrix[ii,1])]
            if None==left_leaf:
                print "error null left"
            if None==right_leaf:
                print "error null right"
            leaf_arr.append(tree_entry(left=left_leaf, right=right_leaf))
        
        leaf_arr.reverse()
        self._leaf_arr = leaf_arr
        self._groups = []
        
    def find_groups(self, distance, subtree = None):
        if None==subtree:
            subtree = self._leaf_arr[0]

        if None != subtree.left() and None != subtree.right():
            if abs(subtree.left().average_x() - subtree.right().average_x()) > distance:
                self.find_groups(subtree = subtree._left, distance = distance)
                self.find_groups(subtree = subtree._right, distance = distance)
                return
        self._groups.append(subtree.average_x())
    
    def sort_groups(self):
        self._groups.sort()
        
    def groups(self):
        return self._groups
            
    
class PointCluster:
    def __init__(self, file_name = None, extremums = None):
        if None != file_name:
            swtt_s = swtt_state(file_name)
            swtt_s.load()
            self.extremums = swtt_s.extremums
            return
        if None != extremums:
            self.extremums = extremums
            return
        raise "Neither file name nor extremums matrix specified"
    
    def cluster(self, cluster_count = None, cluster_radius = 10.0):
        x = numpy.matrix(self.extremums[1]).T
        nx = x.shape[0]
        D=pdist(x)
        l = fc.linkage(D,'single')
        l0 = numpy.hstack((x,x, numpy.zeros((nx,1)), numpy.ones((nx,1))))
            
        self._ct = ClusterTree(l0, l)
        self._ct.find_groups(cluster_radius)
        self._ct.sort_groups()
    def groups(self):
        return self._ct.groups()

    
def main(argv=None):
    import_analize_modules()
    pc = PointCluster(file_name = './a_o.store')
    pc.cluster()
    print pc.groups()


if __name__ == "__main__":
    main()
