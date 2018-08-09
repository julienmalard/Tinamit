import math
import unittest

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
        símismo.assertEquals(ec_py([], {'x': val_x}), resp)

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
