#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import numpy
import pylab
import swt_conv
import swt_template
import cluster

from exceptions import ValueError

def print_help():
    print "-n --name         - Название или идентификатор шаблона"
    print "-r --ref-file     - Опорный файл, по которому должен быть построен шаблон"
    print "-f --train-file   - Список файлов, по которым шаблон должен быть уточнен"
    print "-o --train-folder - Список папок с файлами, по которым шаблон должен быть уточнен"
    print "-t --template     - Имя файла с сохраненным шаблоном"

def parse_options(argv = None):
    run_opts = {}
    run_opts["name"] = None      #Название или идентификатор шаблона
    run_opts["ref_file"] = None  #Опорный файл, по которому должен быть построен шаблон
    run_opts["files"] = []       #Список файлов (и папок), по которым шаблон должен быть уточнен
    run_opts["folders"] = []     #
    run_opts["template"] = None  #Имя файла с сохраненным шаблоном
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hf:o:n:t:r:", ["",""])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
    
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print_help()
            sys.exit(0)
        if o in ("-f","--train-file"):
            run_opts["files"].append(a)
            
        if o in ("-o","--train-folder"):
            run_opts["folders"].append(a)
            
        if o in ("-n","--name"):
            run_opts["name"] = a
            
        if o in ("-r","--ref-file"):
            run_opts["ref_file"] = a
            
        if o in ("-t","--template"):
            run_opts["template"] = a
            
    run_opts["n_files"] = len(run_opts["files"])
    run_opts["n_folders"] = len(run_opts["folders"])
    
    if not run_opts["template"]:
        raise ValueError("Требуется название файла для сохранения шаблона")
    
    if not run_opts["ref_file"]:
        raise ValueError("Требуется название файла для построения шаблона")
    
    if not run_opts["name"]:
        raise ValueError("Требуется название или идентификатор шаблона")

    if 0==run_opts["n_folders"]:
        #Выходные папки не указаны, будем создавать их названия автоматически
        for f in run_opts["files"]:
            file_path, file_name = os.path.split(f)
            file_name, file_extension = os.path.splitext(file_name)
            run_opts["folders"].append(file_name + "_data/")
    run_opts["n_folders"] = len(run_opts["folders"])
    return run_opts


class TemplateBuilder:
    def __init__(self, file_name):
        self._swtt = swt_conv.SwtTransform("db2")
        self._file_name = file_name
        
    def find_xextremums(self):
        self._swtt.transform(self._file_name, self._max_levels)
        #self._swtt.find_extremums()
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
        
    def build(self, template_name, max_levels = 9):
        self._max_levels = max_levels
        self._edges = self.find_xextremums()
        edges = self._edges[1]
        edge_coords = numpy.nonzero(edges)
        etb = swt_template.ExtremumTemplate(template_name, self._max_levels)
        for i in range(len(edge_coords[0])):
            coord = numpy.array((edge_coords[0][i], edge_coords[1][i]))
            base_extremum = swt_template.BaseExtremumPoint(coord, 1, is_max = True)
            etb.add_extremum(base_extremum)
            
        edges = self._edges[0]
        edge_coords = numpy.nonzero(edges)
        etb = swt_template.ExtremumTemplate(template_name, self._max_levels)
        for i in range(len(edge_coords[0])):
            coord = numpy.array((edge_coords[0][i], edge_coords[1][i]))
            base_extremum = swt_template.BaseExtremumPoint(coord, 1, is_max = False)
            etb.add_extremum(base_extremum)
            
        etb.rebuild()
        return etb
    
    def plot(self):
        combined = numpy.fmax(self._swtt._swt_matrix, self._edges*4)
        tmp_sig = numpy.repeat(combined, 20, axis=0)
        tmp_sig = numpy.repeat(tmp_sig, 3, axis=1)
        pylab.imshow(numpy.flipud(tmp_sig))
        pylab.show()
        
def main(argv=None):
    run_opts = parse_options()
    swt_conv.import_analize_modules()
    cluster.import_analize_modules()
    
    tf = swt_template.TemplateFinder()
    tb = TemplateBuilder(run_opts["ref_file"])
    etb = tb.build(run_opts["name"])
    tf.add_template(etb)
    for i in range(len(run_opts["files"])):
        tf.analize_file(run_opts["files"][i])
        tf.recalculate_probabilities()
        
    etb.save(run_opts["template"])
    
if __name__ == "__main__":
    main()
    
    