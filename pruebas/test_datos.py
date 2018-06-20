import os

import pandas as pd
import unittest
import numpy.testing as npt

from tinamit.Análisis.Datos import DatosIndividuales, DatosRegión, SuperBD


dir_act = os.path.split(__file__)[0]
arch_reg = os.path.join(dir_act, 'recursos/datos/datos_reg.csv')
arch_indiv = os.path.join(dir_act, 'recursos/datos/datos_indiv.csv')


class Test_Datos(unittest.TestCase):
    def test_de_pandas(símismo):
        bd_pds = pd.DataFrame({'y': [1,2,3], 'x': [4,5,6]})
        bd_datos = DatosIndividuales('Datos Generados', bd_pds)
        datos = bd_datos.obt_datos(['x', 'y'])
        npt.assert_allclose(datos['x'], [4,5,6])


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = DatosRegión(nombre='prueba regional', archivo=arch_reg, fecha='fecha', lugar='lugar')
        bd_indiv = DatosIndividuales(nombre='prueba individual', archivo=arch_indiv, fecha='fecha', lugar='lugar')
        cls.bd = SuperBD(nombre='BD Central', bds=[bd_región, bd_indiv], auto_conectar=True)

        cls.bd.espec_var(var='completo', var_bd='var_completo')
        cls.bd.espec_var(var='incompleto', var_bd='var_incompleto')

    def test_espec_borrar_var(símismo):
        símismo.bd.espec_var(var='var para borrar', var_bd='temp')
        símismo.assertIn('var para borrar', símismo.bd.vars)
        símismo.bd.borrar_var(var='var para borrar')
        símismo.assertNotIn('var para borrar', símismo.bd.vars)

    def test_renombrar_var(símismo):
        símismo.bd.renombrar_var('completo', nuevo_nombre='var renombrado')
        símismo.assertIn('var renombrado', símismo.bd.vars)
        símismo.assertNotIn('completo', símismo.bd.vars)
        símismo.bd.renombrar_var('var renombrado', nuevo_nombre='completo')

    def test_desconectar_datos(símismo):
        bd_temp = DatosIndividuales(nombre='temp', archivo=arch_indiv, fecha='fecha', lugar='lugar')
        símismo.bd.conectar_datos(bd=bd_temp)
        símismo.bd.desconectar_datos(bd=bd_temp)
        símismo.assertNotIn(bd_temp.nombre, símismo.bd.bds)

    def test_guardar_cargar_datos(símismo):
        símismo.bd.guardar_datos()
        símismo.bd.cargar_datos()

        símismo.assertIn('completo', list(símismo.bd.vars))

        # Limpiar
        símismo.bd.borrar_archivo_datos()

    def test_exportar_datos_csv(símismo):
        símismo.bd.exportar_datos_csv()

        egresos = [os.path.join(os.path.abspath(''), símismo.bd.nombre + '_' + x + '.csv')
                   for x in ['ind', 'reg', 'error_reg']]

        símismo.assertTrue(all([os.path.isfile(x) for x in egresos]))

        # Limpiar
        for x in egresos:
            os.remove(x)

    def test_obt_datos(símismo):
        res = símismo.bd.obt_datos('completo')
        símismo.assertSetEqual(set(res['lugar'].unique().tolist()), {'701', '708', '7'})

        símismo.assertIn('completo', res)

    def test_obt_datos_de_lugar(símismo):
        res = símismo.bd.obt_datos('completo', lugares='708')
        símismo.assertTrue(set(res['lugar'].unique().tolist()) == {'708'})

    def test_obt_datos_excluir_faltan(símismo):
        res = símismo.bd.obt_datos(['completo', 'incompleto'], excl_faltan=True)
        símismo.assertFalse(res.isnull().values.any())

    def test_obt_datos_fecha_única(símismo):
        res = símismo.bd.obt_datos('completo', fechas=2000)
        símismo.assertTrue(all(res['fecha'] == '2000-1-1'))

    def test_obt_datos_fecha_lista(símismo):
        res = símismo.bd.obt_datos('completo', fechas=[2000, 2002])
        símismo.assertTrue(all(res['fecha'].isin(['2000-1-1', '2002-1-1'])))

    def test_obt_datos_fecha_rango(símismo):
        res = símismo.bd.obt_datos('completo', fechas=(2000, '2002-6-1'))
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_obt_datos_reg_con_interpol_no_necesario(símismo):
        res = símismo.bd.obt_datos('completo', fechas=(2000, '2002-6-1'), tipo='regional')
        símismo.assertTrue(res.shape[0] > 0)
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_obt_datos_reg_fecha_única_con_interpol(símismo):
        res = símismo.bd.obt_datos(['incompleto', 'completo'], fechas=2001, tipo='regional')

        # Verificar interpolaciones
        npt.assert_allclose(res.loc[res.lugar == '708'][res.fecha == '2001-1-1']['completo'].values, 1.500684)
        npt.assert_allclose(res.loc[res.lugar == '7'][res.fecha == '2001-1-1']['incompleto'].values, 23.3394,
                            rtol=0.001)

    def test_obt_datos_reg_fecha_rango_con_interpol(símismo):
        res = símismo.bd.obt_datos(['incompleto', 'completo'], fechas=(2000, '2002-6-1'), tipo='regional')
        símismo.assertTrue(res.shape[0] > 0)
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_graficar(símismo):
        símismo.bd.graficar_hist('completo')
        símismo.assertTrue(os.path.isfile('./completo.jpg'))

    def test_graficar_línea(símismo):
        símismo.bd.graficar_línea(var='completo', archivo='línea completo.jpg')
        símismo.assertTrue(os.path.isfile('./línea completo.jpg'))

    def test_graficar_comparar(símismo):
        símismo.bd.graf_comparar(var_x='completo', var_y='incompleto')
        símismo.assertTrue(os.path.isfile('./completo_incompleto.jpg'))

    @classmethod
    def tearDownClass(cls):
        for c in os.walk('./'):
            for a in c[2]:
                nmbr, ext = os.path.splitext(a)
                try:
                    if ext in ['.jpg', '.jpeg', '.png']:
                        os.remove(a)
                except (FileNotFoundError, PermissionError):
                    pass
