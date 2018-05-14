from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import EnvoltDSSAT
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import arch_DSSAT_WTH
from tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT_senc import plantilla_wth

plantilla_wth = plantilla_wth

arch_DSSAT_WTH = arch_DSSAT_WTH


class EnvoltDSSAT(EnvoltDSSAT):

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()
