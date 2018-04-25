import numpy as np
import regex
from lark import Lark, Transformer
from pkg_resources import resource_filename
import math as mat

from tinamit import _

try:
    import pymc3 as pm
except ImportError:
    pm = None


def sacar_variables(texto, rgx, n=None, excluir=None):
    """
    Esta ecuación saca los variables de un texto.

    :param texto: El texto de cual extraer los nombres de los variables.
    :type texto: str

    :param rgx: La expersión regex correspondiendo al formato de los variables.
    :type rgx: str

    :param n: El número máximo de variables que sacar.
    :type n: int

    :param excluir: Nombres de variables para excluir
    :type excluir: list

    :return: Una lista de los nombres de los variables.
    :rtype: list

    """

    # Poner el variable excluir en el formato necesario.
    if excluir is None:
        excluir = []
    if type(excluir) is str:
        excluir = [excluir]

    # Buscar los nombres
    b = regex.finditer(rgx, texto)

    # Quitar espacios extras
    b = [x.groupdict()['var'].strip(' ') for x in b]

    # Devolver una lista de nombres de variables únicos.
    if n is None:
        return [x for x in set(b) if x not in excluir]
    else:
        return [x for x in set(b[:n]) if x not in excluir]


def sacar_arg(ec, regex_var, regex_fun, i=None):
    """
    Esta función saca los argumentos de una función.

    :param ec: La ecuación que contiene una función.
    :type ec: str

    :param regex_var:
    :type regex_var: str

    :param regex_fun:
    :type regex_fun: str

    :param i: El índice del argumento que querremos extraer (opcional)
    :type i: int

    :return: Una lista de los argumentos de la función
    :rtype: list[str] | str

    """

    # El principio de la función
    princ_fun = regex.match(regex_fun, ec).end()

    # El fin de la función
    fin_fun = regex.search(r' *\).*$', ec).start()

    # La parte de la ecuación con los argumentos de la función
    sec_args = ec[princ_fun:fin_fun]

    # Una lista de tuples con los índices de las ubicaciones de los variables
    pos_vars = [m.span() for m in regex.finditer(regex_var, sec_args)]

    # Una lista de las ubicaciones de TODAS las comas en el ecuación
    pos_comas = [m.start() for m in regex.finditer(r',', sec_args)]

    # Las índes de separación de argumentos de la función. Solo miramos las comas que NO hagan parte de un variable,
    # y agregamos un 0 al principio, y el último índice del texto al final.
    sep_args = [0] + [j for j in pos_comas if not any([p[0] <= j < p[1] for p in pos_vars])] + [len(sec_args)]

    # Dividimos la ecuación en argumentos
    args = [sec_args[p:sep_args[j + 1]] for j, p in enumerate(sep_args[:-1])]

    # Y devolvemos el argumento pedido.
    if i is None:
        return args
    else:
        return args[i]


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


def cortar_líns(texto, máx_car, lín_1=None, lín_otras=None):
    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            l = texto
        else:
            dif = máx_car - texto

            l = regex.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(l)
        texto = texto[len(l):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, l in enumerate(lista[1:]):
            lista[n] = lín_otras + l

    return lista


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

    args = list
    ec = list


class Ecuación(object):
    def __init__(símismo, ec, dialecto):
        símismo.ec = ec
        símismo.dialecto = dialecto.lower()

        if símismo.dialecto == 'tinamït':
            gramática = resource_filename('tinamit.EnvolturaMDS', 'gram_ec_tinamït.g')
        elif símismo.dialecto in ['modelovensimmdl', 'modelovensim']:
            gramática = resource_filename('tinamit.EnvolturaMDS', 'gram_Vensim.g')
        else:
            raise ValueError('')

        with open(gramática) as gm:
            anlzdr = Lark(gm, parser='lalr', start='ec')

        try:
            símismo.árbol = _Transformador().transform(anlzdr.parse(ec))[0]
        except BaseException as e:
            raise ValueError('Error en la ecuación "{}". Detalles: {}'.format(ec, e))

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
                            return set([i for x in v[1] for i in _obt_vars(x) ])

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

    def gen_func_python(símismo, paráms):

        dialecto = símismo.dialecto

        def _a_python(á, l_prms=paráms):

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

                        if v[0] == '+':
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)
                            return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
                        elif v[0] == '/':
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)
                            return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
                        elif v[0] == '-':
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)
                            return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
                        elif v[0] == '*':
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)
                            return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
                        elif v[0] == '^':
                            comp_1 = _a_python(v[1][0], l_prms=l_prms)
                            comp_2 = _a_python(v[1][1], l_prms=l_prms)
                            return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)
                        else:
                            fun = conv_fun(v[0], dialecto, 'python')
                            comp = _a_python(v[1][1], l_prms=l_prms)

                            return lambda p, vr: fun(*comp(p=p, vr=vr))

                    elif ll == 'var':
                        try:

                            í_var = l_prms.index(v)

                            return lambda p, vr: p[í_var]

                        except ValueError:
                            # Si el variable no es un parámetro calibrable, debe ser un valor observado
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

    def gen_mod_bayes(símismo, paráms, líms_paráms, obs_x, obs_y, aprioris=None, binario=False):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        dialecto = símismo.dialecto

        def _a_bayes(á, d_pm=None):
            if d_pm is None:
                d_pm = {}

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

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
                            return conv_fun(v[0], 'tinamït', 'pm')(*_a_bayes(v[1], d_pm=d_pm))  # para hacer: arreglar dialecto

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

                            # Si el variable no es un parámetro calibrable, debe ser un valor observado
                            return obs_x[v]
                    elif ll == 'neg':
                        return -_a_bayes(v, d_pm=d_pm)
                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return [_a_bayes(x, d_pm=d_pm) for x in á]
            elif isinstance(á, int) or isinstance(á, float):
                return á
            else:
                raise TypeError('')

        modelo = pm.Model()
        with modelo:
            mu = _a_bayes(símismo.árbol)
            sigma = pm.HalfNormal(name='sigma', sd=max(obs_y)/3)

            if binario:
                x = pm.Normal(name='logit_prob', mu=mu, sd=sigma, shape=obs_y.shape, testval=np.full(obs_y.shape, 0))
                pm.Bernoulli(name='Y_obs', p=pm.invlogit(-x), observed=obs_y)  #

            else:
                pm.Normal(name='Y_obs', mu=mu, sd=sigma, observed=obs_y)

        return modelo

    def gen_texto(símismo, paráms=None):

        dialecto = símismo.dialecto
        if paráms is None:
            paráms = []

        def _a_tx(á, d_v):

            if isinstance(á, dict):
                for ll, v in á.items():
                    if ll == 'func':
                        if v[0] == '+':
                            return '({} + {})'.format(_a_tx(v[1][0], d_v=d_v), _a_tx(v[1][1], d_v=d_v))
                        elif v[0] == '/':
                            return '({} / {})'.format(_a_tx(v[1][0], d_v=d_v), _a_tx(v[1][1], d_v=d_v))
                        elif v[0] == '-':
                            return '({} - {})'.format(_a_tx(v[1][0], d_v=d_v), _a_tx(v[1][1], d_v=d_v))
                        elif v[0] == '*':
                            return '({} * {})'.format(_a_tx(v[1][0], d_v=d_v), _a_tx(v[1][1], d_v=d_v))
                        elif v[0] == '^':
                            return '({} ^ {})'.format(_a_tx(v[1][0], d_v=d_v), _a_tx(v[1][1], d_v=d_v))
                        else:
                            return '{nombre}({args})'.format(nombre=dic_funs_inv[dialecto][v[0]],
                                                             args=_a_tx(v[1], d_v=d_v))
                    elif ll == 'var':
                        try:
                            nmbr = 'p[{}]'.format(paráms.index(v))
                        except ValueError:
                            if v in d_v:
                                return d_v[v]
                            else:
                                nmbr = "d_x['v{}']".format(len(d_v))

                        d_v[v] = nmbr
                        return nmbr
                    elif ll == 'neg':
                        return '-{}'.format(_a_tx(v, d_v=d_v))
                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return ', '.join([_a_tx(x, d_v=d_v) for x in á])
            elif isinstance(á, int) or isinstance(á, float):
                return str(á)
            else:
                raise TypeError('')

        d_vars = {}
        return _a_tx(símismo.árbol, d_v=d_vars), d_vars

    def __str__(símismo):
        return símismo.gen_texto()[0]


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


def conv_fun(fun, dialecto_0, dialecto_1):
    if dialecto_0 == 'tinamït':
        return dic_funs[fun][dialecto_1]
    else:
        return dic_funs[dic_funs_inv[dialecto_0][fun]][dialecto_1]


if __name__ == '__main__':

    ecs = ['1', 'a', 'abv', "ab c", 'MIN(a[poli, canal],3)', '"abs()(\"#$0978"', '0.004/(5*12)',
           'MIN(2+ 3, abc d + 4) * 1 + 3', '1 + 2 * 3',
           'வண்க்கம்']

    with open('C:\\Users\\jmalar1\\PycharmProjects\\Tinamit\\tinamit\\EnvolturaMDS\\gram_Vensim.g') as grm:
        analizador = Lark(grm, parser='lalr', start='ec')

    for Ec in ecs:
        print('=============')
        Ec = 'b/(educación+a)+c'
        print(Ec)
        árbol = analizador.parse(Ec)
        print(árbol.pretty())
        print(_Transformador().transform(árbol))
        e = Ecuación(Ec, dialecto='Vensim')
        print(e.gen_texto(paráms=['a', 'b', 'c']))

        m = e.gen_mod_bayes(paráms=['a', 'b', 'c'], líms_paráms=[(None, None), (None, None), (None, None)],
                            obs_x={'educación': np.array([1, 2, 3])}, obs_y=np.array([0, 0, 1]))
        with m:
            pm.sample()