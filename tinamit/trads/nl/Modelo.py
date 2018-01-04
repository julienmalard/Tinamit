from tinamit.Modelo import Modelo


class Modelo(Modelo):

    def inic_vars(símismo):
        return super().inic_vars()

    def obt_unidad_tiempo(símismo):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def inic_val(símismo, var, val):
        return super().inic_val(var=var, val=val)

    def limp_vals_inic(símismo):
        return super().limp_vals_inic()

    def conectar_var_clima(símismo, var, var_clima, combin=None):
        return super().conectar_var_clima(var=var, var_clima=var_clima, combin=combin)

    def desconectar_var_clima(símismo, var):
        return super().desconectar_var_clima(var=var)

    def cambiar_vals(símismo, valores):
        return super().cambiar_vals(valores=valores)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)
