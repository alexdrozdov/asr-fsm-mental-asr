#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import scipy.signal
import pickle
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
    run_opts["save"] = []
    run_opts["restore"] = []
    run_opts["wavelet"] = "db2"
    run_opts["level"] = 10
    run_opts["exact"] = False
    run_opts["plot"] = False
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hf:w:l:s:r:xp", ["help","file","wavelet","level", "save", "reload"])
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
            
        if o in ("-r","--restore"):
            run_opts["restore"].append(a)
            
        if o in ("-s","--save"):
            run_opts["save"].append(a)
            
        if o in ("-w","--wavelet"):
            run_opts["wavelet"] = a
            
        if o in ("-l","--level"):
            run_opts["level"] = int(a)
            
        if o in ("-x","--exact"):
            run_opts["exact"] = True
            
        if o in ("-p","--plot"):
            run_opts["plot"] = True
            
    run_opts["n_files"] = len(run_opts["files"])
    run_opts["n_save"] = len(run_opts["save"])
    run_opts["n_restore"] = len(run_opts["restore"])
    if not run_opts["n_restore"]:
        if not run_opts["n_files"]:
            raise ValueError("Требуется имя минимум одного обрабатываемого файла")
        if run_opts["n_save"]>0 and run_opts["n_save"]!=run_opts["n_files"]:
            raise ValueError("Для сохранения результатов обработки необходимо указать файл с результатами по каждому входному файлу")
            
    return run_opts

class swtt_state:
    def __init__(self, file_name, sig=None, edges=None, crosses=None, extremums=None):
        self.file_name = file_name
        self.sig = sig
        self.edges = edges
        self.crosses = crosses
        self.extremums = extremums
        
    def save(self):
        with open(self.file_name, 'w') as f:
            pickle.dump(self, f)
            
    def load(self):
        with open(self.file_name, 'r') as f:
            tmp_swtt = pickle.load(f)
            self.sig = tmp_swtt.sig
            self.edges = tmp_swtt.edges
            self.crosses = tmp_swtt.crosses
            self.extremums = tmp_swtt.extremums

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
        
    def plot_edges(self):
        pylab.imshow(numpy.flipud(self.edges+ self.tmp_sig*0.1))
        
    def plot_extremums(self):
        pylab.imshow(numpy.flipud(self.crosses + self.tmp_sig*0.1))
    
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
        a = numpy.copy(img)
        b = numpy.copy(pattern)
        a[a==0] = -1
        b[b==0] = -1
        a[a>0] = 1
        b[b>0] = 1
        max_peak = numpy.prod(b.shape)
        
        c = scipy.signal.correlate(a, b, 'valid')
        
        overlaps = numpy.where(c == max_peak)
        crosses[overlaps] = 1.0
        #print overlaps
    
    def save_extremums(self, file_name, complete=False):
        if complete:
            swtt_s = swtt_state(file_name, self.tmp_sig, self.edges, self.crosses, self.extremums)
        else:
            swtt_s = swtt_state(file_name, extremums=self.extremums)
        swtt_s.save()
        
    def load_extremums(self, file_name):
        swtt_s = swtt_state(file_name)
        swtt_s.load()
        self.tmp_sig = swtt_s.sig
        self.edges = swtt_s.edges
        self.crosses = swtt_s.crosses
        self.extremums = swtt_s.extremums
    
    def find_edges(self, sig):
        sz = sig.shape
        tmp_min = numpy.zeros(sz)
        tmp_max = numpy.zeros(sz)
        
        sig_v1 = numpy.vstack((numpy.zeros((1, sz[1])), sig[0:sz[0]-1, :]))
        sig_v2 = numpy.vstack((numpy.zeros((2, sz[1])), sig[0:sz[0]-2, :]))
        sig_v3 = numpy.vstack((sig[1:sz[0], :], numpy.zeros((1, sz[1]))))
        sig_v4 = numpy.vstack((sig[2:sz[0], :], numpy.zeros((2, sz[1]))))
        positive_v1 = numpy.int32((sig - sig_v1)>0)
        positive_v2 = numpy.int32((sig - sig_v2)>0)
        positive_v3 = numpy.int32((sig - sig_v3)>0)
        positive_v4 = numpy.int32((sig - sig_v4)>0)
        max_v = numpy.int32((positive_v1 + positive_v2 + positive_v3 + positive_v4)==4)
        negative_v1 = numpy.int32((sig - sig_v1)<0)
        negative_v2 = numpy.int32((sig - sig_v2)<0)
        negative_v3 = numpy.int32((sig - sig_v3)<0)
        negative_v4 = numpy.int32((sig - sig_v4)<0)
        min_v = numpy.int32((negative_v1 + negative_v2 + negative_v3 + negative_v4)==4)
        
        sig_h1 = numpy.hstack((numpy.zeros((sz[0],1)), sig[:,0:sz[1]-1]))
        sig_h2 = numpy.hstack((numpy.zeros((sz[0],2)), sig[:,0:sz[1]-2]))
        sig_h3 = numpy.hstack((sig[:,1:sz[1]], numpy.zeros((sz[0],1))))
        sig_h4 = numpy.hstack((sig[:,2:sz[1]], numpy.zeros((sz[0],2))))
        positive_h1 = numpy.int32((sig - sig_h1)>0)
        positive_h2 = numpy.int32((sig - sig_h2)>0)
        positive_h3 = numpy.int32((sig - sig_h3)>0)
        positive_h4 = numpy.int32((sig - sig_h4)>0)
        max_h = numpy.int32((positive_h1 + positive_h2 + positive_h3 + positive_h4)==4)
        negative_h1 = numpy.int32((sig - sig_h1)<0)
        negative_h2 = numpy.int32((sig - sig_h2)<0)
        negative_h3 = numpy.int32((sig - sig_h3)<0)
        negative_h4 = numpy.int32((sig - sig_h4)<0)
        min_h = numpy.int32((negative_h1 + negative_h2 + negative_h3 + negative_h4)==4)
        
        tmp_min = numpy.fmax(min_v, min_h);
        tmp_max = numpy.fmax(max_v, max_h);
        return (tmp_min, tmp_max)
        
    def find_crosses(self, sig):
        tmp_crosses = numpy.zeros(sig.shape)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0],[1,1,1],[0,1,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[1,0,1],[0,1,0],[1,0,1]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,0,1,0],[0,1,1,1],[1,1,0,0],[0,1,0,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0,0],[1,1,0,0],[0,1,1,1],[0,0,1,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0,0],[1,1,1,0],[0,0,1,1],[0,0,1,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,0,1,0],[0,0,1,1],[1,1,1,0],[0,1,0,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0],[0,1,1],[1,1,0],[0,1,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0],[1,1,0],[0,1,1],[0,1,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,0,1,0],[1,1,1,1],[0,1,0,0]]), tmp_crosses)
        self.find_cross_pattern(sig, numpy.matrix([[0,1,0,0],[1,1,1,1],[0,0,1,0]]), tmp_crosses)
        return tmp_crosses
    
    def find_extremums(self, alternate_size):
        self.tmp_sig = self.swt_resize(alternate_size)
        (tmp_min, tmp_max) = self.find_edges(self.tmp_sig)
        self.edges = tmp_min + tmp_max*2.0
        self.crosses = self.find_crosses(tmp_min) + self.find_crosses(tmp_max)
        self.extremums = numpy.nonzero(self.crosses)

def main(argv=None):
    run_opts = parse_options()
    import_analize_modules()
    swtt = SwtTransform(run_opts["wavelet"])
    f_cnt = 1
    
    if run_opts["n_restore"]:
        for f_name in run_opts["restore"]:
            swtt.load_extremums(f_name)
            pylab.subplot(run_opts["n_restore"]*2,1,f_cnt*2-1)
            swtt.plot_edges()
            pylab.subplot(run_opts["n_restore"]*2,1,f_cnt*2)
            swtt.plot_extremums()
            f_cnt += 1
            
        if run_opts["plot"]:
            pylab.show()
        return
        
    for f_name in run_opts["files"]:
        swtt.transform(f_name,run_opts["level"])
        swtt.find_extremums((350,1000))
        pylab.subplot(run_opts["n_files"]*2,1,f_cnt*2-1)
        swtt.plot_edges()
        pylab.subplot(run_opts["n_files"]*2,1,f_cnt*2)
        swtt.plot_extremums()
        if run_opts["n_save"]>0:
            swtt.save_extremums(run_opts["save"][f_cnt-1], complete=run_opts["exact"])

        f_cnt += 1
    
    if run_opts["plot"]:
        pylab.show()



if __name__ == "__main__":
    main()

