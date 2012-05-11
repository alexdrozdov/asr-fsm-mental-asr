#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import pylab
import math
import scipy, scipy.signal, scipy.interpolate

class EqualLoadness:
    def __init__(self, max_freq=15000.0, step=1.0, zero_freq = 200.0):
        self._def_x = numpy.array([20,  26.3, 33,    43,    58,    85,    158, 316,  1000, 1200, 2000, 2514, 3465, 4458, 5000, 6300,  7400,  9000, 10000, 11000, 12000, 13000, 15000])
        self._def_y = numpy.array([126, 120,  115.5, 111.4, 107.3, 103.6, 100, 96.4, 99,   100,  93.6, 90.4, 87.3, 90.4, 93.6, 100,   103.6, 104,  105,   106,   107,   108,   110])
        
        self._max_freq = min((max_freq, max(self._def_x)))
        self._min_freq = min(self._def_x)
        self._step = step
        
        self._resampled_size = int(math.ceil((self._max_freq-self._min_freq)/step))

        self._resampled_freq = numpy.linspace(0,self._max_freq-self._min_freq,self._resampled_size+1)+self._min_freq
        f = scipy.interpolate.interp1d(self._def_x, self._def_y,kind="cubic")
        self._resampled = f(self._resampled_freq)
        
        zero_val = f(zero_freq)
        self._resampled -= zero_val
        self._resampled = 10.0**(self._resampled/10.0)
        
        self._value_dict = {}
        for ii in range(len(self._resampled_freq)):
            self._value_dict[self._resampled_freq[ii]] = self._resampled[ii]

    
    def get(self, freq):
        return self._value_dict[freq]
    
    def plot(self):
        pylab.plot(self._resampled_freq, self._resampled) 
        pylab.show()


def main():
    pylab.figure()
    
    el = EqualLoadness()
    el.plot()
    



if __name__ == "__main__":
    main()