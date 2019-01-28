from tinamit.Análisis.Sens.muestr import gen_problema
from tinamit.Calib.ej.sens_análisis import gen_mod
from tinamit.Calib.ej.info_paráms import calib_líms_paráms, calib_mapa_paráms
from tinamit.Calib.ej.cor_patrón import calib_obs, valid_obs

mod = gen_mod()

líms_paráms_final = gen_problema(líms_paráms=calib_líms_paráms, mapa_paráms=calib_mapa_paráms, ficticia=False)[1]

calib_res = mod.calibrar(paráms=list(líms_paráms_final), b_d=calib_obs, líms_paráms=calib_líms_paráms,
             vars_obs='mds_Watertable depth Tinamit', final_líms_paráms=líms_paráms_final,
             mapa_paráms=calib_mapa_paráms, tipo_proc='multidim', obj_func='NSE')

# valid_res