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
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hpfr:", ["help","play","filter","repeat"])
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
    
    sm = SoundModel(44100)
    
    # Часть №1
    sm.add_sinus(
        {
            "time_start" : 0.0,
            "frequency" : 1120.0,
            "time" : 0.0013393,
            "phase" : 0,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    sm.add_sinus(
        {
            "time_start" : 0.0013393,
            "frequency" : 940.0,
            "time" : 0.002,
            "phase" : 180.0,
            "offset" : 0.0,
            "ampl" : 0.08
        })
    sm.add_line(
        {
            "time_start" : 0.0,
            "points" : [(0.0,0.0), (0.002,-0.1), (0.00510, 0.0)],
            "interpolate" : "linear"
        })
    sm.add_sinus(
        {
            "time_start" : 0.003098,
            "frequency" : 1100.0,
            "time" : 0.00245,
            "phase" : 0,
            "offset" : 0.0,
            "ampl" : 0.08*0
        })
    #sm.add_line(
    #    {
    #        "time_start" : 0.00310,
    #        "points" : [(0.0,0.1), (0.00245-0.00001,0.5)],
    #        "interpolate" : "linear"
    #    })
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
        wv_ref = music.WavSound("aaa_0.wav")
        wp = WavPlotter()
        wp.add_wave(wv, offset=0.00731)
        wp.add_wave(wv_ref, label="reference")
        wp.plot()
    
    t = [0.0111667, 0.012046, 0.0132493, 0.0143668, 0.0153319, 0.0163732,0.0171224, 0.0179351, 0.0189383, 0.0199415 0.021578 0.0225153 0.0238988 0.0250146 0.0260113 0.0269783 0.0277816 0.0286147 0.0297156 0.0307868 0.0322149 0.332861 0.0344316 0.0355473 0.0365441 0.0375111 0.0383442 0.0391178 0.0401442 0.0412005 0.0426733 0.0439676 0.045009 0.0461545 0.0471958 0.0481628 0.0489959 0.0497695 0.0508407 0.0519713 0.0533548 0.0543813 0.0556458 0.0567765 0.0577881 0.05877 0.0595138 0.0603469 0.0613585 0.0624297 0.0641702 0.065048 0.0661489 ]
plot(1./(t - [0 t(1:52)]))



if __name__ == "__main__":
    main()