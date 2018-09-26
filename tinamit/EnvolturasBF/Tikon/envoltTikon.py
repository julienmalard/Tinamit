from tinamit.BF import ModeloDeterminado


class ModeloTikon(ModeloDeterminado):  # pragma: sin cobertura
    """

    """

    def _escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        pass

    def _gen_dic_vals_inic(símismo):
        pass

    def _act_vals_clima(símismo, n_paso, f):
        pass

    def leer_archivo_egr(símismo, n_años_egr):
        pass

    def _inic_dic_vars(símismo):
        pass

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        super().iniciar_modelo(n_pasos, nombre_corrida, vals_inic)

    def avanzar_modelo(símismo):
        pass

    def cerrar_modelo(símismo):
        pass
