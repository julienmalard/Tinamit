from tinamit.BF import ModeloFlexible


class Envoltura(ModeloFlexible):

    def _incrementar(símismo, paso, guardar_cada=None):
        pass

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'días'

    def _inic_dic_vars(símismo):
        símismo.variables['Escala'] = {
            'val': 0,
            'ingreso': False,
            'egreso': True,
            'unidades': 'sdmn',
            'líms': (0, None),
            'dims': (1,)
        }

    def leer_archivo_vals_inic(símismo):
        pass

    def mandar_simul(símismo):
        pass

    def leer_archivo_egr(símismo, n_años_egr):
        pass

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        pass
