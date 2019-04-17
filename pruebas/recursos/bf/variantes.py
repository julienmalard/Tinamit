import numpy as np

from tinamit.envolt.bf import ModeloBloques, ModeloDeterminado, ModeloIndeterminado


class EjBloques(ModeloBloques):

    def __init__(símismo, nombre, blqs, unid_tiempo):
        símismo.blqs = blqs
        símismo.unid_tiempo = unid_tiempo

        super().__init__(nombre=nombre)

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        dic = {
            'ciclo': símismo.ciclo, 'pasito': np.arange(símismo.obt_tmñ_ciclo()),
            'bloque': np.arange(len(símismo.blqs))
        }

        dic.update(
            {'egr_{}'.format(x): símismo.obt_val_actual_var('ingr_{}'.format(x))
             for x in ['último', 'suma', 'prom', 'máx']}
        )

        return dic

    def _gen_dic_vals_inic(símismo):
        por_pasito = símismo._vars_por_pasito()
        tmñ = símismo.obt_tmñ_ciclo()
        blqs = len(símismo.obt_tmñ_bloques())

        por_blqs = símismo._vars_por_bloques()

        dic_inic = {
            vr: (np.zeros(tmñ) if vr in por_pasito else (np.zeros(blqs) if vr in por_blqs else -1))
            for vr in símismo.variables
        }
        dic_inic['pasito'] = np.arange(tmñ)
        dic_inic['bloque'] = np.arange(blqs)

        return dic_inic

    def cerrar(símismo):
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
                'por': 'pasito',
            },
            'bloque': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'por': 'bloque'
            },
            'ingr_directo': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'por': 'pasito'
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
            } for x in ['último', 'suma', 'prom', 'máx']}
        )

    def obt_tmñ_bloques(símismo):
        return símismo.blqs

    def avanzar_modelo(símismo, n_ciclos):
        pass

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        pass


class EjDeterminado(ModeloDeterminado):

    def __init__(símismo, nombre, n, unid_tiempo):
        símismo.n = n
        símismo.unid_tiempo = unid_tiempo

        super().__init__(nombre=nombre)

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
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
            if vr in por_pasito else -1 for vr in símismo.variables
        }

    def cerrar(símismo):
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
                'por': 'pasito',
            },
            'ingr_directo': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'por': 'pasito'
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
            } for x in ['último', 'suma', 'prom', 'máx']}
        )

    def obt_tmñ_ciclo(símismo):
        return símismo.n

    def avanzar_modelo(símismo, n_ciclos):
        pass

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        pass


class EjIndeterminado(ModeloIndeterminado):

    def __init__(símismo, nombre, rango_n, unid_tiempo):
        símismo.rango_n = rango_n
        símismo.unid_tiempo = unid_tiempo
        símismo.n = np.random.randint(*rango_n)

        super().__init__(nombre=nombre)

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        dic = {'ciclo': símismo.ciclo, 'pasito': np.arange(símismo.n)}

        dic.update(
            {'egr_{}'.format(x): símismo.obt_val_actual_var('ingr_{}'.format(x))
             for x in ['último', 'suma', 'prom', 'máx']}
        )

        return dic

    def _gen_dic_vals_inic(símismo):
        return {
            vr: -1 if vr == 'ciclo' else 0 for vr in símismo.variables
        }

    def cerrar(símismo):
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
                'por': 'pasito',
            },
            'ingr_directo': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'por': 'ciclo'
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
            } for x in ['último', 'suma', 'prom', 'máx']}
        )

    def mandar_modelo(símismo):
        símismo.n = np.random.randint(*símismo.rango_n)
        return símismo.n

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        pass
