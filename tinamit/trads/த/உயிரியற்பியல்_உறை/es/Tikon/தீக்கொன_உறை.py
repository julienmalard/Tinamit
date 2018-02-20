from tinamit.EnvolturaBF.es.Tikon.envoltTikon import ModeloTikon


class தீக்கொன_மாதிரி(ModeloTikon):

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return தன்.escribir_archivo_ingr(n_años_simul, dic_ingr)

    def leer_archivo_vals_inic(தன்):
        return தன்.leer_archivo_vals_inic()

    def act_vals_clima(தன், n_paso, f):
        return தன்.act_vals_clima(n_paso, f)

    def leer_archivo_egr(தன், n_años_egr):
        return தன்.leer_archivo_egr(n_años_egr)

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def iniciar_modelo(தன்):
        return தன்.iniciar_modelo()

    def avanzar_modelo(தன்):
        return தன்.avanzar_modelo()

    def cerrar_modelo(தன்):
        return தன்.cerrar_modelo()

