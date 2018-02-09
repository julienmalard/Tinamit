from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT


class ModeloDSSAT(ModeloDSSAT):

    def iniciar_modelo(خود, tiempo_final):
        return super().iniciar_modelo(tiempo_final=tiempo_final)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def inic_vars(خود):
        return super().inic_vars()

    def obt_unidad_tiempo(خود):
        return super().obt_unidad_tiempo()

    def leer_vals(خود):
        return super().leer_vals()

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def cambiar_vals_modelo_interno(خود, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def mandar_simul(خود):
        return super().mandar_simul()

    def inic_vars_clima(خود, tiempo_final):
        return super().inic_vars_clima(tiempo_final=tiempo_final)

vars_DSSAT = vars_DSSAT
