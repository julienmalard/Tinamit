import math as mat

import numpy as np
import regex
from pkg_resources import resource_filename

from lark import Lark, Tree
from lark.lexer import Token
from lark.visitors import Transformer_InPlace, Visitor
from tinamit.config import _

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None

l_dialectos_potenciales = {
    'vensim': resource_filename('tinamit.Análisis', 'grams/gram_ecs.g'),
    'tinamït': resource_filename('tinamit.Análisis', 'grams/gram_ecs.g')  # Por el momento, es lo mismo
}
l_grams_def_var = {}
l_grams_var = {}


class _TrnsfSubstNmbrs(Transformer_InPlace):
    def __init__(símismo, subst):
        símismo.subst = subst
        super().__init__()

    def var(símismo, x):
        try:
            sub = símismo.subst[x[0]]
            if isinstance(sub, str):
                return Tree('var', Token('NOMBRE', sub))
            else:
                return sub
        except KeyError:
            return Tree('var', x)


class _VstrSacarVars(Visitor):
    def __init__(símismo):
        símismo.c_vars = set()

    def var(símismo, x):
        símismo.c_vars.add(str(x.children[0]))

    def __call__(símismo, árbol):
        símismo.c_vars.clear()
        símismo.visit(árbol)
        return símismo.c_vars


class _VstrAPy(object):
    def __init__(símismo, l_prms, dialecto):
        símismo.l_prms = l_prms
        símismo.dialecto = dialecto

    def func(símismo, x):
        fun = _conv_fun(x.children[0], símismo.dialecto, 'python')  # Traducir la función a Python
        comp = [símismo.transformar(a) for a in
                x.children[1].children]  # Recursar a través de los argumentos de la función

        # Devolver la función dinámica
        return lambda p, vr: fun(*[a(p=p, vr=vr) for a in comp])

    def neg(símismo, x):
        comp = símismo.transformar(x.children[0])
        return lambda p, vr: -comp(p=p, vr=vr)

    def var(símismo, x):
        v = str(x.children[0])
        try:
            # Si el variable existe en la lista de parámetros, obtenerlo de `p`.
            í_var = símismo.l_prms.index(v)

            return lambda p, vr: p[í_var]

        except ValueError:
            # Si el variable no es un parámetro calibrable, debe ser un valor observado.
            return lambda p, vr: vr[v]

    def num(símismo, x):
        return lambda p, vr: float(x.children[0])

    def prod(símismo, x):
        # Recursar a través de los componentes del operador ahora. Es importante hacerlo antes de
        # las expresiones ``lambda``; sino se llamará `transformar()` sí mismo cada vez que se llama
        # la función generada.
        comp_1 = símismo.transformar(x.children[0])
        comp_2 = símismo.transformar(x.children[2])
        op = símismo.transformar(x.children[1])

        if op == '*':
            return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
        elif op == '/':
            return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        comp_1 = símismo.transformar(x.children[0])
        comp_2 = símismo.transformar(x.children[2])
        op = símismo.transformar(x.children[1])

        if op == '+':
            return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
        elif op == '-':
            return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        comp_1 = símismo.transformar(x.children[0])
        comp_2 = símismo.transformar(x.children[1])
        return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)

    def comp(símismo, x):
        comp_1 = símismo.transformar(x.children[0])
        comp_2 = símismo.transformar(x.children[2])
        op = símismo.transformar(x.children[1])

        if op == '>':
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
            raise ValueError(op)

    def op_comp(símismo, x):
        return str(x.children[0])

    def transformar(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class _VstrATx(object):
    def __init__(símismo, dialecto):
        símismo.dialecto = dialecto

    def func(símismo, x):
        args = [símismo.transformar(a) for a in x.children[1].children]
        if len(args) != 1:
            return str(x.children[0]) + '(' + ', '.join(args) + ')'
        elif len(args) == 1:
            return str(x.children[0]) + '(' + args[0] + ')'

    def neg(símismo, x):
        return '-' + símismo.transformar(x.children[0])

    def var(símismo, x):
        return str(x.children[0])

    def num(símismo, x):
        return str(x.children[0])

    def prod(símismo, x):
        return ''.join(símismo.transformar(a) for a in x.children)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        return ''.join(símismo.transformar(a) for a in x.children)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        return símismo.transformar(x.children[0]) + '^' + símismo.transformar(x.children[1])

    def comp(símismo, x):
        return ''.join(símismo.transformar(a) for a in x.children)

    def op_comp(símismo, x):
        return str(x.children[0])

    def transformar(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class _VstrExtrArgs(Visitor):
    def __init__(símismo, f, i, dial):
        símismo.f = f
        símismo.i = i
        símismo.dial = dial
        símismo.args_f = None

    def func(símismo, x):
        if x.children[0] == símismo.f:
            símismo.args_f = [
                _VstrATx(dialecto=símismo.dial).transformar(e) for e in x.children[1].children[:símismo.i]
            ]

    def __call__(símismo, árbol):
        símismo.args_f = None
        símismo.visit(árbol)
        return símismo.args_f


class _VstrCoefDe(Visitor):
    def __init__(símismo):
        símismo.coef = None
        símismo.inv = None
        símismo.vr = None
        símismo.l_vars = []

    def _valid_consist(símismo, coef, inv):
        if símismo.coef is None:
            símismo.coef = coef
            símismo.inv = inv
        else:
            if símismo.coef != coef or símismo.inv != inv:
                símismo.coef = símismo.inv = None

    def prod(símismo, x):
        coef = None
        if x.children[1].children[0] == '*':
            inv = False

            if x.children[0].children[0] == símismo.vr and x.children[0].children[0] not in símismo.l_vars:
                if x.children[2].data == 'var':
                    coef = str(x.children[2].children[0])
            elif x.children[2].children[0] == símismo.vr and x.children[0].children[0] not in símismo.l_vars:
                if x.children[0].data == 'var':
                    coef = str(x.children[0].children[0])
        else:
            inv = True
            if x.children[0].children[0] == símismo.vr and x.children[0].children[0] not in símismo.l_vars:
                if x.children[2].data == 'var':
                    coef = str(x.children[2].children[0])
            elif x.children[2].children[0] == símismo.vr and x.children[0].children[0] not in símismo.l_vars:
                if x.children[0].data == 'var':
                    coef = str(x.children[0].children[0])

        if coef is not None:
            símismo._valid_consist(coef, inv)

    def __call__(símismo, árbol, var, l_vars=None):
        símismo.vr = var
        símismo.coef = símismo.inv = None
        símismo.l_vars = [] if l_vars is None else l_vars
        símismo.visit(árbol)
        if símismo.coef is None:
            return None
        else:
            return símismo.coef, símismo.inv


def _coef_de_ec(árbol, l_vars=None):
    if l_vars is None:
        l_vars = []
    if árbol.data == 'prod':
        arg1 = árbol.children[0]
        arg2 = árbol.children[2]
        op = árbol.children[1].children[0]

        v = None
        if op == '*':
            if arg1.data == 'var':
                v = arg1.children[0]
            elif arg2.data == 'var':
                v = arg2.children[0]
            inv = False

        else:
            if arg1.data == 'var':
                v = arg1.children[0]
            elif arg2.data == 'var':
                v = arg2.children[0]
            inv = True

        if v is not None and v not in l_vars:
            return v, inv
    return None


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

        # Si es una ecuación de vaariable o de subscripto
        símismo.tipo = 'var'

        # Cargar la gramática
        if dialecto not in l_grams_var:
            with open(l_dialectos_potenciales[dialecto], encoding='UTF-8') as d:
                l_grams_var[dialecto] = Lark(d, parser='lalr', start='ec')

        # Analizar la ecuación
        anlzdr = l_grams_var[dialecto]
        árbol = anlzdr.parse(ec)

        # Aplicar subsituciones de ecuaciones de variables
        subst = {v_otr: Ecuación(ec_otr, otras_ecs={v: otr for v, otr in otras_ecs.items() if v != v_otr}).árbol for
                 v_otr, ec_otr in otras_ecs.items()}
        _TrnsfSubstNmbrs(subst).transform(árbol)

        # Aplicar substituciones de nombres
        _TrnsfSubstNmbrs(nombres_equiv).transform(árbol)

        # Analizar los resultados
        if árbol.data == 'asign_var':
            # Si la ecuación incluía el nombre del variable y...
            try:
                # Intentar para declaración de variables
                símismo.nombre = str(árbol.children[0].children[0])
                símismo.árbol = árbol.children[1]
            except KeyError:
                # Si no funcionó, debe sser declaración de subsripto
                símismo.nombre = str(árbol.children[0].children[0])
                símismo.árbol = str(árbol.children[1])
                símismo.tipo = 'sub'
        else:
            # Si no había el nombre del variable y, simplemente aplicamos el árbol.
            símismo.árbol = árbol
            símismo.nombre = nombre if nombre not in nombres_equiv else nombres_equiv[nombre]

    def variables(símismo):
        """
        Devuelve una lista de los variable de esta ecuación.

        Returns
        -------
        set:
            Un conjunto con todos los variables presentes en esta ecuación.
        """

        return _VstrSacarVars()(símismo.árbol)

    def a_python(símismo, paráms):
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

        return _VstrAPy(l_prms=paráms, dialecto=símismo.dialecto).transformar(símismo.árbol)

    def coef_de(símismo, var, l_vars=None):
        if var == símismo.nombre:
            return _coef_de_ec(símismo.árbol, l_vars=l_vars)
        else:
            return _VstrCoefDe()(símismo.árbol, var, l_vars)

    def normalizar(símismo, líms_paráms, obs_x, obs_y):
        x_norm = obs_x.copy(deep=True)
        y_norm = obs_y.copy(deep=True)
        líms_norm = líms_paráms.copy()
        escls_prms = {}
        prms_vrs = {}

        for var in x_norm.data_vars:
            res = símismo.coef_de(var, l_vars=x_norm.data_vars)
            if res is not None:
                prm, inv = res
                escl = x_norm[var].values.std()
                if prm not in escls_prms:
                    escls_prms[prm] = {'escl': escl, 'inv': inv}
                    prms_vrs[var] = prm

        res_y = símismo.coef_de(símismo.nombre, l_vars=x_norm.data_vars)
        if res_y is not None:
            prm, inv = res_y
            escl = y_norm.values.std()
            if prm not in escls_prms:
                escls_prms[prm] = {'escl': escl, 'inv': inv}
                prms_vrs[símismo.nombre] = prm

        for v, p in prms_vrs.items():
            if v in x_norm.data_vars:
                if escls_prms[p]['inv']:
                    np.multiply(x_norm[v].values, escls_prms[p]['escl'], out=x_norm[v].values)
                else:
                    np.divide(x_norm[v].values, escls_prms[p]['escl'], out=x_norm[v].values)
            else:
                np.divide(y_norm.values, escls_prms[p], out=y_norm.values)

        return escls_prms, líms_norm, x_norm, y_norm

    def gen_mod_bayes(símismo, líms_paráms, obs_x, obs_y, aprioris=None, binario=False, nv_jerarquía=None):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        dialecto = símismo.dialecto

        escls_prms, líms_paráms, obs_x, obs_y = símismo._normalizar(líms_paráms, obs_x, obs_y)

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
                        últ_niv = í == (len(nv_jerarquía) - 2)
                        tmñ_nv = nv.shape

                        nmbr_mu = p if últ_niv else 'mu_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)
                        nmbr_sg = 'sg_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)

                        mu = pm.Normal(name=nmbr_mu, mu=mu[nv], sd=sg[nv], shape=tmñ_nv)
                        if not últ_niv:
                            sg = pm.HalfNormal(name=nmbr_sg.format(p, í), sd=obs_y.ptp(), shape=tmñ_nv)
                else:
                    for í, nv in enumerate(nv_jerarquía[:-1]):
                        tmñ_nv = nv.shape
                        últ_niv = í == (len(nv_jerarquía) - 2)
                        nmbr_mu = p if últ_niv else 'mu_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)
                        nmbr_sg = 'sg_{}_nv_{}'.format(p, len(nv_jerarquía) - 2 - í)

                        acotada = pm.Bound(pm.Normal, lower=líms[0], upper=líms[1])
                        mu = acotada(nmbr_mu, mu=mu[nv], sd=sg[nv], shape=tmñ_nv)
                        if not últ_niv:
                            sg = pm.HalfNormal(name=nmbr_sg.format(p, í), sd=obs_y.ptp(), shape=tmñ_nv)

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

        return modelo, escls_prms

    def sacar_args_func(símismo, func, i=None):
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

        # Aplicar la función recursiva.
        return _VstrExtrArgs(f=func, i=i, dial=símismo.dialecto)(símismo.árbol)

    def __str__(símismo):
        return _VstrATx(símismo.dialecto).transformar(símismo.árbol)


# Funciones auxiliares para ecuaciones.
_error_comp_ec = _('Componente de ecuación "{}" no reconocido.')

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
