from tinamit.Conectado import Conectado
from tinamit.Conectado import SuperConectado


class SuperConectado(SuperConectado):

    def __init__(தன், பெயர்="SuperConectado"):
        super().__init__(nombre=பெயர்)

    def estab_modelo(தன், modelo):
        return தன்.estab_modelo(modelo)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def estab_conv_tiempo(தன், mod_base, conv):
        return தன்.estab_conv_tiempo(mod_base, conv)

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def _conectar_clima(தன், n_pasos, lugar, fecha_inic, tcr, recalc):
        return தன்._conectar_clima(n_pasos, lugar, fecha_inic, tcr, recalc)

    def act_vals_clima(தன், n_paso, f):
        return தன்.act_vals_clima(n_paso, f)

    def simular(தன், tiempo_final, படி=False, nombre_corrida=True, fecha_inic, lugar, tcr, recalc="Corrida Tinamït", clima=1):
        return தன்.simular(tiempo_final, paso=False, nombre_corrida=True, fecha_inic, lugar, tcr, recalc="Corrida Tinamït", clima=1)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def conectar_vars(தன், dic_vars, modelo_fuente, conv):
        return தன்.conectar_vars(dic_vars, modelo_fuente, conv)

    def desconectar_vars(தன், var_fuente, modelo_fuente):
        return தன்.desconectar_vars(var_fuente, modelo_fuente)



class Conectado(Conectado):

    def __init__(தன்):
        super().__init__()

    def estab_mds(தன், அமை_இய_மா_கோப்பு):
        return தன்.estab_mds(archivo_mds)

    def estab_bf(தன், உயி_இய_கோப்பு):
        return தன்.estab_bf(archivo_bf)

    def இணைக்க(தன், var_mds, var_bf, mds_fuente, conv):
        return தன்.conectar(var_mds, var_bf, mds_fuente, conv)

    def desconectar(தன், var_mds):
        return தன்.desconectar(var_mds)

    def dibujar(தன், geog, var, corrida, directorio, i_paso, colores, escala):
        return தன்.dibujar(geog, var, corrida, directorio, i_paso, colores, escala)

