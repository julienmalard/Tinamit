import ctypes
import io
import os
import re


class ModeloMDS(object):
    """


    :type tipo: str

    :type regex_var: str
    :type regex_fun: str
    :type regex_op: str
    :type lím_línea: int
    """

    tipo = NotImplemented

    regex_var = NotImplemented
    regex_fun = NotImplemented
    regex_op = NotImplemented
    regex_núm = r'\d+(\.[\d]*)?'

    lím_línea = NotImplemented

    def __init__(símismo, archivo_mds):
        """

        :param archivo_mds:
        :type archivo_mds: str
        """

        símismo.archivo_mds = archivo_mds

        # Formato {var1: {ecuación: '', unidades: '', comentarios: ''}
        símismo.vars = {}

        símismo.internos = []
        símismo.auxiliares = []
        símismo.flujos = []
        símismo.niveles = []
        símismo.constantes = []

        # Para guardar en memoria información necesaria para reescribir el documento del modelo MDS
        símismo.dic_doc = {}

        símismo.leer_modelo()

    def vacíos(símismo):
        """

        :return:
        :rtype: list
        """
        return [x for x in símismo.vars if símismo.vars[x]['ecuación'] is None]

    def detalles_var(símismo, var):
        """

        :param var:
        :type var: str

        :return:
        :rtype: dict
        """

        return símismo.vars[var]

    def leer_modelo(símismo):
        with open(símismo.archivo_mds, 'r', encoding='utf8') as d:
            doc = d.readlines()

        símismo._leer_doc_modelo(doc)

    def naturalizar_ec(símismo, ec):

        mensaje_error = 'La ecuación siguiente no se puede convertir a una ecuación Tinamit: \n%s' % ec

        regex_núm = símismo.regex_núm
        regex_fun = símismo.regex_fun
        regex_op = símismo.regex_op
        regex_var = símismo.regex_var

        ec_nat = ''

        l_regex = [regex_núm, regex_fun, regex_op, regex_var]

        while len(ec):
            for n, regex in enumerate(l_regex):
                res = re.match(regex, ec)
                if res:
                    texto = res.group(0)
                    ec = ec[res.span()[1]:]

                    if regex == regex_núm:
                        ec_nat += texto
                    elif regex == regex_op:
                        try:
                            ec_nat += dic_ops_inv[símismo.tipo][texto]
                        except KeyError:
                            raise ValueError(mensaje_error)
                    elif regex == regex_fun:
                        try:
                            ec_nat += dic_funs_inv[símismo.tipo][texto]
                        except KeyError:
                            raise ValueError(mensaje_error)
                    elif regex == regex_var:
                        ec_nat += texto

                    break

                else:
                    if n == len(l_regex):
                        raise ValueError(mensaje_error)

    def exportar_ec(símismo, ec):

        mensaje_error = 'La ecuación siguiente no se puede exportar: \n%s' % ec

        regex_núm = símismo.regex_núm
        regex_fun = símismo.regex_fun
        regex_op = símismo.regex_op
        regex_var = símismo.regex_var

        ex_exp = ''

        l_regex = [regex_núm, regex_fun, regex_op, regex_var]

        while len(ec):
            for n, regex in enumerate(l_regex):
                res = re.match(regex, ec)
                if res:
                    texto = res.group(0)
                    ec = ec[res.span()[1]:]

                    if regex == regex_núm:
                        ex_exp += texto
                    elif regex == regex_op:
                        try:
                            ex_exp += dic_ops[texto]['VENSIM']
                        except KeyError:
                            raise ValueError(mensaje_error)
                    elif regex == regex_fun:
                        try:
                            ex_exp += dic_funs[texto]['VENSIM']
                        except KeyError:
                            raise ValueError(mensaje_error)
                    elif regex == regex_var:
                        ex_exp += texto

                    break

                else:
                    if n == len(l_regex):
                        raise ValueError(mensaje_error)

    def parientes(símismo, var):
        return símismo.vars[var]['parientes']

    def hijos(símismo, var):
        return símismo.vars[var]['hijos']

    def correr(símismo, nombre_corrida):
        raise NotImplementedError

    def correr_incert(símismo, nombre_corrida):
        raise NotImplementedError

    def _gen_doc_modelo(símismo):
        raise NotImplementedError

    def _leer_doc_modelo(símismo, doc):
        raise NotImplementedError

    def _leer_var(símismo, texto):
        raise NotImplementedError

    def guardar_mds(símismo, archivo=None):
        if archivo is None:
            archivo = símismo.archivo_mds
        else:
            símismo.archivo_mds = archivo
        doc = símismo._gen_doc_modelo()
        with io.open(archivo, 'w', encoding='utf8') as d:
            d.write(doc)


class ModeloVENSIMmdl(ModeloMDS):

    tipo = 'VENSIM'
    lím_línea = 80

    # l = ['abd = 1', 'abc d = 1', 'abc_d = 1', '"ab3 *" = 1', '"-1\"f" = 1', 'a', 'é = A FUNCTION OF ()',
    #      'வணக்கம்', 'a3b', '"5a"']
    regex_var = r'[^\W\d][\w\d_ ்्੍્]+|\".*?(?<!\\)\"'
    # for i in l:
    #     print(re.findall(regex_var, i))

    regex_fun = r'(?<= *)[^\W\d]+[\w\d_ ்]*\('
    regex_op = r'(?<= *)[\^\*\-\+/\(\)]'

    def __init__(símismo, archivo_mds):
        símismo.vpm = None
        super().__init__(archivo_mds=archivo_mds)

    def correr(símismo, nombre_corrida):
        if símismo.vpm is None:
            símismo.publicar_vpm()

        símismo.vpm.correr(nombre_corrida)

    def correr_incert(símismo, nombre_corrida):
        if símismo.vpm is None:
            símismo.publicar_vpm()

        símismo.vpm.correr_incert(nombre_corrida)

    def _leer_doc_modelo(símismo, d):
        """
        Esta función extrae la información del modelo DS.

        :param d: El archivo ya abierto, en forma de lista.
        :type d: list

        """

        # Borrar lo que podría haber allí desde antes.
        símismo.vars.clear()

        l_texto_var = []  # Una lista para combinar información en línea múltiples

        # La primera línea del documento, con {UTF-8}
        símismo.dic_doc['cabeza'] = d[0]

        # Inicializar la línea y su número
        n = 1
        l = d[n]

        while re.match(r'\*+$', l) is None:
            # Pasar a través de todas las líneas en la sección de variables del documento

            while re.match(r'(\t~\t)?\t\|', l) is None:
                # Pasar a través de cada variable

                if l != '\n':
                    # Si la línea no es vacía...

                    # Agregar la línea a la lista de líneas que pertenecen a este variable
                    l_texto_var.append(l)
                n += 1
                l = d[n]

            # Extraer la información del variable
            nombre, dic_var = símismo._leer_var(l_texto=l_texto_var)

            símismo.vars[nombre] = dic_var
            l_texto_var = []

            # Pasa a la próxima línea
            n += 1
            l = d[n]

        # Guardar todo el resto del archivo (que no contiene información de ecuaciones de variables)
        símismo.dic_doc['cola'] = d[n:]

        # Transferir los nombres de los variables parientes a los diccionarios de sus hijos correspondientes
        for var, d_var in símismo.vars.items():
            for pariente in d_var['parientes']:
                símismo.vars[pariente]['hijos'].append(var)

        # Borrar lo que había antes en las listas siguientes:
        símismo.flujos.clear()
        símismo.auxiliares.clear()
        símismo.constantes.clear()
        símismo.niveles.clear()

        # Guardar una lista de los nombres de variables de tipo "nivel"
        símismo.niveles += [x for x in símismo.vars if re.match(r'INTEG *\(', símismo.vars[x]['ec']) is not None]

        # Los flujos, por definición, son los parientes de los niveles.
        for niv in símismo.niveles:

            for flujo in símismo.vars[niv]['parientes']:
                # Para cada nivel en el modelo...

                if flujo not in símismo.flujos:
                    # Evitar agregar un flujo dos veces
                    símismo.flujos.append(flujo)

        # Los auxiliares son los variables con parientes que son ni niveles, ni flujos.
        símismo.auxiliares += [x for x, d in símismo.vars.items()
                               if x not in símismo.niveles and x not in símismo.flujos
                               and len(d['parientes'])]

        # Los constantes son los variables que quedan.
        símismo.constantes += [x for x in símismo.vars if x not in símismo.niveles and x not in símismo.flujos
                               and x not in símismo.auxiliares]

    def _gen_doc_modelo(símismo):
        dic_doc = símismo.dic_doc
        doc = ''.join([dic_doc['cabeza'], *[símismo.escribir_var(x) for x in símismo.vars], dic_doc['fin']])

        return doc

    def _leer_var(símismo, l_texto):
        """
        Esta función toma un lista de las líneas de texto que especifican un variable y le extrae su información.

        :param l_texto: Una lista del texto que corresponde a este variable.
        :type l_texto: list

        :return: El numbre del variable, y un diccionario con su información
        :rtype: (str, dict)
        """

        # Identificar el nombre del variable
        nombre = sacar_variables(l_texto[0], regex=símismo.regex_var, n=1)[0]

        # El diccionario en el cual guardar todo
        dic_var = {'nombre': nombre, 'unidades': '', 'comentarios': '', 'hijos': [], 'parientes': [], 'ec': ''}

        # Empezar una lista para todas las líneas del documento que corresponden ala ecuación de este variable
        l_tx_ec = []

        # Sacar el inicio de la ecuación que puede empezar después del signo de igualdad.
        m = re.match(r' +=.*$', l_texto[0][len(nombre) :])
        if m is not None:
            l_tx_ec.append(m.groups()[0])

        # Seguir con la segunda línea
        n = 1
        l = l_texto[n]

        while re.match(r'\t~\t', l) is None:
            # Mientras no llegamos a la marca de fin de ecuación, seguir con la lectura.

            # Quitar el tabulador de la izquierda de la línea
            l_tx_ec.append(l.lstrip('\t').rstrip('\n'))
            n += 1
            l = l_texto[n]

        # Combinar las líneas de texto de la ecuación
        ec = juntar(l_tx_ec)

        # Extraer los nombre de los variables parientes
        dic_var['parientes'] = sacar_variables(texto=ec, regex=símismo.regex_var)

        # Si no hay ecuación especificada, dar una ecuación vacía.
        if re.match(r'A FUNCTION OF *\(', ec) is not None:
            dic_var['ec'] = ''
        else:
            dic_var['ec'] = ec

        # Ahora sacamos las unidades.
        l = l.replace('\t~\t', '')  # Quitar el marcador de especificación de unidades
        l_tx_unid = []

        while re.match(r'\t~\t', l) is None:
            # Mientras no llegamos al marcador de empezamiento de comentarios...

            # Agregar la línea a la lista de lineas de unidades.
            l_tx_unid.append(l.lstrip('\t'))

            # ...y seguir con la próxima línea.
            n += 1
            l = l_texto[n]

        # Guardar las unidades
        dic_var['unidades'] = juntar(l_tx_unid)

        # Agregar todas las líneas que quedan para la sección de comentarios
        l_tx_temp = [l.lstrip('\t~\t')] + l_texto[n+1:]

        dic_var['comentarios'] = juntar(l_tx_temp)

        return nombre, dic_var

    def publicar_vpm(símismo):

        try:
            dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
        except OSError:
            raise OSError('Esta computadora no cuenta con el DLL de VENSIM DSS.')

        comanda_vensim(dll.vensim_command, 'SPECIAL>LOADMODEL|%s' % símismo.archivo_mds)
        símismo.guardar_mds()

        archivo_vpm = os.path.join(os.path.split(símismo.archivo_mds)[0], 'Tinamit.vpm')

        archivo_frm = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'VENSIM.frm')

        comanda_vensim(dll.vensim_command, ('FILE>PUBLISH|%s' % archivo_frm))

        símismo.vpm = ModeloVENSIMvpm(archivo_mds=archivo_vpm)

    def escribir_var(símismo, var):
        """

        :param var:
        :type var: str

        :return:
        :rtype: str
        """

        dic_var = símismo.vars[var]

        if dic_var['ec'] == '':
            dic_var['ec'] = 'A FUNCTION OF (%s)' % ', '.join(dic_var['parientes'])

        texto = [var + '=\n',
                 cortar(dic_var['ec'], símismo.lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar(dic_var['unidades'], símismo.lím_línea, lín_1='\t', lín_otras='\t\t'),
                 cortar(dic_var['comentarios'], símismo.lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

        return texto


class ModeloVENSIMvpm(ModeloMDS):

    def __init__(símismo, archivo_mds):
        super().__init__(archivo_mds=archivo_mds)

        try:
            símismo.dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        except OSError:
            raise OSError('Esta computadora no cuenta con el DLL de VENSIM DSS.')

        comanda_vensim(símismo.dll.vensim_command, 'SPECIAL>LOADMODEL|%s' % archivo_mds)

    def correr(símismo, nombre_corrida):
        comanda_vensim(símismo.dll.vensim_command, 'SIMULATE>RUNNAME|%s' % nombre_corrida)
        comanda_vensim(símismo.dll.vensim_command, 'MENU>RUN')

    def correr_incert(símismo, nombre_corrida):
        raise NotImplementedError

    def _gen_doc_modelo(símismo):
        raise NotImplementedError

    def _leer_doc_modelo(símismo, doc):

        tamaño_mem = 10

        for var in símismo.vars:

            mem_inter = ctypes.create_string_buffer(tamaño_mem)
            comanda_vensim(símismo.dll.vensim_get_varattrib, [var, 14, mem_inter, tamaño_mem])
            tipo_var = mem_inter.raw.decode()

            if tipo_var == 'Auxiliary':
                símismo.auxiliares.append(var)
            elif tipo_var == 'Constant':
                símismo.constantes.append(var)
            elif tipo_var == 'Level':
                símismo.niveles.append(var)
            else:
                pass

        for var in símismo.constantes:
            for hijo in símismo.vars[var]['hijos']:
                if hijo in símismo.niveles:
                    símismo.flujos.append(var)
                    símismo.constantes.remove(var)

    def _leer_var(símismo, texto):
        raise NotImplementedError


def comanda_vensim(función, args):

    if type(args) is not list:
        args = [args]

    for n, a in enumerate(args):
        if type(a) is str:
            args[n] = a.encode()

    resultado = función(*args)

    if resultado != 1:
        raise OSError('Error con la comanda')


def mds(archivo_mds):
    """
    Esta función crea una instancia de modelo de DS de la subclase apropiada para el tipo de modelo dado.

    :param archivo_mds: La ubicación del archivo de MDS.
    :type archivo_mds: str

    :return: El objeto de MDS apropiado.
    :rtype: ModeloMDS

    """
    ext = os.path.splitext(archivo_mds)[1]

    if ext == '.mdl':
        modelo = ModeloVENSIMmdl(archivo_mds=archivo_mds)
    elif ext == '.vpm':
        modelo = ModeloVENSIMvpm(archivo_mds=archivo_mds)
    else:
        raise NotImplementedError('No se han implementado modelos de tipo "{}"'.format(ext))

    return modelo


def cortar(texto, máx_car, lín_1=None, lín_otras=None):

    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            l = texto
        else:
            dif = máx_car - texto

            l = re.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(l)
        texto = texto[len(l):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, l in enumerate(lista[1:]):
            lista[n] = lín_otras + l

    return lista


def juntar(l):
    """
    Esta función junta una lista de líneas de texto en una sola línea de texto.

    :param l: La lexta de líneas de texto.
    :type l: list[str]

    :return: El texto combinado.
    :rtype: str

    """

    # Quitar tabulaciones y símbolos de final de línea
    l = [x.lstrip('\t').rstrip('\n').rstrip('\\') for x in l]

    # Combinar las líneas y quitar espacios al principio y al final
    texto = ''.join(l).strip(' ')

    # Devolver el texto combinado.
    return texto


def sacar_variables(texto, regex, n=None):
    """
    Esat ecuación saca los variables de un texto.

    :param texto: El texto de cual extraer los nombres de los variables.
    :type texto: str

    :param regex: La expersión regex correspondiendo al formato de los variables.
    :type regex: str

    :param n: El número máximo de variables que sacar.
    :type n: int

    :return: Una lista de los nombres de los variables.
    :rtype: list

    """

    # Buscar los nombres
    b = re.findall(regex, texto)

    if n is None:
        return b
    else:
        return b[:n]


dic_funs = {
    'min(': {'VENSIM': 'MIN('},
    'max(': {'VENSIM': 'MAX('},
    'abs(': {'VENSIM': 'ABS('},
    'math.exp(': {'VENSIM': 'EXP('},
    'int(': {'VENSIM': 'INTEGER('},
    'math.log(': {'VENSIM': 'LN('},
    'math.sin(': {'VENSIM': 'SIN('},
    'math.cos(': {'VENSIM': 'COS('},
    'math.tan(': {'VENSIM': 'TAN('},
    'math.asin(': {'VENSIM': 'ARCSIN('},
    'math.acos(': {'VENSIM': 'ARCCOS('},
    'math.atan(': {'VENSIM': 'ARCTAN('},
    'math.log10(': {'VENSIM': 'LOG('},

}


dic_ops = {
    '+': {'VENSIM': '+'},
    '-': {'VENSIM': '-'},
    '*': {'VENSIM': '*'},
    '/': {'VENSIM': '/'}
}

dic_funs_inv = {}
for fun, d_fun in dic_funs.items():
    for tipo, v in d_fun.items():
        if tipo not in dic_funs_inv:
            dic_funs_inv[tipo] = {}
        dic_funs_inv[tipo][v] = fun

dic_ops_inv = {}
for op, d_op in dic_ops.items():
    for tipo, v in d_op.items():
        if tipo not in dic_ops_inv:
            dic_ops_inv[tipo] = {}
        dic_ops_inv[tipo][v] = op
