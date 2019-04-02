from ast import literal_eval

from tinamit.Análisis.sintaxis import Ecuación
from tinamit.envolt.mds import EnvolturaMDS
from ._funcs import gen_mod_pysd, obt_paso_mod_pysd
from ._vars import VarPySDAuxiliar, VarPySDNivel, VarPySDConstante, VariablesPySD


class EnvolturaPySD(EnvolturaMDS):

    def __init__(símismo, archivo, nombre='mds'):

        símismo.mod = gen_mod_pysd(archivo)
        símismo.archivo = archivo

        super().__init__(nombre=nombre)

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()

    def cerrar(símismo):
        pass

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
