from tinamit.MDS.MDS import leer_egr_mds
from tinamit.MDS.MDS import generar_mds
from tinamit.MDS.MDS import comanda_vensim
from tinamit.MDS.MDS import ModeloVensim
from tinamit.MDS.MDS import EnvolturaMDS


class அமைப்பு_இயக்கவியல்_உறை(EnvolturaMDS):

    def __init__(தன், கோப்பு):
        super().__init__(archivo=கோப்பு)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def iniciar_modelo(தன், nombre_corrida, tiempo_final):
        return தன்.iniciar_modelo(nombre_corrida, tiempo_final)

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def leer_resultados_mds(தன், corrida, மாறி):
        return தன்.leer_resultados_mds(corrida, var)



class ModeloVensim(ModeloVensim):

    def __init__(தன், கோப்பு):
        super().__init__(archivo=கோப்பு)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return தன்.iniciar_modelo(tiempo_final, nombre_corrida)

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def verificar_vensim(தன்):
        return தன்.verificar_vensim()



def comanda_vensim(func, args, mensaje_error=False, val_error, devolver):
    return comanda_vensim(func=func, args=args, mensaje_error=mensaje_error, val_error=val_error, devolver=devolver)


def generar_mds(கோப்பு, interpret):
    return generar_mds(archivo=கோப்பு, interpret=interpret)


def leer_egr_mds(கோப்பு, மாறி):
    return leer_egr_mds(archivo=கோப்பு, var=மாறி)
