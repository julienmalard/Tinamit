from tinamit.EnvolturaMDS.Vensim import comanda_vensim
from tinamit.EnvolturaMDS.Vensim import ModeloVensim
from tinamit.EnvolturaMDS.Vensim import ModeloVensimMdl


class ModeloVensimMdl(ModeloVensimMdl):

    def calib_ec(símismo, var, ec=None, paráms=None, método=None):
        return super().calib_ec(var=var, ec=ec, paráms=paráms, método=método)

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloVensim(ModeloVensim):

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def verificar_vensim(símismo):
        return super().verificar_vensim()

    def obt_atrib_var(símismo, var, cód_attrib, mns_error=None):
        return super().obt_atrib_var(var=var, cód_attrib=cód_attrib, mns_error=mns_error)

    def paralelizable(símismo):
        return super().paralelizable()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()
