import numpy as np
import re
from pprint import pprint

n_year = 5
SAHYSMOD_output_vars = ['It','FfA','JsA','LrA','RrA','Gti','Gqi','Gd','Dw','Sto','A','Uc','CrA','C1*','Cxf','Cti','Ci','Is','FfB','JsB','LrB','RrB','Gto','Gqo','Ga','Hw','Zs','B','Kr','CrB','C2*','Cxa','Cqi','Cd','IaA','FfT','EaU','LrU','RrU','Qv','Gaq','Gb','Hq','U','CrU','C3*','Cxb','Cw','IaB','Io','RrT','RrT','Gnt','Gw','Cr4','Cqf']
[x for x in SAHYSMOD_output_vars if x not in out0], [x for x in out0 if x not in SAHYSMOD_output_vars]
#print(dic_data)

        #print((x.split('=')[0])+ (x.split(' ')[5]))
        #while 'Season:    %i' % season not in l:

