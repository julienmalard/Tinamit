from ._impac import ModeloImpaciente


class ModeloIndeterminado(ModeloImpaciente):
    def incrementar(símismo, corrida):
        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        # Aplicar el incremento de paso
        i += int(paso)
        while i >= símismo.tmñ_ciclo:

            # Escribir el archivo de ingresos
            símismo.escribir_ingr(n_ciclos=1)

            símismo.ciclo += 1
            i -= símismo.tmñ_ciclo

            símismo.tmñ_ciclo = símismo.mandar_modelo()

            if i <= símismo.tmñ_ciclo:
                # Leer los egresos del modelo
                símismo.procesar_egr_modelo(n_ciclos=1)
                for ll in símismo.dic_ingr:
                    símismo.dic_ingr[ll] = None

                    # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Apuntar el diccionario interno de los valores al valor de este paso del ciclo
        símismo._act_vals_dic_var({var: matr[i] for var, matr in símismo.matrs_egr.items()})

