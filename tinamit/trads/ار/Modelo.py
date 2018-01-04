from tinamit.Modelo import Modelo


class Modelo(Modelo):

    def inic_vars(خود):
        return super().inic_vars()

    def obt_unidad_tiempo(خود):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def inic_val(خود, var, val):
        return super().inic_val(var=var, val=val)

    def limp_vals_inic(خود):
        return super().limp_vals_inic()

    def conectar_var_clima(خود, var, var_clima, combin=None):
        return super().conectar_var_clima(var=var, var_clima=var_clima, combin=combin)

    def desconectar_var_clima(خود, var):
        return super().desconectar_var_clima(var=var)

    def cambiar_vals(خود, valores):
        return super().cambiar_vals(valores=valores)

    def cambiar_vals_modelo_interno(خود, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def act_vals_clima(خود, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)
