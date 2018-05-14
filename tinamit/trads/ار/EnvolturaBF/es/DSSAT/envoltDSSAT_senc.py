from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import EnvoltDSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import arch_DSSAT_WTH
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import plantilla_wth

plantilla_wth = plantilla_wth

arch_DSSAT_WTH = arch_DSSAT_WTH


class EnvoltDSSAT(EnvoltDSSAT):

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def leer_vals(símismo):
        return super().leer_vals()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()
