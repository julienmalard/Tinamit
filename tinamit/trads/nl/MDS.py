from tinamit.MDS import EnvolturaMDS
from tinamit.MDS import MDSEditable
from tinamit.MDS import leer_egr_mds


class EnvolturaMDS(EnvolturaMDS):

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class MDSEditable(MDSEditable):
