import io
import json
import numpy as np
import math
import re

from scipy.optimize import minimize
from Incertidumbre.Datos import BaseDeDatos
from Incertidumbre.Modelo import ModeloMDS


class Control(object):

    def __init__(símismo, bd, modelo, fuente=None):
        """

        :param bd:
        :type bd: BaseDeDatos

        :param modelo:
        :type modelo: ModeloMDS

        :param fuente:
        :type fuente: str

        """

        símismo.fuente = fuente

        símismo.bd = bd
        símismo.modelo = modelo

        símismo.receta = {'conexiones': {},
                          'ecs': {},
                          'constantes': {}}

    def conectar_vars(símismo, datos, var_bd, var_modelo, transformación):
        símismo.receta['conexiones'][var_modelo] = {'var_bd': var_bd, 'datos': datos}

    def comparar(símismo, var_mod_x, var_mod_y, escala):
        var_bd_x = símismo.receta['conexiones'][var_mod_x]
        var_bd_y = símismo.receta['conexiones'][var_mod_y]

        símismo.bd.comparar(var_x=var_bd_x, var_y=var_bd_y, escala=escala)

    def estimar(símismo, constante, escala, años=None, lugar=None, cód_lugar=None):

        try:
            var_bd = símismo.receta['conexiones'][constante]
        except KeyError:
            raise ValueError('No hay datos vinculados con este variable (%s).' % constante)

        est = símismo.bd.estimar(var=var_bd, escala=escala, años=años, lugar=lugar, cód_lugar=cód_lugar)

        dic = símismo.receta['constantes'][constante] = {}
        dic['distr'] = est['distr']
        dic['máx'] = est['máx']

        símismo.modelo.vars['ec'] = est['máx']

    def importar_ec(símismo, var, ec_desparám):

        try:
            ec_nat = símismo.modelo.naturalizar_ec(ec_desparám)
            ec_mod = símismo.modelo.exportar_ec(ec_desparám)
        except ValueError:
            raise ValueError('')

        dic = símismo.receta['ecs'][var] = {}
        dic['ec_desparám'] = ec_mod
        dic['ec_nativa'] = ec_nat
        dic['paráms'] = None
        dic['líms_paráms'] = None

    def calibrar_ec(símismo, var, escala, años=None, lugar=None, cód_lugar=None, datos=None, ec_desparám=None,
                    límites=None):
        """

        :param var:
        :type var:
        :param escala:
        :type escala:
        :param años:
        :type años:
        :param lugar:
        :type lugar:
        :param cód_lugar:
        :type cód_lugar:
        :param datos:
        :type datos:
        :param ec_desparám:
        :type ec_desparám:
        :param límites:
        :type límites: (float | int, float | int)
        :return:
        :rtype:

        """
        # ec_desparám : "x = y * p[0] + p[1] + y2 * 3 * p[0]"

        if ec_desparám is None:
            try:
                ec_nativa = símismo.receta['ecs'][var]['ec_nativa']
            except KeyError:
                raise ValueError('Hay que especificar una ecuación desparametrizada la primera vez que se calibra'
                                 'la ecuación de un variable.')
        else:
            símismo.importar_ec(var, ec_desparám)
            ec_nativa = símismo.receta['ecs'][var]['ec_nativa']

        if límites is None:
            límites = símismo.receta['ecs'][var]['líms_paráms']
        else:
            símismo.receta['ecs'][var]['líms_paráms'] = límites

        dic_datos = símismo.bd.pedir_datos(l_vars=[var], escala=escala, años=años,
                                           cód_lugar=cód_lugar, lugar=lugar, datos=datos)

        parientes = símismo.modelo.vars[var]['parientes']
        parientes.sort(key=len, reverse=True)

        n_paráms = len(set(re.findall(r'd\[\d\]', ec_desparám)))  # No funacionará si un variable contiene "d[0]"

        ec_con_vars = ec_nativa
        for v in parientes:
            ec_con_vars.replace(v, 'dic_datos[%s]' % v)

        var_dep = dic_datos[var]

        def función(paráms):

            ec = ec_con_vars.format(p=paráms)

            pred = eval(ec)

            return error_cuad(pred=pred, obs=var_dep)

        if límites:
            iniciales = np.array([(x[0] + x[1])/2 for x in límites])
        else:
            iniciales = np.zeros(len(n_paráms))

        calibrados = minimize(fun=función, x0=iniciales, bounds=límites)

        símismo.receta['ecs'][var]['párams'] = calibrados

        símismo.modelo.vars[var]['ec'] = ec_desparám.format(p=calibrados)

    def estimados(símismo):
        return [x for x in símismo.receta['constantes']]

    def calibrados(símismo):
        return [x for x in símismo.receta['conexiones']]

    def escribir_modelo(símismo, archivo):
        símismo.modelo.guardar_mds(archivo=archivo)

    def correr(símismo, nombre_corrida):
        símismo.modelo.correr(nombre_corrida=nombre_corrida)

    def analizar_incert(símismo, nombre_corrida):
        símismo.modelo.correr_incert(nombre_corrida=nombre_corrida)

    def guardar(símismo, archivo=None):

        if archivo is None:
            archivo = símismo.fuente
        else:
            símismo.fuente = archivo

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):

        with open(fuente, 'r', encoding='utf8') as d:
            nuevo_dic = json.load(d)

        símismo.receta.clear()
        símismo.receta.update(nuevo_dic)

        símismo.fuente = fuente


def error_cuad(pred, obs):
    return np.sum(np.square(np.subtract(pred, obs)))
