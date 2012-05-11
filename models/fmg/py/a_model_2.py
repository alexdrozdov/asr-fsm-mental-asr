#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
from sound_cmp import *

def main(argv=None):
    play = False
    plot = True
    filter  = False
    repeat = None
    noline = False
    ampl = None
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hpfr:nc:", ["help","play","filter","repeat","no-line","const-amplitude"])
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
        if o in ("-f","--filter"):
            filter = True
        if o in ("-r","--repeat"):
            repeat = int(a)
        if o in ("-n","--no-line"):
            noline = True
        if o in ("-c","--const-amplitude"):
            ampl = float(a)
    
    
    sm = SoundModel(44100, noline = noline, const_ampl = ampl)
    sm.add_sinus(
        {
            "time_start" : 0.0,
            "frequency" : 1180.0,
            "time" : 0.00310,
            "phase" : 160,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    
    sm.add_line(
        {
            "time_start" : 0.0,
            "points" : [(0.0,0.0), (0.002,-0.2), (0.00310, 0.0)],
            "interpolate" : "linear"
        })
    
    sm.add_sinus(
        {
            "time_start" : 0.003098,
            "frequency" : 1100.0,
            "time" : 0.00245,
            "phase" : 0,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    
    sm.add_line(
        {
            "time_start" : 0.00310,
            "points" : [(0.0,0.1), (0.00245-0.00001,0.5)],
            "interpolate" : "linear"
        })
    
    sm.add_sinus(
        {
            "time_start" : 0.00557,
            "frequency" : 980.0,
            "time" : 0.0032920,
            "phase" : 80.0,
            "offset" : 0.0,
            "ampl" : 0.3
        })
    
    sm.add_line(
        {
            "time_start" : 0.0055700,
            "points" : [(0.0,-0.2), (0.003,0.0)],
            "interpolate" : "linear"
        })
    
    
    sm.add_sinus(
        {
            "time_start" : 0.0088620,
            "frequency" : 1200.0,
            "time" : 0.0015280,
            "phase" : 180.0,
            "offset" : 0.0,
            "ampl" : 0.1
        })
    
    sm.add_line(
        {
            "time_start" : 0.0088620,
            "points" : [(0.0,0.1), (0.0015280,0.0)],
            "interpolate" : "linear"
        })
    
    
    
    if play:
        flt_params = scipy.signal.iirdesign(2.0*pi*1500.0/44100.0, 2.0*pi*1800.0/44100.0, 1, 30)
        sm.apply_filter(flt_params)
        wv = sm.generate(repeat_count = 800)
        wv.play(0.2)
    else:
        if filter:
            flt_params = scipy.signal.iirdesign(2.0*pi*1500.0/44100.0, 2.0*pi*1800.0/44100.0, 1, 30)
            sm.apply_filter(flt_params)
        
        if not repeat:
            repeat = 1
        
        wv = sm.generate(time_start = 0.0,repeat_count = repeat)
        wv_ref = music.WavSound("aa_2.wav")
        wp = WavPlotter()
        wp.add_wave(wv, offset=0.00733)
        wp.add_wave(wv_ref, label="reference")
        wp.plot()
    
    



if __name__ == "__main__":
    main()