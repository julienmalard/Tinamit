import os
import unittest

import numpy as np
import numpy.testing as npt
from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from pruebas.recursos.BF.variantes import EjBloques, EjImpaciente, EjIndeterminado
from pruebas.test_mds import generar_modelos_prueba, limpiar_mds
from tinamit.BF import EnvolturaBF
from tinamit.Conectado import Conectado, SuperConectado
from tinamit.EnvolturasMDS import ModeloPySD, generar_mds
from tinamit.Unidades import trads

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/BF/prueba_bf.py')
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')
arch_mod_vacío = os.path.join(dir_act, 'recursos/MDS/prueba_vacía.mdl')


# Comprobar Conectado
class Test_Conectado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Preparar los modelos genéricos necesarios para las pruebas.
        """

        # Generar las instancias de los modelos individuales y conectados
        cls.mods_mds = generar_modelos_prueba()
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

    def test_reinic_vals(símismo):
        """
        Asegurarse que los variables se reinicializen correctamente después de una simulación.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                egr1 = mod.simular(t_final=100, vars_interés=list(mod.variables))
                egr2 = mod.simular(t_final=100, vars_interés=list(mod.variables))

                for var in egr1.data_vars:
                    if 'Aleatorio' not in var:
                        npt.assert_array_equal(egr1[var].values, egr2[var].values, err_msg=var)

    def test_intercambio_de_variables_en_simular(símismo):
        """
        Asegurarse que valores intercambiados tengan valores iguales en los resultados de ambos modelos.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                egr = mod.simular(t_final=100, vars_interés=['bf_Aleatorio', 'mds_Aleatorio'])

                npt.assert_array_equal(egr['bf_Aleatorio'], egr['mds_Aleatorio'])

    def test_simular_grupo(símismo):
        """
        Comprobar que simulaciones en grupo den el mismo resultado que las mismas simulaciones individuales.
        """

        for ll, mod in símismo.modelos.items():
            with símismo.subTest(mod=ll):
                t_final = 100
                referencia = {}
                mod.simular(t_final=t_final, vals_inic={'Nivel lago inicial': 50}, vars_interés='Lago')
                referencia['lago_50'] = mod.leer_resultados('Lago')

                mod.simular(t_final=t_final, vals_inic={'Nivel lago inicial': 2000}, vars_interés='Lago')
                referencia['lago_2000'] = mod.leer_resultados('Lago')

                resultados = mod.simular_grupo(
                    t_final=t_final,
                    vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
                    vars_interés='Lago'
                )

                for c in resultados:
                    npt.assert_allclose(referencia[c]['mds_Lago'], resultados[c]['mds_Lago'], rtol=0.001)

    def test_simular_grupo_con_paralelo(símismo):
        """
        Comprobamos que :func:`SuperConectado.simular_grupo` funcione igual con o sin paralelización.

        """
        mod = símismo.modelos['PySDVensim']

        t_final = 100

        sin_paral = mod.simular_grupo(
            t_final=t_final,
            vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
            vars_interés='Lago',
            paralelo=False
        )

        con_paral = mod.simular_grupo(
            t_final=t_final,
            vals_inic={'lago_50': {'Nivel lago inicial': 50}, 'lago_2000': {'Nivel lago inicial': 2000}},
            vars_interés='Lago',
            paralelo=True
        )

        for c in sin_paral:
            npt.assert_allclose(sin_paral[c]['mds_Lago'], con_paral[c]['mds_Lago'], rtol=0.001)

    def test_simular_grupo_inicvals_por_submodelo(símismo):
        """
        Asegurarse que podamos especificar valores iniciales por submodelo en un diccionario.
        """
        mod = símismo.modelos['PySDVensim']

        t_final = 100
        vals_inic = {'mds_Nivel lago inicial': 50}
        ref = mod.simular_grupo(t_final=t_final, vals_inic=vals_inic, vars_interés='Lago')

        vals_inic = {'mds': {'Nivel lago inicial': 50}}
        res = mod.simular_grupo(t_final=t_final, vals_inic=vals_inic, vars_interés='Lago')

        for c in res:
            npt.assert_allclose(ref[c]['mds_Lago'], res[c]['mds_Lago'], rtol=0.001)

    def test_simular_grupo_inicvals_por_corrida_y_submodelo(símismo):
        """
        Simular corridas en grupo con valores iniciales especificadas por submodelo en un diccionario.
        """
        mod = símismo.modelos['PySDVensim']

        t_final = 100
        vals_inic = {'50': {'mds_Nivel lago inicial': 50}}
        ref = mod.simular_grupo(t_final=t_final, vals_inic=vals_inic, vars_interés='Lago')

        vals_inic = {'50': {'mds': {'Nivel lago inicial': 50}}}
        res = mod.simular_grupo(t_final=t_final, vals_inic=vals_inic, vars_interés='Lago')

        for c in res:
            npt.assert_allclose(ref[c]['mds_Lago'], res[c]['mds_Lago'], rtol=0.001)

    def test_inic_vals_por_nombre_completo(símismo):
        mod = símismo.modelos['PySDVensim']
        vals_inic = {'mds_Nivel lago inicial': 50}
        res = mod.simular(100, vals_inic=vals_inic, vars_interés='Nivel lago inicial')
        símismo.assertEqual(res['mds_Nivel lago inicial'][0], 50)

    def test_inic_vals_por_nombre_en_submodelo(símismo):
        mod = símismo.modelos['PySDVensim']
        vals_inic = {'Nivel lago inicial': 40}
        res = mod.simular(100, vals_inic=vals_inic, vars_interés='Nivel lago inicial')
        símismo.assertEqual(res['mds_Nivel lago inicial'][0], 40)

    def test_inic_vals_por_submodelo_y_nombre(símismo):
        mod = símismo.modelos['PySDVensim']
        vals_inic = {'mds': {'Nivel lago inicial': 30}}
        res = mod.simular(100, vals_inic=vals_inic, vars_interés='Nivel lago inicial')
        símismo.assertEqual(res['mds_Nivel lago inicial'][0], 30)

    @classmethod
    def tearDownClass(cls):
        """
        Limpiar todos los archivos temporarios.
        """

        limpiar_mds()


class Test_3ModelosConectados(unittest.TestCase):
    """
    Comprobar 3+ modelos conectados.
    """

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


class Test_GenerarConectado(unittest.TestCase):

    def test_generar_con_submodelos(símismo):
        mds = generar_mds(archivo=arch_mds)
        bf = ModeloPrueba(unid_tiempo='mes')
        cnctd = Conectado(bf, mds)
        símismo.assertSetEqual(set(cnctd.modelos), {'mds', 'bf'})

    def test_generar_sin_submodelos(símismo):
        mds = generar_mds(archivo=arch_mds)
        bf = ModeloPrueba(unid_tiempo='mes')
        cnctd = Conectado()
        cnctd.estab_bf(bf)
        cnctd.estab_mds(mds)
        símismo.assertSetEqual(set(cnctd.modelos), {'mds', 'bf'})


class Test_ConversionesUnidadesTiempo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mds = generar_mds(archivo=arch_mds)

    def test_unidades_tiempo_iguales(símismo):
        bf = ModeloPrueba(unid_tiempo='mes')
        cnctd = Conectado(bf, símismo.mds)
        cnctd.conectar(var_mds='Aleatorio', var_bf='Escala', mds_fuente=False)
        res = cnctd.simular(10, vars_interés=['bf_Escala', 'mds_Aleatorio'])
        npt.assert_array_equal(res['mds_Aleatorio'], np.arange(11))

    def test_unidades_tiempo_mes_y_día(símismo):
        bf = ModeloPrueba(unid_tiempo='días')
        cnctd = Conectado(bf, símismo.mds)
        cnctd.conectar(var_mds='Aleatorio', var_bf='Escala', mds_fuente=False)
        res = cnctd.simular(10, vars_interés=['bf_Escala', 'mds_Aleatorio'])
        npt.assert_array_equal(res['mds_Aleatorio'], np.arange(11 * 30, step=30))

    def test_unidades_con_tiempo_no_definida(símismo):
        bf = ModeloPrueba(unid_tiempo='महिने')
        cnctd = Conectado(bf, símismo.mds)
        cnctd.conectar(var_mds='Aleatorio', var_bf='Escala', mds_fuente=False)
        res = cnctd.simular(10, vars_interés=['bf_Escala', 'mds_Aleatorio'])
        npt.assert_array_equal(res['mds_Aleatorio'], np.arange(11))

    def test_unidades_tiempo_definidas(símismo):
        bf = ModeloPrueba(unid_tiempo='દિવસ')
        cnctd = Conectado(bf, símismo.mds)
        cnctd.conectar(var_mds='Aleatorio', var_bf='Escala', mds_fuente=False)
        cnctd.estab_conv_unid_tiempo(unid_ref='día', unid='દિવસ')
        res = cnctd.simular(10, vars_interés=['bf_Escala', 'mds_Aleatorio'])
        npt.assert_array_equal(res['mds_Aleatorio'], np.arange(11 * 30, step=30))

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


class Test_ConectarModeloBloques(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmñ_blqs = [1, 3, 8]
        mod_bloques = EjBloques(nombre='blq', blqs=cls.tmñ_blqs, unid_tiempo='meses')
        mod_base = ModeloPrueba(nombre='base', unid_tiempo='meses')
        mod_con = SuperConectado(modelos=[mod_base, mod_bloques])
        mod_con.conectar_vars('bloque', modelo_fuente=mod_bloques, var_recip='Vacío', modelo_recip=mod_base)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_suma', modelo_recip=mod_bloques)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_último', modelo_recip=mod_bloques)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_máx', modelo_recip=mod_bloques)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_prom', modelo_recip=mod_bloques)

        cls.n_ciclos = 2
        cls.res = mod_con.simular(
            t_final=int(cls.n_ciclos * np.sum(cls.tmñ_blqs)),
            vars_interés=['blq_ingr', 'base_Vacío'])

    def test_de_mod_bloques(símismo):
        npt.assert_equal(
            símismo.res['base_Vacío'].values,
            [x for i, t in enumerate(símismo.tmñ_blqs) for x in [i] * t] * símismo.n_ciclos
        )

    def test_hacia_mod_bloques_suma(símismo):
        cum = np.insert(np.cumsum(símismo.tmñ_blqs), 0, 0)
        bloques_ingr_escala = [np.arange(cum[i], cum[i + 1]) for i in range(len(cum) - 1)]
        npt.assert_equal(
            símismo.res['blq_ingr_máx'],

        )


class Test_ConectarModeloImpaciente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n_ciclos = 2
        cls.tmñ_ciclo = 12
        mod_impac = EjImpaciente(nombre='imp', n=cls.tmñ_ciclo, unid_tiempo='meses')
        mod_base = ModeloPrueba(nombre='base', unid_tiempo='meses')
        mod_con = SuperConectado(modelos=[mod_base, mod_impac])
        mod_con.conectar_vars('ciclo', modelo_fuente=mod_impac, var_recip='Vacío', modelo_recip=mod_base)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_último', modelo_recip=mod_impac)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_suma', modelo_recip=mod_impac)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_prom', modelo_recip=mod_impac)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_máx', modelo_recip=mod_impac)
        mod_con.conectar_vars('Escala', modelo_fuente=mod_base, var_recip='ingr_directo', modelo_recip=mod_impac)
        cls.res = mod_con.simular(t_final=cls.tmñ_ciclo * cls.n_ciclos, vars_interés=['base_Vacío'])

        cls.escala = [np.arange(c * cls.tmñ_ciclo, c * cls.tmñ_ciclo + cls.tmñ_ciclo) for c in range(cls.n_ciclos)]

    def test_de_mod_impac(símismo):
        npt.assert_equal(
            símismo.res['base_Vacío'], [x for i in range(símismo.n_ciclos) for x in [i] * símismo.tmñ_ciclo]
        )

    def test_hacia_mod_impac_último(símismo):
        npt.assert_equal(
            símismo.res['ingr_último'].values,
            [x for i in símismo.escala for x in [i[-1]] * símismo.tmñ_ciclo]
        )

    def test_hacia_mod_impac_suma(símismo):
        npt.assert_equal(
            símismo.res['ingr_último'].values,
            [x for i in símismo.escala for x in [i.sum()] * símismo.tmñ_ciclo]
        )

    def test_hacia_mod_impac_prom(símismo):
        npt.assert_equal(
            símismo.res['ingr_último'].values,
            [x for i in símismo.escala for x in [i.mean()] * símismo.tmñ_ciclo]
        )

    def test_hacia_mod_impac_máx(símismo):
        npt.assert_equal(
            símismo.res['ingr_último'].values,
            [x for i in símismo.escala for x in [i.max()] * símismo.tmñ_ciclo]
        )

    def test_hacia_mod_impac_directo(símismo):
        npt.assert_equal(
            símismo.res['ingr_último'].values,
            [x for i in símismo.escala for x in i]
        )


class Test_ConectarModeloIndeterminado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_bloques = EjIndeterminado((1, 12), unid_tiempo='meses')
        mod_base = ModeloPrueba(unid_tiempo='meses')
        mod_con = SuperConectado(modelos=[mod_base, mod_bloques])
        mod_con.conectar_vars('')
        cls.res = mod_con.simular(t_final=36, vars_interés=['egr', 'ingr'])

    def test_de_mod_indeter(símismo):
        pass

    def test_hacia_mod_indeter(símismo):
        pass
