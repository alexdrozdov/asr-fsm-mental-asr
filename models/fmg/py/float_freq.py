#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import pylab
import math
import scipy.interpolate

import music
import sound_cmp
import  sound_mix

from math import pi, sin, cos
from exceptions import ValueError

class FloatFreq:
    def __init__(self, samplerate, freq):
        self._samplerate = samplerate
        self._freq = freq
    
    def generate(self, full_time = None, start_phase = 0.0, multiplex=False):
        #Формируем массив приращений фазы
        if full_time:
            nsamples = int(math.ceil(full_time*float(self._samplerate)))
            if multiplex:
                repeat_count = int(math.ceil(float(nsamples)/float(self._freq.shape[0])))
                self._freq = numpy.tile(self._freq, repeat_count)
            else:
                nsamples = min(nsamples, phase.shape[0])
        else:
            nsamples = phase.shape[0]
        
        phase_increment = 2.0*pi*self._freq/float(self._samplerate)
        phase = numpy.add.accumulate(phase_increment)
        
        sound = numpy.sin(phase[0:nsamples]+start_phase)
        return music.WavSound(self._samplerate, sound)
        


def main(argv=None):
    #pylab.figure()
    t = numpy.array([ 0.0171224, 0.0179351, 0.0189383, 0.0199415,
                     0.021578, 0.0225153, 0.0238988, 0.0250146, 0.0260113, 0.0269783, 0.0277816, 0.0286147, 0.0297156, 0.0307868,
                     0.0322149, 0.0332861, 0.0344316, 0.0355473, 0.0365441, 0.0375111, 0.0383442, 0.0391178, 0.0401442, 0.0412005,
                     0.0426733, 0.0439676, 0.045009, 0.0461545, 0.0471958, 0.0481628, 0.0489959, 0.0497695, 0.0508407, 0.0519713,
                     0.0533548, 0.0543813, 0.0556458, 0.0567765, 0.0577881, 0.05877, 0.0595138])#, 0.0603469])#, 0.0613585])#, 0.0624297])#,
                     #0.0641702, 0.065048, 0.0661489 ])
    
    #t = numpy.array([0.0111667, 0.012046, 0.0132493, 0.0143668, 0.0153319, 0.0163732,0.0171224, 0.0179351, 0.0189383, 0.0199415,
    #                 0.021578, 0.0225153, 0.0238988, 0.0250146, 0.0260113, 0.0269783, 0.0277816, 0.0286147, 0.0297156, 0.0307868,
    #                 0.0322149, 0.0332861, 0.0344316, 0.0355473, 0.0365441, 0.0375111, 0.0383442, 0.0391178, 0.0401442, 0.0412005,
    #                 0.0426733, 0.0439676, 0.045009, 0.0461545, 0.0471958, 0.0481628, 0.0489959, 0.0497695, 0.0508407, 0.0519713,
    #                 0.0533548, 0.0543813, 0.0556458, 0.0567765, 0.0577881, 0.05877, 0.0595138, 0.0603469])#, 0.0613585])#, 0.0624297])#,
    #                 #0.0641702, 0.065048, 0.0661489 ])
    
    l = t.shape[0]-1
    freq = (t-numpy.hstack((0, t[0:l])))**-1.0
    freq  = freq[1:]

    t = (t[1:]+t[0:-1])/2.0
    t_offs = t[0]
    t_min = t[0]
    t -= t_min
    t_min = 0.0
    t_max = max(t)
    
    f = scipy.interpolate.interp1d(t, freq,kind = "cubic")
    npoints = int((t_max-t_min)*44100.0)
    x = numpy.linspace(t_min, t_max, npoints)
    freq = f(x)
    
    wv_ref = music.WavSound("aaa_0.wav")
    
    #pylab.plot(freq)
    #pylab.show()
    ff = FloatFreq(44100, freq)
    wv_gen = ff.generate(full_time = wv_ref.time()*40, multiplex = True)
    
    s_carier = numpy.sin(2.0*pi*wv_gen.generate_timeline()*91.996)+numpy.sin(2.0*pi*wv_gen.generate_timeline()*91.996*2)+numpy.sin(2.0*pi*wv_gen.generate_timeline()*91.996*3)+numpy.sin(2.0*pi*wv_gen.generate_timeline()*91.996*4)
    wv_carrier = music.WavSound(44100,s_carier)
    
    smm = sound_mix.SoundMix()
    smm.add_sound(0,wv_carrier,0.1)
    smm.add_sound(0,wv_gen,0.2)
    
    wv_smm = smm.generate(44100)
    wv_smm.play(0.5)
    
    
    #wv_gen.play(0.2)
    #pylab.subplot(2,1,1)
    #ff.generate(multiplex=True).play(0.2)
    
    #pylab.subplot(2,1,1)
    #pylab.plot(x+t_offs,freq)
    #pylab.xlim(0.02, 0.06)
    #pylab.subplot(2,1,2)
    #wv_ref.plot(noshow = True)
    #pylab.xlim(0.02, 0.06)
    #pylab.show()
    
    
    wp = sound_cmp.WavPlotter()
    wp.add_wave(wv_ref)
    wp.add_wave(wv_smm,offset=0.0070200)
    wp.add_wave(music.WavSound(44100,freq/2000.0),offset=0.0070200)
    wp.plot()

if __name__ == "__main__":
    main()