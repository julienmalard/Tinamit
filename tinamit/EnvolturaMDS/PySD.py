import os
from ast import literal_eval

import pysd

from tinamit import _
from tinamit.MDS import EnvolturaMDS


class ModeloPySD(EnvolturaMDS):

    def __init__(símismo, archivo):

        ext = os.path.splitext(archivo)[1]
        if ext == '.mdl':
            símismo.tipo = '.mdl'
            símismo.modelo = pysd.read_vensim(archivo)
        elif ext in ['.xmile', '.xml']:
            símismo.tipo = '.xmile'
            símismo.modelo = pysd.read_xmile(archivo)
        else:
            raise ValueError(_('PySD no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".xmile".')
                             .format(ext))

        símismo.conv_nombres = {}
        símismo.tiempo_final = None
        símismo.cont_simul = False
        símismo.paso_act = 0
        símismo.vars_para_cambiar = {}

        super().__init__(archivo)

    def inic_vars(símismo):
        símismo.variables.clear()
        símismo.conv_nombres.clear()

        for i, f in símismo.modelo.doc().iterrows():
            nombre = f['Real Name']
            if nombre not in ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']:
                nombre_py = f['Py Name']
                unidades = f['Unit']
                líms = literal_eval(f['Lims'])

                símismo.variables[nombre] = {
                    'val': getattr(símismo.modelo.components, nombre_py)(),
                    'dims': (1,),  # Para hacer
                    'unidades': unidades,
                    'líms': líms,
                    'info': f['Comment']
                }

                símismo.conv_nombres[nombre] = nombre_py

    def obt_unidad_tiempo(símismo):
        docs = símismo.modelo.doc()

        if símismo.tipo == '.mdl':
            unid_tiempo = docs.loc[docs['Real Name'] == 'TIME STEP', 'Unit'].values[0]

        else:
            # Solución muy fea para PySD
            with open(símismo.modelo.py_model_file, 'r', encoding='UTF-8') as d:
                f = d.readline()
                while f != 'def time_step():\n':
                    f = d.readline()
                f = d.readline()
                while f.strip() in ['"""', 'TIME STEP', '']:
                    f = d.readline()
                unid_tiempo = f.strip()

        return unid_tiempo

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        símismo.cont_simul = False
        símismo.tiempo_final = tiempo_final
        símismo.paso_act = 0
        símismo.vars_para_cambiar.clear()

        símismo.modelo.initialize()

    def cambiar_vals_modelo_interno(símismo, valores):
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(valores)

    def incrementar(símismo, paso):
        símismo.paso_act += paso

        if símismo.cont_simul:
            símismo.modelo.run(initial_condition='current', params=símismo.vars_para_cambiar,
                               return_timestamps=símismo.paso_act)
        else:
            símismo.modelo.run(return_timestamps=símismo.paso_act, params=símismo.vars_para_cambiar)

        símismo.cont_simul = True

    def leer_vals(símismo):
        for v in símismo.vars_saliendo:
            nombre_py = símismo.conv_nombres[v]
            val = getattr(símismo.modelo.components, nombre_py)()

            if símismo.variables[v]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...
                símismo.variables[v]['val'] = val
            else:
                símismo.variables[v]['val'][:] = val

    def cerrar_modelo(símismo):
        pass
