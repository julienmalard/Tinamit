import math as mat

import numpy as np
import regex
from lark import Lark, Transformer
from pkg_resources import resource_filename

from tinamit import _

try:
    import pymc3 as pm
except ImportError:
    pm = None

l_dialectos_potenciales = {
    'vensim': resource_filename('tinamit.Análisis', 'grams/gram_Vensim.g'),
    'tinamït': resource_filename('tinamit.Análisis', 'grams/gram_Vensim.g')  # Por el momento, es lo mismo
}
l_grams_def_var = {}
l_grams_var = {}


class _Transformador(Transformer):
    @staticmethod
    def num(x):
        return float(x[0])

    @staticmethod
    def neg(x):
        return {'neg': x[0]}

    @staticmethod
    def var(x):
        return {'var': x[0]}

    @staticmethod
    def nombre(x):
        return str(x[0])

    @staticmethod
    def cadena(x):
        return str(x[0])

    @staticmethod
    def func(x):
        return {'func': x}

    @staticmethod
    def pod(x):
        return {'func': ['^', x]}

    @staticmethod
    def mul(x):
        return {'func': ['*', x]}

    @staticmethod
    def div(x):
        return {'func': ['/', x]}

    @staticmethod
    def suma(x):
        return {'func': ['+', x]}

    @staticmethod
    def sub(x):
        return {'func': ['-', x]}

    @staticmethod
    def asign_var(x):
        return {'var': x[0]['var'], 'ec': x[1]}

    @staticmethod
    def asign_sub(x):
        return {'sub': x[0]['var'], 'nmbr_dims': x[1]}

    args = list
    ec = list


class Ecuación(object):
    def __init__(símismo, ec, nombre=None, dialecto=None):

        if dialecto is None:
            dialecto = 'tinamït'
        símismo.dialecto = dialecto

        símismo.nombre = nombre
        símismo.tipo = 'var'
        símismo.árbol = None

        if dialecto not in l_grams_var:
            with open(l_dialectos_potenciales[dialecto], encoding='UTF-8') as d:
                l_grams_var[dialecto] = Lark(d, parser='lalr', start='ec')
        anlzdr = l_grams_var[dialecto]

        árbol = _Transformador().transform(anlzdr.parse(ec))
        if isinstance(árbol, dict):
            try:
                símismo.nombre = árbol['var']
                símismo.árbol = árbol['ec']
            except KeyError:
                símismo.nombre = árbol['sub']
                símismo.árbol = árbol['nmbr_dims']
                símismo.tipo = 'sub'
        else:
            símismo.árbol = árbol[0]

    def variables(símismo):

        def _obt_vars(á):
            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':
                        if v[0] in ['+', '-', '/', '*', '^']:
                            vrs = _obt_vars(v[1][0])
                            vrs.update(_obt_vars(v[1][1]))

                            return vrs

                        else:
                            return set([i for x in v[1] for i in _obt_vars(x)])

                    elif ll == 'var':
                        return {v}

                    elif ll == 'neg':
                        return set()

                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return {z for x in á for z in _obt_vars(x)}
            elif isinstance(á, int) or isinstance(á, float):
                return set()
            else:
                raise TypeError('{}'.format(type(á)))

        return _obt_vars(símismo.árbol)

    def gen_func_python(símismo, paráms, otras_ecs=None):

        if otras_ecs is None:
            otras_ecs = {}

        dialecto = símismo.dialecto

        def _a_python(á, l_prms=paráms):

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

                        if v[0] in dic_ops_inv[dialecto]:
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)

                        if v[0] == '+':
                            return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
                        elif v[0] == '/':
                            return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
                        elif v[0] == '-':
                            return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
                        elif v[0] == '*':
                            return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
                        elif v[0] == '^':
                            return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)
                        elif v[0] == '>':
                            return lambda p, vr: comp_1(p=p, vr=vr) > comp_2(p=p, vr=vr)
                        elif v[0] == '<':
                            return lambda p, vr: comp_1(p=p, vr=vr) < comp_2(p=p, vr=vr)
                        elif v[0] == '>=':
                            return lambda p, vr: comp_1(p=p, vr=vr) >= comp_2(p=p, vr=vr)
                        elif v[0] == '<=':
                            return lambda p, vr: comp_1(p=p, vr=vr) <= comp_2(p=p, vr=vr)
                        elif v[0] == '==':
                            return lambda p, vr: comp_1(p=p, vr=vr) == comp_2(p=p, vr=vr)
                        elif v[0] == '!=':
                            return lambda p, vr: comp_1(p=p, vr=vr) != comp_2(p=p, vr=vr)

                        else:
                            fun = conv_fun(v[0], dialecto, 'python')
                            comp = _a_python(v[1][1], l_prms=l_prms)

                            return lambda p, vr: fun(*comp(p=p, vr=vr))

                    elif ll == 'var':
                        try:
                            í_var = l_prms.index(v)

                            return lambda p, vr: p[í_var]

                        except ValueError:
                            # Si el variable no es un parámetro calibrable, debe ser un valor observado, al menos
                            # que esté espeficado por otra ecuación.
                            if v in otras_ecs:

                                ec = otras_ecs[v]
                                if isinstance(ec, Ecuación):
                                    árb = ec.árbol
                                else:
                                    árb = Ecuación(ec).árbol
                                return _a_python(á=árb, l_prms=l_prms)

                            else:
                                return lambda p, vr: vr[v]

                    elif ll == 'neg':
                        comp = _a_python(v[1][1], l_prms=l_prms)
                        return lambda p, vr: -comp(p=p, vr=vr)
                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return [_a_python(x) for x in á]
            elif isinstance(á, int) or isinstance(á, float):
                return lambda p, vr: á
            else:
                raise TypeError('{}'.format(type(á)))

        return _a_python(símismo.árbol)

    def gen_mod_bayes(símismo, paráms, líms_paráms, obs_x, obs_y, aprioris=None, binario=False, otras_ecs=None):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        if obs_x is None:
            obs_x = {}
        if obs_y is None:
            obs_y = {}

        if otras_ecs is None:
            otras_ecs = {}

        dialecto = símismo.dialecto

        d_vars_obs = {}

        def _a_bayes(á, d_pm=None):
            if d_pm is None:
                d_pm = {}

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

                        try:
                            op_pm = conv_op(v[0], dialecto, 'pm')
                            return op_pm(_a_bayes(v[1][0], d_pm=d_pm), _a_bayes(v[1][1], d_pm=d_pm))
                        except KeyError:
                            pass

                        if v[0] == '+':
                            return _a_bayes(v[1][0], d_pm=d_pm) + _a_bayes(v[1][1], d_pm=d_pm)
                        elif v[0] == '/':
                            return _a_bayes(v[1][0], d_pm=d_pm) / _a_bayes(v[1][1], d_pm=d_pm)
                        elif v[0] == '-':
                            return _a_bayes(v[1][0], d_pm=d_pm) - _a_bayes(v[1][1], d_pm=d_pm)
                        elif v[0] == '*':
                            return _a_bayes(v[1][0], d_pm=d_pm) * _a_bayes(v[1][1], d_pm=d_pm)
                        elif v[0] == '^':
                            return _a_bayes(v[1][0], d_pm=d_pm) ** _a_bayes(v[1][1], d_pm=d_pm)

                        else:
                            return conv_fun(v[0], dialecto, 'pm')(
                                *_a_bayes(v[1], d_pm=d_pm))

                    elif ll == 'var':
                        try:
                            if v in d_pm:
                                return d_pm[v]
                            else:
                                í_var = paráms.index(v)
                                líms = líms_paráms[í_var]

                                if aprioris is None:
                                    if líms[0] is None:
                                        if líms[1] is None:
                                            dist_pm = pm.Flat(v, testval=0)
                                        else:
                                            dist_pm = líms[1] - pm.HalfFlat(v, testval=1)
                                    else:
                                        if líms[1] is None:
                                            dist_pm = líms[0] + pm.HalfFlat(v, testval=1)
                                        else:
                                            dist_pm = pm.Uniform(name=v, lower=líms[0], upper=líms[1])
                                else:
                                    dist, prms = aprioris[í_var]
                                    if (líms[0] is not None or líms[1] is not None) and dist != pm.Uniform:
                                        acotada = pm.Bound(dist, lower=líms[0], upper=líms[1])
                                        dist_pm = acotada(v, **prms)
                                    else:
                                        if dist == pm.Uniform:
                                            prms['lower'] = max(prms['lower'], líms[0])
                                            prms['upper'] = min(prms['upper'], líms[1])
                                        dist_pm = dist(v, **prms)

                                d_pm[v] = dist_pm
                                return dist_pm

                        except ValueError:

                            # Si el variable no es un parámetro calibrable, debe ser un valor observado, al menos
                            # que haya otra ecuación que lo describa
                            if v in otras_ecs:
                                ec = otras_ecs[v]
                                if isinstance(ec, Ecuación):
                                    árb = ec.árbol
                                else:
                                    árb = Ecuación(ec).árbol
                                return _a_bayes(á=árb, d_pm=d_pm)

                            else:
                                # Si no se especificó otra ecuación para este variable, debe ser un valor observado.
                                try:
                                    return obs_x[v]
                                except KeyError:
                                    d_vars_obs[v] = theano.shared()
                                    return d_vars_obs[v]
                    elif ll == 'neg':
                        return -_a_bayes(v, d_pm=d_pm)
                    else:
                        raise ValueError(_('Llave "{ll}" desconocida en el árbol sintático de la ecuación "{ec}". '
                                           'Éste es un error de programación en Tinamït.').format(ll=ll, ec=símismo))

            elif isinstance(á, list):
                return [_a_bayes(x, d_pm=d_pm) for x in á]
            elif isinstance(á, int) or isinstance(á, float):
                return á
            else:
                raise TypeError('')

        modelo = pm.Model()
        with modelo:
            mu = _a_bayes(símismo.árbol)
            sigma = pm.HalfNormal(name='sigma', sd=max(obs_y) / 3)

            if binario:
                x = pm.Normal(name='logit_prob', mu=mu, sd=sigma, shape=obs_y.shape, testval=np.full(obs_y.shape, 0))
                pm.Bernoulli(name='Y_obs', logit_p=-x, observed=obs_y)  #

            else:
                pm.Normal(name='Y_obs', mu=mu, sd=sigma, observed=obs_y)

        return modelo, d_vars_obs

    def sacar_args_func(símismo, func, i):

        árbol_ec_a_texto = símismo.árbol_ec_a_texto
        dialecto = símismo.dialecto

        def _buscar_func(á, f):

            if isinstance(á, dict):
                for ll, v in á.items():
                    if ll == 'func':
                        if v[0] == f:
                            return [árbol_ec_a_texto(x, dialecto=dialecto) for x in v[1][:i]]
                    else:
                        for p in v[1]:
                            _buscar_func(p, f=func)

            elif isinstance(á, list):
                [_buscar_func(x, f=func) for x in á]
            else:
                pass

        return _buscar_func(símismo.árbol, f=func)

    @staticmethod
    def árbol_ec_a_texto(árb, dialecto):

        def _a_tx(á):

            if isinstance(á, dict):
                for ll, v in á.items():
                    if ll == 'func':
                        try:
                            tx_op = dic_ops_inv[dialecto][v[0]]
                            return '({a1} {o} {a2})'.format(a1=_a_tx(v[1][0]), o=tx_op, a2=_a_tx(v[1][1]))
                        except KeyError:
                            pass

                        try:
                            return '{nombre}({args})'.format(nombre=dic_funs_inv[dialecto][v[0]],
                                                             args=_a_tx(v[1]))
                        except KeyError:
                            return '{nombre}({args})'.format(nombre=v[0], args=_a_tx(v[1]))

                    elif ll == 'var':
                        return v
                    elif ll == 'neg':
                        return '-{}'.format(_a_tx(v))
                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return ', '.join([_a_tx(x) for x in á])
            elif isinstance(á, int) or isinstance(á, float):
                return str(á)
            else:
                raise TypeError('')

        return _a_tx(árb)

    def __str__(símismo):
        return símismo.árbol_ec_a_texto(símismo.árbol, símismo.dialecto)


dic_funs = {
    'mín': {'vensim': 'MIN', 'pm': pm.math.minimum if pm is not None else None, 'python': min},
    'máx': {'vensim': 'MAX', 'pm': pm.math.maximum if pm is not None else None, 'python': max},
    'abs': {'vensim': 'ABS', 'pm': pm.math.abs_ if pm is not None else None, 'python': abs},
    'exp': {'vensim': 'EXP', 'pm': pm.math.exp if pm is not None else None, 'python': mat.exp},
    'ent': {'vensim': 'INTEGER', 'pm': pm.math.floor if pm is not None else None, 'python': int},
    'rcd': {'vensim': 'SQRT', 'pm': pm.math.sqrt if pm is not None else None, 'python': mat.sqrt},
    'ln': {'vensim': 'LN', 'pm': pm.math.log if pm is not None else None, 'python': mat.log},
    'log': {'vensim': 'LOG', 'pm': None if pm is None else lambda x: pm.math.log(x) / mat.log(10), 'python': mat.log10},
    'sin': {'vensim': 'SIN', 'pm': pm.math.sin if pm is not None else None, 'python': mat.sin},
    'cos': {'vensim': 'COS', 'pm': pm.math.cos if pm is not None else None, 'python': mat.cos},
    'tan': {'vensim': 'TAN', 'pm': pm.math.tan if pm is not None else None, 'python': mat.tan},
    'sinh': {'vensim': 'SINH', 'pm': pm.math.sinh if pm is not None else None, 'python': mat.sinh},
    'cosh': {'vensim': 'COSH', 'pm': pm.math.cosh if pm is not None else None, 'python': mat.cosh},
    'tanh': {'vensim': 'TANH', 'pm': pm.math.tanh if pm is not None else None, 'python': mat.tanh},
    'asin': {'vensim': 'ARCSIN', 'python': mat.asin},
    'acos': {'vensim': 'ARCCOS', 'python': mat.acos},
    'atan': {'vensim': 'ARCTAN', 'python': mat.atan},
    'si_sino': {'vensim': 'IF THEN ELSE', 'pm': pm.math.switch if pm is not None else None,
                'python': lambda cond, si, sino: si if cond else sino}
}
dic_ops = {
    '>': {'vensim': '>', 'pm': pm.math.gt if pm is not None else None},
    '<': {'vensim': '<', 'pm': pm.math.lt if pm is not None else None},
    '>=': {'vensim': '>=', 'pm': pm.math.ge if pm is not None else None},
    '<=': {'vensim': '<=', 'pm': pm.math.le if pm is not None else None},
    '==': {'vensim': '=', 'pm': pm.math.eq if pm is not None else None},
    '!=': {'vensim': '<>', 'pm': pm.math.neq if pm is not None else None},
    '+': {'vensim': '+'},
    '-': {'vensim': '-'},
    '*': {'vensim': '*'},
    '^': {'vensim': '^'},
    '/': {'vensim': '/'}
}

dic_funs_inv = {}
for f, d_fun in dic_funs.items():
    for tipo, d in d_fun.items():
        if tipo not in dic_funs_inv:
            dic_funs_inv[tipo] = {}
        dic_funs_inv[tipo][d] = f

dic_ops_inv = {}
for op, d_op in dic_ops.items():
    for tipo, d in d_op.items():
        if tipo not in dic_ops_inv:
            dic_ops_inv[tipo] = {}
        dic_ops_inv[tipo][d] = op


def conv_fun(fun, dialecto_0, dialecto_1):
    if dialecto_0 == 'tinamït':
        return dic_funs[fun][dialecto_1]
    else:
        return dic_funs[dic_funs_inv[dialecto_0][fun]][dialecto_1]


def conv_op(oper, dialecto_0, dialecto_1):
    if dialecto_0 == 'tinamït':
        return dic_ops[oper][dialecto_1]
    else:
        return dic_ops[dic_ops_inv[dialecto_0][oper]][dialecto_1]


# Funciones que hay que reemplazar con algo más elegante
def juntar_líns(l, cabeza=None, cola=None):
    """
    Esta función junta una lista de líneas de texto en una sola línea de texto.

    :param l: La lexta de líneas de texto.
    :type l: list[str]

    :param cabeza:
    :type cabeza:

    :param cola:
    :type cola:

    :return: El texto combinado.
    :rtype: str

    """

    # Quitar text no deseado del principio y del final
    if cabeza is not None:
        l[0] = regex.sub(r'^({})'.format(cabeza), '', l[0])
    if cola is not None:
        l[-1] = regex.sub(r'{}$'.format(cola), '', l[-1])

    # Quitar tabulaciones y símbolos de final de línea
    l = [x.lstrip('\t').rstrip('\n').rstrip('\\') for x in l]

    # Combinar las líneas y quitar espacios al principio y al final
    texto = ''.join(l).strip(' ')

    # Devolver el texto combinado.
    return texto
