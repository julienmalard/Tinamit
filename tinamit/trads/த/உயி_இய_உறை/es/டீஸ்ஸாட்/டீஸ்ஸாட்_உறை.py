from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT


class டிஸ்ஸாட்_மாதிரி(ModeloDSSAT):

    def iniciar_modelo(தன், கடைசி_நேரம்):
        return super().iniciar_modelo(tiempo_final=கடைசி_நேரம்)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def leer_vals(தன்):
        return super().leer_vals()

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def mandar_simul(தன்):
        return super().mandar_simul()

    def inic_vars_clima(தன், கடைசி_நேரம்):
        return super().inic_vars_clima(tiempo_final=கடைசி_நேரம்)

vars_DSSAT = vars_DSSAT
