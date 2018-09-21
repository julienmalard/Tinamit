import numpy as np

from tinamit.BF import ModeloBloques, ModeloImpaciente, ModeloIndeterminado


class EjBloques(ModeloBloques):
    pass


class EjImpaciente(ModeloImpaciente):

    def leer_egr_modelo(símismo):
        dic = {'ciclo': símismo.ciclo, 'pasito': np.arange(símismo.n)}

        dic.update(
            {'egr_{}'.format(x): símismo.obt_val_actual_var('ingr_{}'.format(x))
             for x in ['último', 'suma', 'prom', 'máx']}
        )

        return dic

    def _gen_dic_vals_inic(símismo):
        por_pasito = símismo._vars_por_pasito()
        tmñ = símismo.obt_tmñ_ciclo()
        return {
            vr: (np.arange(tmñ) if vr == 'pasito' else np.zeros(tmñ))
            if vr in por_pasito else 0 for vr in símismo.variables
        }

    def __init__(símismo, nombre, n, unid_tiempo):
        símismo.n = n
        símismo.unid_tiempo = unid_tiempo
        símismo.ciclo = 0

        super().__init__(nombre)

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _inic_dic_vars(símismo):
        símismo.variables.update({
            'ciclo': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
            },
            'pasito': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'pasito': True,
            },
            'ingr_directo': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'pasito': True
            }
        })
        símismo.variables.update(
            {'ingr_{}'.format(x): {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
            } for x in ['último', 'suma', 'prom', 'máx']}
        )
        símismo.variables.update(
            {'egr_{}'.format(x): {
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'pasito': False,
            } for x in ['último', 'suma', 'prom', 'máx']}
        )

    def obt_tmñ_ciclo(símismo):
        return símismo.n

    def avanzar_modelo(símismo, n_ciclos):
        símismo.ciclo += n_ciclos


class EjIndeterminado(ModeloIndeterminado):
    pass
