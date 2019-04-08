from tinamit.mod.var import Variable
from ._impac import ModeloImpaciente, VariablesModImpaciente


class ModeloBloques(ModeloImpaciente):

    def __init__(símismo, nombre='bf'):
        super().__init__(nombre)
        símismo.tmñ_bloques = None

    def incrementar(símismo, corrida):
        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        paso = int(paso)

        # Aplicar el incremento de paso
        primer_incr = i == símismo.ciclo == -1

        i += paso
        avanzar = primer_incr or (i // símismo.tmñ_ciclo > 0)
        i %= símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if avanzar:
            # El número de ciclos para simular
            c = mat.ceil(paso / símismo.tmñ_ciclo)  # type: int
            símismo.ciclo += c

            # Escribir los archivos de ingreso
            símismo.escribir_ingr(n_ciclos=c)

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

            # Leer los egresos del modelo
            símismo.procesar_egr_modelo(n_ciclos=c)

        # Apuntar los valores de egreso al bloque actual
        b = símismo._bloque_actual()
        símismo._act_vals_dic_var(
            {var: símismo.matrs_egr[var][b] for var in símismo._vars_por_bloques() if var in símismo.egresos()})

        símismo._act_vals_dic_var(
            {var: símismo.matrs_egr[var][i] for var in símismo._vars_por_pasito() if var in símismo.egresos()})

    def _bloque_actual(símismo):
        tmñ_bloques_cum = np.cumsum(símismo.obt_tmñ_bloques())
        n_bloques = len(tmñ_bloques_cum)

        for i in range(n_bloques):
            if símismo.paso_en_ciclo < tmñ_bloques_cum[i]:
                return i

        raise ValueError(símismo.paso_en_ciclo)


class VariablesModBloques(VariablesModImpaciente):
    def vars_bloque(símismo):
        return [v for v in símismo if isinstance(v, VarBloque)]

    def vars_ciclo_ingr(símismo):
        return [v for v in símismo if isinstance(v, VarBloqueIngr)]

    def vars_ciclo_egr(símismo):
        return [v for v in símismo if isinstance(v, VarBloqueEgr)]


class VarBloqueIngr(Variable):
    pass


class VarBloqueEgr(Variable):
    pass


class VarBloque(VarBloqueIngr, VarBloqueEgr):
    pass
