

class CoberturaBF(object):
    def __init__(símismo, ubicación_modelo):
        símismo.vars = símismo.sacar_vars()
        símismo.modelo =
        símismo.vars_entrando = {}
        símismo.vars_saliendo = []

    def sacar_vars(símismo):
        variables = símismo.modelo.

        return variables

    def conectar(símismo, var_mds, var_bf):
        símismo.vars_entrando[var_mds] = var_bf
        símismo.vars_saliendo.append(var_mds)

    def iniciar_modelo(símismo):
        if hasattr(símismo.modelo, 'ejec'):
            símismo.modelo.ejec()
        else:
            raise ConnectionError('El modelo biofísico no tiene un método "ejec()".')

    def incrementar(símismo, paso):
        if hasattr(símismo.modelo, 'incr'):
            símismo.modelo.incr(paso)
        else:
            raise ConnectionError('El modelo biofísico no tiene un método "incr()".')

    def leer_vals(símismo):
        egresos = {}
        for var in símismo.vars_saliendo:
            egresos[var] = símismo.modelo.

        return egresos

    def actualizar_vars(símismo, valores):
        for variables in símismo.vars_entrando.items():
            var_mds = variables[0]
            valor = valores[variables[1]]
            símismo.modelo.
