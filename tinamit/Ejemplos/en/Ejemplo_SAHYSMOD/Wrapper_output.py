import numpy as np
import re
from pprint import pprint
n_s = 2
n_p = 214
n_year = 5
SAHYSMOD_output_vars = ['It','FfA','JsA','LrA','RrA','Gti','Gqi','Gd','Dw','Sto','A','Uc','CrA','C1*','Cxf','Cti','Ci','Is','FfB','JsB','LRB','RrB','Gto','Gqo','Ga','Hw','Zs','B','Kr','CrB','C2*','Cxa','Cqi','Cd','IaA','FfT','EaU','LrU','RrU','Qv','Gaq','Gb','Hq','U','CrU','C3*','Cxb','Cw','IaB','Io','RrT','RrT','Gnt','Gw','Cr4','Cqf']
dic_data = dict([(k, np.empty((n_s, n_p))) for k in SAHYSMOD_output_vars])
#print(dic_data)
with open('test.out', 'r') as d:
    l = ''
    while 'YEAR:      %i' % n_year not in l:
        l = d.readline()
    for season in range(n_s):
        for season_poly in range(n_p):  # Read output for the last year's seasons from the output file
            season_poly_output = []  # To hold the output file lines with the desired season
            if n_p == 1 and n_s == 1:
                Poly = [next(d)for s in range(23)]
            else:
                Poly = [next(d)for s in range(24)]
            season_poly_output.append(Poly)
            print(season_poly_output)

            for cod in SAHYSMOD_output_vars:
                var_out = cod.replace('#', '').replace('*', '\*')

                for line in Poly:

                    line += ' '
                    m = re.search(' %s += +([^ ]*)' % var_out, line)

                    if m:
                        val = m.groups()[0]
                        if val == '-':
                            val = -1
                        else:
                            try:
                                val = float(val)
                            except ValueError:
                                raise ValueError('The variable "%s" was not read from the SAHYSMOD output.'
                                         % var_out)
                        dic_data[cod][(season,season_poly)]= val
                            #print('%s  =' % var_out, val)
                        break
        #print((x.split('=')[0])+ (x.split(' ')[5]))
        #while 'Season:    %i' % season not in l:

pprint(dic_data)