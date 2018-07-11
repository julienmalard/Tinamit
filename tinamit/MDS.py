import os

from tinamit.Modelo import Modelo
from tinamit.config import _


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (EnvolturasMDS). Se debe crear una subclase para cada
    tipo de EnvolturasMDS. Al momento, el único incluido es VENSIM.
    """

    def __init__(símismo, archivo, nombre='mds'):
        """
        Iniciamos el modelo DS.

        :param archivo: El fuente con el modelo DS.
        :type archivo: str
        """

        if not os.path.isfile(archivo):
            raise FileNotFoundError(_('El fuente "{}" no existe.').format(archivo))

        # Listas vacías para distintos tipos de variables.
        símismo.constantes = []
        símismo.niveles = []
        símismo.flujos = []
        símismo.auxiliares = []

        # Acordarse de dónde venimos
        símismo.archivo = archivo

        # Modelos DS se identifican por el nombre 'mds'.
        super().__init__(nombre=nombre)

    def _inic_dic_vars(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar. Además de
        los diccionarios de variables normales, debe establecer `símismo.constantes`, `símismo.flujos`,
        `símismo.niveles`, `símismo.editables`, y `símismo.auxiliares`. Este último
        debe tener las llaves "hijos", "parientes" y "ec".

        Ver :func:`Modelo.Modelo._inic_dic_vars` para más información.
        """

        raise NotImplementedError

    def unidad_tiempo(símismo):
        """
        Cada envoltura de programa DS debe implementar este metodo para devolver las unidades de tiempo del modelo DS
        cargado.

        :return: Las unidades del modelo DS cargado.
        :rtype: str

        """
        raise NotImplementedError

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar. Notar que la
        implementación de este método debe incluir la aplicación de valores iniciales.

        Ver :func:`Modelo.Modelo.iniciar_modelo` para más información.

        :param nombre_corrida: El nombre de la corrida (útil para guardar resultados).
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """
        raise NotImplementedError

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Ver :func:`Modelo.Modelo.cambiar_vals_modelo` para más información.

        :param valores: El diccionario de valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe avanzar la simulación del modelo DS de ``paso`` unidades de tiempo.  Ver
        :func:`Modelo.Modelo.incrementar` para más información.

        :param paso: El paso con cual incrementar el modelo.
        :type paso: int

        """
        raise NotImplementedError

    def _leer_vals(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe leer los valores de los variables en el modelo EnvolturasMDS. Si es más fácil, puede simplemente leer los valores
        de los variables que están en la lista ``EnvolturasMDS.vars_saliendo`` (los variables del DS que están
        conectados con el modelo biofísico).

        Ver :func:`Modelo.Modelo.leer_vals` para más información.

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe llamar acciones necesarias para terminar la simulación y cerrar el modelo DS, si aplican.

        Ver :func:`Modelo.Modelo.cerrar_modelo` para más información.

        """
        raise NotImplementedError

    def _leer_vals_inic(símismo):
        raise NotImplementedError

    def __getinitargs__(símismo):
        return símismo.archivo,


class MDSEditable(EnvolturaMDS):
    def __init__(símismo, archivo, nombre='mds'):
        super().__init__(archivo=archivo, nombre=nombre)

        from tinamit.EnvolturasMDS import generar_mds
        símismo.mod = None  # type: EnvolturaMDS
        símismo._estab_mod(generar_mds(archivo=archivo))
        símismo.combin_incrs = símismo.mod.combin_incrs

        símismo.editado = False

    def _estab_mod(símismo, mod):
        """

        Parameters
        ----------
        mod: EnvolturaMDS

        Returns
        -------

        """
        símismo.mod = mod
        mod.mem_vars = símismo.mem_vars
        mod.vars_saliendo = símismo.vars_saliendo
        mod.variables = símismo.variables

    def _act_vals_dic_var(símismo, valores):
        símismo.mod._act_vals_dic_var(valores=valores)
        super()._act_vals_dic_var(valores)

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        from tinamit.EnvolturasMDS import generar_mds
        if símismo.mod is None or símismo.editado:
            símismo.publicar_modelo()
            símismo._estab_mod(generar_mds())
            símismo.editado = False

        símismo.mod.corrida_activa = nombre_corrida
        símismo.mod._iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

    def cambiar_vals_modelo_interno(símismo, valores):
        return símismo.mod.cambiar_vals_modelo_interno(valores=valores)

    def _incrementar(símismo, paso, guardar_cada=None):
        return símismo.mod._incrementar(paso=paso, guardar_cada=guardar_cada)

    def inic_val_var(símismo, var, val):
        símismo.mod.inic_val_var(var=var, val=val)
        super().inic_val_var(var, val)

    def _leer_vals(símismo):
        return símismo.mod._leer_vals()

    def cerrar_modelo(símismo):
        return símismo.mod.cerrar_modelo()

    def leer_arch_resultados(símismo, archivo, var=None):
        return símismo.mod.leer_arch_resultados(archivo=archivo, var=var)

    def _leer_vals_inic(símismo):
        return símismo.mod._leer_vals_inic()

    def publicar_modelo(símismo):
        raise NotImplementedError

    def paralelizable(símismo):
        return símismo.mod.paralelizable()
