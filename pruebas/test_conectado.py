import os
import unittest

import numpy.testing as npt

from pruebas.test_mds import tipos_modelos, limpiar_mds
from tinamit.BF import EnvolturaBF
from tinamit.Conectado import Conectado, SuperConectado
from tinamit.EnvolturasMDS import ModeloPySD
from tinamit.Unidades import trads

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/prueba_bf.py')
arch_mds = os.path.join(dir_act, 'recursos/prueba_senc.mdl')
arch_mod_vacío = os.path.join(dir_act, 'recursos/prueba_vacía.mdl')


# Comprobar Conectado
class Test_Conectado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Preparar los modelos genéricos necesarios para las pruebas.
        """
        print('Test_Conectado')

        # Generar las instancias de los modelos individuales y conectados
        cls.mods_mds = {ll: d['envlt'](d['prueba']) for ll, d in tipos_modelos.items()}
        cls.mod_bf = EnvolturaBF(arch_bf)

        cls.modelos = {ll: Conectado() for ll in cls.mods_mds}  # type: dict[str, Conectado]

        # Agregar traducciones necesarias.
        trads.agregar_trad('year', 'año', leng_trad='es', leng_orig='en')
        trads.agregar_trad('month', 'mes', leng_trad='es', leng_orig='en')

        # Conectar los modelos
        for mds, mod_con in cls.modelos.items():
            mod_con.estab_bf(cls.mod_bf)
            mod_con.estab_mds(cls.mods_mds[mds])

            mod_con.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
            mod_con.conectar(var_mds='Lago', var_bf='Lago', mds_fuente=True)
            mod_con.conectar(var_mds='Aleatorio', var_bf='Aleatorio', mds_fuente=False)

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
        Comprobar que simulaciones en paralelo den el mismo resultado que las mismas simulaciones individuales.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                t_final = 100
                referencia = {}
                mod.inic_val_var('Nivel lago inicial', 50)
                mod.simular(tiempo_final=t_final, vars_interés='Lago')
                referencia['lago_50'] = {'mds_Lago': mod.leer_resultados('Lago')}

                mod.inic_val_var('Nivel lago inicial', 2000)
                mod.simular(tiempo_final=t_final, vars_interés='Lago')
                referencia['lago_2000'] = {'mds_Lago': mod.leer_resultados('Lago')}

                resultados = mod.simular_paralelo(
                    tiempo_final=t_final,
                    vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
                    devolver='Lago'
                )

                for c in resultados:
                    npt.assert_allclose(referencia[c]['mds_Lago'], resultados[c]['mds_Lago'], rtol=0.001)

    def test_simular_paralelo_sin_paralelo(símismo):
        """
        Comprobamos que :func:`SuperConectado.simular_paralelo` funcione igual con o sin paralelización.

        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                t_final = 100

                sin_paral = mod.simular_paralelo(
                    tiempo_final=t_final,
                    vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
                    devolver='Lago',
                    nombre_corrida='Corrida Tinamït Prueba sin paralelo',
                    paralelo=False
                )

                con_paral = mod.simular_paralelo(
                    tiempo_final=t_final,
                    vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
                    devolver='Lago',
                    nombre_corrida='Corrida Tinamït Prueba paralelo'
                )

                for c in sin_paral:
                    npt.assert_allclose(sin_paral[c]['mds_Lago'], con_paral[c]['mds_Lago'], rtol=0.001)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


# Comprobar 3+ modelos conectados
class Test_3ModelosConectados(unittest.TestCase):
    print('Test_3ModelosConectados')
    def test_conexión_horizontal(símismo):
        """
        Comprobar que la conexión de variables se haga correctamente con 3 submodelos conectados directamente
        en el mismo :class:`SuperConectado`.
        """

        # Crear los 3 modelos
        bf = EnvolturaBF(arch_bf, nombre='bf')
        tercio = ModeloPySD(arch_mod_vacío, nombre='tercio')
        mds = ModeloPySD(arch_mds, nombre='mds')

        # El Conectado
        conectado = SuperConectado()
        for m in [bf, mds, tercio]:
            conectado.agregar_modelo(m)

        # Conectar variables entre dos de los modelos por el intermediario del tercero.
        conectado.conectar_vars(var_fuente='Aleatorio', modelo_fuente='bf',
                                var_recip='Aleatorio', modelo_recip='tercio')
        conectado.conectar_vars(var_fuente='Aleatorio', modelo_fuente='tercio',
                                var_recip='Aleatorio', modelo_recip='mds')

        # Simular
        res = conectado.simular(100, vars_interés=['bf_Aleatorio', 'mds_Aleatorio'])

        # Comprobar que los resultados son iguales.
        npt.assert_allclose(res['bf_Aleatorio'], res['mds_Aleatorio'], rtol=0.001)

    def test_conexión_jerárquica(símismo):
        """
        Comprobar que 3 modelos conectados de manera jerárquica a través de 2 :class:`SuperConectados` funcione
        bien. No es la manera más fácil o directa de conectar 3+ modelos, pero es importante que pueda funcionar
        esta manera también.
        """

        # Los tres modelos
        bf = EnvolturaBF(arch_bf, nombre='bf')
        tercio = ModeloPySD(arch_mod_vacío, nombre='tercio')
        mds = ModeloPySD(arch_mds, nombre='mds')

        # El primer Conectado
        conectado_sub = SuperConectado(nombre='sub')
        conectado_sub.agregar_modelo(tercio)
        conectado_sub.agregar_modelo(mds)
        conectado_sub.conectar_vars(
            var_fuente='Aleatorio', modelo_fuente='tercio',
            var_recip='Aleatorio', modelo_recip='mds'
        )

        # El segundo Conectado
        conectado = SuperConectado()
        conectado.agregar_modelo(bf)
        conectado.agregar_modelo(conectado_sub)
        conectado.conectar_vars(
            var_fuente='Aleatorio', modelo_fuente='bf',
            var_recip='tercio_Aleatorio', modelo_recip='sub'
        )

        # Correr la simulación
        res = conectado.simular(100, vars_interés=['bf_Aleatorio', 'sub_mds_Aleatorio'])

        # Verificar que los resultados sean iguales.
        npt.assert_allclose(res['bf_Aleatorio'], res['sub_mds_Aleatorio'], rtol=0.001)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()
