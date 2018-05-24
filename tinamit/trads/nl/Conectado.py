from tinamit.Conectado import Conectado
from tinamit.Conectado import SuperConectado


class SuperConectado(SuperConectado):

    def estab_modelo(símismo, modelo):
        return super().estab_modelo(modelo=modelo)

    def estab_conv_tiempo(símismo, mod_base, conv):
        return super().estab_conv_tiempo(mod_base=mod_base, conv=conv)

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", fecha_inic=None, lugar=None, tcr=None,
                recalc=True, clima=False, vars_interés=None):
        return super().simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida,
                               fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima,
                               vars_interés=vars_interés)

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def conectar_vars(símismo, modelo_fuente, var_fuente, var_recip, modelo_recip, conv=None):
        return super().conectar_vars(modelo_fuente=modelo_fuente, conv=conv, var_fuente=var_fuente, var_recip=var_recip,
                                     modelo_recip=modelo_recip)

    def desconectar_vars(símismo, var_fuente, modelo_fuente, modelo_recip=None, var_recip=None):
        return super().desconectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente, modelo_recip=modelo_recip,
                                        var_recip=var_recip)

    def paralelizable(símismo):
        return super().paralelizable()

    def estab_conv_meses(símismo, conv):
        return super().estab_conv_meses(conv=conv)

    def valid_var(símismo, var):
        return super().valid_var(var=var)

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def inic_vals_vars(símismo, dic_vals):
        return super().inic_vals_vars(dic_vals=dic_vals)

    def especificar_var_saliendo(símismo, var):
        return super().especificar_var_saliendo(var=var)

    def descomponer_nombre_var(símismo, var):
        return super().descomponer_nombre_var(var=var)


class Conectado(Conectado):

    def estab_mds(símismo, archivo_mds):
        return super().estab_mds(archivo_mds=archivo_mds)

    def estab_bf(símismo, bf):
        return super().estab_bf(bf=bf)

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=None):
        return super().conectar(var_mds=var_mds, var_bf=var_bf, mds_fuente=mds_fuente, conv=conv)

    def desconectar(símismo, var_mds):
        return super().desconectar(var_mds=var_mds)
