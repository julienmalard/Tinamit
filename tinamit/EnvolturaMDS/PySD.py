import os
import pysd

from tinamit import _
from tinamit.MDS import EnvolturaMDS


class ModeloPySD(EnvolturaMDS):

    def __init__(símismo, archivo):

        ext = os.path.splitext(archivo)[1]
        if ext == '.mdl':
            símismo.modelo = pysd.read_vensim(archivo)
        elif ext in ['.xmile', '.xml']:
            símismo.modelo = pysd.read_xmile(archivo)
        else:
            raise ValueError(_('PySD no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".xmile".')
                             .format(ext))

        símismo.conv_nombres = {}
        símismo.tiempo_final = None
        símismo.cont_simul = False

        super().__init__(archivo)

        raise NotImplementedError

    def inic_vars(símismo):
        símismo.variables.clear()
        símismo.conv_nombres.clear()

        for i, f in símismo.modelo.doc().iterrows():
            nombre = f['Real Name']
            nombre_py = f['Py Name']
            unidades, líms = f['Unit'].rsplit('[')  # type: str, str
            unidades = unidades.strip()
            líms = [float(x) if 'inf' not in x else None for x in líms.strip(']').split(',')]

            símismo.variables[nombre] = {
                'val': getattr(símismo.modelo.components, nombre_py)(),
                'dims': (1,),  # Para hacer
                'unidades': unidades,
                'líms': líms,
                'info': f['Comment']
            }

            símismo.conv_nombres[nombre] = nombre_py

    def obt_unidad_tiempo(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        símismo.cont_simul = False
        símismo.tiempo_final = tiempo_final

    def cambiar_vals_modelo_interno(símismo, valores):
        raise NotImplementedError

    def incrementar(símismo, paso):
        if símismo.cont_simul:
            símismo.modelo.run(initial_condition='current', params={'FINAL TIME': paso, 'TIME STEP': 1})
        else:
            símismo.modelo.run(params={'FINAL TIME': paso, 'TIME STEP': 1})

        símismo.cont_simul = True

    def leer_vals(símismo):
        for v, d_v in símismo.variables:
            nombre_py = símismo.conv_nombres[v]
            val = getattr(símismo.modelo.components, nombre_py)()

            if símismo.variables[v]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...
                símismo.variables[v]['val'] = val
            else:
                símismo.variables[v]['val'][:] = val

    def cerrar_modelo(símismo):
        pass
