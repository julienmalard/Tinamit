import os
import unittest

import numpy.testing as npt
import xarray.testing as xrt

from pruebas.recursos.mod.prueba_mod import ModeloAlea
from pruebas.test_mds import generar_modelos_prueba, limpiar_mds
from tinamit.conect import Conectado, SuperConectado
from tinamit.envolt.bf import gen_bf
from tinamit.mod import OpsSimulGrupo
from tinamit.unids import trads

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/bf/prueba_bf.py')
arch_mds = os.path.join(dir_act, 'recursos/mds/prueba_senc_mdl.mdl')


# Comprobar Conectado
class TestConectado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Preparar los modelos genéricos necesarios para las pruebas.
        """

        # Generar las instancias de los modelos individuales y conectados
        cls.mods_mds = generar_modelos_prueba()

        cls.modelos = {ll: Conectado(bf=gen_bf(arch_bf), mds=mod) for ll, mod in cls.mods_mds.items()}

        # Agregar traducciones necesarias.
        trads.agregar_trad('year', 'año', leng_trad='es', leng_orig='en')
        trads.agregar_trad('month', 'mes', leng_trad='es', leng_orig='en')

        # Conectar los modelos
        for mod in cls.modelos.values():
            mod.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
            mod.conectar(var_mds='Lago', var_bf='Lago', mds_fuente=True)

    def test_reinic_vals(símismo):
        """
        Asegurarse que los variables se reinicializen correctamente después de una simulación.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                egr1 = mod.simular(100, vars_interés=list(mod.variables))
                egr2 = mod.simular(100, vars_interés=list(mod.variables))

                for r1, r2 in zip(egr1, egr2):
                    xrt.assert_equal(r1.vals, r2.vals)

    def test_intercambio_de_variables(símismo):
        """
        Asegurarse que valores intercambiados tengan valores iguales en los resultados de ambos modelos.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                res = mod.simular(100)

                npt.assert_array_equal(
                    res['bf']['Lluvia'].vals.values.flatten(), res['mds']['Lluvia'].vals.values.flatten()
                )
                npt.assert_array_equal(
                    res['bf']['Lago'].vals.values.flatten(), res['mds']['Lago'].vals.values.flatten()
                )

    def test_simular_grupo(símismo):
        """
        Comprobar que simulaciones en grupo den el mismo resultado que las mismas simulaciones individuales.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                t_final = 10
                ref = {
                    'lago_%i' % i: mod.simular(t_final, extern={'Nivel lago inicial': i}, vars_interés='Lago')
                    for i in [50, 2000]
                }

                ops = OpsSimulGrupo(
                    t_final, extern=[{'Nivel lago inicial': 50}, {'Nivel lago inicial': 2000}],
                    nombre=['lago_50', 'lago_2000'],
                    vars_interés='Lago'
                )
                resultados = mod.simular_grupo(ops)

                for c in ref:
                    npt.assert_allclose(
                        ref[c]['bf']['Lago'].vals.values.flatten(),
                        resultados[c]['bf']['Lago'].vals.values.flatten(), rtol=0.001
                    )

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


class Test3ModelosConectados(unittest.TestCase):
    """
    Comprobar 3+ modelos conectados.
    """

    def test_conexión_horizontal(símismo):
        """
        Comprobar que la conexión de variables se haga correctamente con 3 submodelos conectados directamente
        en el mismo :class:`SuperConectado`.
        """

        # Crear los 3 modelos
        mod_1 = ModeloAlea(nombre='modelo 1')
        mod_2 = ModeloAlea(nombre='modelo 2')
        mod_3 = ModeloAlea(nombre='modelo 3')

        # El Conectado
        conectado = SuperConectado([mod_1, mod_2, mod_3])

        # Conectar variables entre dos de los modelos por el intermediario del tercero.
        conectado.conectar_vars(
            var_fuente='Aleatorio', modelo_fuente='modelo 1', var_recip='Vacío', modelo_recip='modelo 2'
        )
        conectado.conectar_vars(
            var_fuente='Vacío', modelo_fuente='modelo 2', var_recip='Vacío', modelo_recip='modelo 3'
        )

        # Simular
        res = conectado.simular(10, vars_interés=[mod_1.variables['Aleatorio'], mod_3.variables['Vacío']])

        # Comprobar que los resultados son iguales.
        xrt.assert_equal(res['modelo 1']['Aleatorio'].vals, res['modelo 3']['Vacío'].vals)

    def test_conexión_jerárquica(símismo):
        """
        Comprobar que 3 modelos conectados de manera jerárquica a través de 2 :class:`SuperConectados` funcione
        bien. No es la manera más fácil o directa de conectar 3+ modelos, pero es importante que pueda funcionar
        esta manera también.
        """

        # Los tres modelos
        mod_1 = ModeloAlea(nombre='modelo 1')
        mod_2 = ModeloAlea(nombre='modelo 2')
        mod_3 = ModeloAlea(nombre='modelo 3')

        # El primer Conectado
        conectado_sub = SuperConectado(nombre='sub', modelos=[mod_1, mod_2])
        conectado_sub.conectar_vars(
            var_fuente='Aleatorio', modelo_fuente='modelo 1', var_recip='Vacío', modelo_recip='modelo 2'
        )

        # El segundo Conectado
        conectado = SuperConectado([conectado_sub, mod_3])
        conectado.conectar_vars(
            var_fuente=mod_2.variables['Vacío'], var_recip='Vacío', modelo_recip='modelo 3'
        )

        # Correr la simulación
        res = conectado.simular(10, vars_interés=[mod_1.variables['Aleatorio'], mod_3.variables['Vacío']])

        # Verificar que los resultados sean iguales.
        xrt.assert_equal(res['sub']['modelo 1']['Aleatorio'].vals, res['modelo 3']['Vacío'].vals)
