import math as mat

from dateutil.relativedelta import relativedelta as deltarelativo
from tinamit.tiempo.tiempo import a_unid_tnmt

from ._impac import ModeloImpaciente, VariablesModImpaciente, VarPaso


class ModeloDeterminado(ModeloImpaciente):

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

    def _act_vals_clima(símismo, f_0, f_1):
        # Actualizar datos de clima
        if símismo.corrida.clima and símismo.vars_clima and símismo.paso_en_ciclo == 0:
            t = símismo.corrida.t
            f_inic = t.fecha()

            for i in range(1, símismo.tmñ_ciclo):
                base_t, factor = a_unid_tnmt(símismo.unidad_tiempo())
                f_final = f_inic + deltarelativo(**{base_t: factor})

                # Calcular los datos
                datos = símismo.corrida.clima.combin_datos(
                    vars_clima=símismo.vars_clima, f_inic=f_inic, f_final=f_final
                )

                # Aplicar los valores de variables calculados
                for var, datos_vrs in datos.items():
                    # Guardar el valor para esta estación
                    símismo.variables[var].poner_vals_paso(datos_vrs, paso=i)

                f_inic = f_final

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError


class VariablesModDeter(VariablesModImpaciente):
    pass


class VarPasoDeter(VarPaso):

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_ciclo, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=tmñ_ciclo, inic=inic, líms=líms, info=info)
