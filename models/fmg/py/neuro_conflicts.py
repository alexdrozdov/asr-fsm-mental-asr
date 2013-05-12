#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import scipy.signal
from exceptions import ValueError
import cluster



def main(argv=None):
    import_analize_modules()
    pc = PointCluster(file_name = './a_o.store')
    pc.cluster()
    print pc.groups()


if __name__ == "__main__":
    main()

