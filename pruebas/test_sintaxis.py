import math
import unittest

import numpy as np
import xarray as xr

from tinamit.Análisis.sintaxis import Ecuación


class Test_AnalizarEc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ecs = {
            'neg': ('y=-x', 2, -2),
            'mín': ('y=mín(0, x)', 1, 0),
            'máx': ('y=máx(x, 0)', 1, 1),
            'abs': ('y=abs(x)', -1, 1),
            'exp': ('y=exp(x)', 0, 1),
            'ent': ('y=ent(x*1.0001)', 4, 4),
            'rcd': ('y=rcd(x^2)', 3, 3),
            'ln': ('y=ln(x)', 1, 0),
            'log': ('y=log(x)', 10, 1),
            'sin': ('y=sin(x)', 1, math.sin(1)),
            'cos': ('y=cos(x)', 1, math.cos(1)),
            'tan': ('y=tan(x)', 1, math.tan(1)),
            'sinh': ('y=sinh(x)', 5, math.sinh(5)),
            'cosh': ('y=cosh(x)', 5, math.cosh(5)),
            'tanh': ('y=tanh(x)', 5, math.tanh(5)),
            'asin': ('y=asin(x)', 1, math.asin(1)),
            'acos': ('y=acos(x)', 1, math.acos(1)),
            'atan': ('y=atan(x)', 1, math.atan(1)),
            'si_sino': ('y=si_sino(1, x, -x)', 1, 1),
            '>': ('y=x>1', 1, False),
            '<': ('y=x<3', 1, True),
            '>=': ('y=x>=0', 1, True),
            '<=': ('y=x<=0', 1, False),
            '==': ('y=x==0', 0, True),
            '!=': ('y=x!=1', 1, False),
            '+': ('y=x+3', 3, 6),
            '-': ('y=5.0-x', 1, 4),
            '*': ('y=2*x', 2.5, 5),
            '^': ('y=2^x', 3, 8),
            '/': ('y=x/3', 9, 3)
        }

    def _verificar_ec(símismo, ec, val_x, resp):
        ec_py = ec.a_python(paráms=[])
        símismo.assertEqual(ec_py([], {'x': val_x}), resp)

    def test_ec_a_tx(símismo):
        for nmbr, (ec, x, y) in símismo.ecs.items():
            with símismo.subTest(nmbr):
                obj_ec = Ecuación(ec)
                tx = str(obj_ec)
                obj_ec_2 = Ecuación(tx, nombre='y')

                símismo._verificar_ec(obj_ec, val_x=x, resp=y)
                símismo._verificar_ec(obj_ec_2, val_x=x, resp=y)

    def test_sacar_vars(símismo):
        ec = Ecuación('y=a*x + sin(b) + si_sino(x > d, a/(exp(-b*x)), máx(2, c))')
        símismo.assertSetEqual(ec.variables(), {'a', 'b', 'c', 'd', 'x'})

    def test_ec_de_MDS(símismo):
        ec = Ecuación('y=IF THEN ELSE (MAX (x, 0)>a, 5, 3)', dialecto='vensim')
        símismo.assertEquals(ec.a_python(paráms=['a'])([1], {'x': 2}), 5)

    def test_ec_con_nombre(símismo):
        ec = Ecuación('x*3', nombre='y')
        ec2 = Ecuación('y=x*3')
        símismo.assertEquals(str(ec), str(ec2))
        símismo.assertEquals(ec.nombre, ec2.nombre)

    def test_ec_sin_nombre(símismo):
        símismo.assertIsNone(Ecuación('x*3').nombre)

    def test_ec_otras_ecs(símismo):
        ec_1 = 'y = x*a'
        ec_2 = '2*b'
        ec_3 = '3'
        ec = Ecuación(ec_1, otras_ecs={'a': ec_2, 'b': ec_3})
        símismo.assertEquals(ec.a_python(paráms=[])([], {'x': 2}), 12)

    def test_ec_nombres_equiv(símismo):
        ec = Ecuación('y=a*x + b', nombres_equiv={'x': 'X'})
        símismo.assertEquals(ec.a_python(paráms=['a', 'b'])([4, 5], {'X': 2}), 13)

    def test_sacar_args(símismo):
        ec = Ecuación('y=1/f(a, x, 2*b)')
        for i in [None, 1, 2]:
            with símismo.subTest(i=i):
                símismo.assertListEqual(ec.sacar_args_func('f'), ['a', 'x', '2*b'])
                símismo.assertListEqual(ec.sacar_args_func('f', i=1), ['a'])
                símismo.assertListEqual(ec.sacar_args_func('f', i=2), ['a', 'x'])

    def test_obt_coef_var(símismo):
        ec = Ecuación('y=1/f(a, b*x, 2*c)')
        símismo.assertEquals(ec.coef_de('x'), ('b', False))

    def test_obt_coef_var_neg(símismo):
        ec = Ecuación('y=1/f(a, -b*x, 2*c)')
        símismo.assertEquals(ec.coef_de('x'), ('b', False))

    def test_obt_coef_var_div_coef(símismo):
        ec = Ecuación('y=a+x/b')
        símismo.assertEquals(ec.coef_de('x'), ('b', True))

    def test_obt_coef_var_dos_veces(símismo):
        ec = Ecuación('y=a*x + máx(2, a*x)')
        símismo.assertEquals(ec.coef_de('x'), ('a', False))

    def test_obt_coef_var_dos_veces_incompat(símismo):
        ec = Ecuación('y=a*x + b*x')
        símismo.assertIsNone(ec.coef_de('x'))

    def test_obt_coef_var_dupl_coef(símismo):
        ec = Ecuación('y=a*x + a')
        símismo.assertIsNone(ec.coef_de('x'))

    def test_obt_coef_var_dos_veces_falta_coef(símismo):
        ec = Ecuación('y=a*x + x')
        símismo.assertIsNone(ec.coef_de('x'))

    def test_obt_coef_var_dos_veces_incompat_div_mul(símismo):
        ec = Ecuación('y=a*x + a/x')
        símismo.assertIsNone(ec.coef_de('x'))

    def test_obt_coef_múltiple(símismo):
        ec = Ecuación('y=a*(x+b+a)')
        símismo.assertIsNone(ec.coef_de('x'))

    def test_obt_coef_var_div(símismo):
        ec = Ecuación('y=a+b/x')
        símismo.assertEquals(ec.coef_de('x'), ('b', True))

    def test_obt_coef_ec(símismo):
        ec = Ecuación('y=a*(x+b)')
        símismo.assertEquals(ec.coef_de('y'), ('a', True))  # Inverso porque a y "y" son de lados opuestos del "="

    def test_obt_coef_ec_div_coef(símismo):
        ec = Ecuación('y=(x+b)/a')
        símismo.assertEquals(ec.coef_de('y'), ('a', False))

    def test_obt_coef_ec_div(símismo):
        ec = Ecuación('y=a/(x+b)')
        símismo.assertEquals(ec.coef_de('y'), ('a', True))

    def test_obt_coef_ec_múltiple(símismo):
        ec = Ecuación('y=a*(x+b+a)')
        símismo.assertIsNone(ec.coef_de('y'))


class Test_Normalizar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs_x = xr.Dataset({'x': ('n', np.random.normal(0, 2, 100))})
        cls.obs_y = xr.DataArray(np.random.normal(0, 10, 100))

    def test_normalizar(símismo):
        ec = Ecuación('y=a*x+b')

        escls_prms, líms_norm, x_norm, y_norm = ec.normalizar(
            líms_paráms={'a': (0, 1)}, obs_x=símismo.obs_x, obs_y=símismo.obs_y
        )
        símismo.assertAlmostEqual(x_norm['x'].values.std(), 1)
        símismo.assertTupleEqual(líms_norm['a'], (0, 1 * símismo.obs_x['x'].values.std()))

    def test_normalizar_div(símismo):
        ec = Ecuación('y=x/a+b')
        escls_prms, líms_norm, x_norm, y_norm = ec.normalizar(
            líms_paráms={'a': (0, 1)}, obs_x=símismo.obs_x, obs_y=símismo.obs_y
        )
        símismo.assertAlmostEqual(x_norm['x'].values.std(), 1)
        símismo.assertTupleEqual(líms_norm['a'], (0, 1 / símismo.obs_x['x'].values.std()))

    def test_normalizar_y(símismo):
        ec = Ecuación('y=a*(x+b)')
        escls_prms, líms_norm, x_norm, y_norm = ec.normalizar(
            líms_paráms={'a': (0, 1)}, obs_x=símismo.obs_x, obs_y=símismo.obs_y
        )
        símismo.assertAlmostEqual(y_norm.values.std(), 1)
        símismo.assertTupleEqual(líms_norm['a'], (0, 1 / símismo.obs_y.values.std()))

    def test_normalizar_y_div(símismo):
        ec = Ecuación('y=a/(x+b)')
        escls_prms, líms_norm, x_norm, y_norm = ec.normalizar(
            líms_paráms={'a': (0, 1)}, obs_x=símismo.obs_x, obs_y=símismo.obs_y
        )
        símismo.assertAlmostEqual(y_norm.values.std(), 1)
        símismo.assertTupleEqual(líms_norm['a'], (0, 1 / símismo.obs_y.values.std()))

    def test_normalizar_y_coef_recipr(símismo):
        ec = Ecuación('y=(x+b)/a')
        escls_prms, líms_norm, x_norm, y_norm = ec.normalizar(
            líms_paráms={'a': (0, 1)}, obs_x=símismo.obs_x, obs_y=símismo.obs_y
        )
        símismo.assertAlmostEqual(y_norm.values.std(), 1)
        símismo.assertTupleEqual(líms_norm['a'], (0, 1 * símismo.obs_y.values.std()))
