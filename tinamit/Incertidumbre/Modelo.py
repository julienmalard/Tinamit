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

        # Para guardar en memoria información necesaria para reescribir el documento del modelo EnvolturaMDS
        símismo.dic_doc = {}

        símismo.leer_modelo()

    def vacíos(símismo):
        """
        Devuelve una lista de los nombres de variables sin ecuaciones.

        :return:
        :rtype: list
        """
        return [x for x in símismo.vars if símismo.vars[x]['ec'] is None]

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
    regex_var = r'[^\W\d][\w\d_ ்्੍્]*(?![\w\d_ ்्੍્ ]*\()|\".*?(?<!\\)\"'
    # for i in l:
    #     print(re.findall(_regex_var, i))

    regex_fun = r'([^\W\d]+[\w\d_ ்्੍્]*)(?= *\()'
    regex_op = r'(?<= *)[\^\*\-\+/\(\)]'

    def __init__(símismo, archivo_mds):
        """

        :param archivo_mds:
        :type archivo_mds: str
        """
        super().__init__(archivo_mds=archivo_mds)

        símismo.vpm = None

    def correr(símismo, nombre_corrida):
        if símismo.vpm is None:
            símismo.publicar_vpm()

        símismo.vpm.correr(nombre_corrida)

    def correr_incert(símismo, nombre_corrida):
        if símismo.vpm is None:
            símismo.publicar_vpm()

        símismo.vpm.correr_incert(nombre_corrida)

    def _gen_doc_modelo(símismo):
        dic_doc = símismo.dic_doc
        doc = ''.join([dic_doc['cabeza'], *[símismo.escribir_var(x) for x in símismo.vars], dic_doc['fin']])

        return doc

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


class ModeloVENSIMvpm(ModeloMDS):

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



    def _leer_var(símismo, texto):
        raise NotImplementedError


