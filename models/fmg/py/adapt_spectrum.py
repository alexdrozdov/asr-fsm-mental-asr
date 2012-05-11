#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import pylab
import scipy, scipy.signal
from exceptions import ValueError
import music
import wav_source
import math
import equal_loadness
from math import pi, sin, cos
from mpl_toolkits.mplot3d import Axes3D

class AdaptSpectrum:
    def __init__(self, samplerate, frequencies):
        self._samplerate = samplerate
        self._frequencies = frequencies
        self._eql = equal_loadness.EqualLoadness()
        #self._eql = equal_loadness.EqualLoadness(zero_freq=200)
        
    # Определение списка частот, нуждающихся в уточнении
    def preprocess(self, sound):
        pass
    
    def build(self, sound, step = 1):
        #start = time.time()
        print "Построение динамического спектра..."
        sig_len = sound._sound.shape[0]
        self._sig_x = numpy.linspace(0, float(sig_len)/float(sound._samplerate), sig_len)
        
        self._sig_acc = {}
        self._sig_abs = {}
        
        cnt = 0
        nfreq = len(self._frequencies)

        print "Расчет исходной матрицы спектра..."
        for frequency in self._frequencies:
            sig_exp = numpy.e**(2*pi*1j*numpy.arange(sig_len)*frequency/sound._samplerate)
            sig_mlt = sound._sound * sig_exp
            self._sig_acc[frequency] = numpy.add.accumulate(sig_mlt)
            
            cnt += 1
            if 0 == cnt%10:
                print "выполнено", cnt, "из",nfreq
              
        print "Подготовка матриц..."
        A_matrixes = {}
        cnt = 0
        for freq_cnt in range(nfreq):
            frequency = float(self._frequencies[freq_cnt])
            freq_period = 1.0 / frequency #Интервал времени для которого должна выполняться коррекция
            period_len = int(round(freq_period * sound.samplerate())) #Длительность интервала, за который должны браться H(w)
            
            t1 = 0.0
            t2 = self._sig_x[period_len-1]
            
            A = numpy.zeros((nfreq,nfreq),dtype=numpy.complex)
            for i in range(nfreq):
                wc = 2.0*pi*float(self._frequencies[i])
                for j in range(nfreq):
                    if i==j:
                        A[i,j] = t2-t1
                    else:
                        wcc = 2.0*pi*self._frequencies[j]
                        A[i,j] = -1j/(wcc-wc)*(numpy.e**(1j*(wcc-wc)*t2)-numpy.e**(1j*(wcc-wc)*t1))
            A_matrixes[frequency] = numpy.matrix(A).getI()
            cnt += 1
            if 0 == cnt%10:
                print "выполнено", cnt, "из",nfreq
                
                            
                            
        print "Коррекция матрицы..."
        self._corr_spectrum = numpy.zeros((sig_len,nfreq))
        for freq_cnt in range(nfreq):
            frequency = self._frequencies[freq_cnt]
            freq_period = 1.0 / frequency #Интервал времени для которого должна выполняться коррекция
            period_len = int(round(freq_period * sound.samplerate())) #Длительность интервала, за который должны браться H(w)
            
            A = A_matrixes[frequency]
            A_row = A[freq_cnt,:]

            for samp in range(period_len, sig_len):
                H = numpy.zeros((nfreq,1),dtype=numpy.complex)
                for i in range(nfreq):
                    sig_part = sound._sound[samp-period_len:samp]
                    sig_part -= numpy.mean(sig_part)
                    sig_exp = numpy.e**(2*pi*1j*numpy.arange(period_len)*float(self._frequencies[i])/sound._samplerate)
                    sig_mlt = sig_part * sig_exp
                    #H[i,0] = self._sig_acc[self._frequencies[i]][samp] - self._sig_acc[self._frequencies[i]][samp-period_len]
                    H[i,0] = numpy.sum(sig_mlt)
                #A_solve = numpy.dot(A,H)
                #self._corr_spectrum[samp,freq_cnt] = numpy.abs(A_solve[freq_cnt])
                self._corr_spectrum[samp,freq_cnt] = numpy.abs(numpy.dot(A_row, H))
                
            print "Расчет для частоты", frequency, "завершен"
            
            
    def build2(self, sound, step = 1):
        sig_len = sound._sound.shape[0]
        nfreq = len(self._frequencies)
        self._sig_x = numpy.linspace(0, float(sig_len)/float(sound._samplerate), sig_len)

        cnt = 0
        self._corr_spectrum = numpy.zeros((sig_len,nfreq))
        for freq_cnt in range(nfreq):
            frequency = float(self._frequencies[freq_cnt])
            freq_period = 3.0 / frequency #Интервал времени для которого должна выполняться коррекция
            period_len = int(round(freq_period * sound.samplerate())) #Длительность интервала, за который должны браться H(w)
            corr_x = self._sig_x[0:period_len]
            
            wnd = 0.54 - 0.46*numpy.cos(2*pi*numpy.arange(period_len)/period_len)
            samp_start = 0
            samp_stop = samp_start + period_len
            samp_center = period_len / 2
            for samp in range(0, sig_len-period_len):
                sig_part = numpy.array(sound._sound[samp_start:samp_stop])
                sig_part -= numpy.mean(sig_part)
                sig_part *= wnd
                self._corr_spectrum[samp_center,freq_cnt] = self._eql.get(frequency) * numpy.abs(numpy.sum(sig_part * corr_x) / float(period_len))
                samp_start += 1
                samp_stop  += 1
                samp_center += 1
            
            cnt += 1
            if 0 == cnt%10:
                print "выполнено", cnt, "из",nfreq

    def plot_2d(self, show_log = False):
        ax = Axes3D(pylab.figure())
        (n,m) = self._corr_spectrum.shape
        X = numpy.array(self._frequencies)
        Y = numpy.arange(n)
        X, Y = numpy.meshgrid(X, Y)
        print numpy.min(self._corr_spectrum)
        print numpy.max(self._corr_spectrum)

        #if show_log:
        #    ax.plot_surface(X, Y, numpy.log(self._corr_spectrum),cmap = pylab.spectral())#ax.plot_surface(X, Y, numpy.log(self._corr_spectrum))
        #else:
        #    ax.plot_surface(X, Y, self._corr_spectrum) #ax.plot_surface(X, Y, numpy.log(self._corr_spectrum))
        img = (self._corr_spectrum - numpy.min(self._corr_spectrum)) / (numpy.max(self._corr_spectrum) - numpy.min(self._corr_spectrum))
        img = numpy.log(img)
        print numpy.min(img)
        print numpy.max(img)
        pylab.imshow(img)
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

class IntenseArray:
    def __init__(self):
        self._arr = []
    
    def add(self,start, stop, step):
        self._arr.extend(numpy.arange(start, stop, step).tolist())
    
    def generate(self):
        uniq = {}
        for itm in self._arr:
            uniq[itm] = 1
        k = list(uniq.keys())
        k.sort()
        return k

def main():
    wv = music.WavSound("aaa-part-3.wav")
    
    ia = IntenseArray();
    #ia.add(205.0, 230.0, 2)
    #ia.add(360.0, 375.0, 2)
    #ia.add(305.0, 320.0, 2)
    ia.add(100.0, 5000.0, 5)
    
    #ia.add(205.0, 230.0, 5)
    #ia.add(360.0, 375.0, 5)
    #ia.add(80.0, 800.0, 30)
    #ia.add(800.0, 1200.0, 10.0)
    freqs = ia.generate()
    ads = AdaptSpectrum(wv.samplerate(), freqs)
    ads.build2(wv, 1)
    ads.plot_2d(show_log = True)



if __name__ == "__main__":
    main()