import json

from MDS import EnvolturaMDS
from Biofísico import EnvolturaBF


class Conectado(object):
    def __init__(símismo, archivo_mds=None, archivo_biofísico=None, programa_mds='Vensim', receta=None,
                 mds=None, bf=None):
        if receta is not None:
            receta = json.load(receta)
        else:
            receta = {'mds': archivo_mds, 'biofísico': archivo_biofísico, 'programa_mds': programa_mds}

        símismo.dic = receta

        if type(mds) is EnvolturaMDS:
            símismo.mds = mds
        else:
            símismo.mds = EnvolturaMDS(ubicación_modelo=receta['mds'], programa_mds=receta['programa_mds'])

        if type(bf) is EnvolturaBF:
            símismo.bf = bf
        else:
            símismo.bf = EnvolturaBF(ubicación_modelo=receta['biofísico'])

        símismo.vars_mds = símismo.mds.sacar_vars()
        símismo.vars_bf = símismo.mds.sacar_vars()

        try:
            símismo.mds.vars_entrando = receta['mds_entrando']
        except KeyError:
            pass

        try:
            símismo.bf.vars_entrando = receta['bf_entrando']
        except KeyError:
            pass

    def conectar(símismo, originario, var_mds, var_bf):
        if originario.lower() == 'mds':
            símismo.bf.vars_entrando[var_bf] = var_mds
            símismo.mds.vars_saliendo.append(var_mds)
        elif originario.lower() == 'bf':
            símismo.mds.vars_entrando[var_mds] = var_bf
            símismo.bf.vars_saliendo.append(var_bf)
        print('con', símismo.bf.vars_saliendo, símismo.bf.vars_entrando)
        print('con', símismo.mds.vars_saliendo, símismo.mds.vars_entrando)

    def simular(símismo, paso=1, tiempo_final=None):
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
        símismo.mds.incrementar(paso)
        símismo.bf.incrementar(paso)

    def guardar(símismo, archivo):
        símismo.dic['mds_entrando'] = símismo.mds.vars_entrando
        símismo.dic['bf_entrando'] = símismo.bf.vars_entrando

        with open(archivo) as d:
            json.dump(símismo.dic, d)
