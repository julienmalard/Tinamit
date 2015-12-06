import json

from MDS import EnvolturaMDS
from Biofísico import EnvolturaBF


class Conectado(object):
    def __init__(símismo, mds, biofísico, programa_mds='Vensim', archivo=None):
        if archivo is not None:
            dic = json.load(archivo)
        else:
            dic = {'mds': mds, 'biofísico': biofísico, 'programa_mds': programa_mds}

        símismo.dic = dic

        símismo.mds = EnvolturaMDS(ubicación_modelo=dic['mds'], programa_mds=dic['programa_mds'])
        símismo.bf = EnvolturaBF(ubicación_modelo=dic['biofísico'])
        símismo.vars_mds = símismo.mds.sacar_vars()
        símismo.vars_bf = símismo.mds.sacar_vars()

        try:
            símismo.mds.vars_entrando = dic['mds_entrando']
        except KeyError:
            pass

        try:
            símismo.bf.vars_entrando = dic['bf_entrando']
        except KeyError:
            pass

    def conectar(símismo, originario, var_mds, var_bf):
        if originario.lower() == 'mds':
            símismo.bf.vars_entrando[var_bf] = var_mds
            símismo.mds.vars_saliendo.append(var_mds)
        elif originario.lower() == 'bf':
            símismo.mds.vars_entrando[var_mds] = var_bf
            símismo.bf.vars_saliendo.append(var_bf)

    def simular(símismo, paso=1, tiempo_final=None):
        símismo.mds.iniciar_modelo(tiempo_final)
        símismo.bf.iniciar_modelo()

        terminó = False
        while not terminó:
            terminó = símismo.incrementar(paso)
            de_mds = símismo.mds.leer_vals()
            de_bf = símismo.bf.leer_vals()
            símismo.mds.actualizar_vars(de_bf)
            símismo.bf.actualizar_vars(de_mds)
        símismo.mds.terminar_simul()

    def incrementar(símismo, paso=1):
        terminó = (símismo.mds.incrementar(paso) != 1)
        símismo.bf.incrementar(paso)
        return terminó

    def guardar(símismo, archivo):
        símismo.dic['mds_entrando'] = símismo.mds.vars_entrando
        símismo.dic['bf_entrando'] = símismo.bf.vars_entrando

        with open(archivo) as d:
            json.dump(símismo.dic, d)
