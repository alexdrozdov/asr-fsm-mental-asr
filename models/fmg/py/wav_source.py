#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import scipy, scipy.io.wavfile, scipy.signal
#import pylab

class WavSource:
    def __init__(self, src_config):
        self.common_delay = 0
        self.wavname = src_config["wavname"]
        
        try:
            self.point = src_config["point"]
        except:
            self.point = (0.0,0.0,0.0)
        try:
            self.requred_samplerate = src_config["samplerate"]
            self.resample = True
        except:
            self.requred_samplerate = 0
            self.resample = False
        
        (self.samplerate, self.wavdata) = scipy.io.wavfile.read(self.wavname)
        if len(self.wavdata.shape) > 1:
            self.wavdata = numpy.array(self.wavdata[:,0],dtype=float)
            
        self.length = self.wavdata.shape[0]
        
        if self.resample and self.samplerate!=self.requred_samplerate:
            #Необходима передискретизация
            resampled_samples = self.length*self.requred_samplerate/self.samplerate
            self.wavdata = scipy.signal.resample(self.wavdata, resampled_samples)
            self.samplerate = self.requred_samplerate
            self.length = resampled_samples
        
    def set_common_delay(self, delay):
        self.common_delay = delay
        
    def plot(self):
        pass
        #pylab.figure()
        #pylab.plot(self.wavdata)
        #pylab.show()