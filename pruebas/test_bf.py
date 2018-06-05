import os
import unittest

import numpy as np

from pruebas.recursos.prueba_bf import ModeloPrueba
from tinamit.BF import EnvolturaBF

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/prueba_bf.py')


# Comprobar que el modelo BF de prueba corre corectamente
class Test_ModeloSenc(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de MDS.
    """

    @classmethod
    def setUpClass(cls):
        print('Test_ModeloSenc')
        # Generar la Envoltura BF
        cls.envltmodelo = EnvolturaBF(arch_bf)

        # Información sobre los variables del modelo de prueba
        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/año', 'líms': (0, None), 'val_inic': 2.3},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Escala': {'unidades': '', 'líms': (0, None)},
            'Máx lluvia': {'unidades': 'm3/año', 'líms': (0, None), 'val_inic': 15}
        }  # type: dict[str, dict]

        # Iniciar variables
        for v, d_v in cls.info_vars.items():
            if 'val_inic' in d_v:
                cls.envltmodelo.inic_val_var(v, d_v['val_inic'])

        # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
        cls.envltmodelo.simular(tiempo_final=200, vars_interés=['Escala', 'Lluvia'])

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
            símismo.envltmodelo.obt_val_actual_var('Máx lluvia'),
            símismo.info_vars['Máx lluvia']['val_inic']
        )

    def test_cambiar_vals_inic_var_dinámico(símismo):
        """
        Comprobar que los valores iniciales de variables cuyos valores cambian aparezcan correctamente en
        los resultados.
        """

        símismo.assertEqual(
            símismo.envltmodelo.leer_resultados('Lluvia')[0],
            símismo.info_vars['Lluvia']['val_inic']
        )

    def test_simul(símismo):
        """
        Asegurarse que la simulación dió los resultados esperados.
        """

        val_simulado = símismo.envltmodelo.leer_resultados('Escala')

        símismo.assertTrue(np.array_equal(val_simulado, np.arange(0, 201)))

    def test_nombre_inválido(símismo):
        """
        Asegurarse que nombres inválidos para modelos se corrijan automáticamente.
        """

        mod = EnvolturaBF(arch_bf, nombre='Nombre_inválido')

        símismo.assertNotIn('_', mod.nombre)


# Comprobar que la EnvolturasBF pueda leer el modelo BF de prueba en todas las formas posibles para cargar un modelo BF.
class Test_CrearEnvolturaBF(unittest.TestCase):
    print('Test_CrearEnvolturaBF')
    def test_crear_desde_archivo(símismo):
        # Comprobar creación de la envoltura desde un archivo que contiene un modelo BF.
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
