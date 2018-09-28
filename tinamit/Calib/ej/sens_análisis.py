import os

from xarray import Dataset

from tinamit.Análisis.Sens.anlzr import behavior_anlzr
from tinamit.cositas import guardar_json, cargar_json
from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms
from tinamit.Calib.ej.info_paráms import líms_paráms, mapa_paráms

# call analysis func here
mor_simul_arch = os.path.abspath('D:\Thesis\pythonProject\localuse\Dt\Mor\simular\\val_Mor\\3')
simulation_data =cargar_json(mor_simul_arch)
simulation_data2={'3': Dataset.from_dict(simulation_data)}

behavior_anlzr(simulation_data2, 'mds_Watertable depth Tinamit', 'calibration')