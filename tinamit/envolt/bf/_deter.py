import math as mat

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

        # Solamante hay que cambiar los datos si es el principio de un nuevo ciclo.
        if símismo.paso_en_ciclo == 0:

            # La fecha inicial
            f_inic = f_0

            for b, tmñ in enumerate(símismo.tmñ_bloques):
                # Para cada bloque...

                # La fecha final
                base_t, factor = símismo._unid_tiempo_python()
                f_final = f_0 + deltarelativo(**{base_t: tmñ * factor})

                # Calcular los datos
                datos = símismo.corrida.clima.combin_datos(vars_clima=símismo.vars_clima, f_inic=f_0, f_final=f_1)

                # Aplicar los valores de variables calculados
                for var, datos_vrs in símismo.vars_clima.items():
                    # Guardar el valor para esta estación
                    símismo.matrs_ingr[var][b, ...] = datos[var_clima] * conv

                # Avanzar la fecha
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
