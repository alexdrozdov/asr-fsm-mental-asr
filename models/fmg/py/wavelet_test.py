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
            run_opts["level"] = a
            
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


def main(argv=None):
    run_opts = parse_options()
    
    import_analize_modules()
            
    swtt = SwtTransform(run_opts["wavelet"])
    
    f_cnt = 1
    for f_name in run_opts["files"]:
        swtt.transform(f_name,run_opts["level"])
        #swtt.transform_high(run_opts["level"])
        pylab.subplot(run_opts["n_files"],1,f_cnt)
        swtt.plot((1000,4000))
        f_cnt += 1
    
    pylab.show()



if __name__ == "__main__":
    main()

