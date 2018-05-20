import ctypes
import os
import struct
import sys
from functools import reduce
from operator import mul
from warnings import warn as avisar

import numpy as np
import regex

from tinamit import _
from tinamit.MDS import EnvolturaMDS, leer_egr_mds
from .sintaxis import sacar_arg, sacar_variables, juntar_líns, cortar_líns

try:
    import pymc3 as pm
except ImportError:
    pm = None

if sys.platform[:3] == 'win':
    try:
        ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
        dll_Vensim = 'C:\\Windows\\System32\\vendll32.dll'
    except OSError:
        try:
            ctypes.WinDLL('C:\\Windows\\SysWOW64\\vendll32.dll')
            dll_Vensim = 'C:\\Windows\\SysWOW64\\vendll32.dll'
        except OSError:
            dll_Vensim = None
            avisar('Esta computadora no tiene el DLL de Vensim DSS. Las funcionalidades con modelos Vensim se verán'
                   'limitados.')
else:
    dll_Vensim = None


class ModeloVensimMdl(EnvolturaMDS):
    rgx_var_base = r'([\p{l}\p{m}]+[\p{l}\p{m}\p{n} ]*(?![\p{l}\p{m}\p{n} ]*\())|(".+"(?<!\\))'
    _regex_var = r'(?<var>{var})(\[(?<subs>{var})\])?'.format(var=rgx_var_base)
    regex_fun = r'[\p{l}\p{m}]+[\p{l}\p{m}\p{n} ]*(?= *\()'

    # l = [' abd = 1', 'abc d[SUBS] = 1 * abd', '"A." = 1', '"ab3 *" = 1', '"-1\"f" = 1', 'a', 'é = A FUNCTION OF ()', 'வணக்கம்',
    #      'a3b', '"5a"']
    #
    # for i in l:
    #     print(i)
    #     m = regex.match(_regex_var, i)
    #
    #     if m:
    #         print(m.groupdict())
    #         print(m.group())
    #     print('===')

    instalado = False  # para hacer: Por el momento lo dejamos inactivado.

    def __init__(símismo, archivo):

        símismo.dic_doc = {'cabeza': [], 'cuerpo': [], 'cola': []}

        # Leer las tres secciones generales del archivo
        with open(archivo, encoding='UTF-8') as d:
            # La primera línea del documento, con {UTF-8}
            símismo.dic_doc['cabeza'] = [d.readline()]

            l = d.readline()
            # Seguir hasta la primera línea que NO contiene información de variables ("****...***" para Vensim).
            while not regex.match(r'\*+\n$', l):
                símismo.dic_doc['cuerpo'].append(l)
                l = d.readline()

            # Guardar todo el resto del archivo (que no contiene información de ecuaciones de variables).
            cola = d.readlines()
            símismo.dic_doc['cola'] += [l] + cola

        super().__init__(archivo=archivo)

    def _inic_dic_vars(símismo):

        # Borrar lo que podría haber allí desde antes.
        símismo.variables.clear()

        cuerpo = símismo.dic_doc['cuerpo']

        # Variables internos a VENSIM
        símismo.internos = ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']

        # Una lista de tuples que indican dónde empieza y termina cada variable
        índs_vars = [(n, (n + 1) + next(i for i, l_v in enumerate(cuerpo[n + 1:]) if regex.match(r'\n', l_v)))
                     for n, l in enumerate(cuerpo) if regex.match(r'{}='.format(símismo._regex_var), l)]

        for ubic_var in índs_vars:
            # Extraer la información del variable
            nombre, dic_var = símismo._leer_var(l_texto=cuerpo[ubic_var[0]:ubic_var[1]])

            if nombre not in símismo.variables:
                símismo.variables[nombre] = dic_var

        # Transferir los nombres de los variables parientes a los diccionarios de sus hijos correspondientes
        for var, d_var in símismo.variables.items():
            for pariente in d_var['parientes']:
                try:
                    símismo.variables[pariente]['hijos'].append(var)
                except KeyError:
                    pass

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
            arg_integ = sacar_arg(símismo.variables[niv]['ec'], regex_var=símismo._regex_var,
                                  regex_fun=símismo.regex_fun, i=0)

            # Extraer los variables flujos
            flujos = sacar_variables(arg_integ, rgx=símismo._regex_var, excluir=símismo.internos)

            for flujo in flujos:
                # Para cada nivel en el modelo...

                if flujo not in símismo.flujos:
                    # Agregar el flujo, si no está ya en la lista de flujos.

                    símismo.flujos.append(flujo)

        # Los auxiliares son los variables con parientes que son ni niveles, ni flujos.
        símismo.auxiliares += [x for x, d in símismo.variables.items()
                               if x not in símismo.niveles and x not in símismo.flujos
                               and len(d['parientes'])]

        # Los constantes son los variables que quedan.
        símismo.constantes += [x for x in símismo.variables if x not in símismo.niveles and x not in símismo.flujos
                               and x not in símismo.auxiliares]

    def _leer_var(símismo, l_texto):
        """
        Esta función toma un lista de las líneas de texto que especifican un variable y le extrae su información.

        :param l_texto: Una lista del texto que corresponde a este variable.
        :type l_texto: list

        :return: El numbre del variable, y un diccionario con su información
        :rtype: (str, dict)
        """

        # Identificar el nombre del variable
        d_rgx = regex.match(símismo._regex_var, l_texto[0]).groupdict()
        nombre = d_rgx['var'].strip()
        subs = d_rgx['subs']

        # El diccionario en el cual guardar todo
        dic_var = {'val': None,
                   'unidades': '',
                   'ingreso': None,
                   'dims': (1,),  # Para hacer
                   'líms': (),
                   'subscriptos': subs,
                   'egreso': None,
                   'hijos': [],
                   'parientes': [],
                   'info': ''}

        # Sacar el inicio de la ecuación que puede empezar después del signo de igualdad.
        m = regex.search(r'( *=)(.*)$', l_texto[0][len(nombre):])
        princ_ec = m.groups()[1]

        # El principio de las unidades
        prim_unid = next(n for n, l in enumerate(l_texto) if regex.match(r'\t~\t', l))

        # El principio de los comentarios
        prim_com = next(n + (prim_unid + 1) for n, l in enumerate(l_texto[prim_unid + 1:]) if regex.match(r'\t~\t', l))

        # Combinar las líneas de texto de la ecuación
        try:
            fin_ec = next(n for n, l in enumerate(l_texto) if regex.match(r'.*~~|\n$', l))
            ec = juntar_líns([princ_ec] + l_texto[1:fin_ec + 1])
        except StopIteration:
            ec = juntar_líns([princ_ec] + l_texto[1:prim_unid])

        # Extraer los nombre de los variables parientes
        dic_var['parientes'] = sacar_variables(texto=ec, rgx=símismo._regex_var, excluir=símismo.internos + [nombre])

        # Si no hay ecuación especificada, dar una ecuación vacía.
        if regex.match(r'A FUNCTION OF *\(', ec) is not None:
            dic_var['ec'] = ''
        else:
            dic_var['ec'] = ec

        # Ahora sacamos las unidades y los límites.
        l_unidades = juntar_líns(l_texto[prim_unid:prim_com], cabeza=r'\t~?\t')
        unid_líms = l_unidades.split('[')
        dic_var['unidades'] = unid_líms[0].strip()
        try:
            líms = unid_líms[1].strip(']').split(',')
            dic_var['líms'] = tuple(float(l) if l.strip() != '?' else None for l in líms)
        except IndexError:
            dic_var['líms'] = (None, None)

        # Y ahora agregamos todas las líneas que quedan para la sección de comentarios
        dic_var['info'] = juntar_líns(l_texto[prim_com:], cabeza=r'\t~?\t', cola=r'\t\|')

        # Devolver el variable decifrado.
        return nombre, dic_var

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
                 cortar_líns(dic_var['ec'], lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar_líns(dic_var['unidades'], lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar_líns(dic_var['comentarios'], lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

        return texto

    def calib_ec(símismo, var, ec=None, paráms=None, método=None):

        if símismo.bd is None:
            raise ValueError('')
        if símismo.conex_datos is None:
            símismo.conex_datos = ConexDatos(bd=símismo.bd, modelo=símismo)

        símismo.conex_datos.calib_var(var=var, ec=ec, paráms=paráms, método=método)

    def unidad_tiempo(símismo):
        # Para hacer: algo mucho más elegante
        i_f = next(i for i, f in enumerate(símismo.dic_doc['cola']) if 'INITIAL TIME' in f) + 1
        unid_tiempo = símismo.dic_doc['cola'][i_f].split('\t')[-1].strip()
        return unid_tiempo

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        pass

    def _cambiar_vals_modelo_interno(símismo, valores):
        pass

    def _incrementar(símismo, paso):
        pass

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass


class ModeloVensim(EnvolturaMDS):
    """
    Esta es la envoltura para modelos de tipo VENSIM. Puede leer y controlar (casi) cualquier modelo VENSIM para que
    se pueda emplear en Tinamit.
    Necesitarás la __versión__ DSS de VENSIM para que funcione en Tinamit.
    """

    ext_arch_egr = '.vdf'

    instalado = dll_Vensim is not None

    def __init__(símismo, archivo, nombre='mds'):
        """
        La función de inicialización del modelo. Creamos el vínculo con el DLL de VENSIM y cargamos el modelo
        especificado.

        :param archivo: El archivo del modelo que quieres cargar en formato .vpm.
        :type archivo: str
        """

        # Llamar el DLL de Vensim.
        if dll_Vensim is None:
            raise OSError(_('Esta computadora no tiene el DLL de Vensim DSS.'))
        else:
            símismo.dll = dll = ctypes.WinDLL(dll_Vensim)

        # Inicializar Vensim
        comanda_vensim(func=dll.vensim_command,
                       args=[''],
                       mensaje_error=_('Error iniciando VENSIM.'))

        # Cargar el modelo
        comanda_vensim(func=dll.vensim_command,
                       args='SPECIAL>LOADMODEL|%s' % archivo,
                       mensaje_error=_('Error cargando el modelo de VENSIM.'))

        # Parámetros estéticos de ejecución.
        comanda_vensim(func=dll.vensim_be_quiet, args=[2],
                       mensaje_error=_('Error en la comanda "vensim_be_quiet".'),
                       val_error=-1)

        # El paso para incrementar
        símismo.paso = 1

        # Una lista de variables editables
        símismo.editables = []

        # Inicializar ModeloVENSIM como una EnvolturaMDS.
        super().__init__(archivo=archivo, nombre=nombre)

    def _inic_dic_vars(símismo):
        """
        Inicializamos el diccionario de variables del modelo VENSIM.
        """

        # Sacar las unidades y las dimensiones de los variables, e identificar los variables constantes
        for l in [símismo.editables, símismo.constantes, símismo.niveles, símismo.auxiliares, símismo.flujos,
                  símismo.variables, símismo.dic_info_vars]:
            l.clear()

        editables = símismo.editables
        constantes = símismo.constantes
        niveles = símismo.niveles
        auxiliares = símismo.auxiliares
        flujos = símismo.flujos
        dic_info_vars = símismo.dic_info_vars

        # Primero, verificamos el tamañano de memoria necesario para guardar una lista de los nombres de los variables.

        mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

        # Verificar el tamaño necesario
        tamaño_nec = comanda_vensim(func=símismo.dll.vensim_get_varnames,
                                    args=['*', 0, mem, 0],
                                    mensaje_error=_('Error obteniendo eñ tamaño de los variables VENSIM.'),
                                    val_error=-1, devolver=True
                                    )

        mem = ctypes.create_string_buffer(tamaño_nec)  # Una memoria intermedia con el tamaño apropiado

        # Guardar y decodar los nombres de los variables.
        comanda_vensim(func=símismo.dll.vensim_get_varnames,
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
        comanda_vensim(func=símismo.dll.vensim_get_varnames,
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

            # Actualizar el diccionario de variables.
            # Para cada variable, creamos un diccionario especial, con su valor y unidades. Puede ser un variable
            # de ingreso si es de tipo editable ("Gaming"), y puede ser un variable de egreso si no es un valor
            # constante.
            dic_var = {'val': None if dims == (1,) else np.empty(dims),
                       'unidades': unidades,
                       'ingreso': var in editables,
                       'dims': dims,
                       'subscriptos': nombres_subs,
                       'egreso': var not in constantes,
                       'líms': rango,
                       'info': info}

            # Guadar el diccionario del variable en el diccionario general de variables.
            símismo.variables[var] = dic_var

            # Guardar información adicional
            hijos = símismo.obt_atrib_var(var, 5)
            parientes = símismo.obt_atrib_var(var, 4)
            ec = símismo.obt_atrib_var(var, 3)
            dic_info_vars[var] = {
                'hijos': hijos,
                'parientes': parientes,
                'ec': ec}

        # Actualizar los auxiliares
        for var in símismo.auxiliares.copy():
            for hijo in dic_info_vars[var]['hijos']:
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

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Acciones necesarias para iniciar el modelo VENSIM.

        :param nombre_corrida: El nombre de la corrida del modelo.
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """

        # En Vensim, tenemos que incializar los valores de variables constantes antes de empezar la simulación.
        símismo.cambiar_vals({var: val for var, val in símismo.vals_inic.items()
                              if var in símismo.constantes})

        # Establecer el nombre de la corrida.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                       mensaje_error=_('Error iniciando la corrida VENSIM.'))

        # Establecer el tiempo final.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', tiempo_final + 1),
                       mensaje_error=_('Error estableciendo el tiempo final para VENSIM.'))

        # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
        # a través de la simulación.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="MENU>GAME",
                       mensaje_error=_('Error inicializando el juego VENSIM.'))

        # Es ABSOLUTAMENTE necesario establecer el intervalo del juego aquí. Sino, no reinicializa el paso
        # correctamente entre varias corridas (aún modelos) distintas.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % símismo.paso,
                       mensaje_error=_('Error estableciendo el paso de VENSIM.'))

        # Aplicar los valores iniciales de variables editables
        símismo.cambiar_vals({var: val for var, val in símismo.vals_inic.items()
                              if var not in símismo.constantes})

    def _leer_vals_inic(símismo):

        símismo._leer_vals_de_vensim()

    def _aplicar_cambios_vals_inic(símismo):
        # Vensim tiene su manera personal de inicializar los variables iniciales, en _iniciar_modelo.
        # Así que no haremos nada aquí.
        pass

    def _cambiar_vals_modelo_interno(símismo, valores):
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
                comanda_vensim(func=símismo.dll.vensim_command,
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

                    comanda_vensim(func=símismo.dll.vensim_command,
                                   args='SIMULATE>SETVAL|%s = %f' % (var_s, val_s),
                                   mensaje_error=_('Error cambiando el variable %s.') % var_s)

    def _incrementar(símismo, paso):
        """
        Esta función avanza la simulación VENSIM de ``paso`` pasos.

        :param paso: El número de pasos para tomar.
        :type paso: int

        """

        # Establecer el paso.
        if paso != símismo.paso:
            comanda_vensim(func=símismo.dll.vensim_command,
                           args="GAME>GAMEINTERVAL|%i" % paso,
                           mensaje_error=_('Error estableciendo el paso de VENSIM.'))
            símismo.paso = paso

        # Avanzar el modelo.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="GAME>GAMEON", mensaje_error=_('Error para incrementar VENSIM.'))

    def _pedir_val_var(símismo, var):

        # Una memoria
        mem_inter = ctypes.create_string_buffer(4)

        # Leer el valor del variable
        comanda_vensim(func=símismo.dll.vensim_get_val,
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
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="GAME>GAMEON",
                       mensaje_error=_('Error para terminar la simulación VENSIM.'))

        # Leer el tiempo final
        tiempo_final = símismo._pedir_val_var('FINAL TIME')

        # ¡Por fin! Llamar la comanda para terminar la simulación.
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="GAME>ENDGAME",
                       mensaje_error=_('Error para terminar la simulación VENSIM.'))

        #
        comanda_vensim(func=símismo.dll.vensim_command,
                       args="MENU>VDF2CSV|!|!|||||{}|".format(tiempo_final - 1))
        comanda_vensim(func=símismo.dll.vensim_command, args="MENU>CSV2VDF|!|!")

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
        estatus = comanda_vensim(func=símismo.dll.vensim_check_status,
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
        tmñ = comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                             args=[var, cód_attrib, mem, 0],
                             mensaje_error=mns_error1,
                             val_error=-1,
                             devolver=True)

        mem = ctypes.create_string_buffer(tmñ)
        comanda_vensim(func=símismo.dll.vensim_get_varattrib,
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

        if os.path.splitdrive(corrida)[0] == '':
            archivo = os.path.join(os.path.split(símismo.archivo)[0], corrida)
        else:
            archivo = corrida

        if os.path.splitext(archivo)[1] == '':
            archivo += '.vdf'

        return leer_egr_mds(archivo, var)


def comanda_vensim(func, args, mensaje_error=None, val_error=None, devolver=False):
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
