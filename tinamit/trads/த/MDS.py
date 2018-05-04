from tinamit.MDS import MDSEditable
from tinamit.MDS import leer_egr_mds
from tinamit.MDS import EnvolturaMDS


class EnvolturaMDS(EnvolturaMDS):

    def inic_vars(símismo):
        return super().inic_vars()

    def obt_unidad_tiempo(símismo):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()


class MDSEditable(MDSEditable):
