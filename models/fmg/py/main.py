#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy.fft import *
import pylab
from mgrid import *
from wav_source import *

def p2c(point):
    try:
        angle_measure = point["measure"]
    except:
        angle_measure = "rad"
    
    phi = point["phi"]
    theta = point["theta"]
    L = point["L"]
    
    if "deg"==angle_measure:
        phi *= pi/180.0
        theta *= pi/180.0
    
    px = cos(pi/2.0 - phi) * L;
    py = sin(pi/2.0 - phi) * L * sin(theta);
    pz = sin(pi/2.0 - phi) * L * cos(theta);
    return (px, py,pz)

def main():
    gconfig = {"x"       : 0.0,
               "y"       : 0.0,
               "cols"    : 2,
               "rows"    : 1,
               "delta_x" : 0.2,
               "delta_y" : 0.2,
               "samplerate" : 44100}
    
    mg = MicrophoneGrid(gconfig)
    print "Расположение микрофонов"
    mg.print_geometry()
    
    mg.focus_direction({"phi": 0.0*pi/180.0, "theta":0.0, "L": 10.0})
    
    print "Корректирующие задержки"
    mg.print_focus_delays()
    
    ws_0 = WavSource({"point":   p2c( { "phi"     : 30.0,
                                        "theta"   : 0,
                                        "L"       : 10,
                                        "measure" : "deg"}),
                    "wavname"    : "hello.wav",
                    "samplerate" : 44100*5})
    
    ws_1 = WavSource({"point":   p2c( { "phi"     : 25.0,
                                        "theta"   : 0,
                                        "L"       : 10,
                                        "measure" : "deg"}),
                    "wavname"    : "bye.wav",
                    "samplerate" : 44100*5})
    
    mg.receive_from((ws_0,ws_1))

    
    pylab.figure()
    
    pylab.subplot(3,1,1)
    fft_sum = mg.spectrum()
    pylab.plot(fft_sum["x"], numpy.log(fft_sum["y"]))

    pylab.subplot(3,1,2)
    fft_diff = mg.diff_spectrum((0,0))
    pylab.plot(fft_diff["x"], fft_diff["y"])
    print len(fft_diff["y"])
    
    pylab.subplot(3,1,3)
    fft_dir = mg.dir_spectrum((0,0))
    pylab.plot(fft_dir["x"], fft_dir["y"])
    
    pylab.show()
    
if __name__ == "__main__":
    main()