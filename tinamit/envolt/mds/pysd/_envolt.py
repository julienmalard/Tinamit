from ast import literal_eval

from tinamit.Análisis.sintaxis import Ecuación
from tinamit.envolt.mds import EnvolturaMDS
from ._funcs import gen_mod_pysd, obt_paso_mod_pysd
from ._vars import VarPySDAuxiliar, VarPySDNivel, VarPySDConstante, VariablesPySD


class EnvolturaPySD(EnvolturaMDS):
    ext = None

    def __init__(símismo, archivo, nombre='mds'):

        símismo.mod = gen_mod_pysd(archivo)
        símismo.vars_para_cambiar = {}
        símismo.archivo = archivo

        símismo.cont_simul = False
        símismo.paso_act = 0

        super().__init__(nombre=nombre)

    def iniciar_modelo(símismo, corrida):

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()

        símismo.cont_simul = False

        símismo.paso_act = símismo.mod.time._t

        for var in símismo.variables:
            var.poner_val(getattr(símismo.mod.components, var.nombre_py)())

    def incrementar(símismo, corrida):
        n_pasos = corrida.eje_tiempo.pasos_avanzados(símismo.unidad_tiempo())

        pasos_devolv = list(range(símismo.paso_act, símismo.paso_act + 1 + n_pasos, guardar_cada))
        símismo.paso_act += n_pasos

        initial_condition = 'current' if símismo.cont_simul else 'original'
        símismo._res_recién = símismo.mod.run(
            initial_condition=initial_condition, params=símismo.vars_para_cambiar,
            return_timestamps=pasos_devolv, return_columns=símismo.vars_saliendo
        )
        símismo.cont_simul = True
        símismo._leer_vals_de_pysd(corrida.resultados.vars_interés)

        símismo.vars_para_cambiar.clear()

    def correr(símismo, corrida):
        símismo.incrementar(, corrida.eje_tiempo.n_pasos()
        # para hacer


        símismo._res_recién[v].values
        return corrida.resultados()

    def cambiar_vals(símismo, valores):
        símismo.vars_para_cambiar.update(valores)

    def cerrar(símismo):
        pass

    def paralelizable(símismo):
        True

    def _gen_vars(símismo):
        l_vars = []

        internos = ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']
        for i, f in símismo.mod.doc().iterrows():

            nombre = f['Real Name']
            if f['Type'] == 'lookup' or nombre in internos:
                continue

            nombre_py = f['Py Name']
            unid = f['Unit']
            líms = literal_eval(f['Lims'])
            ec = f['Eqn']
            info = f['Comment']
            obj_ec = Ecuación(ec)
            parientes = {v for v in obj_ec.variables() if v not in internos}

            try:
                getattr(símismo.mod.components, 'integ_' + nombre_py)
                nivel = True

            except AttributeError:
                nivel = False
            if nivel:
                var = VarPySDNivel(
                    nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info
                )
            elif len(parientes):
                var = VarPySDAuxiliar(
                    nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info
                )
            else:
                var = VarPySDConstante(
                    nombre, nombre_py=nombre_py, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info
                )

            l_vars.append(var)

        return VariablesPySD(l_vars)

    def _leer_vals_de_pysd(símismo, l_vars):
        for v in l_vars:
            v.poner_val(símismo._res_recién[v].values[-1])


class EnvolturaPySDMDL(EnvolturaPySD):
    ext = ['.mdl']

    def unidad_tiempo(símismo):
        docs = símismo.mod.doc()
        return docs.loc[docs['Real Name'] == 'TIME STEP', 'Unit'].values[0]


class EnvolturaPySDXMILE(EnvolturaPySD):
    ext = ['.xmile', '.xml']

    def unidad_tiempo(símismo):
        return obt_paso_mod_pysd(símismo.archivo)


class EnvolturaPySDPy(EnvolturaPySD):
    ext = '.py'

    def unidad_tiempo(símismo):
        return obt_paso_mod_pysd(símismo.archivo)
