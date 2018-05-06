import os
import unittest

import numpy as np

from tinamit.BF import EnvolturaBF
from pruebas.recursos.prueba_bf import ModeloPrueba


dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/prueba_bf.py')


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
            'Lluvia': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Escala': {'unidades': '', 'líms': (0, None)},
            'Máx lluvia': {'unidades': 'm3/mes', 'líms': (0, None)}
        }  # type: dict[str, dict]

        # Iniciar constantes
        cls.envltmodelo.inic_val('Máx lluvia', 15)

        # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
        cls.envltmodelo.simular(tiempo_final=200, vars_interés='Escala')

    def test_leer_vars(símismo):
        """
        Comprobar que los variables se leyeron correctamente.
        """
        símismo.assertDictEqual(símismo.envltmodelo.variables, símismo.envltmodelo.modelo.variables)

    def test_unid_tiempo(símismo):
        """
        Comprobar que las unidades de tiempo se leyeron correctamente.
        """
        símismo.assertEqual('meses', símismo.envltmodelo.unidad_tiempo.lower())

    def test_cmb_vals_inic(símismo):
        """
        Comprobar que los valores iniciales se establecieron correctamente.
        """

        símismo.assertEqual(símismo.envltmodelo.variables['Máx lluvia']['val'], 15)

    def test_simul(símismo):
        """
        Assegurarse que la simulación dió los resultados esperados.
        """

        val_simulado = símismo.envltmodelo.leer_resultados('Escala')[:, 0]

        símismo.assertTrue(np.array_equal(val_simulado, np.arange(0, 201)))


# Comprobar que la EnvolturaBF pueda leer el modelo BF de prueba en todas las formas posibles para cargar un modelo BF.
class Test_CrearEnvolturaBF(unittest.TestCase):

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
