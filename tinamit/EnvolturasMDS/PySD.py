import os
from ast import literal_eval

import numpy as np

import pysd
from tinamit import _
from tinamit.Análisis.sintaxis import Ecuación
from tinamit.MDS import EnvolturaMDS


class ModeloPySD(EnvolturaMDS):

    def __init__(símismo, archivo, nombre='mds'):

        ext = os.path.splitext(archivo)[1]
        if ext == '.mdl':
            símismo.tipo = '.mdl'
            símismo.modelo = pysd.read_vensim(archivo)
        elif ext in ['.xmile', '.xml']:
            símismo.tipo = '.xmile'
            símismo.modelo = pysd.read_xmile(archivo)
        elif ext == '.py':  # Modelos PySD ya traducidos
            símismo.tipo = '.py'
            símismo.modelo = pysd.load(archivo)
        else:
            raise ValueError(_('PySD no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".xmile".')
                             .format(ext))

        símismo._conv_nombres = {}
        símismo.tiempo_final = None
        símismo.cont_simul = False
        símismo.paso_act = 0
        símismo.vars_para_cambiar = {}
        símismo._res_recién = None  # pd.DataFrame

        super().__init__(archivo, nombre=nombre)
        símismo.combin_incrs = True

    def _inic_dic_vars(símismo):
        símismo.variables.clear()
        símismo._conv_nombres.clear()

        for i, f in símismo.modelo.doc().iterrows():
            nombre = f['Real Name']
            if nombre not in ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']:
                nombre_py = f['Py Name']
                unidades = f['Unit']
                líms = literal_eval(f['Lims'])
                ec = f['Eqn']

                símismo.variables[nombre] = {
                    'val': getattr(símismo.modelo.components, nombre_py)(),
                    'dims': (1,),  # Para hacer
                    'unidades': unidades,
                    'ec': ec,
                    'hijos': [],
                    'parientes': Ecuación(ec).variables(),
                    'líms': líms,
                    'info': f['Comment']
                }

                símismo._conv_nombres[nombre] = nombre_py

        for v, d_v in símismo.variables.items():
            for p in d_v['parientes']:
                d_p = símismo.variables[p]
                d_p['hijos'].append(v)

    def unidad_tiempo(símismo):
        docs = símismo.modelo.doc()

        if símismo.tipo == '.mdl':
            unid_tiempo = docs.loc[docs['Real Name'] == 'TIME STEP', 'Unit'].values[0]

        else:
            with open(símismo.modelo.py_model_file, 'r', encoding='UTF-8') as d:
                f = d.readline()
                while f != 'def time_step():\n':
                    f = d.readline()
                while not f.strip().startswith('Units:'):
                    f = d.readline()
                unid_tiempo = f.split(':')[1].strip()

        return unid_tiempo

    def _leer_vals_inic(símismo):

        for v, d_v in símismo.variables.items():
            nombre_py = símismo._conv_nombres[v]
            val = getattr(símismo.modelo.components, nombre_py)()

            símismo._act_vals_dic_var({v: val})

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.modelo.reload()
        símismo.modelo.initialize()

        símismo.cont_simul = False
        símismo.tiempo_final = tiempo_final
        símismo.paso_act = símismo.modelo.time._t
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(vals_inic)

    def cambiar_vals_modelo_interno(símismo, valores):
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(
            {var: val for var, val in valores.items() if not np.isnan(val)}
        )

    def _incrementar(símismo, paso, guardar_cada=None):
        guardar_cada = guardar_cada or paso
        pasos_devolv = list(range(símismo.paso_act, símismo.paso_act + 1 + paso, guardar_cada))
        símismo.paso_act += paso

        if símismo.cont_simul:
            símismo._res_recién = símismo.modelo.run(
                initial_condition='current', params=símismo.vars_para_cambiar,
                return_timestamps=pasos_devolv, return_columns=símismo.vars_saliendo
            )
        else:
            símismo._res_recién = símismo.modelo.run(
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

    def leer_arch_resultados(símismo, archivo, var=None):

        if archivo != símismo.corrida_activa:
            raise ValueError(_('PySD solamente puede leer los resultados de la última corrida.'))
        if var is None:
            l_vars = list(símismo._res_recién)
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        return {v: símismo._res_recién[v].values for v in l_vars}

    def cerrar_modelo(símismo):
        pass

    def paralelizable(símismo):
        return True
