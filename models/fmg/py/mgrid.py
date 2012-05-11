#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import math
import numpy
import pylab
import scipy, scipy.signal
from numpy.fft import *
from math import sin, cos, pi, sqrt
from exceptions import ValueError

class Microphone:
    def __init__(self, x, y, samplerate):
        self.x = x
        self.y = y
        self.z = 0.0
        self._last_distance = 0.0;
        self.samplerate = samplerate
        self.timedelay = 0.0
        self.dig_delay = 0
    
    def print_position(self):
        print self.x,",",self.y,"\t",
        
    def print_timedelay(self):
        print str(self.timedelay)+"("+str(self.dig_delay)+")\t",
        
    def distance_to(self, point):
        x = point[0]
        y = point[1]
        z = point[2]
        self._last_distance = sqrt((x-self.x)**2.0 +(y-self.y)**2.0 +(z-self.z)**2.0 )
        return self._last_distance
    
    def last_distance(self):
        return self._last_distance
    
    # Установка задержки, необходимой для выравнивания фазового фронта
    def set_time_delay(self, delay):
        self.timedelay = delay
        self.dig_delay = int(round(delay*self.samplerate))
        
    def get_time_delay(self):
        return self.timedelay
    
    def receive_from(self, source):
        oversampled_frq = source[0].samplerate #Частота дискретизации сигнала
        full_sig_len = int(source[0].length*self.samplerate/oversampled_frq)
        sum_sig = numpy.zeros((full_sig_len,))
        for s in source:
            oversampled_sig = s.wavdata     #Сигнал с повышенной частотй дискретизации.
            src_delay = int(round((self.distance_to(s.point)/300.0)*oversampled_frq - s.common_delay))
            oversampled_sig = numpy.hstack((numpy.zeros((src_delay,)), oversampled_sig[0:oversampled_sig.shape[0]-src_delay]))
            mic_input_sig = scipy.signal.resample(oversampled_sig,full_sig_len)
            delay_sig = numpy.zeros((self.dig_delay,))
            sum_sig = sum_sig + numpy.hstack((delay_sig, mic_input_sig[0:full_sig_len-self.dig_delay]))
            
        self.signal = sum_sig
    
    def signal_length(self):
        return self.signal.shape[0]
    
    def eval_min_delay(self, source):
        min_dig_distance = float('inf')
        for s in source:
            dig_delay = (self.distance_to(s.point)/300.0)*self.samplerate
            min_dig_distance = min(dig_delay,min_dig_distance)
            
        return int(round(min_dig_distance))


class MicrophoneGrid:
    def __init__(self, grid_config):
        self.cols = grid_config["cols"]
        self.rows = grid_config["rows"]
        if self.cols < 1 or self.rows<1:
            raise ValueError("Нулевая ширина или высота микрофонной решетки")
        if self.cols>1:
            self.delta_x = grid_config["delta_x"]
        else:
            self.delta_x = 0
            
        if self.rows>1:
            self.delta_y = grid_config["delta_y"]
        else:
            self.delta_y = 0
        
        self.x = grid_config["x"]
        self.y = grid_config["y"]
        self.samplerate = grid_config["samplerate"]
        
        self.width  = (self.cols-1) * self.delta_x
        self.height = (self.rows-1) * self.delta_y
        
        self.microphones = range(self.rows)
        for i in range(self.rows):
            self.microphones[i] = range(self.cols)
            for j in range(self.cols):
                self.microphones[i][j] = Microphone(self.x+j*self.delta_x - self.width/2,
                                                    self.y+i*self.delta_y - self.height/2,
                                                    self.samplerate)
        
    def print_geometry(self):
        for r in self.microphones:
            for m in r:
                m.print_position()
            sys.stdout.write("\n")
            
    def print_focus_delays(self):
        for r in self.microphones:
            for m in r:
                m.print_timedelay()
            sys.stdout.write("\n")
    
    # Установка координаты начальной точки микрофонной решетки
    def set_position(self, x, y):
        pass
    
    # Установка направления к нормали антенной решетки
    def set_grid_orientation(self, u, v):
        pass
    
    # Фокусировка решетки на выбранной точке пространства
    def focus_direction(self, point):
        L0     = point["L"]
        phi    = point["phi"]
        theta  = point["theta"]
        
        #Положение конца вектора относительно центра решетки
        px = cos(pi/2.0 - phi) * L0;
        py = sin(pi/2.0 - phi) * L0 * sin(theta);
        pz = sin(pi/2.0 - phi) * L0 * cos(theta);
        
        max_delay = 0.0
        for r in self.microphones: # Определяем максимальную задержку распространения
            for m in r:
                L = m.distance_to((px, py, pz)) # Расстояние от микрофона до точки
                t = L / 300.0                # Задержка распространения сигнала
                max_delay = max(max_delay,t)
                
        for r in self.microphones: # Устанавливаем всем элементам задержки, выравнивающие
            for m in r:            # время прохождения сигнала от источника до выхода
                t = m.last_distance() / 300.0
                m.set_time_delay(max_delay - t)
    
    # Прием сигнала из указанных источников. Источников может быть несколько.
    def receive_from(self, source):
        #Оцениваем минимальную задержку распространения сигнала от всех источников
        #до всех микрофонов.
        min_dig_delay  = float('inf')
        for r in self.microphones:
            for m in r:
                min_dig_delay = min(m.eval_min_delay(source), min_dig_delay)
                
        min_dig_delay = max(min_dig_delay-1,0)

        #Устанавливаем вычисленную минимальную задержку для всех источников. Её следуеи
        #считать минимальной и вычитать из всех задержек
        for s in source:
            s.set_common_delay(min_dig_delay)
            
        #Все микрофоны принимают сигнал
        min_received_len = float('inf')
        for r in self.microphones:
            for m in r:
                m.receive_from(source)
                min_received_len = min(m.signal_length(), min_received_len)

        self.signal = numpy.zeros((min_received_len,))
        for r in self.microphones:
            for m in r:
                self.signal = self.signal+m.signal[0:min_received_len]

    # Спектр выходного сигнала
    def spectrum(self):
        sig_len = self.signal.shape[0]
        wnd = 0.54 - 0.46*numpy.cos(2*pi*numpy.arange(sig_len)/sig_len)
        fft_orig = fftshift(fft(self.signal*wnd))/sig_len
        fft_freq = numpy.linspace(-self.samplerate/2, self.samplerate/2, sig_len);
        return {"x":fft_freq, "y":fft_orig}
    
    # Разность спектров между выходным сигналом и сигналом на микрофоне, принятом за опорный
    def diff_spectrum(self, ref_mic):
        ref_signal = self.microphones[ref_mic[0]][ref_mic[1]].signal
        min_sig_len = min(ref_signal.shape[0], self.signal.shape[0])
        wnd = 0.54 - 0.46*numpy.cos(2*pi*numpy.arange(min_sig_len)/min_sig_len)
        fft_sum  = fftshift(fft(self.signal[0:min_sig_len]*wnd))/min_sig_len
        fft_ref = fftshift(fft(ref_signal[0:min_sig_len]*wnd))/min_sig_len
        fft_rel  = (fft_sum / fft_ref).real
        fft_freq = numpy.linspace(-self.samplerate/2, self.samplerate/2, min_sig_len);
        return {"x":fft_freq, "y":fft_rel}
    
    # Спектр по направлениям на основании выходного сигнала и сигнала, принятого за опорный
    def dir_spectrum(self, ref_mic):
        diff_fft = self.diff_spectrum(ref_mic)["y"].real
        diff_fft -= numpy.mean(diff_fft)
        
        sig_len = self.diff_spectrum(ref_mic)["x"].shape[0]
        x = numpy.linspace(0.0, self.samplerate,sig_len)
        
        npoints = 200 #Количество точек в анализируемой полосе частот
        max_fft_freq = (self.delta_x*self.samplerate/300.0)*1.15 #Максимальная частота колебаний отношения спектров
                                                                 #Множитель 1.05 добавлен чтобы чуточку расширить полосу
        fft_freq = numpy.linspace(0.0,max_fft_freq, npoints)
        spectrum_dir = numpy.zeros((npoints,))
        for i in range(npoints):
            spectrum_dir[i] = abs(numpy.sum(diff_fft*numpy.e**(-2*numpy.pi*1j/self.samplerate*fft_freq[i]*x)))/sig_len

        fft_delta = fft_freq*300.0/self.samplerate
        fft_angle = self.delta_l_to_alpha(fft_delta)
        return {"x":fft_angle, "y":spectrum_dir}
    
    # Получение сигнала на выбранном микрофоне
    def get_partial_signal(self, microphone):
        pass
    
    # Функция преобразования разности хода фазового фронта в направление на источник звука
    def delta_l_to_alpha(self, delta):
        S = self.delta_x
        L = 10 #FIXME Должно задаваться в виде параметра
        cos_alpha = ((S**2/4.0+L**2)**2-(S**2/4.0+L**2-delta**2/2)**2)**0.5/(S*L)
        alpha = 90.0 - numpy.arccos(cos_alpha) * 180.0/pi
        return alpha
    
    # Получение просуммированного и сфазированного сигнала
    def get_sum_signal(self):
        pass
    
    
    