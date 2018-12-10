import os

from tinamit.MDS import leer_egr_mds
from tinamit.Geog.Geog import Lugar, Geografía
import numpy as np



# 0. Site geography
Rechna_Doab = Geografía(nombre='Rechna Doab')

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')
File_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Vensim')
Map_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Scenario_map_05092018')

Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_orden='Polygon_ID')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua', color='#41b2f4')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', llenar=False, color='#4153f4')
# Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
#Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')


vars_interés = {'Soil salinity Tinamit CropA': {'col': ['#00CC66', '##FFCC66', '#FF431D'],'escala_núm': [0.2, 25]},
                'Watertable depth Tinamit': {'col':['#FF6666', '#FFCC66', '#00CC66'],'escala_núm': [0.828, 11]}}


for v, d in vars_interés.items():
    Escenarios = ['CWU']
    # Escenarios = ['CL 0','CL 2_6','CL 4_5','CL 6_0','CL 8_5',
    #               'CWU 0','CWU 2_6','CWU 4_5','CWU 6_0','CWU 8_5',
    #               'PIM 0','PIM 2_6','PIM 4_5','PIM 6_0','PIM 8_5',
    #               'RWH 0','RWH 2_6','RWH 4_5','RWH 6_0','RWH 8_5',
    #               'VD 0','VD 2_6','VD 4_5','VD 6_0','VD 8_5']

    for a in Escenarios:
        datos = leer_egr_mds((os.path.join(File_dir, '{}.csv')).format(a), var=v)
        n_paso = datos.shape[1]

        for i in range(n_paso):
            valores = datos[:, i]
            if i%2 == 0:
                X = int(1990 + i/2)
                SS = 'Season 1'
            else:
                SS = 'Season 2'

            escale = np.int32(0), np.int32(10)
            Rechna_Doab.dibujar(archivo=os.path.join(Map_dir, '{}_{}_{}.png'.format(v, a, i)),
                                valores=valores,
                                título='{}_{}_{}_{}'.format(v, a, X, SS),
                                unidades='', colores=d['col'], escala_num=d['escala_núm']
                                )
            # if escala_num is None:
            #     escala_num = (np.min(valores), np.max(valores))
            # if len(escala_num) != 2:
            #     raise ValueError






    # raise SystemExit(0)