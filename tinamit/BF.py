from dateutil.relativedelta import relativedelta as deltarelativo


class ModeloBloques(ModeloImpaciente):

    def _act_vals_clima(símismo, f_0, f_1, lugar):

        # Solamante hay que cambiar los datos si es el principio de un nuevo ciclo.
        if símismo.ciclo == 0 and símismo.paso_en_ciclo == 0:

            # La fecha inicial
            f_inic = f_0

            for b, tmñ in enumerate(símismo.tmñ_bloques):
                # Para cada bloque...

                # La fecha final
                base_t, factor = símismo._unid_tiempo_python()
                f_final = f_0 + deltarelativo(**{base_t: tmñ * factor})

                # Calcular los datos
                datos = lugar.comb_datos(vars_clima=nombres_extrn, combin=combins, f_inic=f_inic, f_final=f_final)

                # Aplicar los valores de variables calculados
                for i, var in enumerate(vars_clima):
                    # Para cada variable en la lista de clima...

                    # El nombre oficial del variable de clima
                    var_clima = nombres_extrn[i]

                    # El factor de conversión
                    conv = convs[i]

                    # Guardar el valor para esta estación
                    símismo.matrs_ingr[var][b, ...] = datos[var_clima] * conv

                # Avanzar la fecha
                f_inic = f_final
