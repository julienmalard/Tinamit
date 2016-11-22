import io
import json

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
        símismo.bd.comparar(var_x=var_mod_x, var_y=var_mod_y, escala=escala)

    def estimar(símismo, constante, escala, años=None, lugar=None, cód_lugar=None):
        if constante not in símismo.receta['conexiones']:
            raise ValueError('No hay datos vinculados con este variable (%s).' % constante)

        datos = símismo.bd.estimar(var=constante, escala=escala, años=años, lugar=lugar, cód_lugar=cód_lugar)



    def estimados(símismo):
        return [x for x in símismo.receta['constantes']]

    def calibrados(símismo):
        return [x for x in símismo.receta['conexiones']]

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
