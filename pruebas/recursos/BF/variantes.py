from tinamit.BF import ModeloBloques, ModeloImpaciente, ModeloIndeterminado


class EjBloques(ModeloBloques):
    pass


class EjImpaciente(ModeloImpaciente):

    def _gen_dic_vals_inic(símismo):
        pass

    def __init__(símismo, nombre, n, unid_tiempo):
        símismo.n = n
        símismo.unid_tiempo = unid_tiempo

        super().__init__(nombre)

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _inic_dic_vars(símismo):
        símismo.variables.update({
            'ciclo': {
                'val': 0,
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
            },
            'pasito': {
                'val': 0,
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'pasito': True,
            }
        })
        símismo.variables.update(
            {'ingr_{}'.format(x): {
                'val': 1,
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'pasito': True,
            } for x in ['último', 'suma', 'prom', 'máx', 'directo']}
        )

    def obt_tmñ_ciclo(símismo):
        return símismo.n

    def avanzar_modelo(símismo, n_ciclos):
        pass


class EjIndeterminado(ModeloIndeterminado):
    pass
