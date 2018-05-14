from tinamit.Conectado import Conectado
from tinamit.Conectado import SuperConectado


class SuperConectado(SuperConectado):

    def estab_modelo(símismo, modelo):
        return super().estab_modelo(modelo=modelo)

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def obt_unidad_tiempo(símismo):
        return super().unidad_tiempo()

    def estab_conv_tiempo(símismo, mod_base, conv):
        return super().estab_conv_tiempo(mod_base=mod_base, conv=conv)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida="Corrida Tinamït", fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False):
        return super().simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida, fecha_inic=fecha_inic, lugar=lugar, tcr=tcr, recalc=recalc, clima=clima)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def conectar_vars(símismo, dic_vars, modelo_fuente, conv=None):
        return super().conectar_vars(dic_vars=dic_vars, modelo_fuente=modelo_fuente, conv=conv)

    def desconectar_vars(símismo, var_fuente, modelo_fuente):
        return super().desconectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente)


class Conectado(Conectado):

    def estab_mds(símismo, archivo_mds):
        return super().estab_mds(archivo_mds=archivo_mds)

    def estab_bf(símismo, archivo_bf):
        return super().estab_bf(archivo_bf=archivo_bf)

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=None):
        return super().conectar(var_mds=var_mds, var_bf=var_bf, mds_fuente=mds_fuente, conv=conv)

    def desconectar(símismo, var_mds):
        return super().desconectar(var_mds=var_mds)

    def dibujar(símismo, geog, var, corrida, directorio, i_paso=None, colores=None, escala=None):
        return super().dibujar(geog=geog, var=var, corrida=corrida, directorio=directorio, i_paso=i_paso, colores=colores, escala=escala)
