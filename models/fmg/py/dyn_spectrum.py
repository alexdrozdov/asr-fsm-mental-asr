#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy
import pylab
import scipy, scipy.signal
from exceptions import ValueError
import music
import wav_source
import math
from math import pi, sin, cos
import time
from mpl_toolkits.mplot3d import Axes3D
import equal_loadness

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


class DynSpectrum:
    def __init__(self, samplerate, frequencies):
        self._frequencies = frequencies
        self._eql = equal_loadness.EqualLoadness(zero_freq=200)
        
    # Определение списка частот, нуждающихся в уточнении
    def preprocess(self, sound):
        pass
    
    def build(self, sound):
        #start = time.time()
        print "Построение динамического спектра..."
        sig_len = sound._sound.shape[0]
        self._sig_x = numpy.linspace(0, sig_len/sound._samplerate, sig_len)
        
        (b,a) = scipy.signal.iirdesign(5.0*pi*5.0/sound._samplerate, 2.0*pi*15.0/sound._samplerate, 1, 30)
        
        self._sig_mlt = {}
        self._sig_acc = {}
        self._sig_abs = {}
        self._sig_med = {}
        self._sig_dif = {}
        self._sig_step = {}
        
        cnt = 0
        nfreq = len(self._frequencies)
        self._catch_freq = []
        self._catch_freq_time = 7000
        for frequency in self._frequencies:
            sig_exp = numpy.e**(2*pi*1j*numpy.arange(sig_len)*frequency/sound._samplerate)
            self._sig_mlt[frequency] = sound._sound * sig_exp
            self._sig_acc[frequency] = numpy.add.accumulate(self._sig_mlt[frequency])
            self._sig_abs[frequency] = numpy.abs(self._sig_acc[frequency])
            self._sig_med[frequency] = scipy.signal.lfilter(b,a,self._sig_abs[frequency])
            self._sig_dif[frequency] = numpy.hstack((numpy.array(0), abs(numpy.diff(self._sig_med[frequency]))))
            #self._sig_step[frequency] = self._sig_dif[frequency] > (self._eql.get(frequency)*1200.0/(sound._samplerate))
            #self._sig_step[frequency] *= self._sig_dif[frequency]
            self._sig_step[frequency] = self._sig_dif[frequency]
            
            self._catch_freq.append(self._sig_dif[frequency][self._catch_freq_time])
            
            self._sig_mlt[frequency] = {}
            self._sig_acc[frequency] = {}
            self._sig_abs[frequency] = {}
            self._sig_med[frequency] = {}
            self._sig_dif[frequency] = {}
            
            cnt += 1
            if 0 == cnt%10:
                print "выполнено", cnt, "из",nfreq
        
    def plot_catched(self):
        pylab.subplot(2,1,1)
        pylab.plot(self._catch_freq)
        pylab.subplot(2,1,2)
        pylab.plot(numpy.convolve(self._catch_freq,numpy.array([-1,2,-1]),"valid"))
        pylab.show()
        
    def remove_short(self, min_time):
        print "Удаление случайных пиков..."
        self._sig_long_step = {}
        
        cnt = 0
        nfreq = len(self._frequencies)
        for frequency in self._frequencies:
            cur_sig = self._sig_step[frequency]
            state = 0
            start_point = 0
            l = cur_sig.shape[0]
            for ii in range(l):
                if state==0 and cur_sig[ii]:
                    state = 1
                    start_point = ii
                if state==1 and not cur_sig[ii]:
                    state = 0
                    #print ii-state
                    if ii-start_point < min_time:
                        cur_sig[start_point:ii] = 0
                    
            cnt += 1
            if 0 == cnt%10:
                print "выполнено", cnt, "из",nfreq
        
    def plot_abs(self):
        pylab.plot(self._sig_x, self._sig_abs)
        pylab.show()
        
    def find_frequency(self, freq):
        nearest_freq = self._frequencies[0]
        min_delta = abs(nearest_freq - freq)
        
        for frequency in self._frequencies:
            d = abs(frequency-freq)
            if d<min_delta:
                nearest_freq = frequency
                n=min_delta = d
                
        if nearest_freq!=freq:
            print "Запрошеная частота", freq, "не найдена. Используется", nearest_freq
        return nearest_freq
        
    def plot_filt(self, freq):
        nearest_freq = self.find_frequency(freq)
        pylab.plot(self._sig_x, self._sig_med[nearest_freq])
        pylab.show()
        
    def plot_diff(self, freq):
        nearest_freq = self.find_frequency(freq)
        pylab.plot(self._sig_x, self._sig_dif[nearest_freq])
        pylab.show()
        
    def plot_filt(self, freq):
        nearest_freq = self.find_frequency(freq)
        pylab.plot(self._sig_x, self._sig_med[nearest_freq])
        pylab.show()
        
    def plot_step(self, freq):
        nearest_freq = self.find_frequency(freq)
        pylab.plot(self._sig_x, self._sig_step[nearest_freq])
        pylab.show()
        
    def plot_step_2d(self):
        #Перекомпановываем данные в массив
        n = self._sig_step[self._frequencies[0]].shape[0]
        nn = n
        m = len(self._frequencies)
        step_2d = numpy.zeros((nn,m))
        for ii in range(m):
            step_2d[:,ii] = scipy.signal.resample(self._sig_dif[self._frequencies[ii]],nn)
            
        print step_2d.shape
            
        ax = Axes3D(pylab.figure())
        X = numpy.linspace(self._frequencies[0],self._frequencies[m-1],m)
        Y = numpy.arange(nn)
        X, Y = numpy.meshgrid(X, Y)
        ax.plot_surface(X, Y, step_2d)
        #pylab.plot_surface(step_2d)
        pylab.show()
    

class Attractor:
    def __init__(self, data, sample, freq):
        self._data = data
        self._len = data.shape[0]
        self._nfrq = data.shape[1]
        self._points = []
        self._last_sample_row = []
        
        self._first_sample = sample
        self._last_sample  = sample
        
        #Готовим первую строку данных
        self._data[sample,freq] = 0
        self._points.append((sample, freq))
        self._last_sample_row.append((sample, freq))
        self._look_left(sample, freq-1)
        self._look_right(sample, freq+1)
        self._zero_offset = 0
        
        #Формируем все остальные строки данных
        
        while len(self._last_sample_row):
            self._last_sample += 1
            prev_sample_row = self._last_sample_row
            self._last_sample_row = []
            for (s,f) in prev_sample_row:
                self._look_forward(s+1,f)
                
            if not len(self._last_sample_row):
                #Не удалось найти путь, примыкающий к последнему ряду. Попробуем попрыгать =)
                for jump in range(1,10):
                    for (s,f) in prev_sample_row:
                        self._look_forward(s+1+jump,f)
                    if len(self._last_sample_row):
                        break
    
    def set_zero_offset(self,v):
        self._zero_offset = v
          
    def area(self):
        return len(self._points)
        
    def length(self):
        return self._last_sample - self._first_sample
                
    def _look_forward(self, sample, freq):
        if sample >= self._len:
            return
        
        if self._data[sample,freq]:
            self._data[sample,freq] = 0
            self._points.append((sample, freq))
            
        self._look_left(sample, freq-1)
        self._look_right(sample, freq+1)
        
    def _look_left(self, sample, freq):
        if freq < 0:
            return
        if not self._data[sample,freq]:
            return
        
        self._data[sample,freq] = 0
        self._points.append((sample, freq))
        self._last_sample_row.append((sample, freq))
        self._look_left(sample, freq-1)
    
    def _look_right(self, sample, freq):
        if freq>=self._nfrq:
            return
        if not self._data[sample,freq]:
            return
        self._data[sample,freq] = 0
        self._points.append((sample, freq))
        self._last_sample_row.append((sample, freq))
        self._look_right(sample, freq+1)
        
    def conv_to_path(self):
        #Группируем точки по одинаковой абсциссе
        by_sample = {}
        for pn in self._points:
            try:
                sample = by_sample[pn[0]]
                sample.append(pn[1])
            except:
                by_sample[pn[0]] = [pn[1]]
        #Находим мат ожидание в каждой из групп
        
        self._path_x = numpy.arange(len(by_sample))
        self._path_y = numpy.zeros((len(by_sample,)))
        ii = 0
        for sample_x in by_sample.keys():
            self._path_x[ii] = sample_x
            sample_arr = by_sample[sample_x]
            self._path_y[ii] = numpy.average(sample_arr) + self._zero_offset
            ii += 1
            
    def conv_to_set(self):
        #Группируем точки по одинаковой абсциссе
        self._set_x = numpy.zeros((len(self._points),))
        self._set_y = numpy.zeros((len(self._points),))
        ii = 0
        for pn in self._points:
            self._set_x[ii] = pn[0]
            self._set_y[ii] = pn[1] + self._zero_offset
            ii += 1
    
    def get_path(self):
        return (self._path_x,self._path_y)
        
    def get_set(self):
        return (self._set_x,self._set_y)

class Attractors:
    def __init__(self):
        pass
    
    def search_attractors(self, dyn_spectrum):
        self._ds = dyn_spectrum
        self._min_freq = self._ds._frequencies[0]
        self._reshape()
        self._search_maximums()
        print "Поиск точек притяжения..."
        
        self._len  = self._2d.shape[0]
        self._nfrq = self._2d.shape[1]
        
        self._attractors = []
        
        for l in range(self._len):
            for f in range(self._nfrq):
                if self._2d[l,f]:
                    attr = Attractor(self._2d, l,f)
                    if attr.length() >= 500:
                        self._attractors.append(attr)
                        attr.set_zero_offset(self._ds._frequencies[0])
                        print "Аттрактор на частоте" , self._ds._frequencies[0]+f, "по смещению",l
                    
                    
        print "Обнаружено", len(self._attractors), "точек притежения"
    
    def _search_line_maximums(self, line):
        detect = numpy.array([-1,2,-1])
        line_conv = numpy.convolve(line, detect, "valid")
        
        line_maxs = []
        
        current_part = []
        in_sequence = False
        seq_start = 0
        for ii in range(len(line_conv)):
            v = line_conv[ii]
            if in_sequence and v>0:
                current_part.append(v)
                continue
            if in_sequence and v<=0:
                in_sequence = False
                max_ind = numpy.array(current_part).argmax() + seq_start
                if line[max_ind-2]<line[max_ind]>line[max_ind+2]:
                    line_maxs.extend([max_ind-2,max_ind-1, max_ind,max_ind+1,max_ind+2])

                current_part = []                
                continue
            if v>0 and not in_sequence:
                in_sequence = True
                seq_start = ii
                current_part.append(v)
                
        return line_maxs
    
    def _search_maximums(self):
        print "Поиск максимумов..."
        self._len  = self._2d.shape[0]
        self._nfrq = self._2d.shape[1]
        
        self._eql = equal_loadness.EqualLoadness()
        
        for l in range(self._len):
            line = numpy.array(self._2d[l,:])
            line_maxs = self._search_line_maximums(line)
            self._2d[l,:] = 0
            for lm in line_maxs:
                self._2d[l,lm] = line[lm] > (self._eql.get(lm+self._min_freq)*1100.0/44100.0)
                #print self._2d[l,:]
        #numpy.savetxt("2d.txt",self._2d)
        
        #pylab.plot(self._2d[:,284-self._min_freq])
        #pylab.show()
        
        
    
    def _reshape(self):
        n = self._ds._sig_step[self._ds._frequencies[0]].shape[0]
        m = len(self._ds._frequencies)
        self._2d = numpy.zeros((n,m))
        for ii in range(m):
            self._2d[:,ii] = self._ds._sig_step[self._ds._frequencies[ii]]
            
    def count(self):
        return len(self._attractors)
    
    def conv_to_path(self):
        if not len(self._attractors):
            return
        
        for attr in self._attractors:
            attr.conv_to_path()
    
    def plot_path(self):
        plot_cmd = "pylab.plot("
        for n in range(len(self._attractors)):
            plot_cmd   += "self._attractors[" + str(n) + "].get_path()[0],self._attractors[" + str(n) + "].get_path()[1],"

        plot_cmd = plot_cmd[0:-1] + ")"
        exec(plot_cmd)

        pylab.show()
        
    def conv_to_set(self):
        if not len(self._attractors):
            return
        
        for attr in self._attractors:
            attr.conv_to_set()
    
    def plot_set(self):
        plot_cmd = "pylab.plot("
        for n in range(len(self._attractors)):
            plot_cmd   += "self._attractors[" + str(n) + "].get_set()[0],self._attractors[" + str(n) + "].get_set()[1],'.',"

        plot_cmd = plot_cmd[0:-1] + ")"
        exec(plot_cmd)

        pylab.show()

    
    

def main():
    frq = range(80, 500)#(410, 420)
    #frq.extend(range(410,420))
    dyn_spectrum = DynSpectrum(44100, frq)#440.0*2.0**(-1.0/12.0)+5)
    wav_snd = wav_source.WavSource(
                    {"point":   p2c( { "phi": 0.0, "theta"   : 0, "L" : 10, "measure" : "deg"}),
                    "wavname"    : "a.wav",
                    "samplerate" : 44100})
    
    snd = music.WavSound(44100, wav_snd.wavdata[3000:26000]/32768.0) #[0:9000]
    #snd.plot_spectrum()
    
    pylab.figure()
    dyn_spectrum.build(snd)
    #dyn_spectrum.plot_catched()
    #dyn_spectrum.plot_step(440.0*2.0**(-1.0/12.0))
    #dyn_spectrum.remove_short(4000)
    #dyn_spectrum.plot_step(410)#440.0*2.0**(-2.0/12.0))
    #return
    #pylab.figure()
    attrs = Attractors()
    attrs.search_attractors(dyn_spectrum)
    if attrs.count():
        attrs.conv_to_path()
        attrs.plot_path()



if __name__ == "__main__":
    main()