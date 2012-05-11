#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import pylab
import math
import scipy.interpolate
import random

import music
import sound_cmp
import  sound_mix


def main(argv=None):
    w = {}
    w[0] = music.WavSound("aaa-part.wav")
    w[1] = music.WavSound("aaa-part-2.wav")
    w[2] = music.WavSound("aaa-part-3.wav")
    sm = sound_mix.SoundMix()
    n = 100
    freq = 97.0
    last_time = 0.0
    for ii in range(n):
        r = random.random()
        if r < 0.3:
            wn = 1
        elif r > 0.7:
            wn = 0
        else:
            wn = 2
            
        wn = 2
        #sm.add_sound(1/freq*ii+random.random()*5.0408e-5*0,w[0], 0.90 + math.sin(float(ii)/3)*0)
        sm.add_sound(last_time,w[wn], 0.90 + math.sin(float(ii)/3)*0)
        last_time += w[wn].time()
        
    wv_merge = sm.generate(44100)
    #wv_merge.play(0.2)
    wv_merge.save("aaa-3-pm.wav")

if __name__ == "__main__":
    main()