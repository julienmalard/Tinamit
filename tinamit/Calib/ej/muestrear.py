import os

from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms
from tinamit.Calib.ej.info_paráms import líms_paráms, mapa_paráms

archivo_muestrea = os.path.abspath('./muestra_morris.json')
# archivo_muestrea = "D:\Thesis\pythonProject\localuse\Dt\Morr\sampled data./muestra_morris(25/8).json"

if not os.path.isfile(archivo_muestrea):
    mstr = muestrear_paráms(líms_paráms, 'morris', mapa_paráms=mapa_paráms,
                            ops_método = {'N': 25, 'num_levels': 8, 'grid_jump': 4}
                            )
    #n_sampling (N = 25, 50), n_level (8/16)
    # mstr = muestrear_paráms(líms_paráms, 'fast', mapa_paráms=mapa_paráms, ops_método={})
    # ops_método = {'N': 25, 'num_levels': 8, 'grid_jump': 4}
    guardar_mstr_paráms(mstr, archivo_muestrea)
else:
    mstr = cargar_mstr_paráms(archivo_muestrea)
