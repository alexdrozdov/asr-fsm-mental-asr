#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import scipy.signal
from exceptions import ValueError

def import_analize_modules():
    global numpy
    numpy      = __import__("numpy")
    global pylab
    pylab      = __import__("pylab")
    global pywt
    pywt       = __import__("pywt")
    global music
    music      = __import__("music")
    global wav_source
    wav_source = __import__("wav_source")
    global math
    math       = __import__("math")
    
def parse_options(argv = None):
    run_opts = {}
    run_opts["files"] = []
    run_opts["wavelet"] = "db2"
    run_opts["level"] = 10
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hf:w:l:", ["help","file","wavelet","level"])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
    
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print "help is undefined"
            sys.exit(0)
        if o in ("-f","--file"):
            run_opts["files"].append(a)
            
        if o in ("-w","--wavelet"):
            run_opts["wavelet"] = a
            
        if o in ("-l","--level"):
            run_opts["level"] = int(a)
            
    run_opts["n_files"] = len(run_opts["files"])
    if not run_opts["n_files"]:
        raise ValueError("Требуется имя минимум одного обрабатываемого файла")
    
    return run_opts

class SwtTransform:
    def __init__(self,family):
        self._family = family
        self._wavelet = pywt.Wavelet(self._family)
    
    def transform(self, filename, max_level = None):
        self._wv = music.WavSound(filename)
        self._original_len = self._wv.length()
        self._factor2_len  = int(2**math.ceil(math.log(self._original_len,2)))
        self._wv.extend(self._factor2_len)
        self._max_level = pywt.swt_max_level(self._factor2_len)
        if max_level and self._max_level>max_level:
            self._max_level = max_level
        print "Количество уровней детализации", self._max_level
        
        self._wvl = pywt.swt(self._wv._sound, self._wavelet, self._max_level)
        self.list2matrix()
        
    def transform_high(self, max_level = None):
        self._wv = music.WavSound(44100,numpy.copy(self._swt_matrix[0,:]))
        self._original_len = self._wv.length()
        self._factor2_len  = int(2**math.ceil(math.log(self._original_len,2)))
        self._wv.extend(self._factor2_len)
        self._max_level = pywt.swt_max_level(self._factor2_len)
        if max_level and self._max_level>max_level:
            self._max_level = max_level
        
        self._wvl = pywt.swt(self._wv._sound, self._wavelet, self._max_level)
        self.list2matrix()
    
    def plot(self, plot_size = None, range = None):
        if None==plot_size:
            plot_size = self._swt_matrix.shape
        pylab.imshow(numpy.flipud(
            self.swt_range_scale(
                self.swt_resize(plot_size),
                range
                )
            ))
    
    def list2matrix(self):
        m = len(self._wvl)
        n = min(self._wvl[0][1].shape[0],self._original_len)
        self._swt_matrix = numpy.zeros((m,n))
        for r_cnt in range(m):
            for c_cnt in range(n):
                self._swt_matrix[r_cnt,c_cnt] = self._wvl[r_cnt][1][c_cnt]
    
    def swt_resize(self,new_size):
        tmp_sig = scipy.signal.resample(self._swt_matrix,new_size[0], axis=0)
        tmp_sig = scipy.signal.resample(tmp_sig,new_size[1], axis=1)
        return tmp_sig
        
    def swt_range_scale(self,swt_mtx,range = None):
        max_val = numpy.max(numpy.max(swt_mtx))
        min_val = numpy.min(numpy.min(swt_mtx))
        swt_mtx_norm = (swt_mtx-min_val) / (max_val-min_val)
        if not range:
            range = (0,1)
        swt_mtx_exc = numpy.copy(swt_mtx_norm)
        swt_mtx_exc[swt_mtx_norm < range[0]] = range[0]
        swt_mtx_exc[swt_mtx_norm > range[1]] = range[1]
        
        max_val = numpy.max(numpy.max(swt_mtx_exc))
        min_val = numpy.min(numpy.min(swt_mtx_exc))
        return (swt_mtx_exc-min_val) / (max_val-min_val)
        
    def find_cross_pattern(self, img, pattern, crosses):
        pattern_sum = numpy.sum(pattern)
        pattern_h = pattern.shape[0]
        pattern_w = pattern.shape[1]
        for i in range(img.shape[0]-pattern_w):
            for j in range (img.shape[1]-pattern_h):
                part_sum = numpy.sum(numpy.multiply(pattern,img[i:i+pattern_h,j:j+pattern_w]))
                if part_sum==pattern_sum:
                    crosses[i,j] = 1.0
                    img[i:i+20,j:j+20] = 0.0
                    j += 20
    
    def find_max(self, alternate_size):
        tmp_sig = self.swt_resize(alternate_size)
        tmp_min = numpy.zeros(tmp_sig.shape)
        tmp_max = numpy.zeros(tmp_sig.shape)
        for i in range(2,alternate_size[0]-2):
            for j in range (2,alternate_size[1]-2):
                if tmp_sig[i,j]<=tmp_sig[i,j-1] and tmp_sig[i,j]<=tmp_sig[i,j+1] and tmp_sig[i,j]<=tmp_sig[i,j-2] and tmp_sig[i,j]<=tmp_sig[i,j+2]:
                    tmp_min[i,j] = 1.0
                else:
                    if tmp_sig[i,j]<=tmp_sig[i-1,j] and tmp_sig[i,j]<=tmp_sig[i+1,j] and tmp_sig[i,j]<=tmp_sig[i-2,j] and tmp_sig[i,j]<=tmp_sig[i+2,j]:
                        tmp_min[i,j] = 1.0
                if tmp_sig[i,j]>=tmp_sig[i,j-1] and tmp_sig[i,j]>=tmp_sig[i,j+1] and tmp_sig[i,j]>=tmp_sig[i,j-2] and tmp_sig[i,j]>=tmp_sig[i,j+2]:
                    tmp_max[i,j] = 1.0
                else:
                    if tmp_sig[i,j]>=tmp_sig[i-1,j] and tmp_sig[i,j]>=tmp_sig[i+1,j] and tmp_sig[i,j]>=tmp_sig[i-2,j] and tmp_sig[i,j]>=tmp_sig[i+2,j]:
                        tmp_max[i,j] = 1.0
                    
        pylab.subplot(2,1,1)
        pylab.imshow(numpy.flipud(tmp_min + tmp_max*2.0 + tmp_sig*0.1))
        
        tmp_crosses_min = numpy.zeros(tmp_sig.shape)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0],[1,1,1],[0,1,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[1,0,1],[0,1,0],[1,0,1]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,0,1,0],[0,1,1,1],[1,1,0,0],[0,1,0,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0,0],[1,1,0,0],[0,1,1,1],[0,0,1,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0,0],[1,1,1,0],[0,0,1,1],[0,0,1,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,0,1,0],[0,0,1,1],[1,1,1,0],[0,1,0,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0],[0,1,1],[1,1,0],[0,1,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0],[1,1,0],[0,1,1],[0,1,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,0,1,0],[1,1,1,1],[0,1,0,0]]), tmp_crosses_min)
        self.find_cross_pattern(tmp_min, numpy.matrix([[0,1,0,0],[1,1,1,1],[0,0,1,0]]), tmp_crosses_min)
        #self.find_cross_pattern(tmp_min, numpy.matrix([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]), tmp_crosses_min)
        tmp_crosses_max = numpy.zeros(tmp_sig.shape)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0],[1,1,1],[0,1,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[1,0,1],[0,1,0],[1,0,1]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,0,1,0],[0,1,1,1],[1,1,0,0],[0,1,0,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0,0],[1,1,0,0],[0,1,1,1],[0,0,1,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0,0],[1,1,1,0],[0,0,1,1],[0,0,1,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,0,1,0],[0,0,1,1],[1,1,1,0],[0,1,0,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0],[0,1,1],[1,1,0],[0,1,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0],[1,1,0],[0,1,1],[0,1,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,0,1,0],[1,1,1,1],[0,1,0,0]]), tmp_crosses_max)
        self.find_cross_pattern(tmp_max, numpy.matrix([[0,1,0,0],[1,1,1,1],[0,0,1,0]]), tmp_crosses_max)
        #self.find_cross_pattern(tmp_max, numpy.matrix([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]), tmp_crosses_max)
        
        pylab.subplot(2,1,2)
        pylab.imshow(numpy.flipud(tmp_crosses_min + tmp_crosses_max + tmp_sig*0.1))
        


def main(argv=None):
    run_opts = parse_options()
    
    import_analize_modules()
            
    swtt = SwtTransform(run_opts["wavelet"])
    
    f_cnt = 1
    for f_name in run_opts["files"]:
        swtt.transform(f_name,run_opts["level"])
        #swtt.transform_high(run_opts["level"])
        #pylab.subplot(run_opts["n_files"]*3,1,f_cnt)
        swtt.plot((350,1000))
        swtt.find_max((350,1000))
        f_cnt += 1
    
    pylab.show()



if __name__ == "__main__":
    main()

