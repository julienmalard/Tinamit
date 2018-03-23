import io
import json

import pkg_resources


class Diccionario(object):
    def __init__(símismo):
        símismo.direc = pkg_resources.resource_filename('tinamit.Interfaz', 'Trads.json')
        símismo.arch_config = pkg_resources.resource_filename('tinamit.Interfaz', 'Config.json')

        símismo.estándar = 'Español'
        símismo.config = None

        with open(símismo.direc, encoding='utf8') as d:
            símismo.dic = json.load(d)
        try:
            with open(símismo.arch_config, encoding='utf8') as d:
                símismo.config = json.load(d)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        símismo.lenguas = símismo.dic['Lenguas']

        if símismo.config is None or \
                'leng_act' not in símismo.config or símismo.config['leng_act'] not in símismo.lenguas:
            config = {'leng_act': símismo.estándar}
            símismo.config = config
            with open(símismo.arch_config, encoding='utf8', mode='w') as d:
                json.dump(config, d, ensure_ascii=False, sort_keys=True, indent=2)

        símismo.verificar_estados()

        leng_act = símismo.config['leng_act']
        símismo.leng_act = símismo.lenguas[leng_act]
        símismo.trads_act = símismo.leng_act['Trads']
        símismo.izq_a_derech = símismo.leng_act['IzqaDerech']

    def guardar(símismo):
        with io.open(símismo.direc, 'w', encoding='utf8') as d:
            json.dump(símismo.dic, d, ensure_ascii=False, sort_keys=True, indent=2)
        with io.open(símismo.arch_config, 'w', encoding='utf8') as d:
            json.dump(símismo.config, d, ensure_ascii=False, sort_keys=True, indent=2)

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
            símismo.lenguas[nombre]['Estado'] = sum(llenos)/len(llenos)

        for nombre, leng in símismo.lenguas.items():
            for frase in leng['Trads'].copy():
                if frase not in estándar['Trads'].keys():
                    leng['Trads'].pop(frase)
