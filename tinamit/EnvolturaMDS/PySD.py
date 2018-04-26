import os
import pysd

from tinamit.MDS import EnvolturaMDS


class ModeloPySD(EnvolturaMDS):

    def __init__(símismo, archivo):

        ext = os.path.splitext(archivo)[1]
        if ext == '.mdl':
            símismo.modelo = pysd.read_vensim(archivo)
        elif ext in ['.xmile',
        super().__init__(archivo)

    def inic_vars(símismo):
        pass

    def obt_unidad_tiempo(símismo):
        pass

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        pass

    def cambiar_vals_modelo_interno(símismo, valores):
        pass

    def incrementar(símismo, paso):
        pass

    def leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def _leer_resultados(símismo, var, corrida):
        pass
