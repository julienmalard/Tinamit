from tinamit.Análisis.Sens.muestr import gen_problema
from tinamit.Calib.ej.sens_análisis import gen_mod
from tinamit.Calib.ej.ej_calib.calib_patron import líms_paráms_final
from tinamit.Calib.ej.info_paráms import calib_líms_paráms, calib_mapa_paráms
from tinamit.Calib.ej.cor_patrón import res

mod = gen_mod()

líms_paráms_final = gen_problema(líms_paráms=calib_líms_paráms, mapa_paráms=calib_mapa_paráms, ficticia=False)[1]

mod.calibrar(paráms=list(líms_paráms_final), b_d=res[1], líms_paráms=calib_líms_paráms,
             vars_obs='mds_Watertable depth Tinamit', final_líms_paráms=líms_paráms_final,
             mapa_paráms=calib_mapa_paráms, tipo_proc='multidim', obj_func='NSE')

