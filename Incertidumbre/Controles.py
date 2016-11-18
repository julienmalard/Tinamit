import io
import json


class Control(object):

    def __init__(símismo, fuente):

        símismo.fuente = fuente

        símismo.receta = {}

    def guardar(símismo, archivo=None):

        if archivo is None:
            archivo = símismo.fuente

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):

        with open(fuente, 'r', encoding='utf8') as d:
            nuevo_dic = json.load(d)

        símismo.receta.clear()
        símismo.receta.update(nuevo_dic)

        símismo.fuente = fuente