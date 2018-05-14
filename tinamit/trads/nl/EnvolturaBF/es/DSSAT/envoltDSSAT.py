from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT


class ModeloDSSAT(ModeloDSSAT):

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def mandar_simul(símismo):
        return super().mandar_simul()

    def inic_vars_clima(símismo, tiempo_final):
        return super().inic_vars_clima(tiempo_final=tiempo_final)

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()

vars_DSSAT = vars_DSSAT
