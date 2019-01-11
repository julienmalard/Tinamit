import math as mat

import numpy as np
from pkg_resources import resource_filename

from lark import Lark, Tree
from lark.lexer import Token
from lark.visitors import Transformer_InPlace, Visitor
from tinamit.config import _

try:
    import pymc3 as pm
    import theano.tensor as T
except ImportError:  # pragma: sin cobertura
    pm = T = None

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
        comp = [símismo.convertir(a) for a in
                x.children[1].children]  # Recursar a través de los argumentos de la función

        # Devolver la función dinámica
        return lambda p, vr: fun(*[a(p=p, vr=vr) for a in comp])

    def neg(símismo, x):
        comp = símismo.convertir(x.children[0])
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
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '*':
            return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
        elif op == '/':
            return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '+':
            return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
        elif op == '-':
            return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[1])
        return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)

    def comp(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

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

    def convertir(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class _VstrATx(object):
    def __init__(símismo, dialecto):
        símismo.dialecto = dialecto

    def func(símismo, x):
        args = [símismo.convertir(a) for a in x.children[1].children]
        if len(args) != 1:
            return str(x.children[0]) + '(' + ', '.join(args) + ')'
        elif len(args) == 1:
            return str(x.children[0]) + '(' + args[0] + ')'

    def neg(símismo, x):
        return '-' + símismo.convertir(x.children[0])

    def var(símismo, x):
        return str(x.children[0])

    def num(símismo, x):
        return str(x.children[0])

    def prod(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        return símismo.convertir(x.children[0]) + '^' + símismo.convertir(x.children[1])

    def comp(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_comp(símismo, x):
        return str(x.children[0])

    def convertir(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class _VstrAPyMC3(object):
    def __init__(símismo, d_vars_pm, dialecto, obs_x, nv_jerarquía):
        símismo.d_vars_pm = d_vars_pm
        símismo.dialecto = dialecto
        símismo.nv_jerarquía = nv_jerarquía
        símismo.obs_x = obs_x

    def func(símismo, x):
        fun = _conv_fun(x.children[0], símismo.dialecto, 'pm')  # Traducir la función a PyMC3
        args = [símismo.convertir(a) for a in
                x.children[1].children]  # Recursar a través de los argumentos de la función

        # Devolver la función dinámica
        return fun(*args)

    def neg(símismo, x):
        return -símismo.convertir(x.children[0])

    def var(símismo, x):
        v = str(x.children[0])
        try:
            if símismo.nv_jerarquía is None:
                return símismo.d_vars_pm[v]
            else:
                return símismo.d_vars_pm[v][símismo.nv_jerarquía[-1]]

        except KeyError:
            # Si el variable no es un parámetro calibrable, debe ser un valor observado
            try:
                return símismo.obs_x[v].values

            except KeyError:
                raise ValueError(_('El variable "{}" no es un parámetro, y no se encuentra'
                                   'en la base de datos observados tampoco.').format(v))

    def num(símismo, x):
        return float(x.children[0])

    def prod(símismo, x):
        # Recursar a través de los componentes del operador ahora. Es importante hacerlo antes de
        # las expresiones ``lambda``; sino se llamará `transformar()` sí mismo cada vez que se llama
        # la función generada.
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '*':
            return comp_1 * comp_2
        elif op == '/':
            return comp_1 / comp_2
        else:
            raise ValueError(op)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '+':
            return comp_1 + comp_2
        elif op == '-':
            return comp_1 - comp_2
        else:
            raise ValueError(op)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[1])
        return comp_1 ** comp_2

    def comp(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '>':
            return pm.math.gt(comp_1, comp_2)
        elif op == '<':
            return pm.math.lt(comp_1, comp_2)
        elif op == '>=':
            return pm.math.ge(comp_1, comp_2)
        elif op == '<=':
            return pm.math.le(comp_1, comp_2)
        elif op == '==':
            return pm.math.eq(comp_1, comp_2)
        elif op == '!=':
            return pm.math.neq(comp_1, comp_2)
        else:
            # Si no sabemos lo que tenemos, hay error.
            raise ValueError(op)

    def op_comp(símismo, x):
        return str(x.children[0])

    def convertir(símismo, árbol):
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
                _VstrATx(dialecto=símismo.dial).convertir(e) for e in x.children[1].children[:símismo.i]
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
        símismo.error = False
        símismo.núm = 0
        símismo.l_vars = []

    def _valid_consist(símismo, coef, inv):
        if símismo.coef is None:
            símismo.coef = coef
            símismo.inv = inv
        else:
            if símismo.coef != coef or símismo.inv != inv:
                símismo.error = True
        símismo.núm += 1

    def prod(símismo, x):
        coef = None
        op = x.children[1].children[0]
        args = [x.children[0], x.children[2]]
        for i, a in enumerate(args):
            if a.data == 'neg':
                a = a.children[0]
            if a.data == 'var':
                a = a.children[0]
            else:
                return

            args[i] = a

        if op == '*':
            inv = False

            if args[0] == símismo.vr and args[1] not in símismo.l_vars:
                coef = str(args[1])
            elif args[1] == símismo.vr and args[0] not in símismo.l_vars:
                coef = str(args[0])
        else:
            inv = True
            if args[0] == símismo.vr and args[1] not in símismo.l_vars:
                coef = str(args[1])
            elif args[1] == símismo.vr and args[0] not in símismo.l_vars:
                coef = str(args[0])

        if coef is not None:
            símismo._valid_consist(coef, inv)

    def __call__(símismo, árbol, var, l_vars=None):
        símismo.núm = 0
        símismo.vr = var
        símismo.coef = símismo.inv = None
        símismo.l_vars = [] if l_vars is None else l_vars
        símismo.visit(árbol)
        if símismo.error or símismo.coef is None:
            return None
        elif not (símismo.núm == _VstrContarVar(símismo.coef)(árbol) == _VstrContarVar(símismo.vr)(árbol)):
            return None
        else:
            return símismo.coef, símismo.inv


class _VstrContarVar(Visitor):
    def __init__(símismo, var):
        símismo.vr = var
        símismo.cnt = 0

    def var(símismo, x):
        if x.children[0] == símismo.vr:
            símismo.cnt += 1

    def __call__(símismo, árbol):
        símismo.cnt = 0
        símismo.visit(árbol)
        return símismo.cnt


def _coef_de_ec(árbol, l_vars=None):
    if l_vars is None:
        l_vars = []
    if árbol.data == 'prod':
        arg1 = árbol.children[0]
        arg2 = árbol.children[2]
        op = árbol.children[1].children[0]

        v = inv = ec = None
        if op == '*':
            inv = True  # Y queda del otro lado de la ecuación que el parámetro
            if arg1.data == 'var' and v not in l_vars:
                v = arg1.children[0]
                ec = arg2
            elif arg2.data == 'var' and v not in l_vars:
                v = arg2.children[0]
                ec = arg1
        else:
            if arg1.data == 'var' and v not in l_vars:
                v = arg1.children[0]
                ec = arg2
                inv = True
            elif arg2.data == 'var' and v not in l_vars:
                v = arg2.children[0]
                ec = arg1
                inv = False
        if v is not None and _VstrContarVar(v)(ec) == 0:
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

        return _VstrAPy(l_prms=paráms, dialecto=símismo.dialecto).convertir(símismo.árbol)

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

        for var in x_norm.data_vars:
            res = símismo.coef_de(var, l_vars=x_norm.data_vars)
            if res is not None:
                prm, inv = res
                rango = x_norm[var].values.std()
                escls_prms[prm] = escl = 1 / rango if inv else rango
                np.divide(x_norm[var].values, rango, out=x_norm[var].values)
                if prm in líms_paráms:
                    líms_norm[prm] = tuple(lm * escl if lm is not None else None for lm in líms_paráms[prm])

        res_y = símismo.coef_de(símismo.nombre, l_vars=x_norm.data_vars)
        if res_y is not None:
            prm, inv = res_y
            rango = y_norm.values.std()
            escls_prms[prm] = escl = 1 / rango if inv else rango
            np.divide(y_norm.values, rango, out=y_norm.values)
            if prm in líms_paráms:
                líms_norm[prm] = tuple(lm * escl if lm is not None else None for lm in líms_paráms[prm])

        return escls_prms, líms_norm, x_norm, y_norm

    def gen_mod_bayes(símismo, líms_paráms, obs_x, obs_y, aprioris=None, binario=False, nv_jerarquía=None,
                      trsld_sub=False):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

        # escls_prms, líms_paráms, obs_x, obs_y = símismo.normalizar(líms_paráms, obs_x, obs_y)

        def _gen_d_vars_pm(tmñ=(), fmt_nmbrs='{}'):
            egr = {}
            norm = {}
            for p, líms in líms_paráms.items():
                nmbr = fmt_nmbrs.format(p)
                if aprioris is None:
                    if líms[0] is líms[1] is None:
                        final = pm.Normal(name=nmbr, mu=0, sd=100 ** 2, shape=tmñ)
                    else:
                        dist_norm = pm.Normal(name='transf' + nmbr, mu=0, sd=1, shape=tmñ)
                        if líms[0] is None:
                            final = pm.Deterministic(nmbr, líms[1] - pm.math.exp(dist_norm))
                        elif líms[1] is None:
                            final = pm.Deterministic(nmbr, líms[0] + pm.math.exp(dist_norm))
                        else:
                            final = pm.Deterministic(
                                nmbr, (pm.math.tanh(dist_norm) / 2 + 0.5) * (líms[1] - líms[0]) + líms[0]
                            )
                        norm[p] = dist_norm
                else:
                    dist, prms = aprioris[p]
                    if (líms[0] is not None or líms[1] is not None) and dist != pm.Uniform:
                        acotada = pm.Bound(dist, lower=líms[0], upper=líms[1])
                        final = acotada(nmbr, shape=tmñ, **prms)
                    else:
                        if dist == pm.Uniform:
                            prms['lower'] = max(prms['lower'], líms[0])
                            prms['upper'] = min(prms['upper'], líms[1])
                        final = dist(nmbr, shape=tmñ, **prms)

                egr[p] = final
            for p, v in egr.items():
                if p not in norm:
                    norm[p] = v
            return {'final': egr, 'norm': norm}

        def _gen_d_vars_pm_jer():
            dists_base = _gen_d_vars_pm(
                tmñ=(len(set(nv_jerarquía[0])),), fmt_nmbrs='mu_{}_nv_' + str(len(nv_jerarquía) - 1)
            )['norm']

            egr = {}

            for p, líms in líms_paráms.items():
                mu_v = dists_base[p]

                if líms[0] is líms[1] is None:
                    mu_sg = 2
                else:
                    mu_sg = 0.5

                sg_v = pm.Gamma(name='sg_{}_nv_{}'.format(p, len(nv_jerarquía) - 1), mu=mu_sg, sd=0.2,
                                shape=(1,))  # type: pm.model.TransformedRV

                for í, nv in enumerate(nv_jerarquía[:-1]):
                    tmñ_nv = nv.shape
                    últ_niv = í == (len(nv_jerarquía) - 2)
                    í_nv = len(nv_jerarquía) - 2 - í

                    nmbr_mu = p if últ_niv else 'mu_{}_nv_{}'.format(p, í_nv)
                    nmbr_sg = 'sg_{}_nv_{}'.format(p, í_nv)
                    nmbr_trsld = 'trlsd_{}_nv_{}'.format(p, í_nv)

                    if False and (trsld_sub or últ_niv):
                        trsld = pm.Normal(name=nmbr_trsld, mu=0, sd=1, shape=tmñ_nv)
                        if líms[0] is líms[1] is None:
                            mu_v = pm.Deterministic(nmbr_mu, mu_v[nv] + trsld * sg_v[nv])

                        else:
                            mu_v = pm.Deterministic('transf' + nmbr_mu, mu_v[nv] + trsld * sg_v[nv])
                            if líms[0] is None:
                                final = pm.Deterministic(nmbr_mu, líms[1] - pm.math.exp(mu_v))
                            elif líms[1] is None:
                                final = pm.Deterministic(nmbr_mu, líms[0] + pm.math.exp(mu_v))
                            else:
                                final = pm.Deterministic(
                                    nmbr_mu, (pm.math.tanh(mu_v) / 2 + 0.5) * (líms[1] - líms[0]) + líms[0]
                                )

                            if últ_niv:
                                mu_v = final
                    else:
                        if líms[0] is líms[1] is None:
                            mu_v = pm.Normal(name=nmbr_mu, mu=mu_v[nv], sd=sg_v[nv], shape=tmñ_nv)
                        else:
                            mu_v = pm.Normal(name='transf' + nmbr_mu, mu=mu_v[nv], sd=sg_v[nv], shape=tmñ_nv)
                            if líms[0] is None:
                                final = pm.Deterministic(nmbr_mu, líms[1] - pm.math.exp(mu_v))
                            elif líms[1] is None:
                                final = pm.Deterministic(nmbr_mu, líms[0] + pm.math.exp(mu_v))
                            else:
                                final = pm.Deterministic(
                                    nmbr_mu, (pm.math.tanh(mu_v) / 2 + 0.5) * (líms[1] - líms[0]) + líms[0]
                                )
                            if últ_niv:
                                mu_v = final

                    if not últ_niv:
                        sg_v = pm.Gamma(name=nmbr_sg, mu=mu_sg, sd=0.2, shape=tmñ_nv)

                egr[p] = mu_v

            return egr

        modelo = pm.Model()
        with modelo:
            if nv_jerarquía is None:
                d_vars_pm = _gen_d_vars_pm()['final']
            else:
                d_vars_pm = _gen_d_vars_pm_jer()

            mu = _VstrAPyMC3(
                d_vars_pm=d_vars_pm, dialecto=símismo.dialecto, obs_x=obs_x, nv_jerarquía=nv_jerarquía,
            ).convertir(símismo.árbol)

            if binario:
                pm.Bernoulli(name='Y_obs', logit_p=mu, observed=obs_y.values)

            else:
                sigma = pm.HalfNormal(name='sigma', sd=obs_y.values.std())
                theta = pm.Normal(name='theta', sd=1)
                beta = pm.HalfNormal(name='beta', sd=1/obs_y.values.std())
                pm.Normal(name='Y_obs', mu=mu,
                          sd=sigma , #* (beta*pm.math.abs_(mu) + 1),
                          observed=obs_y.values)

        return modelo

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
        return _VstrATx(símismo.dialecto).convertir(símismo.árbol)


# Funciones auxiliares para ecuaciones.

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
    'asin': {'vensim': 'ARCSIN', 'pm': T.arcsin if T is not None else None, 'python': mat.asin},
    'acos': {'vensim': 'ARCCOS', 'pm': T.arccos if T is not None else None, 'python': mat.acos},
    'atan': {'vensim': 'ARCTAN', 'pm': T.arctan if T is not None else None, 'python': mat.atan},
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
