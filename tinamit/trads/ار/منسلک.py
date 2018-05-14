from tinamit.Conectado import Conectado
from tinamit.Conectado import SuperConectado


class ہڑامنسلک(SuperConectado):

    def estab_modelo(خود, نمونہ):
        return super().estab_modelo(modelo=نمونہ)

    def _inic_dic_vars(خود):
        return super()._inic_dic_vars()

    def unidad_tiempo(خود):
        return super().unidad_tiempo()

    def estab_conv_tiempo(خود, mod_base, conv):
        return super().estab_conv_tiempo(mod_base=mod_base, conv=conv)

    def _cambiar_vals_modelo_interno(خود, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(خود, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def simular(خود, tiempo_final, قدم=1, nombre_corrida="Corrida Tinamït", fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, vars_interés=None):
        return super().simular(tiempo_final=tiempo_final, paso=قدم, nombre_corrida=nombre_corrida, fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima, vars_interés=vars_interés)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def iniciar_modelo(خود):
        return super().iniciar_modelo()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def conectar_vars(خود, dic_vars, modelo_fuente, conv=None):
        return super().conectar_vars(dic_vars=dic_vars, modelo_fuente=modelo_fuente, conv=conv)

    def desconectar_vars(خود, var_fuente, modelo_fuente):
        return super().desconectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente)

    def paralelizable(símismo):
        return super().paralelizable()

    def inic_vals_vars(símismo, dic_vals):
        return super().inic_vals_vars(dic_vals=dic_vals)

    def estab_conv_meses(símismo, conv):
        return super().estab_conv_meses(conv=conv)

    def valid_var(símismo, var):
        return super().valid_var(var=var)


class منسلک(Conectado):

    def estab_mds(خود, archivo_mds):
        return super().estab_mds(archivo_mds=archivo_mds)

    def estab_bf(خود, bf):
        return super().estab_bf(bf=bf)

    def conectar(خود, var_mds, var_bf, mds_fuente, conv=None):
        return super().conectar(var_mds=var_mds, var_bf=var_bf, mds_fuente=mds_fuente, conv=conv)

    def desconectar(خود, var_mds):
        return super().desconectar(var_mds=var_mds)

    def leer_resultados(símismo, corrida, var):
        return super().leer_resultados(corrida=corrida, var=var)
