#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
from sound_cmp import *

def main(argv=None):
    play = False
    plot = True
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hp", ["help","play"])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print "help is undefined"
            sys.exit(0)
        if o in ("-p","--play"):
            play = True
    
    sm = SoundModel(44100)
    sm.add_sinus(
        {
            "time_start" : 0.0,
            "frequency" : 1150.0,
            "time" : 0.00329,
            "phase" : 160,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    
    sm.add_line(
        {
            "time_start" : 0.0,
            "points" : [(0.0,0.0), (0.002,-0.2), (0.00329, 0.0)],
            "interpolate" : "linear"
        })
    
    sm.add_sinus(
        {
            "time_start" : 0.00328999,
            "frequency" : 1200.0,
            "time" : 0.0022,
            "phase" : 0,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    
    sm.add_line(
        {
            "time_start" : 0.00330999,
            "points" : [(0.0,0.1), (0.0022-0.00001,0.6)],
            "interpolate" : "linear"
        })
    
    sm.add_sinus(
        {
            "time_start" : 0.00582,
            "frequency" : 1000.0,
            "time" : 0.003,
            "phase" : -180.0,
            "offset" : 0.0,
            "ampl" : 0.3
        })
    
    sm.add_line(
        {
            "time_start" : 0.00579,
            "points" : [(0.0,-0.2), (0.003,0.0)],
            "interpolate" : "linear"
        })
    
    sm.add_line(
        {
            "time_start" : 0.00889,
            "points" : [(0.0,0.0), (0.0015,0.0)],
            "interpolate" : "linear"
        })
    
    
    
    if play:
        flt_params = scipy.signal.iirdesign(2.0*pi*1500.0/44100.0, 2.0*pi*1800.0/44100.0, 1, 30)
        sm.apply_filter(flt_params)
        wv = sm.generate(repeat_count = 800)
        wv.play(0.2)
    else:
        wv = sm.generate(time_start = 0.00711,repeat_count = 1)#time_start = 0.00711,
        wv_ref = music.WavSound("aa_0.wav")
        wp = WavPlotter()
        wp.add_wave(wv)
        wp.add_wave(wv_ref, label="reference")
        wp.plot()
    
    



if __name__ == "__main__":
    main()