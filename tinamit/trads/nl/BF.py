from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente
from tinamit.BF import ModeloBF
from tinamit.BF import EnvolturaBF


class EnvolturaBF(EnvolturaBF):

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()


class ModeloBF(ModeloBF):

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()


class ModeloImpaciente(ModeloImpaciente):

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def avanzar_modelo(símismo):
        return super().avanzar_modelo()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()

    def leer_archivo_vals_inic(símismo):
        return super().leer_archivo_vals_inic()

    def leer_egr(símismo, n_años_egr):
        return super().leer_egr(n_años_egr=n_años_egr)

    def escribir_ingr(símismo, n_años_simul):
        return super().escribir_ingr(n_años_simul=n_años_simul)

    def leer_archivo_egr(símismo, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)


class ModeloFlexible(ModeloFlexible):

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def leer_archivo_vals_inic(símismo):
        return super().leer_archivo_vals_inic()

    def mandar_simul(símismo):
        return super().mandar_simul()

    def leer_archivo_egr(símismo, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)
