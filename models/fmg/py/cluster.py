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
    def __init__(self):
        self.left = None
        self.right = None
    
class PointCluster:
    def __init__(self, file_name):
        swtt_s = swtt_state(file_name)
        swtt_s.load()
        self.extremums = swtt_s.extremums
        #print self.extremums[0]
    
    def cluster(self, cluster_count = None, cluster_radius = None):
        x = numpy.matrix(self.extremums[0]).T
        nx = x.shape[0]
        #print x
        D=pdist(x)
        l = fc.linkage(D,'single')
        l0 = numpy.hstack((x,x, numpy.zeros((nx,1)), numpy.ones((nx,1))))
        l = numpy.vstack((l0,l))
        for i in range(l.shape[0]-1, nx-1, -1):
            print i, l[i,:]

    
def main(argv=None):
    import_analize_modules()
    pc = PointCluster('./a_o.store')
    pc.cluster()


if __name__ == "__main__":
    main()
