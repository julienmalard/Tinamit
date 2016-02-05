import os
import json

from MDS import EnvolturaMDS
from Biofísico import EnvolturaBF


class Conectado(object):
    def __init__(símismo, archivo_receta=None):

        símismo.archivo_receta = archivo_receta
        símismo.receta = {'mds': '', 'bf': '', 'conexiones': [], 'ref_tiempo_mds': True, 'conv_unid_tiempo': 1}

        símismo.mds = None
        símismo.vars_mds = []
        símismo.bf = None
        símismo.vars_bf = []
        símismo.conexiones = []
        símismo.ref_tiempo_mds = True

        símismo.cargar()
        símismo.actualizar()

    def actualizar(símismo):
        receta = símismo.receta

        if 'mds' in receta.keys() and len(receta['mds']):
            símismo.estab_mds(receta['mds'])

        if 'bf' in receta.keys() and len(receta['bf']):
            símismo.estab_bf(receta['bf'])

        símismo.actualizar_conexiones()

    def actualizar_conexiones(símismo):
        receta = símismo.receta

        if 'conexiones' in receta.keys():
            for conex in receta['conexiones'].copy():
                try:
                    símismo.conectar(conex)
                except ValueError:
                    símismo.receta['conexiones'].remove(conex)

    def estab_mds(símismo, mds):
        try:
            dic_programas_mds = {'.vpm': 'vensim'}
            ext = os.path.splitext(mds)[1]
            programa_mds = dic_programas_mds[ext]
            símismo.mds = EnvolturaMDS(ubicación_modelo=símismo.receta['mds'], programa_mds=programa_mds)
            símismo.mds.sacar_vars()
            símismo.vars_mds = símismo.mds.vars
            símismo.receta['mds'] = mds
        except (FileNotFoundError, KeyError, AssertionError):
            símismo.mds = None
            símismo.vars_mds = []
            símismo.receta['mds'] = None
            raise ConnectionError

    def estab_bf(símismo, bf):
        try:
            símismo.receta['bf'] = bf
            símismo.bf = EnvolturaBF(ubicación_modelo=símismo.receta['bf'])
            símismo.vars_bf = símismo.bf.vars
        except (FileNotFoundError, AssertionError):
            símismo.bf = None
            símismo.vars_bf = []
            símismo.receta['bf'] = None
            raise ConnectionError

    def conectar(símismo, conexión):
        if conexión not in símismo.receta['conexiones']:
            símismo.receta['conexiones'].append(conexión)

        var_mds = conexión['var_mds']
        var_bf = conexión['var_bf']
        if var_mds not in símismo.vars_mds or var_bf not in símismo.vars_bf:
            raise ValueError

        mds_fuente = conexión['mds_fuente']
        conv = conexión['conv']

        if mds_fuente:
            símismo.bf.conex_entrando[var_bf] = {'var': var_mds, 'conv': conv}
            símismo.mds.vars_saliendo.append(var_mds)
        else:
            símismo.mds.conex_entrando[var_mds] = {'var': var_bf, 'conv': conv}
            símismo.bf.vars_saliendo.append(var_bf)

    def desconectar(símismo, conexión):
        símismo.receta['conexiones'].remove(conexión)

    def simular(símismo, tiempo_final, paso=1):
        símismo.mds.iniciar_modelo(tiempo_final)
        símismo.bf.iniciar_modelo()

        tiempo = 0
        while tiempo < tiempo_final:
            símismo.incrementar(paso)
            de_mds = símismo.mds.leer_vals()
            de_bf = símismo.bf.leer_vals()
            símismo.mds.actualizar_vars(de_bf)
            símismo.bf.actualizar_vars(de_mds)
            tiempo += 1
        símismo.mds.terminar_simul()

    def incrementar(símismo, paso=1):
        if símismo.ref_tiempo_mds:
            símismo.mds.incrementar(paso)
            símismo.bf.incrementar(paso*símismo.receta['conv_unid_tiempo'])
        else:
            símismo.mds.incrementar(paso*símismo.receta['conv_unid_tiempo'])
            símismo.bf.incrementar(paso)

    def cargar(símismo, archivo_receta=None):
        símismo.reinic()
        if archivo_receta is not None:
            símismo.archivo_receta = archivo_receta
            temp = json.load(símismo.archivo_receta)
            símismo.receta['mds'] = temp['mds']
            símismo.receta['bf'] = temp['bf']
            for i in temp['conexiones']:
                símismo.receta['conexiones'].append(i)
            símismo.receta['conv_unid_tiempo'] = temp['conv_unid_tiempo']
            símismo.receta['ref_tiempo_mds'] = temp['ref_tiempo_mds']

    def reinic(símismo):
        símismo.receta['mds'] = ''
        símismo.receta['bf'] = ''
        for i in reversed(símismo.receta['conexiones']):
            símismo.receta['conexiones'].remove(i)
        símismo.receta['conv_unid_tiempo'] = 1
        símismo.receta['ref_tiempo_mds'] = True

        símismo.mds = None
        símismo.vars_mds = {}
        símismo.bf = None
        símismo.vars_bf = []
        símismo.conexiones = []

    def guardar(símismo):
        if símismo.archivo_receta is not None:
            with open(símismo.archivo_receta, 'w') as d:
                json.dump(símismo.receta, d)
