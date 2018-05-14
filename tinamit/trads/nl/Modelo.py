from tinamit.Modelo import Modelo


class Modelo(Modelo):

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def conectar_var_clima(símismo, var, var_clima, conv, combin=None):
        return super().conectar_var_clima(var=var, var_clima=var_clima, combin=combin, conv=conv)

    def desconectar_var_clima(símismo, var):
        return super().desconectar_var_clima(var=var)

    def cambiar_vals(símismo, valores):
        return super().cambiar_vals(valores=valores)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, vars_interés=None):
        return super().simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida, fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima, vars_interés=vars_interés)

    def simular_paralelo(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", vals_inic=None, fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, combinar=True, dibujar=None, paralelo=True, devolver=None):
        return super().simular_paralelo(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida, vals_inic=vals_inic, fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima, combinar=combinar, dibujar=dibujar, paralelo=paralelo, devolver=devolver)

    def estab_conv_meses(símismo, conv):
        return super().estab_conv_meses(conv=conv)

    def dibujar_mapa(símismo, geog, var, directorio, corrida=None, i_paso=None, colores=None, escala=None):
        return super().dibujar_mapa(geog=geog, var=var, directorio=directorio, corrida=corrida, i_paso=i_paso, colores=colores, escala=escala)

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
