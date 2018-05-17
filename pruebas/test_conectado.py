import os
import unittest

import numpy.testing as npt

from tinamit.Unidades import trads
from pruebas.test_mds import tipos_modelos, limpiar_mds
from tinamit.BF import EnvolturaBF
from tinamit.Conectado import Conectado

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
        trads.agregar_trad('month', 'mes', leng_trad='es', leng_orig='en')

        for mds, mod_con in cls.modelos.items():
            mod_con.estab_bf(cls.mod_bf)
            mod_con.estab_mds(cls.mods_mds[mds])

            mod_con.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
            mod_con.conectar(var_mds='Lago', var_bf='Lago', mds_fuente=True)

    def test_intercambio_de_variables_en_simular(símismo):
        """
        Asegurarse que valores intercambiados tengan valores iguales en los resultados de ambos modelos.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                mod.simular(tiempo_final=100, vars_interés=['bf_Aleatorio', 'mds_Aleatorio'])
                egr_bf = mod.leer_resultados('bf_Aleatorio')[1:]

                try:
                    egr_mds = mod.mds.leer_resultados('Aleatorio')[::12][1:]
                except NotImplementedError:
                    egr_mds = mod.leer_resultados('mds_Aleatorio')[1:]

                npt.assert_allclose(egr_bf, egr_mds, rtol=0.001)

    def test_simular_paralelo(símismo):
        """

        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                t_final = 100
                referencia = {}
                mod.inic_val_var('Nivel lago inicial', 50)
                mod.simular(tiempo_final=t_final, vars_interés='Lago')
                referencia['Corrida Tinamït_lago_50'] = {'mds_Lago': mod.leer_resultados('Lago')}

                mod.inic_val_var('Nivel lago inicial', 2000)
                mod.simular(tiempo_final=t_final, vars_interés='Lago')
                referencia['Corrida Tinamït_lago_2000'] = {'mds_Lago': mod.leer_resultados('Lago')}

                resultados = mod.simular_paralelo(
                    tiempo_final=t_final,
                    vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
                    devolver='Lago'
                )

                for c in resultados:
                    npt.assert_allclose(referencia[c]['mds_Lago'], resultados[c]['mds_Lago'], rtol=0.001)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()

# Comprobar SuperConectado


# Comprobar 3+ modelos conectados


# Comprobar modelos de estructura jerárquica
