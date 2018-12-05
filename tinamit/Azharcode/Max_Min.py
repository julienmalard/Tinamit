import os

import numpy as np
from tinamit.Geog.GabbyGeog import Lugar, Geografía
from tinamit.MDS import leer_egr_mds

# 0. File Path
File_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Vensim')

vars_interés = {'Watertable depth Tinamit': {},
                'Soil salinity Tinamit CropA': {}}

Escenarios = ['CL','CWU','PIM','RWH','VD']
for v, d in vars_interés.items():

    for a in Escenarios:
        datos = leer_egr_mds((os.path.join(File_dir, '{}.csv')).format(a), var=v)

        print(a, v, 'Max: ', np.nanmax(datos), 'Min: ', np.nanmin(datos))