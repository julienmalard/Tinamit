import os

from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms
from tinamit.Calib.ej.info_paráms import líms_paráms, mapa_paráms

archivo_muestrea = './muestra_morris.json'

if not os.path.isfile(archivo_muestrea):
    mstr = muestrear_paráms(líms_paráms, 'morris', mapa_paráms=mapa_paráms)
    guardar_mstr_paráms(mstr, archivo_muestrea)
else:
    mstr = cargar_mstr_paráms(archivo_muestrea)
