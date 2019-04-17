import inspect
import os
import unittest

import numpy as np
from numpy import testing as npt

from pruebas.recursos.bf.prueba_bf import ModeloPrueba
from tinamit.BF import ModeloImpaciente
from tinamit.envolt.bf import gen_bf, EnvolturaBF

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/bf/prueba_mod.py')
arch_bf_flexible = os.path.join(dir_act, 'recursos/bf/modelo_flexible.py')


class TestModeloDeter(unittest.TestCase):
    pass


class TestModeloIndeter(unittest.TestCase):
    pass


class TestModeloBloques(unittest.TestCase):
    pass


class TestGenAuto(unittest.TestCase):
    def test_instancia(símismo):
        mod = gen_bf(ModeloPrueba())
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_clase(símismo):
        mod = gen_bf(ModeloPrueba)
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_instancia(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_instancia.py'))
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_clase(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_clase.py'))
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_instancia_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_instancia_no_identificada.py'))
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_clase_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_clase_no_identificada.py'))
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_múltiples(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_múltiples.py'))
        símismo.assertEqual(mod.unidad_tiempo(), 'años')

    def test_archivo_múltiples_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_múltiples_no_identificada.py'))
        símismo.assertIsInstance(mod, EnvolturaBF)

    def test_archivo_vacío(símismo):
        with símismo.assertRaises(AttributeError):
            gen_bf(símismo._obt_recurso('arch_vacío.py'))

    def test_tipo_no_válido(símismo):
        with símismo.assertRaises(TypeError):
            gen_bf(123)

    def test_archivo_no_existe(símismo):
        with símismo.assertRaises(FileNotFoundError):
            gen_bf('નમસ્તે')

    def test_archivo_no_python(símismo):
        with símismo.assertRaises(ValueError):
            gen_bf(símismo._obt_recurso('no_python.txt'))

    @staticmethod
    def _obt_recurso(archivo):
        return os.path.join('recursos/bf/_prbs_arch', archivo)


# Comprobar que el modelo bf de prueba corre corectamente
class Test_ModeloSenc(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de mds.
    """

    @classmethod
    def setUpClass(cls):
        # Generar la Envoltura bf
        cls.envltmodelo = EnvolturaBF(arch_bf)

        # Información sobre los variables del modelo de prueba
        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/año', 'líms': (0, None), 'val_inic': 2.3},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Escala': {'unidades': '', 'líms': (0, None)},
            'Vacío': {'unidades': 'm3/año', 'líms': (0, None), 'val_inic': 15}
        }  # type: dict[str, dict]

        # Iniciar variables
        vals_inic = {vr: d['val_inic'] for vr, d in cls.info_vars.items() if 'val_inic' in d}

        # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
        cls.envltmodelo.simular(t_final=200, vals_inic=vals_inic, vars_interés=['Escala', 'Lluvia'])

    def test_leer_vars(símismo):
        """
        Comprobar que los variables se leyeron correctamente.
        """
        símismo.assertDictEqual(símismo.envltmodelo.variables, símismo.envltmodelo.modelo.variables)

    def test_unid_tiempo(símismo):
        """
        Comprobar que las unidades de tiempo se leyeron correctamente.
        """
        símismo.assertEqual('años', símismo.envltmodelo.unidad_tiempo())

    def test_cambiar_vals_inic_constante(símismo):
        """
        Comprobar que los valores iniciales se establecieron correctamente.
        """

        símismo.assertEqual(
            símismo.envltmodelo.obt_val_actual_var('Vacío'),
            símismo.info_vars['Vacío']['val_inic']
        )

    def test_cambiar_vals_inic_var_dinámico(símismo):
        """
        Comprobar que los valores iniciales de variables cuyos valores cambian aparezcan correctamente en
        los resultados.
        """

        símismo.assertEqual(
            símismo.envltmodelo.leer_resultados('Lluvia')['Lluvia'][0],
            símismo.info_vars['Lluvia']['val_inic']
        )

    def test_simul(símismo):
        """
        Asegurarse que la simulación dió los resultados esperados.
        """

        val_simulado = símismo.envltmodelo.leer_resultados('Escala')['Escala']

        npt.assert_array_equal(val_simulado, np.arange(0, 201))

    def test_nombre_inválido(símismo):
        """
        Asegurarse que nombres inválidos para modelos se corrijan automáticamente.
        """

        mod = EnvolturaBF(arch_bf, nombre='Nombre_inválido')

        símismo.assertNotIn('_', mod.nombre)


class Test_Envolturas_ModeloImpaciente(unittest.TestCase):
    arch_prb_escrb_ingr = 'prueba_ingr.txt'

    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloImpaciente):
                cls.envolturas_disp[nombre] = obj()

    def test_escribir_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                obj.escribir_ingr(n_años_simul=1, archivo=símismo.arch_prb_escrb_ingr)
                obj.leer_archivo_vals_inic(archivo=símismo.arch_prb_escrb_ingr)

                d_ref = obj.cargar_ref_ejemplo_vals_inic()

                for v in obj.variables:
                    act = obj.variables[v]['val']
                    ref = d_ref[v]['val']
                    npt.assert_equal(ref, act)

    def test_leer_egresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                if obj.prb_arch_egr is not None:
                    dic_ref = obj.cargar_ref_ejemplo_egr()

                    dic_egr = obj.leer_archivo_egr(n_años_egr=1, archivo=obj.prb_arch_egr)

                    for v, val in dic_egr.items():
                        ref = dic_ref[v]
                        npt.assert_equal(val, ref)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.arch_prb_escrb_ingr):
            os.remove(cls.arch_prb_escrb_ingr)


@unittest.SkipTest
class Test_ModeloFlexible(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = EnvolturaBF(arch_bf_flexible)

    def test_simular(símismo):
        res = símismo.mod.simular(100, vars_interés='Escala')
        npt.assert_array_equal(res['Escala'], np.arange(100 + 1))
