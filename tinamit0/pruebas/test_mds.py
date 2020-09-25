import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import xarray.testing as xrt

from tinamit.envolt.mds import ModeloVensimDLL, ModeloPySD, ModeloDS, gen_mds, \
    ErrorNoInstalado
# Los tipos de modelos DS que queremos comprobar.
from tinamit.tiempo.tiempo import EspecTiempo

tipos_modelos = {
    'PySD_Vensim': {'envlt': ModeloPySD, 'prueba': 'recursos/mds/prueba_senc_mdl.mdl'},
    'PySD_XMILE': {'envlt': ModeloPySD, 'prueba': 'recursos/mds/prueba_senc_xml.xmile'},
    'PySD_Py': {'envlt': ModeloPySD, 'prueba': 'recursos/mds/prueba_senc_py.py'},
    'dllVensim': {'envlt': ModeloVensimDLL, 'prueba': 'recursos/mds/prueba_senc_vpm.vpm'}
}

# Agregar la ubicación del fuente actual
dir_act = os.path.split(__file__)[0]
for d_m in tipos_modelos.values():
    d_m['prueba'] = os.path.join(dir_act, d_m['prueba'])


def generar_modelos_prueba():
    mods = {}
    for nmb, dic in tipos_modelos.items():
        cls = dic['envlt']
        if cls.instalado():
            mods[nmb] = cls(dic['prueba'])

    return mods


class TestLeerModelos(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de mds.
    """

    @classmethod
    def setUpClass(cls):

        # Generar las instancias de los modelos
        cls.modelos = generar_modelos_prueba()

        # Información sobre los variables del modelo de prueba
        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/mes', 'líms': (0, np.inf)},
            'Nivel lago inicial': {'unidades': 'm3', 'líms': (0, np.inf)},
            'Flujo río': {'unidades': 'm3/mes', 'líms': (0, np.inf)},
            'Lago': {'unidades': 'm3', 'líms': (0, np.inf)},
            'Evaporación': {'unidades': 'm3/mes', 'líms': (0, np.inf)},
            'Aleatorio': {'unidades': 'Sdmn', 'líms': (0, 1)},
        }

    def test_leer_vars(símismo):
        """
        Comprobar que los nombres de los variables se leyeron correctamente.
        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                vars_modelo = {str(vr) for vr in mod.variables}
                símismo.assertSetEqual(set(símismo.info_vars), vars_modelo)

    def test_unid_tiempo(símismo):
        """
        Comprobar que las unidades de tiempo se leyeron correctamente.
        """
        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                símismo.assertEqual('mes', mod.unidad_tiempo())

    def test_leer_info(símismo):
        """
        Comprobar que la documentación de cada variable se leyó correctamente.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                símismo.assertTrue(len(mod.variables[v].info) > 0 for v in mod.variables)

    def test_leer_unidades(símismo):
        """
        Comprobar que las unidades de los variables se leyeron correctamente.
        """

        unids = {v: d_v['unidades'].lower() for v, d_v in símismo.info_vars.items()}

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                unids_mod = {str(v): mod.variables[v].unid.lower() for v in mod.variables}
                símismo.assertDictEqual(unids, unids_mod)

    def test_leer_líms(símismo):
        """
        Comprobar que los límites de los variables se leyeron correctamente.
        """

        unids = {v: d_v['líms'] for v, d_v in símismo.info_vars.items()}

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                unids_mod = {str(v): mod.variables[v].líms for v in mod.variables}
                símismo.assertDictEqual(unids, unids_mod)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


class TestSimular(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        # Generar las instancias de los modelos
        cls.modelos = generar_modelos_prueba()
        cls.vals_inic = {
            'Nivel lago inicial': 1450,
            'Aleatorio': 2.3,
        }

        cls.res = {}
        for nmb, mod in cls.modelos.items():
            # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
            cls.res[nmb] = mod.simular(
                t=200, extern=cls.vals_inic, vars_interés=['Lago', 'Aleatorio', 'Nivel lago inicial']
            )

    def test_cmb_vals_inic_constante_en_resultados(símismo):
        """
        Comprobar que los valores iniciales se establecieron correctamente en los resultados.
        """

        for nmb, res in símismo.res.items():
            v = 'Nivel lago inicial'

            with símismo.subTest(mod=nmb):
                npt.assert_array_equal(res[v].vals, símismo.vals_inic[v])

    def test_cambiar_vals_inic_var_dinámico(símismo):
        """
        Asegurarse que los valores iniciales de variables dinámicos aparezcan en el paso 0 de los resultados.
        """

        for nmb, res in símismo.res.items():
            v = 'Aleatorio'
            with símismo.subTest(mod=nmb):
                npt.assert_allclose(res[v].vals[0].values, símismo.vals_inic[v], rtol=0.0001)

    def test_cambiar_vals_inic_nivel(símismo):
        """
        Comprobar que valores iniciales pasados a un variable de valor inicial aparezcan en los resultados también.
        """

        for nmb, res in símismo.res.items():
            with símismo.subTest(mod=nmb):
                símismo.assertEqual(
                    res['Lago'].vals.values[0],
                    símismo.vals_inic['Nivel lago inicial']
                )

    def test_resultados_simul(símismo):
        """
        Assegurarse que la simulación dió los resultados esperados.
        """

        for nmb, res in símismo.res.items():
            with símismo.subTest(mod=nmb):
                # Leer el resultado del último día de simulación pára el variable "Lago"
                val_simulado = res['Lago'].vals.values[-1]

                # Debería ser aproximativamente igual a 100
                símismo.assertEqual(np.round(val_simulado, 3), 100)

    def test_simul_con_paso_2(símismo):

        for nmb, mod in símismo.modelos.items():
            with símismo.subTest(mod=nmb):
                res_paso_1 = símismo.res[nmb]['Lago'].vals.values[::2]
                res_paso_2 = mod.simular(
                    t=EspecTiempo(100, tmñ_paso=2), extern=símismo.vals_inic, vars_interés=['Lago']
                )['Lago'].vals.values
                npt.assert_allclose(res_paso_2, res_paso_1, rtol=0.001)

    def test_simul_guardar_cada_2(símismo):

        for nmb, mod in símismo.modelos.items():
            with símismo.subTest(mod=nmb):
                res_paso_1 = símismo.res[nmb]['Lago'].vals.values[::2]
                res_paso_2 = mod.simular(
                    t=EspecTiempo(200, guardar_cada=2), extern=símismo.vals_inic, vars_interés=['Lago']
                )['Lago'].vals.values
                npt.assert_equal(res_paso_1, res_paso_2)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


class TestSimulExpres(unittest.TestCase):

    def test_simul_exprés(símismo):
        for nmb, mod in generar_modelos_prueba().items():
            with símismo.subTest(mod=nmb):
                extern = pd.DataFrame({'Lluvia': np.arange(10)}, index=np.arange(10))
                res_exprés = mod.simular(12, extern=extern)
                mod._correr_hasta_final = lambda: None
                res_por_paso = mod.simular(12, extern=extern)

                for res_var_exp, res_var_paso in zip(res_exprés, res_por_paso):
                    xrt.assert_equal(res_var_exp.vals, res_var_paso.vals)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


class TestGenerarMDS(unittest.TestCase):
    """
    Verifica el funcionamiento del generado automático de modelos DS.
    """

    def test_generación_auto_mds(símismo):
        """
        Verificamos que funcione la generación automática de modelos DS a base de un fuente.
        """

        for m, d in tipos_modelos.items():
            with símismo.subTest(ext=os.path.splitext(d['prueba'])[1], envlt=d['envlt'].__name__):
                try:
                    mod = gen_mds(d['prueba'])  # Generar el modelo
                    símismo.assertIsInstance(mod, ModeloDS)
                except ErrorNoInstalado:
                    # No hay problema si el mds no se pudo leer en la computadora actual. De pronto no estaba instalado.
                    pass

    def test_error_extensión(símismo):
        """
        Comprobar que extensiones no reconocidas devuelvan un error.
        """

        with símismo.assertRaises(ErrorNoInstalado):
            gen_mds('recursos/mds/Modelo con extensión no reconocida.வணக்கம்')

    def test_modelo_erróneo(símismo):
        """
        Asegurarse que un fuente erróneo devuelva un error.
        """

        with símismo.assertRaises(FileNotFoundError):
            gen_mds('Yo no existo.mdl')

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


def limpiar_mds(direc='./recursos/mds'):
    """
    Limpiamos todos los documentos temporarios generados por los programas de modelos DS.
    """
    for c in os.walk(direc):
        for a in c[2]:
            ext = os.path.splitext(a)[1]
            try:
                if ext in ['.2mdl', '.vdf', '.csv'] or (ext == '.py' and any(
                        os.path.isfile(os.path.join(direc, os.path.splitext(a)[0] + e))
                        for e in ['.xmile', '.xml', '.mdl']
                )):
                    os.remove(os.path.join(direc, a))

            except (FileNotFoundError, PermissionError):
                pass
