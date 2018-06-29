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
    """
    Transformador de árboles sintácticos Lark a diccionarios Python.
    """

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
    """
    Un objeto para manejar ecuaciones dinámicas.
    """

    def __init__(símismo, ec, nombre=None, otras_ecs=None, nombres_equiv=None, dialecto=None):
        """
        Inicializa un objeto de ecuación.

        Parameters
        ----------
        ec: str
            La ecuación en formato texto.
        nombre: str
            El nombre del variable, si no está especificado en la ecuación sí misma.
        otras_ecs: dict[str, str]
            Un diccionario de ecuaciones para substituir para variables en la ecuación principal.
        nombres_equiv: dict[str, str]
            Un diccionario de cambios de nombres de variables para efectuar.
        dialecto: str
            El dialecto de la ecuación. Si no se especifica, se adivinará.
        """

        # Formatear parámetros vacíos
        if otras_ecs is None:
            otras_ecs = {}

        if nombres_equiv is None:
            nombres_equiv = {}

        if dialecto is None:
            dialecto = 'tinamït'

        # Guardar el dialecto y el nombre (convertir al nombre equivalente si necesario)
        símismo.dialecto = dialecto
        símismo.nombre = nombre if nombre not in nombres_equiv else nombres_equiv[nombre]

        # Si es una ecuación de vaariable o de subscripto
        símismo.tipo = 'var'

        # Cargar la gramática
        if dialecto not in l_grams_var:
            with open(l_dialectos_potenciales[dialecto], encoding='UTF-8') as d:
                l_grams_var[dialecto] = Lark(d, parser='lalr', start='ec')

        # Analizar la ecuación
        anlzdr = l_grams_var[dialecto]
        árbol = _Transformador().transform(anlzdr.parse(ec))

        # Aplicar subsituciones de ecuaciones de variables
        _subst_var_en_árbol(á=árbol, mp={v_otr: Ecuación(ec_otr).árbol for v_otr, ec_otr in otras_ecs.items()})

        # Aplicar substituciones de nombres
        _subst_var_en_árbol(á=árbol, mp=nombres_equiv)

        # Analizar los resultados
        if isinstance(árbol, dict):
            # Si la ecuación incluía el nombre del variable y...
            try:
                # Intentar para declaración de variables
                símismo.nombre = árbol['var']
                símismo.árbol = árbol['ec']
            except KeyError:
                # Si no funcionó, debe sser declaración de subsripto
                símismo.nombre = árbol['sub']
                símismo.árbol = árbol['nmbr_dims']
                símismo.tipo = 'sub'
        else:
            # Si no había el nombre del variable y, simplemente aplicamos el árbol.
            símismo.árbol = árbol[0]

    def variables(símismo):
        """
        Devuelve una lista de los variable de esta ecuación.

        Returns
        -------
        set:
            Un conjunto con todos los variables presentes en esta ecuación.
        """

        return _obt_vars(símismo.árbol)

    def gen_func_python(símismo, paráms):
        """
        Genera una función dinámica Python basada en la ecuación. La función generada tomará dos argumentos:
            1. p: una lista con valores para parámetros en el orden especificado en `paráms`.
            2. vr: Un diccionario con valores para cada variable presente en la ecuación y no incluido en `paráms`.

        Parameters
        ----------
        paráms: list
            La lista de parámetros.

        Returns
        -------
        Callable:
            La función dinámica Python.
        """

        return _árb_a_python(símismo.árbol, l_prms=paráms, dialecto=símismo.dialecto)

    def gen_mod_bayes(símismo, líms_paráms, obs_x, obs_y, aprioris=None, binario=False, nv_jerarquía=None):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        dialecto = símismo.dialecto

        def _gen_d_vars_pm(tmñ=(), fmt_nmbrs='{}'):
            egr = {}
            for p, líms in líms_paráms.items():
                nmbr = fmt_nmbrs.format(p)
                if aprioris is None:
                    if líms[0] is None:
                        if líms[1] is None:
                            dist_pm = pm.Flat(nmbr, shape=tmñ)
                        else:
                            if líms[1] == 0:
                                dist_pm = -pm.HalfFlat(nmbr, shape=tmñ)
                            else:
                                dist_pm = líms[1] - pm.HalfFlat(nmbr, shape=tmñ)
                    else:
                        if líms[1] is None:
                            if líms[0] == 0:
                                dist_pm = pm.HalfFlat(nmbr, shape=tmñ)
                            else:
                                dist_pm = líms[0] + pm.HalfFlat(nmbr, shape=tmñ)
                        else:
                            dist_pm = pm.Uniform(nmbr, lower=líms[0], upper=líms[1], shape=tmñ)
                else:
                    dist, prms = aprioris[p]
                    if (líms[0] is not None or líms[1] is not None) and dist != pm.Uniform:
                        acotada = pm.Bound(dist, lower=líms[0], upper=líms[1])
                        dist_pm = acotada(nmbr, shape=tmñ, **prms)
                    else:
                        if dist == pm.Uniform:
                            prms['lower'] = max(prms['lower'], líms[0])
                            prms['upper'] = min(prms['upper'], líms[1])
                        dist_pm = dist(nmbr, shape=tmñ, **prms)

                egr[p] = dist_pm
            return egr

        def _gen_d_vars_pm_jer():
            dists_base = _gen_d_vars_pm(
                tmñ=(len(set(nv_jerarquía[0])),), fmt_nmbrs='mu_{}_nv_' + str(len(nv_jerarquía) - 1)
            )

            egr = {}

            for p, líms in líms_paráms.items():
                mu = dists_base[p]
                sg = pm.HalfNormal(name='sg_{}'.format(p), sd=10, shape=(1,))  # type: pm.model.TransformedRV
                if líms[0] is líms[1] is None:
                    for í, nv in enumerate(nv_jerarquía[:-1]):
                        tmñ_nv = nv.shape
                        if í == (len(nv_jerarquía) - 2):
                            nmbr_mu = p
                        else:
                            nmbr_mu = 'mu_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)
                        nmbr_sg = 'sg_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)
                        mu = pm.Normal(name=nmbr_mu, mu=mu[nv], sd=sg[nv], shape=tmñ_nv)
                        sg = pm.HalfNormal(name=nmbr_sg.format(p, í), sd=10, shape=tmñ_nv)
                else:
                    for í, nv in enumerate(nv_jerarquía[:-1]):
                        tmñ_nv = nv.shape
                        if í == (len(nv_jerarquía) - 2):
                            nmbr_mu = p
                        else:
                            nmbr_mu = 'mu_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)
                        nmbr_sg = 'sg_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)

                        acotada = pm.Bound(pm.Normal, lower=líms[0], upper=líms[1])
                        mu = acotada(nmbr_mu, mu=mu[nv], sd=sg[nv], shape=tmñ_nv)
                        sg = pm.HalfNormal(name=nmbr_sg.format(p, í), sd=10, shape=tmñ_nv)

                egr[p] = mu

            return egr

        def _a_bayes(á, d_pm):

            if isinstance(á, dict):

                for ll, v in á.items():

                    if ll == 'func':

                        try:
                            op_pm = _conv_op(v[0], dialecto, 'pm')
                            return op_pm(_a_bayes(v[1][0], d_pm=d_pm), _a_bayes(v[1][1], d_pm=d_pm))
                        except (KeyError, StopIteration):
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
                            return _conv_fun(v[0], dialecto, 'pm')(*_a_bayes(v[1], d_pm=d_pm))

                    elif ll == 'var':
                        try:
                            if nv_jerarquía is None:
                                return d_pm[v]
                            else:
                                return d_pm[v][nv_jerarquía[-1]]

                        except KeyError:

                            # Si el variable no es un parámetro calibrable, debe ser un valor observado
                            try:
                                return obs_x[v].values

                            except KeyError:
                                raise ValueError(_('El variable "{}" no es un parámetro, y no se encuentra'
                                                   'en la base de datos observados tampoco.').format(v))

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
            if nv_jerarquía is None:
                d_vars_pm = _gen_d_vars_pm()
            else:
                d_vars_pm = _gen_d_vars_pm_jer()

            mu = _a_bayes(símismo.árbol, d_vars_pm)
            sigma = pm.HalfNormal(name='sigma', sd=max(1, (obs_y.max() - obs_y.min())))

            if binario:
                # noinspection PyTypeChecker
                x = pm.Normal(name='logit_prob', mu=mu, sd=sigma, shape=obs_y.shape, testval=np.full(obs_y.shape, 0))
                pm.Bernoulli(name='Y_obs', logit_p=-x, observed=obs_y.values)  #

            else:
                # noinspection PyTypeChecker
                pm.Normal(name='Y_obs', mu=mu, sd=sigma, observed=obs_y.values)

        return modelo

    def sacar_args_func(símismo, func, i):
        """
        Devuelve uno o más argumentos de una función presente en el árbol de la Ecuacion, en formato texto.

        Parameters
        ----------
        func: str
            La función cuyos argumentos buscamos.
        i: int
            El número de argumentos que querremos.

        Returns
        -------
        list[str]
            El argumento de la función.

        """

        # Para simplificar el código.
        dialecto = símismo.dialecto

        def _buscar_func(á, f):
            """
            Una función recursiva.

            Parameters
            ----------
            á: dict
                El árbol sintáctico en el cual buscar.
            f: str
                La función de interés.

            Returns
            -------
            list[str]
                Los argumentos de la función.

            """

            if isinstance(á, dict):
                # Visitar cada rama del diccionario de manera recursiva
                for ll, v in á.items():
                    if ll == 'func':
                        # Si es función, verificar si es la función de interés.
                        if v[0] == f:
                            return [_árb_a_txt(x, dialecto=dialecto) for x in v[1][:i]]
                    else:
                        for p in v[1]:
                            _buscar_func(p, f=func)

            elif isinstance(á, list):
                [_buscar_func(x, f=func) for x in á]
            else:
                # Sino, no tenemos nada que hacer.
                pass

        # Aplicar la función recursiva.
        return _buscar_func(símismo.árbol, f=func)

    def __str__(símismo):
        return _árb_a_txt(símismo.árbol, símismo.dialecto)


# Funciones auxiliares para ecuaciones.
_error_comp_ec = _('Componente de ecuación "{}" no reconocido.')


def _subst_var_en_árbol(á, mp):
    """
    Substituye variables en un árbol sintáctico. Funciona de manera recursiva.

    Parameters
    ----------
    á: dict
        El árbol sintáctico.
    mp: dict
        Un diccionario con nombres de variables y sus substituciones.

    """

    # Recursar a través del árbol.
    if isinstance(á, dict):
        # Si es diccionario, visitar todas sus ramas (llaves)

        for ll, v in á.items():

            if ll == 'func':
                # Para funciones, simplemente recursar a través de todos sus argumentos.
                for x in v[1]:
                    _subst_var_en_árbol(x, mp=mp)

            elif ll == 'var':
                # Para variables, subsituir si necesario.
                if v in mp:
                    á[ll] = mp[v]

            elif ll == 'neg' or ll == 'ec':
                # Para negativos y ecuaciones, seguir adelante
                _subst_var_en_árbol(v, mp=mp)

            else:
                # Dar error si encontramos algo que no reconocimos.
                raise TypeError(_error_comp_ec.format(ll))

    elif isinstance(á, list):
        # Para listas, recursar a través de cada elemento
        for x in á:
            _subst_var_en_árbol(x, mp=mp)

    elif isinstance(á, int) or isinstance(á, float):
        pass  # No hay nada que hacer para números.

    else:
        # El caso muy improbable de un error.
        raise TypeError(_error_comp_ec.format(type(á)))


def _árb_a_txt(á, dialecto):
    """
    Convierte un árbol sintáctico de ecuación a formato texto. Funciona como función recursiva.

    Parameters
    ----------
    á: dict
        El árbol sintáctico
    dialecto: str
        El dialecto del árbol.

    Returns
    -------
    str:
        La ecuación en formato texto.

    """

    # Simplificar el código
    dl = dialecto

    # Pasar a través todas las posibilidades para el árbol y sus ramas
    if isinstance(á, dict):
        # Si es diccionario, pasar a través de todas sus ramas (llaves)
        for ll, v in á.items():
            if ll == 'func':
                # Si es función, intentar tratarlo como operador primero
                try:
                    # Intentar convertir a dialecto Tinamït
                    tx_op = _conv_op(v[0], dialecto, 'tinamït')

                    # Devolver el texto correspondiendo a un operado (y recursar a través de los dos argumentos).
                    return '({a1} {o} {a2})'.format(a1=_árb_a_txt(v[1][0], dl), o=tx_op, a2=_árb_a_txt(v[1][1], dl))
                except (KeyError, StopIteration):
                    pass  # Si no funcionó, tal vez no es operador.

                try:
                    # Intentar convertirlo, como nombre de función, a dialecto Tïnamit
                    return '{nombre}({args})'.format(nombre=_conv_fun(v[0], dialecto, 'tinamït'),
                                                     args=_árb_a_txt(v[1], dl))
                except (KeyError, StopIteration):
                    # Si no funcionó, simplemente formatearlo con el nombre original de la función.
                    return '{nombre}({args})'.format(nombre=v[0], args=_árb_a_txt(v[1], dl))

            elif ll == 'var':
                # Si es variable, simplemente devolver el nombre del variable
                return v

            elif ll == 'neg':
                # Formatear negativos
                return '-{}'.format(_árb_a_txt(v, dl))

            else:
                # Si no es función, variable o negativo, tenemos error.
                raise TypeError(_error_comp_ec.format(ll))

    elif isinstance(á, list):
        # Si es lista (por ejemplo, un lista de parámetros de una ecuación), recursar a través de sus elementos.
        return ', '.join([_árb_a_txt(x, dl) for x in á])

    elif isinstance(á, int) or isinstance(á, float):
        # Números se devuelven así
        return str(á)

    else:
        # Si no es diccionario, lista, o número, no sé lo que es.
        raise TypeError(_error_comp_ec.format(type(á)))


def _árb_a_python(á, l_prms, dialecto):
    """
    Función recursiva para convertir el árbol sintáctico a función Python.

    Parameters
    ----------
    á: dict
        El árbol sintáctico.
    l_prms: list
        La lista de parámetros.
    dialecto: str
        El dialecto de la ecuación.

    Returns
    -------
    Callable
        La ecuación dinámico Python.

    """

    # Simplificar el código.
    dl = dialecto

    # Pasar a través del árbol
    if isinstance(á, dict):

        for ll, v in á.items():
            # Para cada rama del diccionario...

            if ll == 'func':
                # Si es función, intentar como operado primero.
                try:
                    op = _conv_op(v[0], dialecto, 'tinamït')

                    # Recursar a través de los componentes del operador ahora. Es importante hacerlo antes de
                    # las expresiones ``lambda``; sino se llamará `_árb_a_python` sí mismo cada vez que se llama
                    # la función generada.
                    comp_1 = _árb_a_python(v[1][0], l_prms, dl)
                    comp_2 = _árb_a_python(v[1][1], l_prms, dl)

                    # Convertir el operado a función Python dinámica.
                    if op == '+':
                        return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
                    elif op == '/':
                        return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
                    elif op == '-':
                        return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
                    elif op == '*':
                        return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
                    elif op == '^':
                        return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)
                    elif op == '>':
                        return lambda p, vr: comp_1(p=p, vr=vr) > comp_2(p=p, vr=vr)
                    elif op == '<':
                        return lambda p, vr: comp_1(p=p, vr=vr) < comp_2(p=p, vr=vr)
                    elif op == '>=':
                        return lambda p, vr: comp_1(p=p, vr=vr) >= comp_2(p=p, vr=vr)
                    elif op == '<=':
                        return lambda p, vr: comp_1(p=p, vr=vr) <= comp_2(p=p, vr=vr)
                    elif op == '==':
                        return lambda p, vr: comp_1(p=p, vr=vr) == comp_2(p=p, vr=vr)
                    elif op == '!=':
                        return lambda p, vr: comp_1(p=p, vr=vr) != comp_2(p=p, vr=vr)
                    else:
                        # Si no sabemos lo que tenemos, hay error.
                        raise ValueError(_('Operador "{}" no reconocido').format(v[0]))

                except (KeyError, StopIteration):
                    # Si no era operado, es función de verdad.
                    fun = _conv_fun(v[0], dialecto, 'python')  # Traducir la función a Python
                    comp = _árb_a_python(v[1][1], l_prms, dl)  # Recursar a través de los argumentos de la función

                    # Devolver la función dinámica
                    return lambda p, vr: fun(*comp(p=p, vr=vr))

            elif ll == 'var':
                try:
                    # Si el variable existe en la lista de parámetros, obtenerlo de `p`.
                    í_var = l_prms.index(v)

                    return lambda p, vr: p[í_var]

                except ValueError:
                    # Si el variable no es un parámetro calibrable, debe ser un valor observado.
                    return lambda p, vr: vr[v]

            elif ll == 'neg':
                # Aplicar negativos
                comp = _árb_a_python(v[1][1], l_prms, dl)
                return lambda p, vr: -comp(p=p, vr=vr)

            else:
                # Avisar si hubo error.
                raise TypeError(_error_comp_ec.format(ll))

    elif isinstance(á, list):
        # Recursar a través de los elementos de una lista.
        return [_árb_a_python(x, l_prms, dl) for x in á]

    elif isinstance(á, int) or isinstance(á, float):
        # Devolver números así
        return lambda p, vr: á

    else:
        # Avisar si hubo error.
        raise TypeError(_error_comp_ec.format(á))


def _obt_vars(á):
    """
    Devuelve los variables presentes en un árbol sintáctico de ecuación.

    Parameters
    ----------
    á: dict
        El árbol sintáctico.

    Returns
    -------
    set:
        El conjunto de variables presentes.
    """

    # Pasar a través del árbol
    if isinstance(á, dict):
        # Para cada rama del árbol...

        for ll, v in á.items():

            if ll == 'func':
                # Iterar a través de los argumentos de la función.
                return set([i for x in v[1] for i in _obt_vars(x)])

            elif ll == 'var':
                # Devolver el variable
                return {v}

            elif ll == 'neg':
                # Hacer nada
                return set()

            else:
                # Hubo error
                raise TypeError(_error_comp_ec.format(ll))

    elif isinstance(á, list):
        # Pasar a través de cada itema de la lista
        return {z for x in á for z in _obt_vars(x)}

    elif isinstance(á, int) or isinstance(á, float):
        # No hay nada que hacer para números
        return set()
    else:
        # Hubo error
        raise TypeError(_error_comp_ec.format(type(á)))


# Un diccionario con conversiones de funciones reconocidas. Si quieres activar más funciones, agregarlas aqui.
_dic_funs = {
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

# Diccionario de operadores. Notar que algunos se traducen por funciones en PyMC3.
_dic_ops = {
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


# Funciones auxiliares
def _conv_fun(fun, dialecto_orig, dialecto_final):
    """
    Traduce una función a otro dialecto.

    Parameters
    ----------
    fun: str
        La función para traducir.
    dialecto_orig: str
        El dialecto original de la función.
    dialecto_final: str
        El dialecto final deseado.

    Returns
    -------
    str | Callable
        La función traducida.
    """

    if dialecto_final == dialecto_orig:
        return fun
    if dialecto_orig == 'tinamït':
        return _dic_funs[fun][dialecto_final]
    else:
        if dialecto_final == 'tinamït':
            return next(ll for ll, d in _dic_funs.items() if d[dialecto_orig] == fun)
        else:
            return next(d[dialecto_final] for ll, d in _dic_funs.items() if d[dialecto_orig] == fun)


def _conv_op(oper, dialecto_orig, dialecto_final):
    """
    Traduce un operador a otro dialecto.

    Parameters
    ----------
    oper: str
        El operador para traducir.
    dialecto_orig: str
        El dialecto original del operador.
    dialecto_final: str
        El dialecto final deseado.

    Returns
    -------
    str | Callable
        El operador traducido.
    """

    if dialecto_final == dialecto_orig:
        return oper
    if dialecto_orig == 'tinamït':
        return _dic_ops[oper][dialecto_final]
    else:
        if dialecto_final == 'tinamït':
            return next(ll for ll, d in _dic_ops.items() if d[dialecto_orig] == oper)
        else:
            return next(d[dialecto_final] for ll, d in _dic_ops.items() if d[dialecto_orig] == oper)


# Para hacer: Funciones que hay que reemplazar con algo más elegante
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
