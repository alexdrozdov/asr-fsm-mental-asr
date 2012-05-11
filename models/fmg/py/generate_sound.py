#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
import numpy
import pylab
import scipy, scipy.io.wavfile
import os
from math import pi

import pylab

def generate_sound(sound_spec):
    samplerate = sound_spec["samplerate"]
    time = sound_spec["time"]
    frequencies = sound_spec["frequencies"]
    ampl = 1.0
    phase = 0.0
    
    save_to_file = False
    try:
        filename    = sound_spec["filename"]
        save_to_file = True
    except:
        pass
        
    n_freq = len(frequencies)
    sig_len = int(time*samplerate)
    
    x = numpy.arange(0,sig_len)
    snd = numpy.zeros((sig_len,))
    for frq in frequencies:
        snd = snd+ampl*numpy.sin(2*x*pi*frq/samplerate + phase*pi/180.0)
        
    snd /= n_freq
    
    snd = math.e**(snd+1)
    snd -= numpy.mean(snd)
    snd /= numpy.max(snd)
        
    if save_to_file:
        scipy.io.wavfile.write(filename,samplerate,numpy.int16(snd*32767.0))
    else:
        return snd



def main():
    
    start_freq = 440.0
    stop_freq  = 880.0
    delta_freq = 10.0
    
    count = int((stop_freq-start_freq)/delta_freq)
    
    #for ii in range(count):
    #    freq = start_freq + ii*delta_freq
    #    print freq
    snd = generate_sound( {
            "samplerate" : 96000,
            "time" : 2.0,
            "frequencies" : (440, 460),
            "filename" : "beat_20.wav"
        })
    
        #os.popen("aplay gen100.wav")
    
    #pylab.figure()
    #pylab.plot(snd)    
    #pylab.show()
    
if __name__ == "__main__":
    main()