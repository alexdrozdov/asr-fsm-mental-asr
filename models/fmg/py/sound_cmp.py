#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import pylab
import math
import scipy.interpolate

import wav_source
import music
import sound_mix

from math import pi, sin, cos
from exceptions import ValueError

class SoundModelPart:
    def __init__(self, part_spec):
        self._time_start = part_spec["time_start"]
    
    def generate(self, samplerate):
        print "Нереализован метод generate()"

class SoundModelSin(SoundModelPart):
    def __init__(self, part_spec):
        SoundModelPart.__init__(self,part_spec)
        self._freq = part_spec["frequency"]
        self._time = 0
        try:
            self._time = part_spec["time_end"]-self._time_start
        except:
            try:
                self._time = part_spec["time"]
            except:
                raise ValueError("Не задана длительность сигнала. Необходимы параметры time_end или time")
        
        if self._time < 0:
            raise ValueError("Отрицательная длительность сигнала")
        
        try:
            self._phase = part_spec["phase"]
        except:
            self._phase = 0
        try:
            self._offset = part_spec["offset"]
        except:
            self._offset = 0
        try:
            self._ampl = part_spec["ampl"]
        except:
            self._ampl = 1.0
        
            
    def generate(self, samplerate):
        npoints = int(math.ceil(self._time * samplerate))
        wave = numpy.sin(2*pi*self._freq*numpy.arange(npoints)/float(samplerate) + self._phase*pi/180.0) * self._ampl + self._offset
        wav_sound = music.WavSound(samplerate,wave)
        return wav_sound

class SoundModelLine(SoundModelPart):
    def __init__(self, part_spec):
        SoundModelPart.__init__(self,part_spec)
        self._points = part_spec["points"]
        self._points_x = []
        self._points_y = []
        prev_px = -10e-10
        for p in self._points:
            px = p[0]
            py = p[1]
            if px <= prev_px:
                raise ValueError("Точка " + str(p) + "имеет недопустимую координату. Координаты должны возрастать")
            prev_px = px
            self._points_x.append(px)
            self._points_y.append(py)
        
        self._max_x = px    
        
        try:
            self._interpolate = part_spec["interpolate"]
        except:
            self._interpolate = "linear"
    
    def generate(self, samplerate):
        f = scipy.interpolate.interp1d(self._points_x, self._points_y,kind=self._interpolate)
        npoints = int(math.floor((self._max_x-self._points_x[0]) * float(samplerate)))
        x = numpy.linspace(self._points_x[0], self._max_x, npoints+1)
        wave = f(x)
        if self._points_x[0]>0:
            trailing_zeros = numpy.zeros((int(self._points_x[0]*samplerate),))
            wave = numpy.hstack((trailing_zeros, wave))
        wav_sound = music.WavSound(samplerate,wave)
        return wav_sound

class SoundModel:
    def __init__(self, samplerate, time_start = 0.0, noline = False, const_ampl = None):
        self._parts = []
        self._samplerate = samplerate
        self._sm = sound_mix.SoundMix()
        self._time_start = time_start
        self._flt_params = None
        self._noline = noline
        self._const_ampl = const_ampl
    
    def add_sinus(self, sin_spec):
        if self._const_ampl:
            sin_spec["ampl"] = self._const_ampl
        self._parts.append(SoundModelSin(sin_spec))
    
    def add_line(self, line_spec):
        if self._noline:
            return
        self._parts.append(SoundModelLine(line_spec))
        
    def apply_filter(self, params):
        self._flt_params = params
    
    def generate(self, time_start = 0.0, repeat_count = 1):
        time_start += self._time_start
        
        for p in self._parts:
            self._sm.add_sound(p._time_start+time_start,p.generate(self._samplerate))
        
        ws = self._sm.generate(self._samplerate)
        ws.repeat(repeat_count)
        if self._flt_params:
            ws.apply_filter(self._flt_params)
        return ws

class WavPlotter:
    def __init__(self):
        pylab.figure()
        self._waves = []
        self._max_time = 0.0
        
    def add_wave(self, wave, label=None, offset=0.0):
        self._waves.append((wave,label, offset))
        self._max_time = max(self._max_time, wave.time())
        
    def plot(self):
        plot_cmd = "pylab.plot("
        for ii in range(len(self._waves)):
            w_ref = "self._waves["+ str(ii) + "]"
            plot_cmd += w_ref+"[0].generate_timeline()+" + w_ref+ "[2], " + w_ref + "[0]._sound,"
        
        plot_cmd = plot_cmd[0:-1] + ")"
        exec(plot_cmd)
        pylab.show()

def main():
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
    
    
    flt_params = scipy.signal.iirdesign(2.0*pi*1500.0/44100.0, 2.0*pi*1800.0/44100.0, 1, 30)
    #sm.apply_filter(flt_params)
    wv = sm.generate(time_start = 0.00732,repeat_count = 1)#time_start = 0.00711,
    #wv.play(0.2)
    
    
    
    
    wv_ref = music.WavSound("aa_2.wav")
    wp = WavPlotter()
    wp.add_wave(wv)
    wp.add_wave(wv_ref, label="reference")
    wp.plot()
    
    
    #wav_snd = {}
    #snd_x = {}
    #snd_y = {}
    #
    #time_offset = [0.00075, 0.00068, 0.0006, 0.00045, 0.0, 0.00005]
    #
    #plot_cmd = "pylab.plot("
    #
    #for ii in range(2):
    #    wav_snd[ii] = wav_source.WavSource(
    #                    {"point":   p2c( { "phi": 0.0, "theta"   : 0, "L" : 10, "measure" : "deg"}),
    #                    "wavname"    : "aa_"+str(ii)+".wav",
    #                    "samplerate" : 44100})
    #    snd_y[ii] = music.WavSound(44100, wav_snd[ii].wavdata/32768.0)
    #    snd_x[ii] = numpy.linspace(0, float(snd_y[ii]._sound.shape[0]) / float(snd_y[ii]._samplerate), snd_y[ii]._sound.shape[0])  + time_offset[ii]
    #    
    #    plot_cmd += "snd_x["+str(ii)+"], snd_y["+str(ii)+"]._sound," #
    #    
    #plot_cmd = plot_cmd[0:-1]+")"
    #exec(plot_cmd)
    #pylab.show()
        
    



if __name__ == "__main__":
    main()