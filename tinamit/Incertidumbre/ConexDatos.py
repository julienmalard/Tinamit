from warnings import warn as avisar

import numpy as np
import pandas as pd

from tinamit.Incertidumbre.Estadísticas import calib_bayes, optimizar, regresión
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

            # Para hacer: terminar para casos con aprioris_por
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

    def simular(símismo, tiempo_final, paso, nombre_corrida='Corrida Tinamït', fecha_inic=None, tcr=None,
                recalc=False, clima=False, escala=None, en=None, por=None, orden=None):

        lugares = símismo.bd.geog.obt_lugares_en(escala=escala, en=en, por=por)

        n_rep = 1  # para hacer: implementar incertidumbre
        vals_paráms_calib = símismo.prep_paráms_simul(n_rep=n_rep, lugares=lugares, orden=orden)
        for lg, prms in vals_paráms_calib.items():

            símismo.modelo.inic_vals(prms)

            if fecha_inic is not None:
                vals_inic = símismo.prep_vals_inic(fecha_inic=fecha_inic, lugar=lg)
                símismo.modelo.inic_vals(vals_inic)

            símismo.modelo.simular(tiempo_final=tiempo_final, paso=paso,
                                   nombre_corrida='{}_{}'.format(nombre_corrida, lg),
                                   fecha_inic=fecha_inic, tcr=tcr,
                                   recalc=recalc, clima=clima)

    def validar(símismo, tiempo_final, paso, nombre_corrida='Corrida Tinamït', fecha_inic=None, tcr=None,
                recalc=False, clima=False, escala=None, en=None, por=None, orden=None, vars_valid=None):

        if vars_valid is None:
            vars_valid = [v for v in símismo.bd.vars]

        resultados = símismo.simular()  # arreglarme

        dic_valid = {}
        for v in vars_valid:
            for lg in lugares:
                raise NotImplementedError

        return dic_valid

    def prep_paráms_simul(símismo, n_rep, lugares, orden=None):
        d_prms = {}
        if orden is None:
            orden = símismo.bd.geog.orden_jer[::-1]
        for lg in lugares:
            d_prms[lg] = {}
            for c, d_c in símismo.dic_info_const.items():
                est = símismo.estim_constante(c, **d_c)
                for niv in orden:
                    lg_niv = símismo.bd.geog.árbol_geog_inv[lg][niv]
                    if lg_niv in est:
                        if n_rep == 1:
                            d_prms[lg_niv][c] = est[lg_niv]['val']
                        else:
                            if 'ES' in est[lg_niv]:
                                d_prms[lg_niv][c] = np.random.normal(loc=est[lg_niv]['val'], scale=est[lg_niv]['ES'], size=n_rep)
                            elif 'dist' in est[lg_niv]:
                                devolver = n_rep > est[lg_niv]['dist'].size
                                d_prms[lg_niv][c] = np.random.choice(est[lg_niv]['dist'], size=n_rep, replace=devolver)
                            else:
                                raise NotImplementedError
                        break
            for v, d_v in símismo.dic_info_calib.items():
                est = símismo.calib_var(v, **d_v)
                for niv in orden:
                    lg_niv = símismo.bd.geog.árbol_geog_inv[lg][niv]
                    if lg_niv in est:
                        for p, d_p in est[lg_niv].items():
                            if n_rep == 1:
                                d_prms[lg_niv][p] = d_p['val']
                            else:
                                if 'ES' in d_p:
                                    d_prms[lg_niv][p] = np.random.normal(loc=d_p['val'], scale=d_p['ES'], size=n_rep)
                                elif 'dist' in d_p:
                                    devolver = n_rep > d_p['dist'].size
                                    d_prms[lg_niv][p] = np.random.choice(d_p['dist'], size=n_rep, replace=devolver)
                                else:
                                    raise NotImplementedError
                            break

        return d_prms

    def prep_vals_inic(símismo, fecha_inic, lugar, orden=None):

        if orden is None:
            orden = símismo.bd.geog.orden_jer[::-1]
        else:
            raise NotImplementedError  # para hacer

        d_vals_inic = {}
        for var_mod, var_bd in símismo.dic_info_vals_inic.items():
            vals = símismo.bd.obt_datos(l_vars=var_bd, lugar=lugar)['regional'].dropna(subset=var_bd)
            # Interpolar la fecha, si necesitamos y podemos
            try:
                d_vals_inic[var_mod] = vals.loc[fecha_inic][var_bd]
            except KeyError:
                if vals.shape[0] == 1:
                    d_vals_inic[var_mod] = vals[var_bd]
                elif vals.index.min() > pd.to_datetime(fecha_inic):
                    d_vals_inic[var_mod] = vals.loc[vals.index.min()][var_bd]
                else:
                    val_interpol = vals.append(
                        vals.Series(None,
                                    name=vals.to_datetime(fecha_inic))
                    ).sort_index().interpolate(method='time').loc[fecha_inic][var_bd]

                    d_vals_inic[var_mod] = val_interpol

        return d_vals_inic

    def no_calibrados(símismo):
        return [var for var in símismo.modelo.variables if var not in símismo.dic_info_calib]
