from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import vars_DSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT import ModeloDSSAT


class ModeloDSSAT(ModeloDSSAT):

    def iniciar_modelo(símismo, tiempo_final):
        return super().iniciar_modelo(tiempo_final=tiempo_final)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def leer_vals(símismo):
        return super().leer_vals()

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def mandar_simul(símismo):
        return super().mandar_simul()

    def inic_vars_clima(símismo, tiempo_final):
        return super().inic_vars_clima(tiempo_final=tiempo_final)

vars_DSSAT = vars_DSSAT
