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

    def vacíos(símismo):
        """
        Devuelve una lista de los nombres de variables sin ecuaciones.

        :return:
        :rtype: list
        """
        return [x for x in símismo.vars if símismo.vars[x]['ec'] is None]

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


    def guardar_mds(símismo, archivo=None):
        if archivo is None:
            archivo = símismo.archivo_mds
        else:
            símismo.archivo_mds = archivo
        doc = símismo._gen_doc_modelo()
        with io.open(archivo, 'w', encoding='utf8') as d:
            d.write(doc)


class ModeloVENSIMmdl(ModeloMDS):

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
        doc = ''.join([dic_doc['cabeza'], *[símismo.escribir_var(x) for x in símismo.vars], dic_doc['cola']])

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



