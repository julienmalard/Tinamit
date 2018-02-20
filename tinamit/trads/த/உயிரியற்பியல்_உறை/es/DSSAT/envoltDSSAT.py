from tinamit.உயிரியற்பியல்_உறை.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.உயிரியற்பியல்_உறை.es.DSSAT.envoltDSSAT import ModeloDSSAT


class ModeloDSSAT(ModeloDSSAT):

    def __init__(தன், exe_DSSAT, archivo_ingr):
        super().__init__(exe_DSSAT=exe_DSSAT, archivo_ingr=archivo_ingr)

    def iniciar_modelo(தன், tiempo_final):
        return தன்.iniciar_modelo(tiempo_final)

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def leer_vals(தன்):
        return தன்.leer_vals()

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def mandar_simul(தன்):
        return தன்.mandar_simul()

    def inic_vars_clima(தன், tiempo_final):
        return தன்.inic_vars_clima(tiempo_final)


vars_DSSAT = vars_DSSAT
