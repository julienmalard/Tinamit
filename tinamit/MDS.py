import csv
import ctypes
import os
import re

import numpy as np

from tinamit import _
from tinamit.Modelo import Modelo


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (EnvolturasMDS). Se debe crear una subclase para cada
    tipo de EnvolturasMDS. Al momento, el único incluido es VENSIM.
    """

    ext_arch_egr = '.csv'

    def __init__(símismo, archivo, nombre='mds'):
        """
        Iniciamos el modelo DS.

        :param archivo: El archivo con el modelo DS.
        :type archivo: str
        """

        if not os.path.isfile(archivo):
            raise FileNotFoundError(_('El archivo "{}" no existe.').format(archivo))

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

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
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

    def _cambiar_vals_modelo_interno(símismo, valores):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Ver :func:`Modelo.Modelo.cambiar_vals_modelo` para más información.

        :param valores: El diccionario de valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def _incrementar(símismo, paso):
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

    def _leer_resultados(símismo, var, corrida):
        """
        Esta función lee los resultados desde un archivo de egresos del modelo DS.

        :param corrida: El nombre de la corrida. Debe corresponder al nombre del archivo de egresos.
        :type corrida: str
        :param var: El variable de interés.
        :type var: str
        :return: Una matriz de los valores del variable de interés.
        :rtype: np.ndarray
        """

        raise NotImplementedError

    def _leer_vals_inic(símismo):
        raise NotImplementedError

    def _aplicar_cambios_vals_inic(símismo):
        raise NotImplementedError

    def __getinitargs__(símismo):

        return símismo.archivo,


class MDSEditable(EnvolturaMDS):
    def __init__(símismo, archivo, nombre='mds'):
        super().__init__(archivo=archivo, nombre=nombre)

        from tinamit.EnvolturasMDS import generar_mds
        símismo.mod = None  # type: EnvolturaMDS
        símismo._estab_mod(generar_mds(archivo=archivo))

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

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        from tinamit.EnvolturasMDS import generar_mds
        if símismo.mod is None or símismo.editado:
            símismo.publicar_modelo()
            símismo._estab_mod(generar_mds())
            símismo.editado = False
        símismo.mod._iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def _cambiar_vals_modelo_interno(símismo, valores):
        return símismo.mod._cambiar_vals_modelo_interno(valores=valores)

    def _incrementar(símismo, paso):
        return símismo.mod._incrementar(paso=paso)

    def inic_val_var(símismo, var, val):
        símismo.mod.inic_val_var(var=var, val=val)
        super().inic_val_var(var, val)

    def _leer_vals(símismo):
        return símismo.mod._leer_vals()

    def cerrar_modelo(símismo):
        return símismo.mod.cerrar_modelo()

    def _leer_resultados(símismo, var, corrida):
        return símismo.mod._leer_resultados(var=var, corrida=corrida)

    def _leer_vals_inic(símismo):
        return símismo.mod._leer_vals_inic()

    def _aplicar_cambios_vals_inic(símismo):
        return símismo.mod._aplicar_cambios_vals_inic()

    def publicar_modelo(símismo):
        raise NotImplementedError


def leer_egr_mds(archivo, var, saltar_última_vdf=True):
    """
    Lee archivos de egresos de simulaciones EnvolturasMDS.

    :param archivo: El archivo de egresos.
    :type archivo: str
    :param var: El variable de interés
    :type var: str
    :return: Una matriz con los valores del variable de interés.
    :rtype: np.ndarray
    """

    ext = os.path.splitext(archivo)[1]
    if ext == '':
        ext = '.vdf'
        archivo += ext

    datos = []

    if ext == '.vdf':
        ext = '.csv'
        archivo_csv = os.path.split(archivo)[1].replace('.vdf', '.csv')

        dll_vensim = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        dll_vensim.vensim_command('MENU>VDF2CSV|{vdffile}|{CSVfile}'
                                  .format(vdffile=archivo, CSVfile=archivo_csv).encode())

        archivo = archivo.replace('.vdf', '.csv')
        if saltar_última_vdf:
            with open(archivo, 'r', encoding='UTF-8') as d:
                lect = csv.reader(d)
                filas = [f[:-1] if len(f) > 2 else f for f in lect]
            with open(archivo, 'w', encoding='UTF-8', newline='') as d:
                escr = csv.writer(d)
                escr.writerows(filas)

    if ext == '.csv':
        with open(archivo, encoding='UTF-8') as d:
            lector = csv.reader(d)
            filas = [f for f in lector if re.match('{}(\[.*\])?$'.format(var), f[0])]

        for f in filas:
            datos.append(f[1:])

    else:
        raise ValueError(_('El formato de datos "{}" no se puede leer al momento.').format(ext))

    datos = np.array(datos, dtype=float).swapaxes(0, -1)
    if datos.shape[-1] == 1:
        datos = datos[..., 0]

    return datos
