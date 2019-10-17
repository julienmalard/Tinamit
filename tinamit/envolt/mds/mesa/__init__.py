import mesa

from tinamit.envolt.mds import ModeloDS


class ModeloMesa(ModeloDS):
    """
    Envoltura para Modelos basados en agentes (MBA) en Python, con la librería ``mesa``.

    Por supuesto, MBAs no son modelos de dinámicas de sistemas (MDS). Pero al nivel de simulación se parecen más a éstes
    que a modelos biofísicos, así que los ponemos aquí con los MDS.
    """

    def __init__(símismo, modelo, unid_tiempo, nombre='mesa'):
        """

        Parameters
        ----------
        modelo: str or mesa.Model
            El modelo mesa, o el archivo donde se encuentra.
        unid_tiempo: str
            La unidad de tiempo del modelo.
        nombre: str
            El nombre de tu modelo.
        """

        símismo._unid_tiempo = unid_tiempo
        variables = _
        super().__init__(nombre=nombre)


    def iniciar_modelo(símismo, corrida):
        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()

        super().iniciar_modelo(corrida)
        
    def incrementar(símismo, rebanada):
        super().incrementar(rebanada)
        

    def cambiar_vals(símismo, valores):
        símismo.vars_para_cambiar.update({vr: float(vl) for vr, vl in valores.items()})
        super().cambiar_vals(valores)

    def paralelizable(símismo):
        return True

    def unidad_tiempo(símismo):
        return símismo._unid_tiempo
