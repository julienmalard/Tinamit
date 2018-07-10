import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd

from tinamit.Análisis.Datos import SuperBD, Datos
from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from pruebas.test_geog import arch_clim_diario
from pruebas.test_mds import limpiar_mds
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

    def test_simular_fecha_a_entero(símismo):
        res = símismo.mod.simular(t_final=10, t_inic='01/01/2001', vars_interés='Lluvia')
        símismo.assertEqual(len(res['Lluvia']), 10 + 1)

    def test_simular_fecha_a_fecha(símismo):
        res = símismo.mod.simular(t_final='01/01/2002', t_inic='01/01/2001', vars_interés='Lluvia')
        símismo.assertEqual(len(res['Lluvia']), 365 + 1)

    def test_simular_entero_a_entero(símismo):
        res = símismo.mod.simular(t_final=20, t_inic=5, vars_interés='Lluvia')
        símismo.assertEqual(len(res['Lluvia']), 15 + 1)

    def test_simular_entero_a_fecha(símismo):
        with símismo.assertRaises(TypeError):
            símismo.mod.simular(t_final='01/01/2002', t_inic=10)

    def test_fecha_inic_ulterior(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final='01/01/2001', t_inic='01/01/2002')


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


class Test_SimularEnPlazoConDatos(unittest.TestCase):
    def test_simular_none_a_fecha_con_datos(símismo):
        pass

    def test_simular_none_a_entero_con_datos(símismo):
        pass

    def test_simular_none_a_none_con_datos(símismo):
        pass

    def test_simular_fecha_a_none_con_datos(símismo):
        pass

    def test_simular_entero_a_none_con_datos(símismo):
        pass


@unittest.skip
class Test_SimulConDatos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.datos = {
            '708': {'Vacío': [1, 2, 3, 4, 5]},
            '701': {'Vacío': [10, 9, 8, 7, 6]}
        }
        cls.datos_pandas = pd.DataFrame({'Vacío': [1, 2, 3, np.nan, 5]}, index=pd.date_range('1/1/2001', periods=5))
        cls.datos_superbd = SuperBD('prueba', bds=Datos('prb', cls.datos_pandas))

    def test_simular_con_datos_externos_dic(símismo):
        mod = ModeloPrueba(unid_tiempo='día')
        res = mod.simular(t_final=5, vars_interés='Vacío', vals_extern=símismo.datos['708'])
        npt.assert_array_equal(res['Vacío'][1:], símismo.datos['708']['Vacío'])

    def test_simular_con_datos_externos_pandas(símismo):
        mod = ModeloPrueba(unid_tiempo='día')
        res = mod.simular(t_inic='01/01/2001', t_final=5, vars_interés='Vacío', vals_extern=símismo.datos_pandas)
        faltaban = np.isnan(símismo.datos_pandas['Vacío'])
        npt.assert_array_equal(res['Vacío'][not faltaban], símismo.datos_pandas['Vacío'][not faltaban])

    def test_simular_con_datos_espaciales_dic(símismo):
        mod = ModeloPrueba(unid_tiempo='día')
        mod.conectar_datos(símismo.datos, corresp_vars='Vacío')
        res = mod.simular_en(t_final=5)
        for lg, d_res in res.items():
            npt.assert_array_equal(d_res['Vacío'], símismo.datos[lg]['Vacío'])

    def test_simular_con_datos_espaciales_superbd(símismo):
        mod = ModeloPrueba(unid_tiempo='día')
        mod.conectar_datos(símismo.datos_superbd, corresp_vars='Vacío')
        res = mod.simular(t_inic='01/01/2001', t_final=5, vars_interés='Vacío', vals_extern=símismo.datos_pandas)
        for lg, d_res in res.items():
            npt.assert_array_equal(d_res['Vacío'], símismo.datos[lg]['Vacío'])

    def test_simular_en_con_escala_sin_geog(símismo):

        with símismo.assertRaises(ValueError):
            ModeloPrueba(unid_tiempo='día').simular_en(100, escala='municipio')
