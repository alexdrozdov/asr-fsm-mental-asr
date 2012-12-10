#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import scipy.signal
import pickle
from exceptions import ValueError
import swt_conv
import cluster

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
    run_opts["folders"] = []
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "hf:o:", ["file","folder"])
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
            
        if o in ("-o","--folder"):
            run_opts["folders"].append(a)
            
    run_opts["n_files"] = len(run_opts["files"])
    run_opts["n_folders"] = len(run_opts["folders"])

    if not run_opts["n_files"]:
        raise ValueError("Требуется имя минимум одного обрабатываемого файла")
    if run_opts["n_folders"]!=0 and run_opts["n_files"]!=run_opts["n_folders"]:
        raise ValueError("Количество выходных папок должно соответствовать количеству входных файлов")
    if 0==run_opts["n_folders"]:
        #Выходные папки не указаны, будем создавать их названия автоматически
        for f in run_opts["files"]:
            file_path, file_name = os.path.split(f)
            file_name, file_extension = os.path.splitext(file_name)
            run_opts["folders"].append(file_name + "_data/")
    run_opts["n_folders"] = len(run_opts["folders"])
    return run_opts
    
class FsmBuilder:
    class FsmState:
        def __init__(self, state_id, name, train_data, output_data):
            self._id = state_id
            self._name = name
            self._train_data = train_data
            self._output_data = output_data
            self._min_time = None
            self._min_time_def_state = None
            self._max_time = None
            self._max_time_def_state = None
            self._next_state = None
            self._input_links_count = 0
            self._output_links_count = 0
            
        def next_state(self, next_state = None):
            if None!=next_state:
                self._next_state = next_state
            return self._next_state
        
        def input_links(self, count = None):
            if None != count:
                self._input_liks_count = count
            return self._input_liks_count
        
        def output_links(self, count = None):
            if None != count:
                self._output_liks_count = count
            return self._output_liks_count
        
        def min_state_time(self, min_time = None, def_state = None):
            if None != min_time and None != def_state:
                self._min_time = min_time
                self._min_time_def_state = def_state
            return (self._min_time, self._min_time_def_state)
        
        def max_state_time(self, max_time = None, def_state = None):
            if None != max_time and None != def_state:
                self._max_time = max_time
                self._max_time_def_state = def_state
            return (self._max_time, self._max_time_def_state)
        
        def create_xml_property(self, xml, prop_name, prop_value):
            return " " + prop_name + "=\"" + prop_value + "\""
        def create_xml_str(self, fann_name):
            xml = ""
            xml += "<i" + str(self._id)
            xml += self.create_xml_property("caption", self._name)
            xml += self.create_xml_property("logic", "")
            xml += self.create_xml_property("stable", "true")
            xml += self.create_xml_property("fann", fann_name)
            xml += self.create_xml_property("id", self._id)
            xml += ">"
            
            xml += "<mintime"
            if None != self._min_time_def_state:
                xml += self._create_xml_property("next_state", str(self._min_time_def_state._id))
                xml += self._create_xml_property("value", str(self._min_time)+"ms")
                xml += self._create_xml_property("enabled", "true")
            else:
                xml += self._create_xml_property("next_state", "")
                xml += self._create_xml_property("value", "")
                xml += self._create_xml_property("enabled", "false")
            xml += "/>"
            
            xml += "<maxtime"
            if None != self._max_time_def_state:
                xml += self._create_xml_property("next_state", str(self._max_time_def_state._id))
                xml += self._create_xml_property("value", str(self._max_time)+"ms")
                xml += self._create_xml_property("enabled", "true")
            else:
                xml += self._create_xml_property("next_state", "")
                xml += self._create_xml_property("value", "")
                xml += self._create_xml_property("enabled", "false")
            xml += "/>"
            
            xml += "<input_links"
            xml += self._create_xml_property("count", str(self.input_links()))
            xml += ">"
            for i in range(self.input_links()):
                xml += "<i" + str(i)
                xml += self._create_xml_property("in", str(i))
                xml += self._create_xml_property("fann", str(i))
                xml += "/>"
            xml += "</input_links>"
            
            xml += "<output_links"
            xml += self._create_xml_property("count", str(self.output_links()))
            xml += ">"
            for i in range(self.output_links()):
                xml += "<i" + str(i)
                xml += self._create_xml_property("out", str(i))
                xml += self._create_xml_property("fann", "-1")
                if i==self._id:
                    xml += self._create_xml_property("value", "1")
                else:
                    xml += self._create_xml_property("value", "0")
                xml += self._create_xml_property("const", "true")
                xml += "/>"
            xml += "</output_links>"
            
            xml += "<state_coding"
            xml += self._create_xml_property("count", "1")
            xml += ">"
            xml += "</state_coding>"
            xml += "</i" + str(self._id) + ">"
            
            return xml
        
        
    def __init__(self, file_name):
        self._swtt = swt_conv.SwtTransform("db2")
        self._file_name = file_name
        
    def create_tcl(self, project_path):
        def build_state_out(full_count, active_out):
            s = ""
            for i in range(full_count):
                if i==active_out:
                    s += "1.0 "
                else:
                    s += "0.0 "
            return s
        
        if project_path[-1]!='/': project_path+='/'
        if not os.path.exists(project_path): os.makedirs(project_path)
        common_file_name = os.path.splitext(os.path.split(self._file_name)[1])[0]
        
        tcl = "project saveas " + common_file_name + ".fpr\n"
        tcl += "fann inputs " + str(self._max_levels) + "\n"
        tcl += "fann outputs " + str(len(self._pc.groups())) + "\n"
        tcl += "fann hidden " + str(self._max_levels) + "\n"
        tcl += "fann layers 3\n"
        tcl += "fann max-epochs 10000\n"
        tcl += "fann log-period 1000\n"
        tcl += "fann desired-error 0.01\n"
        tcl += "fann file " + common_file_name + ".fann\n"
        
        state_cnt = 0
        wvl_len = self._swtt.wavelet_length()
        for c in self._pc.groups():
            scaled_c = int(float(c) / 1000.0 * float(wvl_len))
            rng = (max(scaled_c-self._range_width/2, 0), min(scaled_c+self._range_width/2, wvl_len-1))
            range_data = self._swtt.wavelet_range(rng)
            state_name = "st" + str(state_cnt)
            state_output = build_state_out(len(self._pc.groups()), state_cnt)
            in_file = open(project_path + state_name + "_in.dat", 'w')
            for r in range_data.T:
                for c in r:
                    in_file.write(str(c) + " ")
                in_file.write("\n")
            in_file.close()
            tcl += "data add " + state_name + " -input ./" + state_name + "_in.dat -outputs {" + state_output + "}\n"
            state_cnt += 1
            
        tcl += "fann train\n"
        tcl += "fann save\n"
        tcl += "project save\n"
        tcl += "exit\n"

        tcl_name = project_path + common_file_name + ".tcl"
        tcl_file = open(tcl_name, 'w')
        tcl_file.write(tcl)
        tcl_file.close()

    def build(self, max_levels = 9, swtt_field = (350,1000), cluster_radius = 40.0, range_width=20):
        self._max_levels = max_levels
        self._range_width = range_width
        self._swtt.transform(self._file_name, self._max_levels)
        self._swtt.find_extremums(swtt_field)
        
        self._pc = cluster.PointCluster(extremums = self._swtt.extremums)
        self._pc.cluster(cluster_radius = cluster_radius)
            
    def save_project(self, project_name = None):
        pass

def main(argv=None):
    run_opts = parse_options()
    
    import_analize_modules()
    swt_conv.import_analize_modules()
    cluster.import_analize_modules()
    
    for i in range(len(run_opts["files"])):
        fsb = FsmBuilder(run_opts["files"][i])
        fsb.build()
        fsb.create_tcl(run_opts["folders"][i])


if __name__ == "__main__":
    main()

