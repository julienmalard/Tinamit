import numpy as np

from tinamit.mod import VariablesMod
from tinamit.mod.var import Variable
from ._envolt import ModeloBF


class ModeloImpaciente(ModeloBF):
    """
    La clase pariente para modelos que deben correr por varios pasos al mismo tiempo, es decir,
    :class:`~tinamit.envolt.bf._indeter.Indeterminado` y :class:`~tinamit.envolt.bf._deter.Determinado`.
    """

    def __init__(símismo, tmñ_ciclo, variables, nombre='bf'):
        símismo.paso_en_ciclo = tmñ_ciclo - 1
        símismo.tmñ_ciclo = tmñ_ciclo

        super().__init__(variables, nombre)

    def iniciar_modelo(símismo, corrida):
        símismo.paso_en_ciclo = símismo.tmñ_ciclo - 1
        super().iniciar_modelo(corrida)

    def unidad_tiempo(símismo):
        raise NotImplementedError


class VariablesModImpaciente(VariablesMod):
    """
    Representa los variables de un modelo :class:`~tinamit.envolt.bf._impac.Impaciente`.
    """

    def vars_paso(símismo):
        """
        Devuelve los variables por paso.

        Returns
        -------
        list

        """
        return [v for v in símismo if isinstance(v, VarPaso)]

    def act_paso(símismo, paso):
        """
        Actualizar el paso de los variables en el ciclo.

        Parameters
        ----------
        paso: int
            El paso actual en el ciclo.

        """
        for v in símismo.vars_paso():
            v.act_paso(paso=paso)


class VarPaso(Variable):
    """
    Un variable de un modelo :class:`~tinamit.envolt.bf._impac.Impaciente` cuyo valor cambia con cada paso (y no
    solamente con cada ciclo).
    """

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_ciclo, inic=0, líms=None, info=''):
        """

        Parameters
        ----------
        nombre: str
            El nombre del variable.
        unid: str or None
            Las unidades del variable.
        ingr: bool
            Si es un ingreso al modelo.
        egr: bool
            Si es un egreso del modelo.
        tmñ_ciclo: int
            El número de pasos en cada ciclo.
        inic: int or float or np.ndarray
            El valor inicial del modelo.
        líms: tuple
            Los límites del variable.
        info: str
            Descripción detallada del variable.
        """
        super().__init__(nombre, unid, ingr, egr, inic=inic, líms=líms, info=info)
        símismo._matr_paso = np.zeros((tmñ_ciclo, *símismo._val.shape))
        símismo._matr_paso[:] = símismo.inic
        símismo.paso = -1

    def poner_val(símismo, val):
        símismo._matr_paso[símismo.paso] = val
        super().poner_val(val)

    def obt_val(símismo):
        return símismo._matr_paso[símismo.paso]

    def poner_vals_paso(símismo, val, paso=None):
        """
        Establece el valor del variable a un paso dado. Si ``paso`` es ``None``, ``val`` debe ser una matriz donde
        eje 0 corresponde a todos los pasos del ciclo.

        Parameters
        ----------
        val: np.ndarray
            El nuevo valor.
        paso: int
            El paso al cual poner el nuevo valor del variable.

        """
        paso = paso if paso is not None else slice(None, None)

        # reformar para variables unidimensionales
        símismo._matr_paso[paso] = val.reshape(*símismo._matr_paso[paso].shape)

        # También hay que actualizar el variable paso
        super().poner_val(símismo._matr_paso[símismo.paso])

    def obt_vals_paso(símismo):
        """
        Obtener los valores del variable a todos los pasos del ciclo actual.

        Returns
        -------
        np.ndarray

        """
        return símismo._matr_paso

    def act_paso(símismo, paso):
        """
        Actualiza el paso actual del variable.

        Parameters
        ----------
        paso: int
            El nuevo paso en el ciclo actual.
        """
        símismo.paso = paso
        super().poner_val(símismo._matr_paso[paso])

    def reinic(símismo):
        símismo.paso = -1
        símismo._matr_paso[:] = símismo.inic
        super().reinic()
