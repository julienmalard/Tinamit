import os

from tinamit.MDS import leer_egr_mds
from tinamit.Geog.GabbyGeog import Lugar, Geografía

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


vars_interés = {'Crops': {'col':['#00CC66', '##FFCC66', '#0066cc', '#cc6600', '#d1f442', '#f4ad42', '#cc00cc', '#FF6666'], 'categs':['Wheat', 'Cotton', 'Water', 'Barren', 'Fodder', 'Rice', 'Forest', 'Maize'],
                         'escala_núm': [1, 8]},
                'Farm Income': {'col': ['#00CC66', '##FFCC66', '#FF431D'], 'categs': ['High', 'Medium', 'Low'],
                           'escala_núm': [1, 3]},
                'Water Availability':{'col':['#00CC66', '##FFCC66', '#FF431D'],'categs': ['High','medium','low'],
                                    'escala_núm': [1, 3]},
                'Soil Salinity': {'col':['#00CC66', '##FFCC66', '#FF6666', '#FF431D'], 'categs': ['Non Saline', 'Slightly saline', 'Moderately Saline', 'Strongly Saline'],
                                'escala_núm': [1, 4]}}

for v, d in vars_interés.items():
    Escenarios = ['CL','BC','EWD','RAW','RWH','SCARP']

    Rechna_Doab.dibujar(archivo=os.path.join('Maps_clustering', '{}_{}_{}.png'.format(v, a, X)),
                        valores=valores,
                        título='{}_{}_{}'.format(v, a, X),
                        unidades='', colores=d['col']
                        )
    # raise SystemExit(0)