import os

import numpy as np
from tinamit.Geog import Lugar, Geografía
from tinamit.MDS import leer_egr_mds

# 0. File Path
File_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Vensim')
Map_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Scenario_map_05142018')

# 0. Site geography
Rechna_Doab = Geografía(nombre='Rechna Doab')

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')

Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_orden='Polygon_ID')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua', color='#41b2f4')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', llenar=False, color='#4153f4')
# Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
#Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')

vars_interés = {'Watertable depth Tinamit': {'col': ['#ea0707', '#eaa607', '#eaea07', '#ccc80c', '#abed49', '#278e1d', '#0f6607'],'categs': ['0-100 cm', '100-120 cm', '150-300 cm', '300-450 cm', '450-600 cm', '600-1200 cm', '> 1200 cm'],
                                'escala_núm': [1, 7]},
                'Soil salinity Tinamit CropA': {'col':['#21bf13', '#FFCC66', '#eaa607', '#ea0707'],'categs': ['Non Saline', 'Slightly saline', 'Moderately Saline', 'Strongly Saline'],
                                'escala_núm': [1, 4]}}

# Escenarios = ['CL','CWU','PIM','RWH','VD']
# Escenarios_climáticos = ['0', '2_6', '4_5', '6_0', '8_5']
Escenarios = ['CL','CWU','PIM','RWH','VD']
for v, d in vars_interés.items():
    # Escenarios = ['CL 0','CL 2_6','CL 4_5','CL 6_0','CL 8_5',
    #               'CWU 0','CWU 2_6','CWU 4_5','CWU 6_0','CWU 8_5',
    #               'PIM 0','PIM 2_6','PIM 4_5','PIM 6_0','PIM 8_5',
    #               'RWH 0','RWH 2_6','RWH 4_5','RWH 6_0','RWH 8_5',
    #               'VD 0','VD 2_6','VD 4_5','VD 6_0','VD 8_5']
    for a in Escenarios:
        datos = leer_egr_mds((os.path.join(File_dir, '{}.csv')).format(a), var=v)
        n_paso = datos.shape[1]

        final = np.empty_like(datos)
        if v == 'Soil salinity Tinamit CropA':
            final[np.less(datos, 4)] = 1
            final[np.logical_and(np.greater_equal(datos, 4), np.less(datos, 8))] = 2
            final[np.logical_and(np.greater_equal(datos, 8), np.less(datos, 16))] = 3
            final[np.greater_equal(datos, 16)] = 4
        if v == 'Watertable depth Tinamit':
            final[np.less(datos, 1)] = 1
            final[np.logical_and(np.greater_equal(datos, 1), np.less(datos, 1.5))] = 2
            final[np.logical_and(np.greater_equal(datos, 1.5), np.less(datos, 3.0))] = 3
            final[np.logical_and(np.greater_equal(datos, 3.0), np.less(datos, 4.5))] = 4
            final[np.logical_and(np.greater_equal(datos, 4.5), np.less(datos, 6.0))] = 5
            final[np.logical_and(np.greater_equal(datos, 6.0), np.less(datos, 12))] = 6
            final[np.greater_equal(datos, 12)] = 7

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
                                unidades='', colores=d['col'], categs=d['categs'],
                                escala_num=d['escala_núm']
                                )

