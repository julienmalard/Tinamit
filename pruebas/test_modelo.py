import unittest

import numpy as np
import numpy.testing as npt
import xarray.testing as xrt

from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from pruebas.test_geog import arch_clim_diario
from pruebas.test_geog import arch_csv_geog
from pruebas.test_mds import limpiar_mds
from tinamit.Geog import Geografía
from tinamit.Geog import Lugar


class Test_SimularGrupo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generar las instancias de los modelos
        cls.mod = ModeloPrueba()

    def test_simular_grupo_ops_lista(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 4}, {'Lluvia': 5}], vars_interés=['Lluvia']
        )
        símismo.assertSetEqual({'vals_inic0', 'vals_inic1'}, set(res))

    def test_simular_grupo_ops_dict(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic={'4': {'Lluvia': 4}, '5': {'Lluvia': 5}},
            vars_interés=['Lluvia']
        )
        símismo.assertSetEqual({'4', '5'}, set(res))

    def test_simular_grupo_sin_combinar_opciones(símismo):
        vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
        tiempo_final = [100, 200]
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=False,
            nombre_corrida=['1', '2']
        )
        símismo.assertEqual(len(res), 2)

    def test_simular_grupo_combinar_opciones_lista(símismo):
        vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
        tiempo_final = [100, 200]
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_opciones_dic(símismo):
        vals_inic = {'a': {'Lluvia': 1}, 'b': {'Lluvia': 2}}
        tiempo_final = {'c': 100, 'd': 200}
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_opciones_dic_y_lista(símismo):
        res = símismo.mod.simular_grupo(
            t_final={'a': 100, 'b': 200}, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_llaves_dic_opciones_no_iguales(símismo):
        with símismo.assertRaises(ValueError):
            vals_inic = {'1': {'Lluvia': 1}, '2': {'Lluvia': 2}}
            tiempo_final = {'1': 100, '3': 300}  # No igual a las llaves en vals_inic
            símismo.mod.simular_grupo(
                t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'],
                combinar=False
            )

    def test_simular_grupo_con_dict_y_listas_sin_combinaciones(símismo):
        with símismo.assertRaises(TypeError):
            símismo.mod.simular_grupo(
                t_final={'1': 100, '2': 200}, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                combinar=False
            )

    def test_simular_grupo_con_prefijo_nombre(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            nombre_corrida='pre'
        )
        símismo.assertTrue(all(x.startswith('pre') for x in res))

    def test_simular_grupo_con_lista_nombres(símismo):
        nombres = ['corrida 1', 'corrida 2']
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            nombre_corrida=nombres, combinar=False
        )
        símismo.assertSetEqual(set(nombres), set(res))

    def test_simular_grupo_con_lista_nombres_tamaño_error(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular_grupo(
                t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                nombre_corrida=['1', '2', '3'],  # 1 demasiado
                combinar=False
            )

    def test_simular_grupo_con_lista_nombres_y_combinaciones(símismo):
        with símismo.assertRaises(TypeError):
            vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
            tiempo_final = [100, 200]
            símismo.mod.simular_grupo(
                t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True,
                nombre_corrida=['1', '2']
            )

    def test_simular_grupo_sin_combinaciones_tamaño_opciones_error(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular_grupo(
                t_final=[100], vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                combinar=False
            )

    def test_simular_grupo_combinar_con_1_opción(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}], vars_interés=['Lluvia'], combinar=True,
        )
        símismo.assertIn('Lluvia', res['vals_inic0'])

    def test_simular_grupo_sin_opciones_múltiples(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic={'Lluvia': 1}, vars_interés=['Lluvia'], combinar=True,
        )
        símismo.assertIn('Lluvia', res['Corrida Tinamït'])

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


class Test_SimularEnPlazo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')

    def test_simular_none_a_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final='01/01/2001')

    def test_simular_none_a_entero(símismo):
        res = símismo.mod.simular(t_final=10, vars_interés='Lluvia')
        símismo.assertEqual(len(res['Lluvia']), 10 + 1)
        npt.assert_array_equal(res['tiempo'], np.arange(10 + 1))

    def test_simular_fecha_a_entero(símismo):
        res = símismo.mod.simular(t_final=10, t_inic='01/01/2001', vars_interés='Lluvia')

        símismo.assertEqual(len(res['Lluvia']), 10 + 1)
        # noinspection PyTypeChecker
        npt.assert_array_equal(res['tiempo'], np.arange('2001-01-01', '2001-01-12', dtype='datetime64'))

    def test_simular_fecha_a_fecha(símismo):
        res = símismo.mod.simular(t_final='01/01/2002', t_inic='01/01/2001', vars_interés='Lluvia')

        símismo.assertEqual(len(res['Lluvia']), 365 + 1)
        # noinspection PyTypeChecker
        npt.assert_array_equal(res['tiempo'], np.arange('2001-01-01', '2002-01-02', dtype='datetime64'))

    def test_simular_entero_a_entero(símismo):
        res = símismo.mod.simular(t_final=20, t_inic=5, vars_interés='Lluvia')
        símismo.assertEqual(len(res['Lluvia']), 15 + 1)
        npt.assert_array_equal(res['tiempo'], np.arange(5, 20 + 1))

    def test_simular_entero_a_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final='01/01/2002', t_inic=10)


class Test_SimulConClima(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='mes')

    def test_simular_con_datos_clima(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_diarios(
            arch_clim_diario, cols_datos={'Precipitación': 'Lluvia'}, conv={'Precipitación': 1}, c_fecha='Fecha'
        )
        símismo.mod.conectar_var_clima(var='Lluvia', var_clima='Precipitación', conv=1)
        res = símismo.mod.simular(t_final=1, t_inic='1-1-2018', lugar_clima=lugar, vars_interés='Lluvia')
        símismo.assertEqual(res['Lluvia'][0], 15)

    def test_simular_con_escenario_sin_lugar(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final=100, clima='8.5')


class Test_SimulConDatos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')
        cls.datos = {
            'tiempo': np.arange(21), 'Vacío': np.random.random(21)
        }  # 21 días

        # noinspection PyTypeChecker
        cls.datos_fecha = {
            'tiempo': np.arange('1999-12-31', '2000-01-20', dtype='datetime64'), 'Vacío': np.random.random(20)
        }  # 21 días

    def test_simular_datos_fecha(símismo):
        res = símismo.mod.simular(
            t_inic='2000-01-01', t_final='2000-01-10', bd=símismo.datos_fecha, vars_interés='Vacío'
        )
        _verificar_resultados('Vacío', res=res, datos=símismo.datos_fecha, rango_t=['2000-01-01', '2000-01-11'])

    def test_simular_datos_sin_fecha(símismo):
        res = símismo.mod.simular(t_inic=5, t_final=10, bd=símismo.datos, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, datos=símismo.datos, rango_t=[5, 11])

    def test_simular_datos_fecha_sin_rango_tiempo(símismo):
        res = símismo.mod.simular(bd=símismo.datos_fecha, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, datos=símismo.datos_fecha, rango_t=[None, None])

    def test_simular_datos_sin_fecha_sin_rango_tiempo(símismo):
        res = símismo.mod.simular(bd=símismo.datos, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, símismo.datos, [None, None])

    def test_simular_datos_fecha_con_tiempo_inic(símismo):
        res = símismo.mod.simular(t_inic='01-01-2000', bd=símismo.datos_fecha, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, datos=símismo.datos_fecha, rango_t=['2000-01-01', None])

    def test_simular_datos_fecha_con_tiempo_final(símismo):
        res = símismo.mod.simular(t_final='2000-01-10', bd=símismo.datos_fecha, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, datos=símismo.datos_fecha, rango_t=[None, '2000-01-11'])

    def test_simular_datos_sin_fecha_con_tiempo_inic(símismo):
        res = símismo.mod.simular(t_inic=5, bd=símismo.datos, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, símismo.datos, [5, None])

    def test_simular_datos_sin_fecha_con_tiempo_final(símismo):
        res = símismo.mod.simular(t_final=10, bd=símismo.datos, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, símismo.datos, [0, 11])

    def test_simular_datos_sin_fecha_tiempo_inic_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_inic='01-01-2002', bd=símismo.datos)

    def test_simular_datos_sin_fecha_tiempo_final_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final='01-01-2002', bd=símismo.datos)

    def test_simular_datos_fecha_tiempo_inic_numérico(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_inic=10, bd=símismo.datos_fecha)

    def test_simular_datos_fecha_tiempo_final_numérico(símismo):
        res = símismo.mod.simular(t_final=10, bd=símismo.datos_fecha, vars_interés='Vacío')
        _verificar_resultados('Vacío', res, datos=símismo.datos_fecha, rango_t=[None, 11])

    def test_simular_datos_vars_inic(símismo):
        res = símismo.mod.simular(t_final=10, bd=símismo.datos, vals_inic='Vacío', vars_interés='Vacío')
        símismo.assertEqual(res['Vacío'][0], símismo.datos['Vacío'][0])

    def test_simular_datos_vars_extern(símismo):
        res = símismo.mod.simular(t_final=10, bd=símismo.datos, vals_extern='Vacío', vars_interés='Vacío')
        _verificar_resultados('Vacío', res, símismo.datos, [0, 11])

    def test_simular_datos_corresp_vars_inic(símismo):
        res = símismo.mod.simular(
            t_final=10, bd=símismo.datos, vals_inic={'Lluvia': 'Vacío'},
            vars_interés='Lluvia'
        )
        npt.assert_array_equal(res['Lluvia'].values[0], símismo.datos['Vacío'][0])

    def test_simular_datos_corresp_vars_extern(símismo):
        res = símismo.mod.simular(
            t_final=10, bd=símismo.datos, vals_extern={'Lluvia': 'Vacío'},
            vars_interés='Lluvia'
        )
        npt.assert_array_equal(res['Lluvia'].values, símismo.datos['Vacío'][:11])

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


class Test_SimulConDatosGeog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')
        cls.geog = Geografía('Prueba Guatemala', archivo=arch_csv_geog)
        cls.datos = {
            '708': {'tiempo': np.arange(21), 'Vacío': np.random.random(21)},
            '701': {'tiempo': np.arange(21), 'Vacío': np.random.random(21)},
            '7': {'tiempo': np.arange(21), 'Vacío': np.random.random(21)}
        }  # 3 lugares, 21 días

    def _verificar_simul(símismo, res, var='Vacío'):
        for lg, res_lg in res.items():
            if lg in símismo.datos:
                verdad = símismo.datos[lg][var][np.isin(símismo.datos[lg]['tiempo'], res[lg]['tiempo'])]
                npt.assert_array_equal(verdad, res[lg][var].values)

    def test_simular_en_lugar_único(símismo):
        res = símismo.mod.simular_en(t_final=10, en='7', geog=símismo.geog, bd=símismo.datos, vars_interés='Vacío')
        símismo.assertSetEqual(set(res), {'7'})
        símismo._verificar_simul(res)

    def test_simular_en_lugar_con_escala(símismo):
        res = símismo.mod.simular_en(
            t_final=10, en='7', escala='municipio', geog=símismo.geog, bd=símismo.datos, vars_interés='Vacío'
        )
        símismo.assertSetEqual(set(res), set([str(i) for i in range(701, 720)]))
        símismo._verificar_simul(res)

    def test_simular_en_lugar_sin_datos(símismo):
        res = símismo.mod.simular_en(t_final=10, en='7', escala='municipio', geog=símismo.geog, vars_interés='Vacío')
        símismo.assertSetEqual(set(res), set([str(i) for i in range(701, 720)]))

    def test_simular_en_lugar_sin_geog(símismo):
        res = símismo.mod.simular_en(t_final=10, en='7', bd=símismo.datos, vars_interés='Vacío')
        símismo.assertSetEqual(set(res), {'7'})
        símismo._verificar_simul(res)

    def test_simular_en_lugar_con_escala_sin_geog(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular_en(t_final=10, en='7', escala='municipio', bd=símismo.datos, vars_interés='Vacío')


def _verificar_resultados(var, res, datos, rango_t):
    rango_t[0] = rango_t[0] or datos['tiempo'][0]
    rango_t[1] = rango_t[1] or datos['tiempo'][-1] + 1

    # noinspection PyTypeChecker
    if isinstance(rango_t[0], str):
        npt.assert_array_equal(res['tiempo'], np.arange(*rango_t, dtype='datetime64'))
    else:
        npt.assert_array_equal(res['tiempo'], np.arange(*rango_t))
    npt.assert_array_equal(
        res[var], datos[var][np.isin(datos['tiempo'], res['tiempo'].values)]
    )
