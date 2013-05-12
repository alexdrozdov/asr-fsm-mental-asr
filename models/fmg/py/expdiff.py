#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import csv
import scipy.signal
from exceptions import ValueError

def import_analize_modules():
    global numpy
    numpy      = __import__("numpy")
    global pylab
    pylab      = __import__("pylab")
    math       = __import__("math")
    
def parse_options(argv = None):
    run_opts = {}
    run_opts["files"] = []
    run_opts["folders"] = []
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hf:d:", ["help","file","folder"])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
    
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print "help is undefined"
            sys.exit(0)
        if o in ("-f","--file"):
            run_opts["files"].append(a)
            
        if o in ("-d","--folder"):
            run_opts["folders"].append(a)
            
    run_opts["n_files"] = len(run_opts["files"])
    run_opts["n_folders"] = len(run_opts["folders"])
    
    if not run_opts["n_files"] and not run_opts["n_folders"]:
        raise ValueError("Требуется имя минимум одного обрабатываемого файла или каталога")
            
    return run_opts

def swt_range_scale(swt_mtx,range = None):
    max_val = numpy.max(numpy.max(swt_mtx))
    min_val = numpy.min(numpy.min(swt_mtx))
    swt_mtx_norm = (swt_mtx-min_val) / (max_val-min_val)
    return swt_mtx_norm

def swt_resize(mtx,new_size):
    tmp_sig = scipy.signal.resample(mtx,new_size[0], axis=0)
    tmp_sig = scipy.signal.resample(tmp_sig,new_size[1], axis=1)
    return tmp_sig

class ExpDiff:
    def __init__(self, filename):
        mtx = []
        with open(filename, 'rb') as csvfile:
            cvsreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in cvsreader:
                r = []
                for v in row[0:-1]:
                    r.append(float(v))
                mtx.append(r)
                
        mtx = numpy.matrix(mtx)
        print mtx
        pylab.imshow(swt_range_scale(swt_resize(mtx, mtx.shape)))
        pylab.show()
        return

def main(argv=None):
    run_opts = parse_options()
    import_analize_modules()
    if run_opts["n_folders"]:
        for folder in run_opts["folders"]:
            for files in os.listdir(folder):
                if files.endswith(".dat"):
                    run_opts["files"].append(os.path.join(folder, files))
                    
    run_opts["n_files"] = len(run_opts["files"])
    print "n_files =", run_opts["n_files"]
    ed = ExpDiff(run_opts["files"][0])

if __name__ == "__main__":
    main()