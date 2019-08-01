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

    def _act_vals_clima(símismo, f_0, f_1, vars_clima=None):

        vars_clima = vars_clima or símismo.vars_clima

        # Actualizar datos de clima
        p = símismo.paso_en_ciclo

        if símismo.corrida.clima and vars_clima and p == (símismo.tmñ_ciclo - 1):
            t = símismo.corrida.t
            f_inic = t.fecha()

            un_día = deltarelativo(days=1)

            vars_clim_bloque = {
                vr: d for vr, d in vars_clima.items() if isinstance(símismo.variables[vr], VarBloque)
            }
            vars_otros = {vr: d for vr, d in vars_clima.items() if vr not in vars_clim_bloque}

            super()._act_vals_clima(f_0=f_0, f_1=f_1, vars_clima=vars_otros)

            base_t, factor = a_unid_tnmt(símismo.unidad_tiempo())

            for i, b in enumerate(símismo.tmñ_bloques):

                f_final = f_inic + deltarelativo(**{a_unid_ft[base_t]: factor * b}) - un_día

                # Calcular los datos
                datos = símismo.corrida.clima.combin_datos(
                    vars_clima=vars_clim_bloque, f_inic=f_inic, f_final=f_final
                )

                # Aplicar los valores de variables calculados
                for var, datos_vrs in datos.items():
                    # Guardar el valor para esta estación
                    símismo.variables[var].poner_vals_paso(datos_vrs, paso=i)

                f_inic = f_final + un_día

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
