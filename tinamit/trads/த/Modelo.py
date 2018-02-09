from tinamit.Modelo import Modelo


class Modelo(Modelo):

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(தன், கடைசி_நேரம், பாவனைப்பெயர்):
        return super().iniciar_modelo(tiempo_final=கடைசி_நேரம், nombre_corrida=பாவனைப்பெயர்)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def inic_val(தன், var, val):
        return super().inic_val(var=var, val=val)

    def limp_vals_inic(தன்):
        return super().limp_vals_inic()

    def conectar_var_clima(தன், var, var_clima, combin=None):
        return super().conectar_var_clima(var=var, var_clima=var_clima, combin=combin)

    def desconectar_var_clima(தன், var):
        return super().desconectar_var_clima(var=var)

    def cambiar_vals(தன், valores):
        return super().cambiar_vals(valores=valores)

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def act_vals_clima(தன், படி_எண், f):
        return super().act_vals_clima(n_paso=படி_எண், f=f)
