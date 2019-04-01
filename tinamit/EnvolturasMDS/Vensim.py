import csv
import ctypes
import os
import struct
import sys

import numpy as np
import regex

from tinamit.Análisis.sintaxis import Ecuación
from tinamit.MDS import EnvolturaMDS
from tinamit.config import _
from tinamit.cositas import arch_más_recién

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None


def crear_dll_vensim(archivo):  # pragma: sin cobertura

    if sys.platform[:3] != 'win':
        raise OSError(_('Desafortunadamente, el dll de Vensim únicamente funciona en Windows.'))

    try:
        return ctypes.WinDLL(archivo)
    except OSError:
        raise OSError(_('Archivo "{}" erróneo para el DLL de Vensim DSS.').format(archivo))


_mnsj_falta_dll = _('Esta computadora no cuenta con el DLL de Vensim DSS.')


class ModeloVensim(EnvolturaMDS):  # pragma: sin cobertura
    """
    Esta es la envoltura para modelos de tipo_mod Vensim. Puede leer y controlar (casi) cualquier modelo Vensim para que
    se pueda emplear en Tinamit.
    Necesitarás la __versión__ DSS de Vensim para que funcione en Tinamit.
    """

    combin_pasos = True

    def __init__(símismo, archivo, nombre='mds', dll_vensim=None):
        """
        La función de inicialización del modelo. Creamos el vínculo con el DLL de Vensim y cargamos el modelo
        especificado.

        :param archivo: El fuente del modelo que quieres cargar en formato .vpm.
        :type archivo: str
        """

        # El paso para incrementar
        símismo.paso = 1

        # Una lista de variables editables
        símismo.editables = []

        símismo.tipo_mod = None

        # Inicializar ModeloVensim como una EnvolturasMDS.
        super().__init__(archivo=archivo, nombre=nombre, ops_mód={'dll_Vensim': dll_vensim})

    def _inic_dic_vars(símismo):
        """
        Inicializamos el diccionario de variables del modelo Vensim.
        """

        # Aplicar los variables iniciales
        símismo._leer_vals_de_vensim()

    def _vals_inic(símismo):
        """
        Inecesario porque llamar una nueva simulación de Vensim en :meth:`iniciar_modelo` reinicializa valores
        automáticamente, y la función :meth:`iniciar_modelo` los copia al diccionario interno después.
        """

        return {}

    def unidad_tiempo(símismo):
        """
        Aquí, sacamos las unidades de tiempo del modelo Vensim.

        :return: Las unidades de tiempo.
        :rtype: str

        """

        # Leer las unidades de tiempo
        unidades = símismo._obt_atrib_var(
            var='TIME STEP', cód_attrib=1,
            mns_error=_('Error obteniendo la unidad de tiempo para el modelo Vensim.')
        )

        return unidades

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        # En Vensim, tenemos que incializar los valores de variables constantes antes de empezar la simulación.
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var not in símismo.editables})

        # Establecer el nombre de la corrida.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                   mensaje_error=_('Error iniciando la corrida Vensim.'))

        # Establecer el tiempo final.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', n_pasos + 1),
                   mensaje_error=_('Error estableciendo el tiempo final para Vensim.'))

        # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
        # a través de la simulación.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="MENU>GAME",
                   mensaje_error=_('Error inicializando el juego Vensim.'))

        # Es ABSOLUTAMENTE necesario establecer el intervalo del juego aquí. Sino, no reinicializa el paso
        # correctamente entre varias corridas (aún modelos) distintas.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>GAMEINTERVAL|%i" % símismo.paso,
                   mensaje_error=_('Error estableciendo el paso de Vensim.'))

        # Aplicar los valores iniciales de variables editables
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var in símismo.editables})

        # Reinicializar el diccionario interno también.
        símismo._leer_vals_de_vensim()

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función cambiar los valores de variables en Vensim. Notar que únicamente los variables identificados como
        de tipo_mod "Gaming" en el modelo podrán actualizarse.

        :param valores: Un diccionario de variables y sus nuevos valores.
        :type valores: dict

        """

        for var, val in valores.items():
            # Para cada variable para cambiar...

            if símismo.obt_dims_var(var) == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Actualizar el valor en el modelo Vensim.
                if not np.isnan(val):
                    cmd_vensim(func=símismo.mod.vensim_command,
                               args='SIMULATE>SETVAL|%s = %f' % (var, val),
                               mensaje_error=_('Error cambiando el variable %s.') % var)
            else:
                # Para hacer: opciones de dimensiones múltiples
                # La lista de subscriptos
                subs = símismo.variables[var]['subscriptos']
                if isinstance(val, np.ndarray) and len(val.shape) > 0:
                    matr = val
                else:
                    matr = np.empty(len(subs))
                    matr[:] = val

                for n, s in enumerate(subs):
                    var_s = var + s
                    val_s = matr[n]
                    if not np.isnan(val_s):
                        cmd_vensim(func=símismo.mod.vensim_command,
                                   args='SIMULATE>SETVAL|%s = %f' % (var_s, val_s),
                                   mensaje_error=_('Error cambiando el variable %s.') % var_s)

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función avanza la simulación Vensim de ``paso`` pasos.

        :param paso: El número de pasos para tomar.
        :type paso: int

        """

        # Establecer el paso.
        if paso != símismo.paso:
            cmd_vensim(func=símismo.mod.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % paso,
                       mensaje_error=_('Error estableciendo el paso de Vensim.'))
            símismo.paso = paso

        # Avanzar el modelo.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>GAMEON", mensaje_error=_('Error para incrementar Vensim.'))

    def _pedir_val_var(símismo, var):

        # Una memoria
        mem_inter = ctypes.create_string_buffer(4)

        # Leer el valor del variable
        cmd_vensim(func=símismo.mod.vensim_get_val,
                   args=[var, mem_inter],
                   mensaje_error=_('Error con Vensim para leer variable "{}".').format(var))

        # Decodar
        return struct.unpack('f', mem_inter)[0]

    def _leer_vals(símismo):
        """
        Este método lee los valores intermediaros de los variables del modelo Vensim. Para ahorrar tiempo, únicamente
        lee esos variables que están en la lista de ``ModeloVensim.vars_saliendo``.

        """

        # Para cada variable que está conectado con el modelo biofísico...
        símismo._leer_vals_de_vensim(l_vars=list(símismo.vars_saliendo))

    def _leer_vals_de_vensim(símismo, l_vars=None):
        if l_vars is None:
            l_vars = list(símismo.variables)
        elif isinstance(l_vars, list):
            pass
        elif isinstance(l_vars, str):
            l_vars = [l_vars]
        else:
            raise TypeError(_('`l_vars` debe ser o un nombre de variable, o una lista de nombres de variables, y'
                              'no "{}".').format(type(l_vars)))

        for v in l_vars:
            if símismo.obt_dims_var(v) == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Leer su valor.
                val = símismo._pedir_val_var(v)

                # Guardar en el diccionario interno.
                símismo._act_vals_dic_var({v: val})

            else:
                matr_val = símismo.obt_val_actual_var(v)
                for n, s in enumerate(símismo.variables[v]['subscriptos']):
                    var_s = v + s

                    # Leer su valor.
                    val = símismo._pedir_val_var(var_s)

                    # Guardar en el diccionario interno.
                    matr_val[n] = val  # Para hacer: opciones de dimensiones múltiples

    def cerrar_modelo(símismo):
        """
        Cierre la simulación Vensim.
        """

        # Necesario para guardar los últimos valores de los variables conectados. (Muy incómodo, yo sé.)
        if símismo.paso != 1:
            cmd_vensim(func=símismo.mod.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % 1,
                       mensaje_error=_('Error estableciendo el paso de Vensim.'))
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>GAMEON",
                   mensaje_error=_('Error terminando la simulación Vensim.'))

        # ¡Por fin! Llamar la comanda para terminar la simulación.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>ENDGAME",
                   mensaje_error=_('Error terminando la simulación Vensim.'))

        #
        símismo._vdf_a_csv()

    def verificar_vensim(símismo):
        """
        Esta función regresa el estatus de Vensim. Es particularmente útil para desboguear (no tiene uso en las
        otras funciones de esta clase, y se incluye como ayuda a la programadora.)

        :return: Código de estatus Vensim:
            | 0 = Vensim está listo
            | 1 = Vensim está en una simulación activa
            | 2 = Vensim está en una simulación, pero no está respondiendo
            | 3 = Malas noticias
            | 4 = Error de memoria
            | 5 = Vensim está en modo de juego
            | 6 = Memoria no libre. Llamar vensim_command() debería de arreglarlo.
            | 16 += ver documentación de Vensim para vensim_check_status() en la sección de DLL (Suplemento DSS)
        :rtype: int

        """

        # Obtener el estatus.
        estatus = cmd_vensim(func=símismo.mod.vensim_check_status,
                             args=[],
                             mensaje_error=_('Error verificando el estatus de Vensim. De verdad, la cosa '
                                             'te va muy mal.'),
                             val_error=-1, devolver=True)
        return int(estatus)



    def paralelizable(símismo):
        """
        Modelos en Vensim sí deberían ser paralelizables.

        :return:
        :rtype:
        """
        return True

    def leer_arch_resultados(símismo, archivo, var=None, col_tiempo='Time'):
        """
        Esta función no lee los archivos directamente, pero los convierte en el formato .csv para que se puedan leer
        por Tinamït.

        Parameters
        ----------
        archivo : str
            El nombre del archivo.
        var : str | list[str]
            El variable o lista de variables de interés.
        col_tiempo: str
            El nombre de la columna de tiempo.

        Returns
        -------
        xr.Dataset
            Los resultados de la corrida.
        """

        corr, ext = os.path.splitext(archivo)

        # Si no se especificó extensión, tenemos que decidir entre el formato .vdf o .csv. Tomaremos el archivo más
        # recién, el cuál nos dará la simulación más recién efectuada por el usuario.
        if not len(ext):
            if os.path.isfile(corr + '.vdf'):
                if not os.path.isfile(corr + '.csv'):
                    ext = '.vdf'
                else:
                    ext = '.vdf' if os.path.getmtime(corr + '.vdf') > os.path.getmtime(corr + '.csv') else '.csv'
            elif os.path.isfile(corr + '.csv'):
                ext = '.csv'
            else:
                raise FileNotFoundError(_('No encontramos archivo para "{}".').format(archivo))

        # Si tenemos formato '.vdf', debemos convertirlo a '.csv' primero.
        if ext == '.vdf':
            archivo = corr + '.csv'
            símismo._vdf_a_csv(corr)

        # Delegar la lectura de archivos .csv a la clase pariente
        return super().leer_arch_resultados(archivo=archivo, var=var, col_tiempo=col_tiempo)

    def _vdf_a_csv(símismo, archivo_vdf=None, archivo_csv=None):

        if archivo_csv is None:
            archivo_csv = archivo_vdf

        # En Vensim, "!" quiere decir la corrida activa
        archivo_vdf = archivo_vdf or '!'
        archivo_csv = archivo_csv or '!'

        # Necesitas el dll de Vensim para que funcione
        if símismo.mod is None:
            raise OSError(_mnsj_falta_dll)

        # Vensim hace la conversión para nosotr@s
        símismo.mod.vensim_command(
            'MENU>VDF2CSV|{archVDF}|{archCSV}'.format(
                archVDF=archivo_vdf + '.vdf', archCSV=archivo_csv + '.csv'
            ).encode()
        )

        # Re-aplicar la corrida activa
        if archivo_csv == '!':
            archivo_csv = símismo.corrida_activa

        # Leer el csv
        with open(archivo_csv + '.csv', 'r', encoding='UTF-8') as d:
            lect = csv.reader(d)

            # Cortar el último paso de simulación. Tinamït siempre corre simulaciones de Vensim para 1 paso adicional
            # para permitir que valores de variables conectados se puedan actualizar.
            # Para que queda claro: esto es por culpa de un error en Vensim, no es culpa mía.
            filas = [f[:-1] if len(f) > 2 else f for f in lect]

        # Hay que abrir el archivo de nuevo para re-escribir sobre el contenido existente-
        with open(archivo_csv + '.csv', 'w', encoding='UTF-8', newline='') as d:
            escr = csv.writer(d)
            escr.writerows(filas)

    def _generar_archivo_mod(símismo):

        gen_archivo_mdl(archivo_plantilla=símismo.archivo, d_vars=símismo.variables)

    def publicar_modelo(símismo, dll=None):  # pragma: sin cobertura

        if dll is None:
            dll = símismo.mod

        if símismo.tipo_mod != '.mdl':
            raise ValueError(_('Solamente se pueden publicar a .vpm los modelos de formato .mdl'))

        cmd_vensim(dll.vensim_command, 'SPECIAL>LOADMODEL|%s' % símismo.archivo)

        archivo_frm = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'Vensim.frm')
        cmd_vensim(dll.vensim_command, ('FILE>PUBLISH|%s' % archivo_frm))

    def instalado(símismo):
        return símismo.mod is not None

    def editable(símismo):
        return símismo.instalado() and símismo.tipo_mod == '.mdl'


def gen_archivo_mdl(archivo_plantilla, d_vars):
    # Leer las tres secciones generales de la fuente
    with open(archivo_plantilla, encoding='UTF-8') as d:
        # La primera línea del documento, con {UTF-8}
        cabeza = [d.readline()]

        ln = d.readline()
        # Seguir hasta la primera línea que NO contiene información de variables ("****...***" para Vensim).
        while not regex.match(r'\*+\n$', ln) and not regex.match(r'\\\\\\\-\-\-\/\/\/', ln):
            ln = d.readline()

        # Guardar todo el resto del fuente (que no contiene información de ecuaciones de variables).
        cola = d.readlines()
        cola += [ln] + cola

    cuerpo = [_escribir_var(var, d_var) for var, d_var in d_vars.items()]

    return '\n'.join(*(cabeza + cuerpo + cola))


def _escribir_var(var, dic_var):
    """

    :param var:
    :type var: str

    :return:
    :rtype: str
    """

    if dic_var['ec'] == '':
        dic_var['ec'] = 'A FUNCTION OF (%s)' % ', '.join(dic_var['parientes'])
    lím_línea = 80

    texto = [var + '=\n',
             _cortar_líns(dic_var['ec'], lím_línea, lín_1='\t', lín_otras='\t\t'),
             _cortar_líns(dic_var['unidades'], lím_línea, lín_1='\t', lín_otras='\t\t'),
             _cortar_líns(dic_var['comentarios'], lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

    return texto


def _cortar_líns(texto, máx_car, lín_1=None, lín_otras=None):
    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            ln = texto
        else:
            dif = máx_car - texto

            ln = regex.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(ln)
        texto = texto[len(ln):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, ln in enumerate(lista[1:]):
            lista[n] = lín_otras + ln

    return lista
