#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import numpy
import swt_conv
import swt_template
import pylab
import cluster

from exceptions import ValueError

    
def print_help():
    print "-t --template       - Файл шаблона, который необходимо добавить к поиску"
    print "-c --check-file     - Файл для проверки массива шаблонов"

def parse_options(argv = None):
    run_opts = {}
    run_opts["templates"] = []
    run_opts["check_files"] = []
    
    if argv is None:
        argv = sys.argv
        
    try:
        opts, args = getopt.getopt(argv[1:], "ht:c:", ["help","template","check"])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print_help()
            sys.exit(0)
        if o in ("-c","--check"):
            run_opts["check_files"].append(a)
            
        if o in ("-t","--template"):
            run_opts["templates"].append(a)
            
    run_opts["n_templates"] = len(run_opts["templates"])
    run_opts["n_check"] = len(run_opts["check_files"])

    if not run_opts["n_templates"]:
        raise ValueError("Требуется минимум один шаблон поиска")
    if not run_opts["n_check"]:
        raise ValueError("Требуется минимум один файл для проверки")
    return run_opts

    
def main(argv=None):
    run_opts = parse_options()
    swt_conv.import_analize_modules()
    cluster.import_analize_modules()
    
    tf = swt_template.TemplateFinder();
    for i in range(len(run_opts["templates"])):
        etb = swt_template.ExtremumTemplate()
        etb.load(run_opts["templates"][i])
        tf.add_template(etb)
        
    for i in range(len(run_opts["check_files"])):
        print "Analizing", run_opts["check_files"][i], "..."
        tf.analize_file(run_opts["check_files"][i])
        template_x = tf.get_template_x()
        print type(template_x)
        keys = []
        for k in template_x.keys():
            template_x[k].sort()
            keys.append(k)
        print template_x
        for k in keys:    
            print k,":", tf.get_cluster_groups(k)
            
        tf.print_hit_count()
    
if __name__ == "__main__":
    main()
    
    