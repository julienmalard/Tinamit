import os
import sys
import unittest

import numpy as np
from nose import with_setup

from Unidades import trads
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

        trads.agregar_trad('year', 'año', leng_trad='es', leng_orig='en')
        trads.agregar_trad('year', 'año', leng_trad='es', leng_orig='en')

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

    def test_simular_paralelo(símismo):

        global ejecutando_prueba_primera_vez
        if 'ejecutando_prueba_primera_vez' not in globals():
            ejecutando_prueba_primera_vez = 0
        ejecutando_prueba_primera_vez += 1

        if ejecutando_prueba_primera_vez == 1:
            for ll, mod in símismo.modelos.items():
                with símismo.subTest(mod=ll):

                    t_final = 100
                    sin_paral = {}
                    mod.inic_val_var('Lago', 50)
                    mod.simular(tiempo_final=t_final, vars_interés='Lago')
                    sin_paral['lago_50'] = mod.leer_resultados('Lago')

                    mod.inic_val_var('Lago', 2000)
                    mod.simular(tiempo_final=t_final, vars_interés='Lago')
                    sin_paral['lago_2000'] = mod.leer_resultados('Lago')

                    resultados = mod.simular_paralelo(
                        tiempo_final=t_final, vals_inic={'lago_50': {'Lago': 50}, 'lago_2000': {'Lago': 2000}},
                        devolver='Lago'
                    )

                    símismo.assertDictEqual(sin_paral, resultados)


# Comprobar SuperConectado


# Comprobar 3+ modelos conectados


# Comprobar modelos de estructura jerárquica
