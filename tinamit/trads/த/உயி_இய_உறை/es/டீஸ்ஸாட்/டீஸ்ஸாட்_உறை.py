from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT


class டிஸ்ஸாட்_மாதிரி(ModeloDSSAT):

    def iniciar_modelo(தன், கடைசி_நேரம், nombre_corrida):
        return super().iniciar_modelo(tiempo_final=கடைசி_நேரம், nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def mandar_simul(தன்):
        return super().mandar_simul()

    def inic_vars_clima(தன், கடைசி_நேரம்):
        return super().inic_vars_clima(tiempo_final=கடைசி_நேரம்)

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()

vars_DSSAT = vars_DSSAT
