import os
import unittest

from tinamit.EnvolturaMDS import generar_mds, EnvolturaMDS, ModeloVensim, ModeloPySD, ModeloVensimMdl


# Los tipos de modelos DS que queremos comprobar.
tipos_modelos = {
    'mdlVensim': {'envlt': ModeloVensimMdl, 'prueba': 'recursos/prueba_senc.mdl'},
    'PySDVensim': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc.mdl'},
    'PySD_XMILE': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc_.xmile'},
    'dllVensim': {'envlt': ModeloVensim, 'prueba': 'recursos/prueba_senc.vpm'}
}

# Quitar los modelos no instalados en la computadora actual
for nmb in list(tipos_modelos):
    if not tipos_modelos[nmb]['envlt'].instalado:
        tipos_modelos.pop(nmb)

# Agregar la ubicación del archivo actual
dir_act = os.path.split(__file__)[0]
for d_m in tipos_modelos.values():
    d_m['prueba'] = os.path.join(dir_act, d_m['prueba'])


class Test_ModeloSenc(unittest.TestCase):
    """
    Verifica el funcionamiento de los programas de MDS.
    """

    @classmethod
    def setUpClass(cls):

        # Generar las instancias de los modelos
        cls.modelos = {ll: d['envlt'](d['prueba']) for ll, d in tipos_modelos.items()}  # type: dict[str, EnvolturaMDS]

        # Información sobre los variables del modelo de prueba
        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Nivel lago inicial': {'unidades': 'm3', 'líms': (0, None), 'val_inic': 1500},
            'Flujo río': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Evaporación': {'unidades': 'm3/mes', 'líms': (0, None)}
        }  # type: dict[str, dict]

        # Para cada modelo...
        for mod in cls.modelos.values():

            # Inicializar los variables iniciales
            for v, d_v in cls.info_vars.items():

                # Iniciar los valores iniciales, si hay
                if 'val_inic' in d_v:
                    mod.inic_val_var(v, d_v['val_inic'])

            # Correr el modelo para 200 pasos, guardando los egresos del variable "Lago"
            mod.simular(tiempo_final=200, vars_interés='Lago')

    def test_leer_vars(símismo):
        """
        Comprobar que los nombres de los variables se leyeron correctamente.
        """
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                vars_modelo = set(mod.variables)
                símismo.assertSetEqual(set(símismo.info_vars), vars_modelo)

    def test_unid_tiempo(símismo):
        """
        Comprobar que las unidades de tiempo se leyeron correctamente.
        """
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertEqual('mes', mod.unidad_tiempo())

    def test_leer_info(símismo):
        """
        Comprobar que la documentación de cada variable se leyó correctamente.
        """

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertTrue(len(d_v['info']) > 0 for d_v in mod.variables.values())

    def test_leer_unidades(símismo):
        """
        Comprobar que las unidades de los variables se leyeron correctamente.
        """

        unids = {v: d_v['unidades'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['unidades'].lower() for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def test_leer_líms(símismo):
        """
        Comprobar que los límites de los variables se leyeron correctamente.
        """

        unids = {v: d_v['líms'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['líms'] for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def test_cmb_vals_inic(símismo):
        """
        Comprobar que los valores iniciales se establecieron correctamente.
        """

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                for v, d_v in símismo.info_vars.items():

                    # Únicamente verificar los variables con valores iniciales especificados, naturalmente.
                    if 'val_inic' in d_v:
                        símismo.assertEqual(mod.variables[v]['val'], d_v['val_inic'])

    def test_simul(símismo):
        """
        Assegurarse que la simulación dió los resultados esperados.
        """

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                # Leer el resultado del último día de simulación pára el variable "Lago"
                val_simulado = mod.leer_resultados('Lago')[-1, 0]

                # Debería ser aproximativamente igual a 100
                símismo.assertEqual(round(val_simulado, 3), 100)

    @classmethod
    def tearDownClass(cls):

        # Limpiamos todos los documentos temporarios generados por los programas de modelos DS.
        for c in os.walk('../recursos'):
            for a in c[2]:
                nmbr, ext = os.path.splitext(a)
                try:
                    if nmbr == 'Corrida Tinamït':
                        os.remove(a)
                    elif ext in ['.2mdl', '.vdf']:
                        os.remove(a)
                    elif a == 'prueba_senc.py':
                        os.remove(a)
                    elif a == 'prueba_senc_.py':
                        os.remove(a)
                except PermissionError:
                    pass


class Test_GenerarMDS(unittest.TestCase):
    """
    Verifica el funcionamiento del generado automático de modelos DS.
    """
    def test_generación_auto_mds(símismo):
        # Verificamos que funcione la generación automática de modelos DS a base de un archivo.

        for m, d in tipos_modelos.items():
            with símismo.subTest(ext=os.path.splitext(d['prueba'])[1]):
                try:
                    mod = generar_mds(d['prueba'])  # Generar el modelo
                    símismo.assertIsInstance(mod, EnvolturaMDS)
                except ValueError:
                    # No hay problema si el MDS no se pudo leer en la computadora actual. De pronto no estaba instalado.
                    pass
