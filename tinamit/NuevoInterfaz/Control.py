from warnings import warn as avisar
from tinamit.Conectado import Conectado
from Dibba import cargar_json, guardar_json, guardar_doc, ControlApli


class ClaseControlTinamït(ControlApli):
    def __init__(símismo, archivo=None):
        símismo.receta = {
            'mds': '',
            'bf': '',
            'conexiones': [],
            'paso': 1,
            'tiempo final': None,
            'nombre corrida': 'Corrida Tinamït',
            'simulado': 0
        }

        símismo.modelo = Conectado()
        if archivo is not None:
            símismo.cargar_archivo(archivo)

        super().__init__()

    def estab_mds(símismo, archivo_mds):
        símismo.modelo.estab_mds(archivo_mds=archivo_mds)
        símismo.receta['mds'] = archivo_mds

    def estab_bf(símismo, archivo_bf):
        símismo.modelo.estab_bf(archivo_bf=archivo_bf)
        símismo.receta['bf'] = archivo_bf

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv):
        símismo.modelo.conectar(var_mds=var_mds, var_bf=var_bf, mds_fuente=mds_fuente, conv=conv)
        dic_conex = {'var_mds': var_mds, 'var_bf':var_bf, 'mds_fuente': mds_fuente, 'conv': conv}
        símismo.receta['conexiones'].append(dic_conex)

    def desconectar(símismo, var_mds):
        símismo.modelo.desconectar(var_mds=var_mds)
        i_d_conex = next(i for i, d in enumerate(símismo.receta['conexiones']) if d['var_mds'] == var_mds)
        símismo.receta['conexiones'].pop(i_d_conex)

    def simular(símismo, tiempo_final, paso, nombre_corrida):
        símismo.modelo.simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida)
        símismo.receta['paso'] = paso
        símismo.receta['tiempo final'] = tiempo_final
        símismo.receta['nombre corrida'] = nombre_corrida
        símismo.receta['simulado'] = 1

    def cargar_archivo(símismo, archivo):
        receta = cargar_json(archivo)

        for ll, v in receta:
            if ll not in símismo.receta:
                avisar(
                    'La llave "{}" del archivo \n\t"{}"\n...no corresponde con el formato Tinamït. De pronto tienes'
                    'un archivo incompatible or corrumpido, pero intentaremos seguir de todo modo.'
                    .format(ll, archivo))
            else:
                símismo.receta[ll] = v

        rec = símismo.receta  # type: dict

        if len(rec['mds']):
            try:
                símismo.estab_mds(archivo_mds=rec['mds'])
            except ValueError:
                pass
        if len(rec['bf']):
            try:
                símismo.estab_bf(archivo_bf=rec['mds'])
            except ValueError:
                pass
        if símismo.modelo.mds and símismo.modelo.bf:
            for conex in rec['conexiones']:  # type: dict
                try:
                    símismo.conectar(var_mds=conex['var_mds'], var_bf=conex['var_bf'],
                                     mds_fuente=conex['mds_fuente'], conv=rec['conv'])
                except ValueError:
                    pass

    def guardar_archivo(símismo, archivo):
        guardar_json(archivo, símismo.receta)

    def guardar_escripto(símismo, archivo):

        escripto = [
            'from tinamit.Conectado import Conectado',
            'Modelo = Conectado()'
        ]

        rec = símismo.receta  # type: dict
        if len(rec['mds']):
            escripto.append('Modelo.estab_mds(archivo_mds={})'.format(rec['mds']))
        if len(rec['bf']):
            escripto.append('Modelo.estab_bf(archivo_bf={})'.format(rec['bf']))
        for con in rec['conexiones']:  # type: dict
            escripto.append('Modelo.conectar(var_mds={}, var_bf={}, mds_fuente={}, conv={})'
                            .format(con['var_mds'], con['var_bf'], con['mds_fuente'], con['conv']))
        if rec['simulado']:
            escripto.append('Modelo.simular(tiempo_final={}, paso={}, nombre_corrida={})'
                            .format(rec['tiempo_final'], rec['paso'], rec['nombre_corrida']))

        guardar_doc(escripto, archivo, ext='.py')


Control = ClaseControlTinamït()
