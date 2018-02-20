from tinamit.Modelo import Modelo


class மாதிரி(Modelo):

    def __init__(தன், பெயர்):
        super().__init__(nombre=பெயர்)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def iniciar_modelo(தன், கடைசி_நேரம், பாவனை_பெயர்):
        return தன்.iniciar_modelo(tiempo_final, nombre_corrida)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def inic_val(தன், மாறி, val):
        return தன்.inic_val(var, val)

    def limp_vals_inic(தன்):
        return தன்.limp_vals_inic()

    def conectar_var_clima(தன், மாறி, பருவனிலை_மாறி, combin):
        return தன்.conectar_var_clima(var, var_clima, combin)

    def desconectar_var_clima(தன், மாறி):
        return தன்.desconectar_var_clima(var)

    def cambiar_vals(தன், valores):
        return தன்.cambiar_vals(valores)

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def act_vals_clima(தன், n_paso, f):
        return தன்.act_vals_clima(n_paso, f)

