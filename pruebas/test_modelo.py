import os
import unittest

from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from pruebas.test_mds import limpiar_mds

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/BF/prueba_bf.py')
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')
arch_mod_vacío = os.path.join(dir_act, 'recursos/MDS/prueba_vacía.mdl')


class Test_SimularGrupo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generar las instancias de los modelos
        cls.mod = ModeloPrueba()

    def test_simular_grupo_ops_lista(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 4}, {'Lluvia': 5}], vars_interés=['Lluvia']
        )
        símismo.assertSetEqual({'vals_inic0', 'vals_inic1'}, set(res))

    def test_simular_grupo_ops_dict(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic={'4': {'Lluvia': 4}, '5': {'Lluvia': 5}},
            vars_interés=['Lluvia']
        )
        símismo.assertSetEqual({'4', '5'}, set(res))

    def test_simular_grupo_sin_combinar_opciones(símismo):
        vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
        tiempo_final = [100, 200]
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=False,
            nombre_corrida=['1', '2']
        )
        símismo.assertEqual(len(res), 2)

    def test_simular_grupo_combinar_opciones_lista(símismo):
        vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
        tiempo_final = [100, 200]
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_opciones_dic(símismo):
        vals_inic = {'a': {'Lluvia': 1}, 'b': {'Lluvia': 2}}
        tiempo_final = {'c': 100, 'd': 200}
        res = símismo.mod.simular_grupo(
            t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_opciones_dic_y_lista(símismo):
        res = símismo.mod.simular_grupo(
            t_final={'a': 100, 'b': 200}, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            combinar=True
        )
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_combinar_llaves_dic_opciones_no_iguales(símismo):
        with símismo.assertRaises(ValueError):
            vals_inic = {'1': {'Lluvia': 1}, '2': {'Lluvia': 2}}
            tiempo_final = {'1': 100, '3': 300}  # No igual a las llaves en vals_inic
            símismo.mod.simular_grupo(
                t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'],
                combinar=False
            )

    def test_simular_grupo_con_dict_y_listas_sin_combinaciones(símismo):
        with símismo.assertRaises(TypeError):
            símismo.mod.simular_grupo(
                t_final={'1': 100, '2': 200}, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                combinar=False
            )

    def test_simular_grupo_con_prefijo_nombre(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            nombre_corrida='pre'
        )
        símismo.assertTrue(all(x.startswith('pre') for x in res))

    def test_simular_grupo_con_lista_nombres(símismo):
        nombres = ['corrida 1', 'corrida 2']
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
            nombre_corrida=nombres, combinar=False
        )
        símismo.assertSetEqual(set(nombres), set(res))

    def test_simular_grupo_con_lista_nombres_tamaño_error(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular_grupo(
                t_final=100, vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                nombre_corrida=['1', '2', '3'],  # 1 demasiado
                combinar=False
            )

    def test_simular_grupo_con_lista_nombres_y_combinaciones(símismo):
        with símismo.assertRaises(TypeError):
            vals_inic = [{'Lluvia': 1}, {'Lluvia': 2}]
            tiempo_final = [100, 200]
            símismo.mod.simular_grupo(
                t_final=tiempo_final, vals_inic=vals_inic, vars_interés=['Lluvia'], combinar=True,
                nombre_corrida=['1', '2']
            )

    def test_simular_grupo_sin_combinaciones_tamaño_opciones_error(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular_grupo(
                t_final=[100], vals_inic=[{'Lluvia': 1}, {'Lluvia': 2}],
                combinar=False
            )

    def test_simular_grupo_combinar_con_1_opción(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic=[{'Lluvia': 1}], vars_interés=['Lluvia'], combinar=True,
        )
        símismo.assertIn('Lluvia', res['vals_inic0'])

    def test_simular_grupo_sin_opciones_múltiples(símismo):
        res = símismo.mod.simular_grupo(
            t_final=100, vals_inic={'Lluvia': 1}, vars_interés=['Lluvia'], combinar=True,
        )
        símismo.assertIn('Lluvia', res['Corrida Tinamït'])

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()
