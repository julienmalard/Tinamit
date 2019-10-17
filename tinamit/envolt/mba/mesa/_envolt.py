import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import Grid
from mesa.time import BaseScheduler

from ._auto import _gen_modelo
from .._envolt import ModeloBA
from .._vars import VarAgenteMBA, VarCuadMBA, VariablesMBA


class ModeloMesa(ModeloBA):
    """
    Envoltura para Modelos basados en agentes (MBA) en Python, con la librería ``mesa``.
    """

    def __init__(símismo, clase_modelo, args_modelo, unid_tiempo, nombre='mesa'):
        """

        Parameters
        ----------
        clase_modelo:
            La clase del modelo mesa, o el archivo donde se encuentra.
        args_modelo: dict
            Diccionario de argumentos necesarios para inicializar ``clase_modelo``.
        unid_tiempo: str
            La unidad de tiempo del modelo.
        nombre: str
            El nombre de tu modelo.
        """

        símismo._unid_tiempo = unid_tiempo
        símismo._clase_mod = _gen_modelo(clase_modelo)
        símismo._args_mod = args_modelo or {}
        símismo._mod = símismo._clase_mod(**símismo._args_mod)

        super().__init__(variables=símismo._mod.gen_variables(), nombre=nombre)

    def iniciar_modelo(símismo, corrida):
        # Recrear el modelo mesa, porque al momento no se pueden reinicializar.
        símismo._mod = símismo._clase_mod(**símismo._args_mod)

        super().iniciar_modelo(corrida)

    def incrementar(símismo, rebanada):
        for i in range(rebanada.n_pasos):
            símismo._mod.mod.step()

        vals_globales = {
            v: símismo._mod.colector.model_vars[v.nombre][-1]
            for v in rebanada.resultados.variables() if not isinstance(v, VarCuadMBA)
        }
        vals_cuad = {
            v: v.f_agreg(np.array([getattr(agt, v.nombre) for agt in símismo._mod.manejador.agents]))
            for v in rebanada.resultados.variables() if isinstance(v, VarCuadMBA)
        }

        símismo.variables.cambiar_vals({**vals_globales, **vals_cuad})

        super().incrementar(rebanada)

    def cambiar_vals(símismo, valores):
        for vr, vl in valores.items():
            var = símismo.variables[vr]
            if isinstance(var, VarAgenteMBA):
                for agt in símismo._mod.manejador.agents:
                    setattr(agt, vr, vl)
            elif isinstance(var, VarCuadMBA):
                for cél, vl_cél in zip(símismo._mod.cuad, vl):
                    for agt in símismo._mod.cuad.get_cell_list_contents(cél):
                        setattr(agt, vr, vl_cél)
            else:
                setattr(símismo._mod.mod, vr, vl)
                símismo._mod.colector.model_vars[vr][-1] = vl
        super().cambiar_vals(valores)

    def cerrar(símismo):
        símismo._mod = None  # Justo en caso

    def paralelizable(símismo):
        return True

    def unidad_tiempo(símismo):
        return símismo._unid_tiempo


class EnvoltModeloMesa(Model):
    def __init__(símismo):
        super().__init__()
        símismo.cuad = símismo._obt_atributo(Grid)
        símismo.colector = símismo._obt_atributo(DataCollector)
        símismo.manejador = símismo._obt_atributo(BaseScheduler)

    def variables(símismo):
        """

        Returns
        -------
        VariablesMBA
        """
        raise NotImplementedError

    def _obt_atributo(símismo, cls):
        try:
            return next(a for a in símismo.__dict__.values() if isinstance(a, cls))
        except StopIteration:
            return
