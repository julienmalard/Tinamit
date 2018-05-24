from tinamit.Modelo import Modelo


class மாதிரி(Modelo):

    def iniciar_modelo(தன், கடைசி_நேரம், பாவனைப்பெயர்):
        return super().iniciar_modelo(tiempo_final=கடைசி_நேரம், nombre_corrida=பாவனைப்பெயர்)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def conectar_var_clima(தன், மாறி, பருவனிலை_மாறி, conv, combin=None):
        return super().conectar_var_clima(var=மாறி, var_clima=பருவனிலை_மாறி, combin=combin, conv=conv)

    def desconectar_var_clima(தன், மாறி):
        return super().desconectar_var_clima(var=மாறி)

    def cambiar_vals(தன், valores):
        return super().cambiar_vals(valores=valores)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def act_vals_clima(தன், படி_எண், தேதி):
        return super().act_vals_clima(n_paso=படி_எண், f=தேதி)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", fecha_inic=None, lugar=None, tcr=None,
                recalc=True, clima=False, vars_interés=None):
        return super().simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida,
                               fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima,
                               vars_interés=vars_interés)

    def simular_paralelo(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", vals_inic=None,
                         fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, combinar=True, dibujar=None,
                         paralelo=True, devolver=None):
        return super().simular_paralelo(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida,
                                        vals_inic=vals_inic, fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc,
                                        clima=clima, combinar=combinar, dibujar=dibujar, paralelo=paralelo,
                                        devolver=devolver)

    def estab_conv_meses(símismo, conv):
        return super().estab_conv_meses(conv=conv)

    def dibujar_mapa(símismo, geog, var, directorio, corrida=None, i_paso=None, colores=None, escala=None):
        return super().dibujar_mapa(geog=geog, var=var, directorio=directorio, corrida=corrida, i_paso=i_paso,
                                    colores=colores, escala=escala)

    def valid_var(símismo, var):
        return super().valid_var(var=var)

    def leer_resultados(símismo, var, corrida=None):
        return super().leer_resultados(var=var, corrida=corrida)

    def paralelizable(símismo):
        return super().paralelizable()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def especificar_var_saliendo(símismo, var):
        return super().especificar_var_saliendo(var=var)

    def inic_val_var(símismo, var, val):
        return super().inic_val_var(var=var, val=val)

    def inic_vals_vars(símismo, dic_vals):
        return super().inic_vals_vars(dic_vals=dic_vals)

    def obt_info_var(símismo, var):
        return super().obt_info_var(var=var)

    def obt_unidades_var(símismo, var):
        return super().obt_unidades_var(var=var)

    def obt_val_actual_var(símismo, var):
        return super().obt_val_actual_var(var=var)

    def obt_lims_var(símismo, var):
        return super().obt_lims_var(var=var)

    def obt_dims_var(símismo, var):
        return super().obt_dims_var(var=var)

    def egresos(símismo):
        return super().egresos()

    def ingresos(símismo):
        return super().ingresos()

    def paráms(símismo):
        return super().paráms()

    def vars_estado_inicial(símismo):
        return super().vars_estado_inicial()
