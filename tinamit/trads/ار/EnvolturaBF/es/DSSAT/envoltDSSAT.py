from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT


class ModeloDSSAT(ModeloDSSAT):

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def mandar_simul(خود):
        return super().mandar_simul()

    def inic_vars_clima(خود, tiempo_final):
        return super().inic_vars_clima(tiempo_final=tiempo_final)

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


vars_DSSAT = vars_DSSAT
