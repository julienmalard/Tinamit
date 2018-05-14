from tinamit.MDS import EnvolturaMDS
from tinamit.MDS import MDSEditable
from tinamit.MDS import leer_egr_mds


class EnvolturaMDS(EnvolturaMDS):

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()


class MDSEditable(MDSEditable):
