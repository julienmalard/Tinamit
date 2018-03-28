from warnings import warn as avisar

from Incertidumbre.Estadísticas import calib_bayes, optimizar, regresión
from tinamit import _
from tinamit.EnvolturaMDS.sintaxis import Ecuación
from tinamit.Incertidumbre.Datos import SuperBD
from tinamit.MDS import EnvolturaMDS

try:
    import pymc3 as pm
except ImportError:
    pm = None


class ConexDatos(object):
    def __init__(símismo, bd, modelo):
        """

        :param bd:
        :type bd: SuperBD
        :param modelo:
        :type modelo: EnvolturaMDS
        """

        símismo.bd = bd
        símismo.modelo = modelo
        símismo.dic_info_calib = {}
        símismo.dic_info_const = {}

    def estab_calib_var(símismo, var, ec=None, líms_paráms=None, paráms=None,
                        método=None, ops_método=None, regional=True):
        símismo.dic_info_calib[var] = {
            'ec': ec,
            'paráms': paráms,
            'líms_paráms': líms_paráms,
            'método': método,
            'ops_método': ops_método,
            'regional': regional
        }

    def borrar_calib_ec(símismo, var):
        símismo.dic_info_calib.pop(var)

    def calib_ecs(símismo, en=None, escala=None, por=None, fechas=None, bds=None, nombre='Calib Tinamït'):

        mod = símismo.modelo
        if nombre not in mod.calibs:
            mod.calibs[nombre] = {}

        for var, d_info in símismo.dic_info_calib.items():

            if var not in símismo.modelo.variables:
                avisar(_('El variable "{}" no existe en modelo "{}" y por lo tanto no se pudo calibrar.')
                       .format(var, símismo.modelo))
                continue

            calibración = símismo.calib_var(var=var, en=en, escala=escala, fechas=fechas, bds=bds, **d_info)
            for lg, clb_lg in calibración.items():
                if lg not in mod.calibs[nombre]:
                    mod.calibs[nombre][lg] = {}
                mod.calibs[nombre][lg][var] = clb_lg

        for const, d_info in símismo.dic_info_const.items():
            if var not in símismo.modelo.variables:
                avisar(_('El variable "{}" no existe en modelo "{}" y por lo tanto no se pudo estimar.')
                       .format(var, símismo.modelo))
                continue

            estimo = símismo.estim_constante(const=const, en=en, escala=escala, fechas=fechas, bds=bds, **d_info)
            for lg, est_lg in estimo.items():
                if lg not in mod.calibs[nombre]:
                    mod.calibs[nombre][lg] = {}
                mod.calibs[nombre][lg][var] = est_lg

    def estab_estim_const(símismo, const, líms=None, en=None, escala=None, por=None, fechas=None, bds=None, regional=None):
        símismo.dic_info_const[const] = {
            'líms': líms,
            'en': en,
            'escala': escala,
            'por': por,
            'fechas': fechas,
            'bds': bds,
            'regional': regional
        }

    def estim_constante(símismo, const, líms=None, en=None, escala=None, por=None, fechas=None, bds=None,
                        regional=False):

        símismo.estab_estim_const(const=const, líms=líms, en=en, escala=escala, por=por, fechas=fechas, bds=bds,
                                  regional=regional)

        geog = símismo.bd.geog
        lugares = geog.obt_lugares_en(escala=escala, en=en, por=por)

        l_lugs = list(lugares)
        obs = [símismo.bd.obt_datos(l_vars=const, lugar=v, datos=bds, fechas=fechas, excl_faltan=True)
               ['regional' if regional else 'individual'][const] for v in l_lugs]

        d_calib = {}
        for lg, x in zip(lugares, obs):
            import numpy as np

            resultados = {'val': np.mean(x), 'ES': np.std(x) / np.sqrt(x.size)}

            d_calib[lg] = resultados

        return d_calib

    def calib_var(símismo, var, ec=None, paráms=None, líms_paráms=None, método=None, ops_método=None,
                  en=None, escala=None, por=None, fechas=None, bds=None, aprioris=True, aprioris_por=None, regional=False):

        geog = símismo.bd.geog

        símismo.estab_calib_var(var=var, ec=ec, paráms=paráms, líms_paráms=líms_paráms, método=método,
                                ops_método=ops_método, regional=regional)

        mod = símismo.modelo
        try:
            d_var = mod.variables[var]
        except KeyError:
            raise ValueError('El variable "{}" no existe en el modelo "{}".'.format(var, mod.nombre))

        lugares = símismo.bd.geog.obt_lugares_en(escala=escala, en=en, por=por)
        if isinstance(lugares, dict):
            l_lugs = list(lugares.values())
        else:
            l_lugs = lugares

        if ops_método is None:
            ops_método = {}

        if not isinstance(líms_paráms, list):
            líms_paráms = [líms_paráms] * len(paráms)
        líms_paráms = [(None, None) if x is None else x for x in líms_paráms]

        if paráms is None:
            paráms = [x for x in d_var['parientes'] if x in mod.constantes]
            # Buscar los límites teoréticos de los parámetros
            líms_paráms = []
            for p in paráms:
                try:
                    líms_paráms.append(mod.variables[p]['rango'])
                except KeyError:
                    líms_paráms.append((None, None))

        if not isinstance(paráms, list):
            paráms = [paráms]

        parientes = [x for x in d_var['parientes'] if x not in paráms]

        if ec is None:
            ec = d_var['ec']
        if not len(ec):
            líms_var = mod.variables[var]['líms']
            líms_parientes = [mod.variables[v]['líms'] for v in parientes]

            if len(parientes) == 1:
                raise NotImplementedError
            else:
                raise NotImplementedError

        if método is None:
            if pm:
                método = 'Inf Bayes'
            else:
                método = 'Optimizar'
        método = método.lower()

        obj_ec = Ecuación(ec=ec, dialecto=símismo.modelo.__class__.__name__)
        vars_x = [x for x in obj_ec.variables() if x not in paráms]
        l_vars = vars_x + [var]

        obs = [símismo.bd.obt_datos(l_vars=l_vars, lugar=v, datos=bds, fechas=fechas)
               ['regional' if regional else 'individual'].dropna() for v in l_lugs]

        obs_y = [l[var].values for l in obs]
        obs_x = [{x: l[x].values for x in vars_x} for l in obs]

        # Calcular a prioris
        if aprioris and método == 'inf bayes':
            if aprioris_por is None:
                aprioris_por = []
            if not isinstance(aprioris_por, list):
                aprioris_por = [aprioris_por]

            def calib_bayes_en(en_=None, escl=None, apr=None, **ops):
                lgs = geog.obt_lugares_en(en=en_, escala=escl)
                obs_ap = símismo.bd.obt_datos(l_vars=l_vars, lugar=lgs, datos=bds, fechas=fechas) \
                    ['individual' if regional else 'regional'].dropna()

                obs_y_ap = obs_ap[var].values
                obs_x_ap = {x: obs_ap[x].values for x in vars_x}
                return calib_bayes(obj_ec, paráms, líms_paráms, obs_x_ap, obs_y_ap, apr, **ops)

            # Ordenar aprioris_por
            if not all(x in geog.orden_jer or x in geog.grupos for x in aprioris_por):
                raise ValueError('')
            aprioris_por.sort(key=lambda x: geog.orden_jer.index(x))  # Grande a pequeño

            if len(aprioris_por):
                avisar('¡Código experimental!')  # Para hacer: terminar
                dic_lg_pariente = {en: {x: geog.árbol_geog_inv[x][aprioris_por[-1]] for x in lugares}}
                nivel_inf = en
                for n, e in enumerate(reversed(aprioris_por)):
                    try:
                        nivel_sup = list(reversed(aprioris_por))[n+1]
                    except IndexError:
                        nivel_sup = None
                    dic_lg_pariente[e] = {x: geog.árbol_geog_inv[x][nivel_sup] if nivel_sup is not None else None
                                          for x in dic_lg_pariente[nivel_inf].values()}
                    nivel_inf = e

            # Para hacer: terminar para casis cib aprioris_por
            dic_aprioris = {None: calib_bayes_en(o_ec=obj_ec, prms=paráms, líms_prms=líms_paráms, **ops_método)}
            dists_aprioris = [dic_aprioris[None] for _ in lugares]

        else:
            dists_aprioris = [None]*len(lugares)

        d_calib = {}
        for lg, x, y, ap in zip(lugares, obs_x, obs_y, dists_aprioris):

            if método == 'inf bayes':
                resultados = calib_bayes(obj_ec, paráms, líms_paráms, x, y, dists_aprioris=ap, **ops_método)

            elif método == 'optimizar':
                resultados = optimizar(obj_ec, paráms, líms_paráms, x, y, **ops_método)

            elif método == 'regresión':
                resultados = regresión(obj_ec, paráms, líms_paráms, x, y, **ops_método)
            else:
                raise ValueError('')

            d_calib[lg] = resultados

        return d_calib

    def cargar_modelo(símismo, modelo):
        símismo.modelo = modelo
        for var in símismo.dic_info_calib:
            if var not in modelo.variables:
                avisar(_('El variable "{}" no existe en el nuevo modelo.').format(var))

    def no_calibrados(símismo):
        return [var for var in símismo.modelo.variables if var not in símismo.dic_info_calib]


