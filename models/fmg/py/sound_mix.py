#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy
import pylab
import scipy, scipy.io.wavfile
from exceptions import ValueError
import music
import wav_source
import math
from math import pi, sin, cos

class SoundMix:
    def __init__(self):
        self._sounds = []
        self._max_time = 0
    
    def add_sound(self, time, sound, scale = 1.0):
        self._sounds.append((time, sound, scale))
        end_time = time + float(sound._sound.shape[0])/float(sound._samplerate)
        self._max_time = max(self._max_time,end_time)
    
    def generate(self, samplerate):
        #Сортируем по возрастанию времени начала звучания
        self._sounds.sort(cmp=lambda x,y: cmp(x[0],y[0]))
        
        data_len = int(math.ceil(self._max_time*samplerate))
        self._sound = numpy.zeros((data_len,))
        for snd in self._sounds:
            snd_start = int(snd[0]*samplerate)
            snd_end = snd_start + snd[1]._sound.shape[0]
            self._sound[snd_start:snd_end] = self._sound[snd_start:snd_end] + snd[1]._sound*snd[2]
            
        return music.WavSound(samplerate, self._sound)
        
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
    noize = wav_source.WavSource(
                    {"point":   p2c( { "phi": 0.0, "theta"   : 0, "L" : 10, "measure" : "deg"}),
                    "wavname"    : "metro.wav",
                    "samplerate" : 44100})
    
    wav_noize = music.WavSound(44100, noize.wavdata/32768.0)
    
    notelist = music.NoteList(1, 440.0*2.0**(-9.0/12.0), 2.0**(1.0/12.0), 40)
    
    int_0 = music.Interval("большая терция")
    int_1 = music.Interval("малая терция")
    int_2 = music.Interval("чистая квинта")
    
    acc_minor = notelist.build_accord((1,"F",), (int_1,int_2))
    acc_major = notelist.build_accord((1,"C",), (int_0,int_2))
    #acc_major2 = notelist.build_accord((1,"D",), (int_0,int_2))
    
    sound_minor = notelist.generate_accord(44100, 30000, acc_minor)
    sound_major = notelist.generate_accord(44100, 350000, acc_major)
    #sound_major2 = notelist.generate_accord(44100, 350000, acc_major2)
    
    #sound_minor.save("c_minor.wav")
    #sound_major.save("c_major.wav")
    
    snd_mix = SoundMix()
    snd_mix.add_sound(0, wav_noize,0.01)
    snd_mix.add_sound(2, sound_minor,0.4)
    snd_mix.add_sound(4, sound_minor,0.4)
    #snd_mix.add_sound(4, sound_major2,0.3)
    
    snd = snd_mix.generate(44100)
    
    pylab.figure()
    #snd.plot()
    #snd.play()
    snd.save("c_minor.wav")


if __name__ == "__main__":
    main()

