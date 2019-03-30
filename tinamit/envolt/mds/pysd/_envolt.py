from ast import literal_eval

from tinamit.Análisis.sintaxis import Ecuación
from tinamit.envolt.mds import EnvolturaMDS, VariablesMDS
from ._vars import VarPySDAuxiliar, VarPySDNivel, VarPySDConstante


class EnvolturaPySD(EnvolturaMDS):
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
                var = VarPySDNivel(
                    nombre, nombre_py=nombre_py, unid=unid, ec=ec, hijos=hijos, parientes=parientes,
                    líms=líms, info=info
                )

            except AttributeError:
                if len(parientes):
                    var = VarPySDAuxiliar(
                        nombre, nombre_py=nombre_py, unid=unid, ec=ec, hijos=hijos, parientes=parientes,
                        líms=líms, info=info
                    )
                else:
                    var = VarPySDConstante(
                        nombre, nombre_py=nombre_py, unid=unid, ec=ec, hijos=hijos, parientes=parientes,
                        líms=líms, info=info
                    )

            l_vars.append(var)

        return VariablesMDS(l_vars)

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()


class EnvolturaPySDMDL(EnvolturaPySD):
    def unidad_tiempo(símismo):
        docs = símismo.mod.doc()
        return docs.loc[docs['Real Name'] == 'TIME STEP', 'Unit'].values[0]


class EnvolturaPySDXMILE(EnvolturaPySD):
    def unidad_tiempo(símismo):
        with open(símismo.mod.py_model_file, 'r', encoding='UTF-8') as d:
            f = d.readline()
            while f != 'def time_step():\n':
                f = d.readline()
            while not f.strip().startswith('Units:'):
                f = d.readline()
        return f.split(':')[1].strip()
