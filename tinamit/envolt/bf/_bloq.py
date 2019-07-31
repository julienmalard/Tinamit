import numpy as np
from dateutil.relativedelta import relativedelta as deltarelativo

from tinamit.envolt.bf._deter import ModeloDeterminado, VariablesModDeter, VarPasoDeter
from tinamit.tiempo.tiempo import a_unid_tnmt, a_unid_ft


class ModeloBloques(ModeloDeterminado):

    def __init__(símismo, variables, nombre='bf'):
        """

        Parameters
        ----------
        variables: VariablesModBloques
        nombre: str
        """

        símismo.tmñ_bloques = variables.tmñ_bloques
        super().__init__(tmñ_ciclo=np.sum(símismo.tmñ_bloques), variables=variables, nombre=nombre)

    def _act_vals_clima(símismo, f_0, f_1):

        # Solamante hay que cambiar los datos si es el principio de un nuevo ciclo.
        if símismo.corrida.clima and símismo.vars_clima and símismo.paso_en_ciclo == 0:

            # La fecha inicial
            f_inic = f_0

            for b, tmñ in enumerate(símismo.tmñ_bloques):
                # Para cada bloque...

                # La fecha final
                base_t, factor = a_unid_tnmt(símismo.unidad_tiempo())
                f_final = f_inic + deltarelativo(**{a_unid_ft[base_t]: tmñ * factor})

                # Calcular los datos
                datos = símismo.corrida.clima.combin_datos(
                    vars_clima=símismo.vars_clima, f_inic=f_inic, f_final=f_final
                )

                # Aplicar los valores de variables calculados
                for var, datos_vrs in datos.items():
                    # Guardar el valor para esta estación
                    símismo.variables[var].poner_vals_paso(datos_vrs, paso=b)

                # Avanzar la fecha
                f_inic = f_final

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError


class VariablesModBloques(VariablesModDeter):

    def __init__(símismo, variables, tmñ_bloques):
        símismo.tmñ_bloques = tmñ_bloques
        símismo.tmñ_bloques_cum = np.cumsum(tmñ_bloques)
        símismo.n_bloques = len(tmñ_bloques)
        super().__init__(variables)

    def act_paso(símismo, paso):
        b = símismo.bloque(paso)
        for v in símismo.vars_paso():
            if isinstance(v, VarBloque):
                v.act_paso(b)
            else:
                v.act_paso(paso)

    def bloque(símismo, paso):
        return next(i for i, s in enumerate(símismo.tmñ_bloques_cum) if paso < s)


class VarBloque(VarPasoDeter):

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_bloques, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=len(tmñ_bloques), inic=inic, líms=líms, info=info)
