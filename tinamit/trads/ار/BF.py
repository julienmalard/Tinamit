from tinamit.BF import EnvolturaBF
from tinamit.BF import ModeloBF
from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente


class EnvolturaBF(EnvolturaBF):

    def obt_unidad_tiempo(خود):
        return super().unidad_tiempo()

    def inic_vars(خود):
        return super()._inic_dic_vars()

    def cambiar_vals_modelo_interno(خود, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def iniciar_modelo(خود):
        return super().iniciar_modelo()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def paralelizable(símismo):
        return super().paralelizable()


class ModeloBF(ModeloBF):

    def cambiar_vals_modelo_interno(خود, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(خود):
        return super().unidad_tiempo()

    def inic_vars(خود):
        return super()._inic_dic_vars()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()


class ModeloImpaciente(ModeloImpaciente):

    def cambiar_vals_modelo_interno(خود, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(خود, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def obt_unidad_tiempo(خود):
        return super().unidad_tiempo()

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def inic_vars(خود):
        return super()._inic_dic_vars()

    def avanzar_modelo(خود):
        return super().avanzar_modelo()

    def leer_vals_inic(خود):
        return super().leer_vals_inic()

    def leer_archivo_vals_inic(خود):
        return super().leer_archivo_vals_inic()

    def leer_egr(خود, n_años_egr):
        return super().leer_egr(n_años_egr=n_años_egr)

    def escribir_ingr(خود, n_años_simul):
        return super().escribir_ingr(n_años_simul=n_años_simul)

    def leer_archivo_egr(خود, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(خود, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)


class ModeloFlexible(ModeloFlexible):

    def cambiar_vals_modelo_interno(خود, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def iniciar_modelo(خود):
        return super().iniciar_modelo()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(خود):
        return super().unidad_tiempo()

    def inic_vars(خود):
        return super()._inic_dic_vars()

    def leer_archivo_vals_inic(خود):
        return super().leer_archivo_vals_inic()

    def mandar_simul(خود):
        return super().mandar_simul()

    def leer_archivo_egr(خود, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(خود, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()
