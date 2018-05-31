import os
from ast import literal_eval

import pysd
from Análisis.sintaxis import Ecuación
from tinamit import _
from tinamit.MDS import EnvolturaMDS


class ModeloPySD(EnvolturaMDS):

    def __init__(símismo, archivo, nombre='mds'):

        ext = os.path.splitext(archivo)[1]
        if ext == '.mdl':
            símismo.tipo = '.mdl'
            símismo.modelo = pysd.read_vensim(archivo)
            símismo.internos = ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']
        elif ext in ['.xmile', '.xml']:
            símismo.tipo = '.xmile'
            símismo.modelo = pysd.read_xmile(archivo)
            símismo.internos = []
        else:
            raise ValueError(_('PySD no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".xmile".')
                             .format(ext))

        símismo._conv_nombres = {}
        símismo.tiempo_final = None
        símismo.cont_simul = False
        símismo.paso_act = 0
        símismo.vars_para_cambiar = {}

        super().__init__(archivo, nombre=nombre)

    def _inic_dic_vars(símismo):
        símismo.variables.clear()
        símismo._conv_nombres.clear()

        for i, f in símismo.modelo.doc().iterrows():
            nombre = f['Real Name']
            if nombre not in símismo.internos:
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
            # Solución muy fea para PySD
            with open(símismo.modelo.py_model_file, 'r', encoding='UTF-8') as d:
                f = d.readline()
                while f != 'def time_step():\n':
                    f = d.readline()
                for i in range(6):
                    f = d.readline()
                unid_tiempo = f.strip()

        return unid_tiempo

    def _leer_vals_inic(símismo):

        for v, d_v in símismo.variables.items():
            nombre_py = símismo._conv_nombres[v]
            val = getattr(símismo.modelo.components, nombre_py)()

            símismo._act_vals_dic_var({v: val})

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        símismo.cont_simul = False
        símismo.tiempo_final = tiempo_final
        símismo.paso_act = 0
        símismo.vars_para_cambiar.clear()

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.modelo.reload()
        símismo.modelo.initialize()

    def _aplicar_cambios_vals_inic(símismo):
        símismo.vars_para_cambiar.update(símismo.vals_inic)

    def _cambiar_vals_modelo_interno(símismo, valores):
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(valores)

    def _incrementar(símismo, paso):
        símismo.paso_act += paso

        if símismo.cont_simul:
            símismo.modelo.run(initial_condition='current', params=símismo.vars_para_cambiar,
                               return_timestamps=símismo.paso_act)
        else:
            símismo.modelo.run(return_timestamps=símismo.paso_act, params=símismo.vars_para_cambiar)

        símismo.cont_simul = True

    def _leer_vals(símismo):
        for v in símismo.vars_saliendo:
            nombre_py = símismo._conv_nombres[v]
            val = getattr(símismo.modelo.components, nombre_py)()

            if símismo.variables[v]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...
                símismo.variables[v]['val'] = val
            else:
                símismo.variables[v]['val'][:] = val

    def cerrar_modelo(símismo):
        pass

    def paralelizable(símismo):
        return True
