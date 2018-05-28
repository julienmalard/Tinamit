import os
import unittest


from tinamit.Análisis.Datos import DatosIndividuales, DatosRegión, SuperBD


dir_act = os.path.split(__file__)[0]
arch_reg = os.path.join(dir_act, 'recursos/datos/datos_reg.csv')
arch_indiv = os.path.join(dir_act, 'recursos/datos/datos_indiv.csv')


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = DatosRegión(nombre='prueba regional', archivo=arch_reg, fecha='fecha', lugar='lugar')
        bd_indiv = DatosIndividuales(nombre='prueba individual', archivo=arch_indiv, fecha='fecha', lugar='lugar')
        cls.bd = SuperBD(nombre='BD Central', bds=[bd_región, bd_indiv])

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
