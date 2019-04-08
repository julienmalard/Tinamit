from ._impac import ModeloImpaciente
import math as mat

class ModeloDeterminado(ModeloImpaciente):

    def incrementar(símismo, corrida):
        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        # Aplicar el incremento de paso
        avanzar = i == símismo.ciclo == -1  # para hacer
        i += corrida
        avanzar = avanzar or (i // símismo.tmñ_ciclo > 0)
        i %= símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if avanzar:
            # El número de ciclos para simular
            c = mat.ceil(corrida / símismo.tmñ_ciclo)  # type: int
            símismo.ciclo += c

            # Escribir los archivos de ingreso
            símismo.escribir_ingr(n_ciclos=c)

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

            # Leer los egresos del modelo
            símismo.procesar_egr_modelo(n_ciclos=c)

        # Apuntar el diccionario interno de los valores al valor de este paso del ciclo
        símismo._act_vals_dic_var({var: matr[i] for var, matr in símismo.matrs_egr.items()})

