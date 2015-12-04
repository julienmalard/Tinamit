

class Conectado(object):
    def __init__(símismo, mds, bf):
        símismo.mds = mds
        símismo.bf = bf
        símismo.vars_mds = símismo.mds.sacar_vars()
        símismo.vars_bf = símismo.mds.sacar_vars()

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
