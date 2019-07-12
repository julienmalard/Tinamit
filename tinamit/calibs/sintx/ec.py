from lark import Lark
from tinamit.config import _

from ._vstr import VstrSacarVars, VstrCoefDe, VstrExtrArgs, VstrContarVar, TrnsfSubstNmbrs
from ._vstr_transf import VstrATx, VstrAPyMC3, VstrAPy

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None

from pkg_resources import resource_filename


class Gramática(object):
    _arch = resource_filename('tinamit.calibs.sintx', 'gram_ecs.g')

    def __init__(símismo):
        with open(símismo._arch, encoding='UTF-8') as d:
            símismo.gram = Lark(d, parser='lalr', start='ec')


anlzdr = Gramática()


class Ecuación(object):
    """
    Un objeto para manejar ecuaciones dinámicas.
    """

    def __init__(símismo, ec, nombre=None, otras_ecs=None, nombres_equiv=None, dialecto='tinamït'):
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
        """

        # Formatear parámetros vacíos
        if otras_ecs is None:
            otras_ecs = {}

        if nombres_equiv is None:
            nombres_equiv = {}

        # Si es una ecuación de variable o de subscripto
        símismo.tipo = 'var'

        símismo.dialecto = dialecto

        # Analizar la ecuación
        árbol = anlzdr.gram.parse(ec)

        # Aplicar subsituciones de ecuaciones de variables
        subst = {
            v_otr: Ecuación(
                ec_otr, otras_ecs={v: otr for v, otr in otras_ecs.items() if v != v_otr}, dialecto=dialecto
            ).árbol for v_otr, ec_otr in otras_ecs.items()
        }
        TrnsfSubstNmbrs(subst).transform(árbol)

        # Aplicar substituciones de nombres
        TrnsfSubstNmbrs(nombres_equiv).transform(árbol)

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

        return VstrSacarVars()(símismo.árbol)

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

        return VstrAPy(l_prms=paráms, dialecto=símismo.dialecto).convertir(símismo.árbol)

    def coef_de(símismo, var, l_vars=None):
        # para hacer: ¿necesario?
        if var == símismo.nombre:
            return _coef_de_ec(símismo.árbol, l_vars=l_vars)
        else:
            return VstrCoefDe()(símismo.árbol, var, l_vars)

    def gen_mod_bayes(
            símismo, líms_paráms, obs_x, obs_y, aprioris=None, binario=False, nv_jerarquía=None, í_datos=None,
            trsld_sub=False
    ):

        if pm is None:
            return ImportError(_('Hay que instalar PyMC3 para poder utilizar modelos bayesianos.'))

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
                tmñ=(1,), fmt_nmbrs='mu_{}_nv_0' if len(nv_jerarquía) else '{}'
            )['norm']

            egr = {}

            for p, líms in líms_paráms.items():
                mu_v = dists_base[p]

                if líms[0] is líms[1] is None:
                    mu_sg = 2
                else:
                    mu_sg = 0.5

                sg_v = pm.Gamma(name='sg_{}_nv_0'.format(p), mu=mu_sg, sd=0.2, shape=(1,))

                for í, nv in enumerate(nv_jerarquía):
                    tmñ_nv = len(nv)
                    últ_niv = í == (len(nv_jerarquía) - 1)
                    í_nv = í+1

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

            mu = VstrAPyMC3(
                d_vars_pm=d_vars_pm, obs_x=obs_x, í_datos=í_datos, dialecto=símismo.dialecto
            ).convertir(símismo.árbol)

            if binario:
                pm.Bernoulli(name='Y_obs', logit_p=mu, observed=obs_y.values)

            else:
                sigma = pm.HalfNormal(name='sigma', sd=obs_y.values.std())
                # theta = pm.Normal(name='theta', sd=1)
                # beta = pm.HalfNormal(name='beta', sd=1 / obs_y.values.std())
                pm.Normal(name='Y_obs', mu=mu,
                          sd=sigma,  # * (beta*pm.math.abs_(mu) + 1),
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
        return VstrExtrArgs(f=func, i=i, dial='tinamït')(símismo.árbol)

    def __str__(símismo):
        return VstrATx('tinamït').convertir(símismo.árbol)


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
        if v is not None and VstrContarVar(v)(ec) == 0:
            return v, inv
