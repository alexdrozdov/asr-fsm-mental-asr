#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import swt_conv
import pickle
import numpy
import pylab
import cluster

class BaseExtremumPoint:
    def __init__(self, global_coords, probability, is_max = False):
        self._global_coords = global_coords
        self._probability = probability
        self._ref_probabilities = []
        self._is_max = is_max
        
    def append_ref_probability(self, probability):
        self._ref_probabilities.append(probability)
        
    def recalculate_probability(self):
        self._ref_probabilities.append(self._probability)
        self._probability = numpy.mean(self._ref_probabilities)
        self._ref_probabilities = []
        
class RefExtremumPoint:
    def __init__(self, base_extremum, ref_coords):
        self._base_point = base_extremum
        self._ref_coords = ref_coords
        self._probability = self._base_point._probability
        self._point_is_fine = False #Наличие точки снижает вероятность применения шаблона, а не увеличивает ее
        
    def eval_fine(self, signal, x, update_probability = False, update_as_fine = False):
        check_coords = numpy.array([self._ref_coords[0], self._ref_coords[1]+x])
        if not self._point_is_fine:
            if check_coords[1]<0 or check_coords[1]>=len(signal[1]):
                if update_probability:
                    self._probability *= 0.95
                return self._probability
            
            sub_sig = signal[check_coords[0],check_coords[1]-20:check_coords[1]+20]
            if numpy.sum(sub_sig) < 1:
                if update_probability:
                    self._probability *= 0.95
                return self._probability
            
            sh = sub_sig.shape[0]
            sub_x = numpy.arange(sh)-sh/2.0
            signal_mean = abs(numpy.mean(numpy.multiply(sub_sig, sub_x)))
            fine = self._probability * signal_mean/10.0
            return fine
        else:
            if check_coords[1]<0 or check_coords[1]>=len(signal[1]):
                return 0.0
            sub_sig = signal[check_coords[0],check_coords[1]-20:check_coords[1]+20]
            if numpy.sum(sub_sig) < 1:
                return 0.0
            sh = sub_sig.shape[0]
            sub_x = numpy.arange(sh)-sh/2.0
            signal_mean = abs(numpy.mean(numpy.multiply(sub_sig, sub_x)))
            fine = self._probability - self._probability * signal_mean/10.0
            return fine
    
    def update_base_probability(self):
        self._base_point.append_ref_probability(self._probability)
        
    def copy_base_probability(self):
        self._probability = self._base_point._probability

class ExtremumSequence:
    def __init__(self, base_extremum):
        self._base_extremum = base_extremum
        self._ref_extremums = []
        self._hit_count = 0
        self._hit_pattern = []
    
    def add_extremum(self, ref_extremum):
        self._ref_extremums.append(ref_extremum)
        
    def apply(self, high_extremums, low_extremums, x, update_probability = False, update_as_fine = False):
        fine = 0.0
        for ep in self._ref_extremums:
            if ep._base_point._is_max:
                #print "applying as max"
                f = ep.eval_fine(high_extremums, x, update_probability, update_as_fine)
                fine += f
                #print "fine:", f
            else:
                #print "applying as min"
                f = ep.eval_fine(low_extremums, x, update_probability, update_as_fine)
                fine += f#ep.eval_fine(low_extremums, x, update_probability, update_as_fine)
                #print "fine:", f
        return fine
    
    def update_base_probabilities(self):
        for ep in self._ref_extremums:
            ep.update_base_probability()
            
    def copy_base_probabilities(self):
        for ep in self._ref_extremums:
            ep.copy_base_probability()
    
    def print_means(self):
        arr = []
        for ep in self._ref_extremums:
            arr.append(ep._signal_mean)
        print arr

class ExtremumTemplate:
    def __init__(self, name = None, swt_max_scale = None):
        if name and swt_max_scale:
            self._name = name
            self._swt_width = swt_max_scale
            self._base_extremums = []
            self._scale_handlers = []
            for i in range (swt_max_scale):
                self._scale_handlers.append([])
            self._sequences = []
        else:
            self._name = None
            self._swt_width = None
            self._base_extremums = []
            self._scale_handlers = []
            self._sequences = []
    
    #Добавить новую точку к массиву точек, анализируемых шаблоном
    def add_extremum(self, base_extremum):
        self._base_extremums.append(base_extremum)
    
    #Построить шаблон по выбранной базовой точке. Координаты остальных точек будут построены относительно нее
    def rebuild(self):
        for be in self._base_extremums:
            #Определяем, к какому масштабу должен относиться этот массив
            scale = be._global_coords[0]
            if scale<0 or scale>=self._swt_width:
                print "Scale", scale, "is out of range for width", self._swt_width
                continue
            scale_handlers = self._scale_handlers[scale]
            #Строим массив с относительными координатами точек
            ex_sequence = ExtremumSequence(be)
            scale_handlers.append(ex_sequence)
            self._sequences.append(ex_sequence)
            for ex in self._base_extremums:
                ref_coords = numpy.array([ex._global_coords[0], ex._global_coords[1] - be._global_coords[1]]);
                ex_sequence.add_extremum(RefExtremumPoint(ex, ref_coords))
                
    def apply(self, high_extremums, low_extremums, x):
        scales = numpy.nonzero(high_extremums[:, x])[0]
        print scales
        min_fine = len(high_extremums[0])
        base_extremum = None
        best_sequence = None
        for scale in scales:
            scale_handlers = self._scale_handlers[scale]
            for ex_sequence in scale_handlers:
                print "applying at", x
                fine = ex_sequence.apply(high_extremums, low_extremums, x)
                if min_fine > fine:
                    min_fine = fine
                    base_extremum = ex_sequence._base_extremum
                    best_sequence = ex_sequence
        if base_extremum and min_fine < 16:
            start_x = x-base_extremum._global_coords[1]
            best_sequence.apply(high_extremums, low_extremums, x, True)
            best_sequence._hit_count += 1
        else:
            start_x = None
        return (min_fine, start_x)
    
    def recalculate_probabilities(self):
        for se in self._sequences:
            se.update_base_probabilities()
        for be in self._base_extremums:
            be.recalculate_probability()
        for se in self._sequences:
            se.copy_base_probabilities()
            
    def save(self, file_name):
        with open(file_name, 'w') as f:
            pickle.dump(self, f)
            
    def load(self, file_name):
        with open(file_name, 'r') as f:
            tmp_et = pickle.load(f)
            self._name = tmp_et._name
            self._swt_width = tmp_et._swt_width
            self._base_extremums = tmp_et._base_extremums
            self._scale_handlers = tmp_et._scale_handlers
            self._sequences = tmp_et._sequences
            
    def print_hit_count(self):
        for se in self._sequences:
            print se._base_extremum._global_coords, ":", se._hit_count
       
class TemplateFinder:
    def __init__(self):
        self._templates = []
        self._template_x = {}
    
    def add_template(self, template):
        self._templates.append(template)
        self._template_x[template._name] = []
        
    def find_xextremums(self):
        self._swtt.transform(self._file_name, self._max_levels)
        xedges = self._swtt.find_xedges()
        xedges_min = xedges[0]
        edge_coords = numpy.nonzero(xedges_min)
        edge_values = self._swtt._swt_matrix[edge_coords]
        edge_median = numpy.median(edge_values)
        edges_min = numpy.multiply(self._swtt._swt_matrix<=edge_median, xedges_min)
        edges_min[7:,:] = 0
        
        xedges_max = xedges[1]
        edge_coords = numpy.nonzero(xedges_max)
        edge_values = self._swtt._swt_matrix[edge_coords]
        edge_median = numpy.median(edge_values)
        edges_max = numpy.multiply(self._swtt._swt_matrix>=edge_median, xedges_max)
        edges_max[7:,:] = 0
        
        return (edges_min, edges_max)
        
    def analize_file(self, file_name):
        self._swtt = swt_conv.SwtTransform("db2")
        self._file_name = file_name
        self._max_levels = 9
        self._edges = self.find_xextremums()

        edges = self._edges[1]
        edge_coords = numpy.copy(numpy.nonzero(edges)[1])
        edge_coords.sort()
        print edge_coords
        for coord in edge_coords:
            print "coord=", coord
            for etb in self._templates:
                cur_template_x = self._template_x[etb._name]
                res = etb.apply(self._edges[1], self._edges[0], coord)
                if None != res[1]:
                    cur_template_x.append(res[1])
        
    def get_template_x(self):
        return self._template_x
    
    def get_cluster_groups(self, template_name):
        pc = cluster.PointCluster(xpoints = numpy.matrix(self._template_x[template_name]))
        pc.cluster(cluster_radius = 100)
        pg = pc.groups()
        return pg
        
    def recalculate_probabilities(self):
        for etb in self._templates:
            etb.recalculate_probabilities()
            
    def print_hit_count(self):
        for etb in self._templates:
            etb.print_hit_count()