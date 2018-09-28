import os

from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms
from tinamit.Calib.ej.info_paráms import líms_paráms, mapa_paráms

archivo_muestrea_morris = os.path.abspath('./muestra_morris.json')
archivo_muestrea_fast = os.path.abspath('./muestra_fast.json')

if not os.path.isfile(archivo_muestrea_morris):
    mstr_morris = muestrear_paráms(líms_paráms, 'morris', mapa_paráms=mapa_paráms,
                                   ops_método={'N': 25, 'num_levels': 16, 'grid_jump': 8}
                                   )
    guardar_mstr_paráms(mstr_morris, archivo_muestrea_morris)
else:
    mstr_morris = cargar_mstr_paráms(archivo_muestrea_morris)

if not os.path.isfile(archivo_muestrea_fast):
    mstr_fast = muestrear_paráms(líms_paráms, 'fast', mapa_paráms=mapa_paráms, ops_método={'N': 5000})
else:
    mstr_fast = cargar_mstr_paráms(archivo_muestrea_fast)


# mstr = muestrear_paráms(líms_paráms, 'morris', problema_arch, mapa_paráms=mapa_paráms,
#     #                         ops_método = {'N': 25, 'num_levels': 8, 'grid_jump': 4}
#     #                         )