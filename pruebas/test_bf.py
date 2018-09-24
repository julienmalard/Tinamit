import inspect
import os
import unittest

import numpy as np
from numpy import testing as npt

import tinamit.EnvolturasBF
from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from tinamit.BF import EnvolturaBF
from tinamit.BF import ModeloDeterminado

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/BF/prueba_bf.py')


# Comprobar que el modelo BF de prueba corre corectamente
class Test_ModeloSenc(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de MDS.
    """

    @classmethod
    def setUpClass(cls):
        # Generar la Envoltura BF
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


# Comprobar que la EnvolturasBF pueda leer el modelo BF de prueba en todas las formas posibles para cargar un modelo BF.
class Test_CrearEnvolturaBF(unittest.TestCase):
    def test_crear_desde_archivo(símismo):
        # Comprobar creación de la envoltura desde un fuente que contiene un modelo BF.
        envlt = EnvolturaBF(arch_bf)
        símismo.assertIsInstance(envlt, EnvolturaBF)

    def test_crear_desde_clase(símismo):
        # Comprobar creación de la envoltura desde una clase de modelo BF.
        envlt = EnvolturaBF(ModeloPrueba)
        símismo.assertIsInstance(envlt, EnvolturaBF)

    def test_crear_desde_modelobf(símismo):
        # Comprobar creación de la envoltura directamente desde un modelo BF.
        modelo_bf = ModeloPrueba()
        envlt = EnvolturaBF(modelo_bf)
        símismo.assertIsInstance(envlt, EnvolturaBF)


class Test_Envolturas_ModeloImpaciente(unittest.TestCase):
    arch_prb_escrb_ingr = 'prueba_ingr.txt'

    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloDeterminado):
                cls.envolturas_disp[nombre] = obj()

    def test_escribir_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                obj.prep_ingr(n_años_simul=1, archivo=símismo.arch_prb_escrb_ingr)
                obj._gen_dic_vals_inic(archivo=símismo.arch_prb_escrb_ingr)

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
