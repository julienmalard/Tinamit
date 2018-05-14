import os
import unittest

import numpy as np

from tinamit.BF import EnvolturaBF
from tinamit.Conectado import Conectado
from pruebas.test_mds import tipos_modelos

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/prueba_bf.py')


# Comprobar Conectado
class Test_Conectado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Generar las instancias de los modelos
        cls.mods_mds = {ll: d['envlt'](d['prueba']) for ll, d in tipos_modelos.items()}
        cls.mod_bf = EnvolturaBF(arch_bf)

        cls.modelos = {ll: Conectado() for ll in cls.mods_mds}  # type: dict[str, Conectado]
        for mds, mod_con in cls.modelos.items():
            mod_con.estab_bf(cls.mod_bf)
            mod_con.estab_mds(cls.mods_mds[mds])

            mod_con.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)

    def test_simular(símismo):
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                mod.simular(tiempo_final=100, vars_interés=['bf_Lluvia', 'mds_Lluvia'])
                egr_bf = mod.leer_resultados('bf_Lluvia')[1:]
                try:
                    egr_mds = mod.mds.leer_resultados('Lluvia')[::12][1:]
                except NotImplementedError:
                    egr_mds = mod.leer_resultados('mds_Lluvia')[1:]
                símismo.assertTrue(np.array_equal(np.round(egr_bf, 1), np.round(egr_mds, 1)))


# Comprobar SuperConectado


# Comprobar 3+ modelos conectados


# Comprobar modelos de estructura jerárquica
