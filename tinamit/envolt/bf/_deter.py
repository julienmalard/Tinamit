import math as mat

from dateutil.relativedelta import relativedelta as deltarelativo
from tinamit.tiempo.tiempo import a_unid_tnmt, a_unid_ft

from ._impac import ModeloImpaciente, VariablesModImpaciente, VarPaso


class ModeloDeterminado(ModeloImpaciente):
    """
    La clase pariente para todos modelos que correr por un número predeterminado de pasos a cada simulación.
    """

    def incrementar(símismo, rebanada):
        # Para simplificar el código un poco.
        p = símismo.paso_en_ciclo
        n_pasos = rebanada.n_pasos

        # Aplicar el incremento de paso
        p_después = (p + n_pasos) % símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = p_después

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if p_después == 0 or ((p + n_pasos) >= símismo.tmñ_ciclo):
            # El número de ciclos para simular
            c = mat.ceil(n_pasos / símismo.tmñ_ciclo)  # type: int

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

        # Actualizar el paso en los variables
        símismo.variables.act_paso(símismo.paso_en_ciclo)

        super().incrementar(rebanada)

    def _act_vals_clima(símismo, f_0, f_1, vars_clima=None):

        vars_clima = vars_clima or símismo.vars_clima
        # Actualizar datos de clima
        p = símismo.paso_en_ciclo

        if símismo.corrida.clima and vars_clima and p == (símismo.tmñ_ciclo - 1):
            t = símismo.corrida.t
            f_inic = t.fecha()

            un_día = deltarelativo(days=1)

            vars_clim_paso = {
                vr: d for vr, d in vars_clima.items() if isinstance(símismo.variables[vr], VarPasoDeter)
            }
            vars_clim_ciclo = {vr: d for vr, d in vars_clima.items() if vr not in vars_clim_paso}

            base_t, factor = a_unid_tnmt(símismo.unidad_tiempo())

            f_final = f_inic + deltarelativo(**{a_unid_ft[base_t]: factor * símismo.tmñ_ciclo}) - un_día

            datos_ciclo = símismo.corrida.clima.combin_datos(
                vars_clima=vars_clim_ciclo, f_inic=f_inic, f_final=f_final
            )
            for var, vl in datos_ciclo.items():
                símismo.variables[var].poner_val(vl)

            for i in range(símismo.tmñ_ciclo):

                f_final = f_inic + deltarelativo(**{a_unid_ft[base_t]: factor}) - un_día

                # Calcular los datos
                datos = símismo.corrida.clima.combin_datos(
                    vars_clima=vars_clim_paso, f_inic=f_inic, f_final=f_final
                )

                # Aplicar los valores de variables calculados
                for var, datos_vrs in datos.items():
                    # Guardar el valor para esta estación
                    símismo.variables[var].poner_vals_paso(datos_vrs, paso=i)

                f_inic = f_final + un_día

    def avanzar_modelo(símismo, n_ciclos):
        """
        Avanzar el modelo por un número determinado de ciclos.

        Parameters
        ----------
        n_ciclos: int
            El número de ciclos que hay que avanzar.

        """
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError


class VariablesModDeter(VariablesModImpaciente):
    """
    Representa los variables de un modelo :class:`~tinamit.envolt.bf._deter.Determinado`.
    """
    pass


class VarPasoDeter(VarPaso):
    """
    Un variable de un modelo :class:`~tinamit.envolt.bf._deter.Determinado` que toma un valor distinto a cada
    paso (y no solamente a cada ciclo de simulación).
    """

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_ciclo, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=tmñ_ciclo, inic=inic, líms=líms, info=info)
