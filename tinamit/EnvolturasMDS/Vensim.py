import csv
import ctypes
import os
import struct
import sys

import numpy as np
import regex

from tinamit.Análisis.sintaxis import Ecuación
from tinamit.MDS import EnvolturaMDS, MDSEditable
from tinamit.config import _

try:
    import pymc3 as pm
except ImportError:
    pm = None


def crear_dll_Vensim(archivo):  # pragma: sin cobertura

    if sys.platform[:3] != 'win':
        raise OSError(_('Desafortunadamente, el dll de Vensim únicamente funciona en Windows.'))

    try:
        return ctypes.WinDLL(archivo)
    except OSError:
        raise OSError(_('Archivo "{}" erróneo para el DLL de Vensim DSS.').format(archivo))


_mnsj_falta_dll = _('Esta computadora no cuenta con el DLL de VENSIM DSS.')


class ModeloVensimMdl(MDSEditable):

    def __init__(símismo, archivo):

        # Variables internos a VENSIM
        símismo.internos = ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']

        símismo.dic_doc = {'cabeza': [], 'cuerpo': [], 'cola': []}

        # Leer las tres secciones generales del fuente
        with open(archivo, encoding='UTF-8') as d:
            # La primera línea del documento, con {UTF-8}
            símismo.dic_doc['cabeza'] = [d.readline()]

            l = d.readline()
            # Seguir hasta la primera línea que NO contiene información de variables ("****...***" para Vensim).
            while not regex.match(r'\*+\n$', l):
                símismo.dic_doc['cuerpo'].append(l)
                l = d.readline()

            # Guardar todo el resto del fuente (que no contiene información de ecuaciones de variables).
            cola = d.readlines()
            símismo.dic_doc['cola'] += [l] + cola

        super().__init__(archivo=archivo)

    def _inic_dic_vars(símismo):

        # Borrar lo que podría haber allí desde antes.
        símismo.variables.clear()

        cuerpo = símismo.dic_doc['cuerpo']

        l_tx_vars = []
        nuevo_var = True
        for fl in cuerpo:
            f = fl.strip().rstrip('\\')
            if len(f):
                if nuevo_var:
                    l_tx_vars.append(f)
                else:
                    l_tx_vars[-1] += f

                nuevo_var = (f[-1] == '|')

        for tx_var in l_tx_vars:
            tx_ec, tx_unids_líms, tx_info = tx_var.strip('|').split('~')
            obj_ec = Ecuación(tx_ec, dialecto='vensim')
            if obj_ec.tipo == 'sub':
                continue
            var = obj_ec.nombre
            try:
                tx_unids, tx_líms = tx_unids_líms.split('[')
            except ValueError:
                tx_unids = tx_unids_líms
                tx_líms = ''

            if len(tx_líms):
                líms = tuple([float(x) if x.strip() != '?' else None for x in tx_líms.strip(']').split(',')][:2])
            else:
                líms = (None, None)

            símismo.variables[var] = {
                'val': None,
                'unidades': tx_unids.strip(),
                'ec': str(obj_ec),
                'ingreso': None,
                'dims': (1,),  # Para hacer
                'líms': líms,
                'subscriptos': None,  # Para hacer
                'hijos': [],
                'parientes': obj_ec.variables(),
                'egreso': None,
                'info': tx_info.strip(),
                'val_inic': False
            }

        for v, d_v in símismo.variables.items():
            for p in d_v['parientes']:
                d_p = símismo.variables[p]
                d_p['hijos'].append(v)

        # Borrar lo que había antes en las listas siguientes:
        símismo.flujos.clear()
        símismo.auxiliares.clear()
        símismo.constantes.clear()
        símismo.niveles.clear()

        # Guardar una lista de los nombres de variables de tipo "nivel"
        símismo.niveles += [x for x, d in símismo.variables.items() if regex.match(r'INTEG *\(', d['ec'])]

        # Los flujos, por definición, son los parientes de los niveles.
        for niv in símismo.niveles:

            # El primer argumento de la función INTEG de VENSIM
            ec = Ecuación(símismo.variables[niv]['ec'], dialecto='vensim')
            arg_integ = ec.sacar_args_func('INTEG', i=1)[0]
            args_inic = ec.sacar_args_func('INTEG')[1]
            if args_inic in símismo.variables:
                símismo.variables[args_inic]['val_inic'] = True

            # Extraer los variables flujos
            flujos = [v for v in Ecuación(arg_integ, dialecto='vensim').variables() if v not in símismo.internos]

            for flujo in flujos:
                # Para cada nivel en el modelo...

                if flujo not in símismo.flujos and flujo not in símismo.niveles:
                    # Agregar el flujo, si no está ya en la lista de flujos.

                    símismo.flujos.append(flujo)

        # Los auxiliares son los variables con parientes que son ni niveles, ni flujos.
        símismo.auxiliares += [x for x, d in símismo.variables.items()
                               if x not in símismo.niveles and x not in símismo.flujos
                               and len(d['parientes'])]

        # Los constantes son los variables que quedan.
        símismo.constantes += [x for x, d in símismo.variables.items()
                               if not len(d['parientes']) and not any(h in símismo.flujos for h in d['hijos'])]

    def _escribir_var(símismo, var):
        """

        :param var:
        :type var: str

        :return:
        :rtype: str
        """

        dic_var = símismo.variables[var]

        if dic_var['ec'] == '':
            dic_var['ec'] = 'A FUNCTION OF (%s)' % ', '.join(dic_var['parientes'])
        lím_línea = 80

        texto = [var + '=\n',
                 _cortar_líns(dic_var['ec'], lím_línea, lín_1='\t', lín_otras='\t\t'),
                 _cortar_líns(dic_var['unidades'], lím_línea, lín_1='\t', lín_otras='\t\t'),
                 _cortar_líns(dic_var['comentarios'], lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

        return texto

    def unidad_tiempo(símismo):
        # Para hacer: algo mucho más elegante
        i_f = next(i for i, f in enumerate(símismo.dic_doc['cola']) if 'INITIAL TIME' in f) + 1
        unid_tiempo = símismo.dic_doc['cola'][i_f].split('\t')[-1].strip()
        return unid_tiempo

    def publicar_modelo(símismo):
        símismo.publicar_vpm()

    def publicar_vpm(símismo):  # pragma: sin cobertura

        try:
            dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
        except OSError:
            raise OSError(_mnsj_falta_dll)

        cmd_vensim(dll.vensim_command, 'SPECIAL>LOADMODEL|%s' % símismo.archivo_mds)
        símismo.guardar_mds()

        archivo_vpm = os.path.join(os.path.split(símismo.archivo_mds)[0], 'Tinamit.vpm')

        archivo_frm = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'VENSIM.frm')

        cmd_vensim(dll.vensim_command, ('FILE>PUBLISH|%s' % archivo_frm))


class ModeloVensim(EnvolturaMDS):  # pragma: sin cobertura
    """
    Esta es la envoltura para modelos de tipo VENSIM. Puede leer y controlar (casi) cualquier modelo VENSIM para que
    se pueda emplear en Tinamit.
    Necesitarás la __versión__ DSS de VENSIM para que funcione en Tinamit.
    """

    combin_pasos = True

    def instalado(símismo):
        return símismo.dll is not None

    def __init__(símismo, archivo, nombre='mds', dll_Vensim=None):
        """
        La función de inicialización del modelo. Creamos el vínculo con el DLL de VENSIM y cargamos el modelo
        especificado.

        :param archivo: El fuente del modelo que quieres cargar en formato .vpm.
        :type archivo: str
        """

        # Llamar el DLL de Vensim.
        if dll_Vensim is None:
            lugares_probables = [
                'C:\\Windows\\System32\\vendll32.dll',
                'C:\\Windows\\SysWOW64\\vendll32.dll'
            ]
            arch_dll_Vensim = símismo._obt_val_config(llave='dll_Vensim', cond=os.path.isfile,
                                                      respaldo=lugares_probables)
            if arch_dll_Vensim is None:
                símismo.dll = None
            else:
                símismo.dll = crear_dll_Vensim(arch_dll_Vensim)
        else:
            símismo.dll = crear_dll_Vensim(dll_Vensim)

        if dll_Vensim is None:
            return

        # Inicializar Vensim
        cmd_vensim(func=símismo.dll.vensim_command,
                   args=[''],
                   mensaje_error=_('Error iniciando VENSIM.'))

        # Cargar el modelo
        cmd_vensim(func=símismo.dll.vensim_command,
                   args='SPECIAL>LOADMODEL|%s' % archivo,
                   mensaje_error=_('Error cargando el modelo de VENSIM.'))

        # Parámetros estéticos de ejecución.
        cmd_vensim(func=símismo.dll.vensim_be_quiet, args=[2],
                   mensaje_error=_('Error en la comanda "vensim_be_quiet".'),
                   val_error=-1)

        # El paso para incrementar
        símismo.paso = 1

        # Una lista de variables editables
        símismo.editables = []

        # Inicializar ModeloVENSIM como una EnvolturasMDS.
        super().__init__(archivo=archivo, nombre=nombre)

    def _inic_dic_vars(símismo):
        """
        Inicializamos el diccionario de variables del modelo VENSIM.
        """

        # Sacar las unidades y las dimensiones de los variables, e identificar los variables constantes
        for l in [símismo.editables, símismo.constantes, símismo.niveles, símismo.auxiliares, símismo.flujos,
                  símismo.variables]:
            l.clear()

        editables = símismo.editables
        constantes = símismo.constantes
        niveles = símismo.niveles
        auxiliares = símismo.auxiliares
        flujos = símismo.flujos

        # Primero, verificamos el tamañano de memoria necesario para guardar una lista de los nombres de los variables.

        mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

        # Verificar el tamaño necesario
        tamaño_nec = cmd_vensim(func=símismo.dll.vensim_get_varnames,
                                args=['*', 0, mem, 0],
                                mensaje_error=_('Error obteniendo eñ tamaño de los variables VENSIM.'),
                                val_error=-1, devolver=True
                                )

        mem = ctypes.create_string_buffer(tamaño_nec)  # Una memoria intermedia con el tamaño apropiado

        # Guardar y decodar los nombres de los variables.
        cmd_vensim(func=símismo.dll.vensim_get_varnames,
                   args=['*', 0, mem, tamaño_nec],
                   mensaje_error=_('Error obteniendo los nombres de los variables de VENSIM.'),
                   val_error=-1
                   )
        variables = [x for x in mem.raw.decode().split('\x00') if x]

        # Quitar los nombres de variables VENSIM genéricos de la lista.
        for i in ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']:
            if i in variables:
                variables.remove(i)

        # Sacar los nombres de variables editables
        cmd_vensim(func=símismo.dll.vensim_get_varnames,
                   args=['*', 12, mem, tamaño_nec],
                   mensaje_error=_('Error obteniendo los nombres de los variables editables ("Gaming") de '
                                   'VENSIM.'),
                   val_error=-1
                   )

        editables.extend([x for x in mem.raw.decode().split('\x00') if x])

        for var in variables:
            # Para cada variable...

            # Sacar sus unidades
            unidades = símismo.obt_atrib_var(var, cód_attrib=1)

            # Verificar el tipo del variable
            tipo_var = símismo.obt_atrib_var(var, cód_attrib=14)

            # No incluir a los variables de verificación (pruebas de modelo) Vensim
            if tipo_var == 'Constraint':
                variables.remove(var)
                continue

            # Guardamos los variables constantes en una lista.
            if tipo_var == 'Constant':
                constantes.append(var)
            elif tipo_var == 'Level':
                niveles.append(var)
            elif tipo_var == 'Auxiliary':
                auxiliares.append(var)

            # Sacar las dimensiones del variable
            subs = símismo.obt_atrib_var(var, cód_attrib=9)

            if len(subs):
                dims = (len(subs),)  # Para hacer: soporte para más que 1 dimensión
                nombres_subs = subs
            else:
                dims = (1,)
                nombres_subs = None

            # Sacar los límites del variable
            rango = (símismo.obt_atrib_var(var, cód_attrib=11), símismo.obt_atrib_var(var, cód_attrib=12))
            rango = tuple(float(l) if l != '' else None for l in rango)

            # Leer la descripción del variable.
            info = símismo.obt_atrib_var(var, 2)

            # Leer la ecuación del variable, sus hijos y sus parientes directamente de Vensim
            ec = símismo.obt_atrib_var(var, 3)
            hijos = símismo.obt_atrib_var(var, 5)
            parientes = símismo.obt_atrib_var(var, 4)

            # Actualizar el diccionario de variables.
            # Para cada variable, creamos un diccionario especial, con su valor y unidades. Puede ser un variable
            # de ingreso si es de tipo editable ("Gaming"), y puede ser un variable de egreso si no es un valor
            # constante.
            dic_var = {'val': None if dims == (1,) else np.empty(dims),
                       'unidades': unidades,
                       'ingreso': var in editables,
                       'dims': dims,
                       'subscriptos': nombres_subs,
                       'ec': ec,
                       'hijos': hijos,
                       'parientes': parientes,
                       'egreso': var not in constantes,
                       'líms': rango,
                       'info': info}

            # Guardar el diccionario del variable en el diccionario general de variables.
            símismo.variables[var] = dic_var

        # Actualizar los auxiliares
        for var in símismo.auxiliares.copy():
            for hijo in símismo.variables[var]['hijos']:
                if hijo in símismo.niveles:
                    flujos.append(var)
                    if var in auxiliares:
                        auxiliares.remove(var)

    def unidad_tiempo(símismo):
        """
        Aquí, sacamos las unidades de tiempo del modelo VENSIM.

        :return: Las unidades de tiempo.
        :rtype: str

        """

        # Leer las unidades de tiempo
        unidades = símismo.obt_atrib_var(var='TIME STEP', cód_attrib=1,
                                         mns_error='Error obteniendo el paso de tiempo para el modelo Vensim.')

        return unidades

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        """
        Acciones necesarias para iniciar el modelo VENSIM.

        :param nombre_corrida: El nombre de la corrida del modelo.
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """

        # En Vensim, tenemos que incializar los valores de variables constantes antes de empezar la simulación.
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var in símismo.constantes})

        # Establecer el nombre de la corrida.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                   mensaje_error=_('Error iniciando la corrida VENSIM.'))

        # Establecer el tiempo final.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', tiempo_final + 1),
                   mensaje_error=_('Error estableciendo el tiempo final para VENSIM.'))

        # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
        # a través de la simulación.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="MENU>GAME",
                   mensaje_error=_('Error inicializando el juego VENSIM.'))

        # Es ABSOLUTAMENTE necesario establecer el intervalo del juego aquí. Sino, no reinicializa el paso
        # correctamente entre varias corridas (aún modelos) distintas.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="GAME>GAMEINTERVAL|%i" % símismo.paso,
                   mensaje_error=_('Error estableciendo el paso de VENSIM.'))

        # Aplicar los valores iniciales de variables editables
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var not in símismo.constantes})

    def _leer_vals_inic(símismo):

        símismo._leer_vals_de_vensim()

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función cambiar los valores de variables en VENSIM. Notar que únicamente los variables identificados como
        de tipo "Gaming" en el modelo podrán actualizarse.

        :param valores: Un diccionario de variables y sus nuevos valores.
        :type valores: dict

        """

        for var, val in valores.items():
            # Para cada variable para cambiar...

            if símismo.variables[var]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Actualizar el valor en el modelo VENSIM.
                if not np.isnan(val):
                    cmd_vensim(func=símismo.dll.vensim_command,
                               args='SIMULATE>SETVAL|%s = %f' % (var, val),
                               mensaje_error=_('Error cambiando el variable %s.') % var)
            else:
                # Para hacer: opciones de dimensiones múltiples
                # La lista de subscriptos
                subs = símismo.variables[var]['subscriptos']
                if isinstance(val, np.ndarray):
                    matr = val
                else:
                    matr = np.empty(len(subs))
                    matr[:] = val

                for n, s in enumerate(subs):
                    var_s = var + s
                    val_s = matr[n]
                    if not np.isnan(val_s):
                        cmd_vensim(func=símismo.dll.vensim_command,
                                   args='SIMULATE>SETVAL|%s = %f' % (var_s, val_s),
                                   mensaje_error=_('Error cambiando el variable %s.') % var_s)

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función avanza la simulación VENSIM de ``paso`` pasos.

        :param paso: El número de pasos para tomar.
        :type paso: int

        """

        # Establecer el paso.
        if paso != símismo.paso:
            cmd_vensim(func=símismo.dll.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % paso,
                       mensaje_error=_('Error estableciendo el paso de VENSIM.'))
            símismo.paso = paso

        # Avanzar el modelo.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="GAME>GAMEON", mensaje_error=_('Error para incrementar VENSIM.'))

    def _pedir_val_var(símismo, var):

        # Una memoria
        mem_inter = ctypes.create_string_buffer(4)

        # Leer el valor del variable
        cmd_vensim(func=símismo.dll.vensim_get_val,
                   args=[var, mem_inter],
                   mensaje_error=_('Error con VENSIM para leer variable "{}".').format(var))

        # Decodar
        return struct.unpack('f', mem_inter)[0]

    def _leer_vals(símismo):
        """
        Este método lee los valores intermediaros de los variables del modelo VENSIM. Para ahorrar tiempo, únicamente
        lee esos variables que están en la lista de ``ModeloVENSIM.vars_saliendo``.

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
            cmd_vensim(func=símismo.dll.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % 1,
                       mensaje_error=_('Error estableciendo el paso de VENSIM.'))
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="GAME>GAMEON",
                   mensaje_error=_('Error para terminar la simulación VENSIM.'))

        # ¡Por fin! Llamar la comanda para terminar la simulación.
        cmd_vensim(func=símismo.dll.vensim_command,
                   args="GAME>ENDGAME",
                   mensaje_error=_('Error para terminar la simulación VENSIM.'))

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
        estatus = cmd_vensim(func=símismo.dll.vensim_check_status,
                             args=[],
                             mensaje_error=_('Error verificando el estatus de VENSIM. De verdad, la cosa '
                                             'te va muy mal.'),
                             val_error=-1, devolver=True)
        return int(estatus)

    def obt_atrib_var(símismo, var, cód_attrib, mns_error=None):
        """

        :param var:
        :type var: str
        :param cód_attrib:
        :type cód_attrib: int
        :param mns_error:
        :type mns_error: str
        :return:
        :rtype:
        """

        if cód_attrib in [4, 5, 6, 7, 8, 9, 10]:
            lista = True
        elif cód_attrib in [1, 2, 3, 11, 12, 13, 14]:
            lista = False
        else:
            raise ValueError(_('Código "{}" no reconocido para la comanda Vensim de obtener atributos de variables.')
                             .format(cód_attrib))

        if mns_error is None:
            l_atrs = [_('las unidades'), _('la descipción'), _('la ecuación'), _('las causas'), _('las consecuencias'),
                      _('la causas iniciales'), _('las causas activas'), _('los subscriptos'),
                      _('las combinaciones de subscriptos'), _('los subscriptos de gráfico'), _('el mínimo'),
                      _('el máximo'), _('el rango'), _('el tipo')]
            mns_error1 = _('Error leyendo el tamaño de memoria para obtener {} del variable "{}" en Vensim') \
                .format(l_atrs[cód_attrib - 1], var)
            mns_error2 = _('Error leyendo {} del variable "{}" en Vensim.').format(l_atrs[cód_attrib - 1], var)
        else:
            mns_error1 = mns_error2 = mns_error

        mem = ctypes.create_string_buffer(10)
        tmñ = cmd_vensim(func=símismo.dll.vensim_get_varattrib,
                         args=[var, cód_attrib, mem, 0],
                         mensaje_error=mns_error1,
                         val_error=-1,
                         devolver=True)

        mem = ctypes.create_string_buffer(tmñ)
        cmd_vensim(func=símismo.dll.vensim_get_varattrib,
                   args=[var, cód_attrib, mem, tmñ],
                   mensaje_error=mns_error2,
                   val_error=-1)

        if lista:
            return [x for x in mem.raw.decode().split('\x00') if x]
        else:
            return mem.value.decode()

    def paralelizable(símismo):
        """
        Modelos en VENSIM sí deberían ser paralelizables.

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
        if símismo.dll is None:
            raise OSError(_mnsj_falta_dll)

        # Vensim hace la conversión para nosotr@s
        símismo.dll.vensim_command(
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


def cmd_vensim(func, args, mensaje_error=None, val_error=None, devolver=False):  # pragma: sin cobertura
    """
    Esta función sirve para llamar todo tipo de comanda VENSIM.

    :param func: La función DLL a llamar.
    :type func: callable

    :param args: Los argumento a pasar a la función. Si no hay, usar una lista vacía.
    :type args: list | str

    :param mensaje_error: El mensaje de error para mostrar si hay un error en la comanda.
    :type mensaje_error: str

    :param val_error: Un valor de regreso VENSIM que indica un error para esta función. Si se deja ``None``, todos
      valores que no son 1 se considerarán como erróneas.
    :type val_error: int

    :param devolver: Si se debe devolver el valor devuelto por VENSIM o no.
    :type devolver: bool

    """

    # Asegurarse que args es una lista
    if type(args) is not list:
        args = [args]

    # Encodar en bytes todos los argumentos de texto.
    for n, a in enumerate(args):
        if type(a) is str:
            args[n] = a.encode()

    # Llamar la función Vensim y guardar el resultado.
    try:
        resultado = func(*args)
    except OSError as e:
        try:
            resultado = func(*args)
        except OSError as e:
            raise OSError(e)

    # Verificar su hubo un error.
    if val_error is None:
        error = (resultado != 1)
    else:
        error = (resultado == val_error)

    # Si hubo un error, avisar el usuario.
    if error:
        if mensaje_error is None:
            mensaje_error = _('Error con la comanda Vensim.')

        mensaje_error += _(' Código de error {}.').format(resultado)

        raise OSError(mensaje_error)

    # Devolver el valor devuelto por la función Vensim, si aplica.
    if devolver:
        return resultado


def _cortar_líns(texto, máx_car, lín_1=None, lín_otras=None):
    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            l = texto
        else:
            dif = máx_car - texto

            l = regex.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(l)
        texto = texto[len(l):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, l in enumerate(lista[1:]):
            lista[n] = lín_otras + l

    return lista
