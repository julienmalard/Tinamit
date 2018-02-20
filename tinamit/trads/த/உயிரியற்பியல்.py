from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente
from tinamit.BF import ModeloBF
from tinamit.BF import EnvolturaBF


class உயிரியற்பியல்_உறை(EnvolturaBF):

    def __init__(தன், கோப்பு):
        super().__init__(archivo=கோப்பு)

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()



class உயி_இய_மாதிரி(ModeloBF):

    def __init__(தன்):
        super().__init__()

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()



class ModeloImpaciente(ModeloImpaciente):

    def __init__(தன்):
        super().__init__()

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def act_vals_clima(தன், n_paso, f):
        return தன்.act_vals_clima(n_paso, f)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def avanzar_modelo(தன்):
        return தன்.avanzar_modelo()

    def leer_vals_inic(தன்):
        return தன்.leer_vals_inic()

    def leer_archivo_vals_inic(தன்):
        return தன்.leer_archivo_vals_inic()

    def leer_egr(தன், n_años_egr):
        return தன்.leer_egr(n_años_egr)

    def escribir_ingr(தன், n_años_simul):
        return தன்.escribir_ingr(n_años_simul)

    def leer_archivo_egr(தன், n_años_egr):
        return தன்.leer_archivo_egr(n_años_egr)

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return தன்.escribir_archivo_ingr(n_años_simul, dic_ingr)



class ModeloFlexible(ModeloFlexible):

    def __init__(தன்):
        super().__init__()

    def cambiar_vals_modelo_interno(தன், valores):
        return தன்.cambiar_vals_modelo_interno(valores)

    def incrementar(தன், படி):
        return தன்.incrementar(paso)

    def leer_vals(தன்):
        return தன்.leer_vals()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return தன்.obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def leer_archivo_vals_inic(தன்):
        return தன்.leer_archivo_vals_inic()

    def mandar_simul(தன்):
        return தன்.mandar_simul()

    def leer_archivo_egr(தன், n_años_egr):
        return தன்.leer_archivo_egr(n_años_egr)

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return தன்.escribir_archivo_ingr(n_años_simul, dic_ingr)

