import json

import pkg_resources

from tinamit.cositas import guardar_json, cargar_json


class Diccionario(object):
    def __init__(símismo):
        símismo.direc = pkg_resources.resource_filename('tinamit.interfaz', 'Trads.json')
        símismo.arch_config = pkg_resources.resource_filename('tinamit.interfaz', 'Config.json')

        símismo.estándar = 'Español'
        símismo.config = None

        símismo.dic = cargar_json(símismo.direc)
        try:
            símismo.config = cargar_json(símismo.arch_config)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        símismo.lenguas = símismo.dic['Lenguas']

        if símismo.config is None or \
                'leng_act' not in símismo.config or símismo.config['leng_act'] not in símismo.lenguas:
            config = {'leng_act': 'Kaqchikel'}
            símismo.config = config
            guardar_json(config, arch=símismo.arch_config)

        símismo.verificar_estados()

        leng_act = símismo.config['leng_act']
        símismo.leng_act = símismo.lenguas[leng_act]
        símismo.trads_act = símismo.leng_act['Trads']
        símismo.izq_a_derech = símismo.leng_act['IzqaDerech']

    def guardar(símismo):
        guardar_json(símismo.dic, arch=símismo.direc)
        guardar_json(símismo.config, arch=símismo.arch_config)

    def verificar_estados(símismo):
        estándar = símismo.lenguas[símismo.estándar]

        for nombre, leng in símismo.lenguas.items():
            llenos = []
            for frase in estándar['Trads']:
                if frase in leng['Trads'].keys() and leng['Trads'][frase] != '':
                    llenos.append(1)
                else:
                    leng['Trads'][frase] = ''
                    llenos.append(0)
            símismo.lenguas[nombre]['Estado'] = sum(llenos) / len(llenos)

        for nombre, leng in símismo.lenguas.items():
            for frase in leng['Trads'].copy():
                if frase not in estándar['Trads'].keys():
                    leng['Trads'].pop(frase)
