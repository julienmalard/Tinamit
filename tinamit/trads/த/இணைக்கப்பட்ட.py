from tinamit.Conectado import Conectado
from tinamit.Conectado import SuperConectado


class மேலிணைக்கப்பட்ட(SuperConectado):

    def estab_modelo(தன், மாதிரி):
        return super().estab_modelo(modelo=மாதிரி)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்._inic_dic_vars()

    def unidad_tiempo(தன்):
        return super().unidad_tiempo()

    def estab_conv_tiempo(தன், mod_base, conv):
        return super().estab_conv_tiempo(mod_base=mod_base, conv=conv)

    def _cambiar_vals_modelo_interno(தன், valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(தன், படி_எண், தேதி):
        return super().act_vals_clima(n_paso=படி_எண், f=தேதி)

    def simular(தன், கடைசி_நேரம், படி=1, பாவனைப்பெயர்="Corrida Tinamït", ஆரம்பும்_தேதி=None, இடம்=None, tcr=None, recalc=True, பருவநிலை=False, vars_interés=None):
        return super().simular(tiempo_final=கடைசி_நேரம், paso=படி, nombre_corrida=பாவனைப்பெயர், fecha_inic=ஆரம்பும்_தேதி, lugar=இடம், tcr=tcr, recalc=recalc, clima=பருவநிலை, vars_interés=vars_interés)

    def முன்னெடுக்க(தன், படி):
        return தன்.incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def conectar_vars(தன், dic_vars, modelo_fuente, conv=None):
        return super().conectar_vars(dic_vars=dic_vars, modelo_fuente=modelo_fuente, conv=conv)

    def desconectar_vars(தன், var_fuente, modelo_fuente):
        return super().desconectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente)

    def paralelizable(símismo):
        return super().paralelizable()

    def inic_vals_vars(símismo, dic_vals):
        return super().inic_vals_vars(dic_vals=dic_vals)

    def estab_conv_meses(símismo, conv):
        return super().estab_conv_meses(conv=conv)

    def valid_var(símismo, var):
        return super().valid_var(var=var)


class இணைக்கப்பட்ட(Conectado):

    def estab_mds(தன், archivo_mds):
        return super().estab_mds(archivo_mds=archivo_mds)

    def estab_bf(தன், bf):
        return super().estab_bf(bf=bf)

    def conectar(தன், var_mds, var_bf, mds_fuente, conv=None):
        return super().conectar(var_mds=var_mds, var_bf=var_bf, mds_fuente=mds_fuente, conv=conv)

    def desconectar(தன், var_mds):
        return super().desconectar(var_mds=var_mds)

    def leer_resultados(símismo, corrida, var):
        return super().leer_resultados(corrida=corrida, var=var)
