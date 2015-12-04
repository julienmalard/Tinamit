import sys
import importlib

class CoberturaBF(object):
    def __init__(símismo, ubicación_modelo):
        # Cargar el modelo biofísico (debe ser un modelo Python)
        directorio_modelo, nombre_modelo = ('a','b')
        sys.path.append(directorio_modelo)
        módulo = importlib.import_module('nombre_modelo')
        símismo.modelo = módulo.Modelo()

        símismo.vars = símismo.sacar_vars()
        símismo.vars_entrando = {}
        símismo.vars_saliendo = []

    def sacar_vars(símismo):
        variables = list(símismo.modelo.variables.keys())

        return variables

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
            egresos[var] = símismo.modelo.variables[var]['var']

        return egresos

    def actualizar_vars(símismo, valores):
        for variable in símismo.vars_entrando.items():
            var = variable[0]
            valor = valores[variable[1]]
            símismo.modelo.actualizar(var, valor)
