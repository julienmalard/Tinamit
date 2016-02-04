import sys
from importlib import import_module as importar_mod
import os


class EnvolturaBF(object):
    def __init__(símismo, ubicación_modelo):
        # Cargar el modelo biofísico (debe ser un modelo Python)
        directorio_modelo, nombre_modelo = os.path.split(ubicación_modelo)
        sys.path.append(directorio_modelo)
        módulo = importar_mod(os.path.splitext(nombre_modelo)[0])
        assert hasattr(módulo, 'Modelo')
        símismo.modelo = módulo.Modelo()

        # Verificar que el modelo cargado tiene todas las propiedades necesarias
        for a in ['ejec', 'incr', 'variables', 'actualizar']:
            assert hasattr(símismo.modelo, a)

        símismo.vars = símismo.sacar_vars()
        símismo.conex_entrando = {}
        símismo.vars_saliendo = []
        símismo.unidades_tiempo = símismo.modelo.unidades_tiempo

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
        for var_propio, conex in símismo.conex_entrando.items():
            var_entr = conex['var']
            conv = conex['conv']
            valor = valores[var_entr] * conv
            símismo.modelo.actualizar(var_propio, valor)
