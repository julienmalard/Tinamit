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
    Esat ecuación saca los variables de un texto.

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
    fin_fun = regex.search(r' *\) *\n?$', ec).start()

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

        if dialecto.lower() == 'vensim':
            gramática = resource_filename('tinamit.EnvolturaMDS', 'gram_Vensim.g')
        else:
            raise ValueError('')

        with open(gramática) as gm:
            anlzdr = Lark(gm, parser='lalr', start='ec')

        símismo.árbol = _Transformador().transform(anlzdr.parse(ec))

    def gen_mod_bayes(símismo, paráms, líms_paráms, obs_x, obs_y):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        dialecto = símismo.dialecto

        def _a_bayes(á):

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

                        if v[0] == '+':
                            return _a_bayes(v[1][0]) + _a_bayes(v[1][1])
                        elif [1] == '/':
                            _a_bayes(v[0]) / _a_bayes(v[1])
                        elif v[0] == '-':
                            return _a_bayes(v[1][0]) - _a_bayes(v[1][1])
                        elif v[0] == '*':
                            return _a_bayes(v[1][0]) * _a_bayes(v[1][1])
                        else:
                            return conv_fun(v[0], dialecto, 'pymc3')(*_a_bayes(v[1][1]))

                    elif ll == 'var':
                        try:
                            í_var = paráms.index(v)
                            líms = líms_paráms[í_var]
                            nmbr = 'v{}'.format(í_var)
                            if líms[0] == -np.inf:
                                if líms[1] == np.inf:
                                    return pm.Flat(nmbr)
                                else:
                                    return líms[1] - pm.HalfFlat(nmbr)
                            else:
                                if líms[1] == np.inf:
                                    return líms[0] + pm.HalfFlat(nmbr)
                                else:
                                    return pm.Uniform(name=nmbr, lower=líms[0], upper=líms[1])

                        except ValueError:

                            # Si el variable no es un parámetro calibrable, debe ser un valor observado
                            return obs_x[v]
                    else:
                        raise TypeError('')

            elif isinstance(á, list):
                return [_a_bayes(x) for x in á]
            elif isinstance(á, int) or isinstance(á, float):
                return á
            else:
                raise TypeError('')

        modelo = pm.Model()
        with modelo:
            mu = _a_bayes(símismo.árbol)
            sigma = pm.HalfNormal(name='sigma', sd=1)

            pm.Normal(name='Y_obs', mu=mu, sigma=sigma, observed=obs_y)

        return modelo

    def gen_texto(símismo, vars_paráms=None):

        dialecto = símismo.dialecto
        if vars_paráms is None:
            vars_paráms = []

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
                        else:
                            return '{nombre}({args})'.format(nombre=dic_funs_inv[dialecto][v[0]],
                                                             args=_a_tx(v[1], d_v=d_v))
                    elif ll == 'var':
                        try:
                            nmbr = 'p[{}]'.format(vars_paráms.index(v))
                        except ValueError:
                            if v in d_v:
                                return d_v[v]
                            else:
                                nmbr = 'v{}'.format(len(d_v))

                        d_v[v] = nmbr
                        return "d_x['{}']".format(nmbr)
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


dic_funs = {
    'min': {'vensim': 'MIN', 'pm': min, 'python': min},
    'max': {'vensim': 'MAX', 'pm': max, 'python': max},
    'abs': {'vensim': 'ABS', 'pm': pm.math.abs_, 'python': abs},
    'math.exp': {'vensim': 'EXP', 'pm': pm.math.exp, 'python': mat.exp},
    'int': {'vensim': 'INTEGER', 'pm': pm.math.floor, 'python': int},
    'math.log': {'vensim': 'LN', 'pm': pm.math.log, 'python': mat.log},
    'math.sin': {'vensim': 'SIN', 'pm': pm.math.sin},
    'math.cos': {'vensim': 'COS', 'pm': pm.math.cos},
    'math.tan': {'vensim': 'TAN', 'pm': pm.math.tan},
    'math.asin': {'vensim': 'ARCSIN'},
    'math.acos': {'vensim': 'ARCCOS'},
    'math.atan': {'vensim': 'ARCTAN'},
    'math.log10': {'vensim': 'LOG', 'pm': lambda x: pm.math.log(x) / mat.log(10), 'python': mat.log10},
    '+': {'vensim': '+'},
    '-': {'vensim': '-'},
    '*': {'vensim': '*'},
    '/': {'vensim': '/'}
}

dic_funs_inv = {}
for f, d_fun in dic_funs.items():
    for tipo, d in d_fun.items():
        if tipo not in dic_funs_inv:
            dic_funs_inv[tipo] = {}
        dic_funs_inv[tipo][d] = f


def conv_fun(fun, dialecto_0, dialecto_1):
    return dic_funs[dic_funs_inv[dialecto_0][fun]][dialecto_1]


if __name__ == '__main__':

    ecs = ['1', 'a', 'abv', "ab c", 'MIN(a[poli, canal],3)', '"abs()(\"#$0978"', '0.004/(5*12)',
           'MIN(2+ 3, abc d + 4) * 1 + 3', '1 + 2 * 3',
           'வண்க்கம்']

    with open('C:\\Users\\jmalar1\\PycharmProjects\\Tinamit\\tinamit\\EnvolturaMDS\\gram_Vensim.g') as grm:
        analizador = Lark(grm, parser='lalr', start='ec')

    for Ec in ecs:
        print('=============')
        print(Ec)
        árbol = analizador.parse(Ec)
        print(árbol.pretty())
        print(_Transformador().transform(árbol))
        print(Ecuación(Ec, dialecto='Vensim').gen_texto())
