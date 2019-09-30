from ast import literal_eval

import numpy as np
import pandas as pd

from tinamit.calibs.sintx.ec import Ecuación
from tinamit.envolt.mds.pysd._funcs import decodar
from ._funcs import gen_mod_pysd, obt_paso_mod_pysd
from ._vars import VarPySDAuxiliar, VarPySDNivel, VarPySDConstante, VariablesPySD
from .._envolt import ModeloDS


class ModeloPySD(ModeloDS):
    """
    Envoltura para modelos PySD.
    """
    ext = ['.mdl', '.xmile', '.xml', '.py']

    def __init__(símismo, archivo, nombre='mds'):
        símismo.mod = gen_mod_pysd(archivo)
        símismo.vars_para_cambiar = {}
        símismo.archivo = archivo

        símismo.cont_simul = False
        símismo.paso_act = 0

        super().__init__(variables=_gen_vars(símismo.mod), nombre=nombre)

    def iniciar_modelo(símismo, corrida):
        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()
        símismo.paso_act = 0

        símismo.cont_simul = False

        super().iniciar_modelo(corrida)

    def incrementar(símismo, rebanada):

        símismo.paso_act += rebanada.n_pasos
        devolv = [símismo.paso_act - 1, símismo.paso_act]
        res = símismo.mod.run(
            initial_condition='current' if símismo.cont_simul else 'original', params=símismo.vars_para_cambiar,
            return_timestamps=devolv, return_columns=[v.nombre_py for v in rebanada.resultados.variables()]
        )

        # Guardar valores iniciales
        for v in rebanada.resultados.variables():
            rebanada.resultados[v].vals[símismo.paso_act - 1] = res[v.nombre_py][símismo.paso_act - 1]

        símismo.cont_simul = True
        símismo.variables.cambiar_vals({v: res[v.nombre_py].values[-1] for v in rebanada.resultados.variables()})

        símismo.vars_para_cambiar.clear()
        super().incrementar(rebanada)

    def _correr_hasta_final(símismo):
        t = símismo.corrida.t

        t_inic_mod = símismo.mod.time._t
        eje_pysd = np.arange(
            t_inic_mod, t_inic_mod + t.n_pasos * t.tmñ_paso + 1, t.guardar_cada * t.tmñ_paso
        )

        if símismo.corrida.extern is not None:
            vals_extern = símismo.corrida.extern.obt_vals(t.eje(), var=símismo.variables)
            paráms = {
                vr: vl.squeeze().to_pandas()
                for vr, vl in vals_extern.items()
            }
            for ll, v in paráms.items():
                if isinstance(v, pd.Series):
                    v.index = eje_pysd[t.eje().isin(v.index.values)]
        else:
            paráms = {}

        if símismo.corrida.clima is not None:
            vars_clima = símismo.corrida.clima.obt_todos_vals(t.eje(), vars_clima=símismo.vars_clima)
            paráms.update(vars_clima)

        símismo._proc_paráms(paráms)

        res_pysd = símismo.mod.run(
            params=paráms,
            return_timestamps=eje_pysd
        )
        return {vr: res_pysd[str(vr)].values for vr in símismo.corrida.resultados.variables()}

    def unidad_tiempo(símismo):
        return obt_paso_mod_pysd(símismo.mod)

    def cambiar_vals(símismo, valores):
        símismo.vars_para_cambiar.update({vr: float(vl) for vr, vl in valores.items()})
        super().cambiar_vals(valores)

    def paralelizable(símismo):
        return True

    def _proc_paráms(símismo, prms):
        for p in list(prms):
            v = símismo.variables[p]
            if isinstance(v, VarPySDNivel):
                val = prms.pop(p)
                if v.var_inic:
                    prms[v.var_inic.nombre] = val


def _gen_vars(mod):
    l_vars = []

    internos = ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']
    for i, f in mod.doc().iterrows():

        nombre = f['Real Name']
        if f['Type'] == 'lookup' or nombre in internos:
            continue

        nombre_py = f['Py Name']
        unid = decodar(f['Unit'])
        líms = literal_eval(f['Lims'])
        ec = decodar(f['Eqn'])
        info = decodar(f['Comment'])
        obj_ec = Ecuación(ec, dialecto='vensim')
        parientes = {v for v in obj_ec.variables() if v not in internos}
        inic = getattr(mod.components, nombre_py)()

        try:
            getattr(mod.components, '_integ_' + nombre_py)
            nivel = True

        except AttributeError:
            nivel = False
        if nivel:
            var = VarPySDNivel(
                nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, inic=inic, líms=líms, info=info
            )
        elif len(parientes):
            var = VarPySDAuxiliar(
                nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, inic=inic, líms=líms, info=info
            )
        else:
            var = VarPySDConstante(
                nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, inic=inic, líms=líms, info=info
            )

        l_vars.append(var)

    for vr in l_vars:
        if isinstance(vr, VarPySDNivel):
            # para hacer: no funciona con XMILE, solamente con vensim (.mdl)
            args_integ = Ecuación(vr.ec).sacar_args_func('INTEG', 2)
            if args_integ:
                arg_inic = args_integ[1]
                vr.estab_var_inic(next((
                    v for v in l_vars if v.nombre == arg_inic
                ), None))

    return VariablesPySD(l_vars)
