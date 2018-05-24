from tinamit.BF import EnvolturaBF
from tinamit.BF import ModeloBF
from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente


class EnvolturaBF(EnvolturaBF):

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def paralelizable(símismo):
        return super().paralelizable()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloBF(ModeloBF):

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloImpaciente(ModeloImpaciente):

    def act_vals_clima(خود, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

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

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloFlexible(ModeloFlexible):

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

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

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()
