import numpy as np
import xarray as xr

from tinamit.EnvolturasMDS.Vensim import gen_archivo_mdl
from tinamit.MDS import EnvolturaMDS
from tinamit.config import _


class ModeloPySD(EnvolturaMDS):
    combin_pasos = True

    def __init__(símismo, archivo, nombre='mds'):

        símismo.tipo_mod = None
        símismo.tiempo_final = None
        símismo.cont_simul = False
        símismo.paso_act = 0
        símismo.vars_para_cambiar = {}
        símismo._res_recién = None  # pd.DataFrame

        super().__init__(archivo, nombre=nombre)

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        símismo.cont_simul = False
        símismo.tiempo_final = n_pasos
        símismo.paso_act = símismo.mod.time._t
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(vals_inic)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def _vals_inic(símismo):

        return {var: getattr(símismo.mod.components, símismo._conv_nombres[var])() for var in símismo.variables}

    def _cambiar_vals_modelo_externo(símismo, valores):
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(
            {var: val for var, val in valores.items() if not np.isnan(val)}
        )

    def _incrementar(símismo, paso, guardar_cada=None):
        guardar_cada = guardar_cada or paso
        pasos_devolv = list(range(símismo.paso_act, símismo.paso_act + 1 + paso, guardar_cada))
        símismo.paso_act += paso

        if símismo.cont_simul:
            símismo._res_recién = símismo.mod.run(
                initial_condition='current', params=símismo.vars_para_cambiar,
                return_timestamps=pasos_devolv, return_columns=símismo.vars_saliendo
            )
        else:
            símismo._res_recién = símismo.mod.run(
                return_timestamps=pasos_devolv, params=símismo.vars_para_cambiar,
                return_columns=símismo.vars_saliendo
            )
            símismo.cont_simul = True

        símismo.vars_para_cambiar.clear()

    def _leer_vals(símismo):
        valores = {}
        for v in símismo.vars_saliendo:
            valores[v] = símismo._res_recién[v].values[-1]

        símismo._act_vals_dic_var(valores)

    def leer_arch_resultados(símismo, archivo, var=None, col_tiempo='tiempo'):

        if archivo != símismo.corrida_activa:
            raise ValueError(_('PySD solamente puede leer los resultados de la última corrida.'))
        if var is None:
            l_vars = list(símismo._res_recién)
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var
        return xr.Dataset({v: ('n', símismo._res_recién[v].values) for v in l_vars})

    def _generar_archivo_mod(símismo):
        if símismo.tipo_mod == '.mdl':
            return gen_archivo_mdl(archivo_plantilla=símismo.archivo, d_vars=símismo.variables)
        else:
            raise NotImplementedError(símismo.tipo_mod)

    def paralelizable(símismo):
        return True

    def editable(símismo):
        return símismo.tipo_mod != '.py' and símismo.tipo_mod != '.xmile'  # para hacer: agregar xmile
