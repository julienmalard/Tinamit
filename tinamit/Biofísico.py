import os
import sys
from importlib import import_module as importar_mod


class EnvolturaBF(object):
    def __init__(símismo, ubicación_modelo):

        # Cargar el modelo biofísico (debe ser un modelo Python)
        directorio_modelo, nombre_modelo = os.path.split(ubicación_modelo)
        sys.path.append(directorio_modelo)

        módulo = importar_mod(os.path.splitext(nombre_modelo)[0])
        assert hasattr(módulo, 'Modelo')
        símismo.modelo = módulo.Modelo()
        assert isinstance(símismo.modelo, ClaseModeloBF)

        # Verificar que el modelo cargado tiene todas las propiedades necesarias
        for a in ['unidades_tiempo', 'ejec', 'incr', 'variables', 'actualizar']:
            assert hasattr(símismo.modelo, a)

        símismo.vars = []
        símismo.unidades = {}
        símismo.conex_entrando = {}
        símismo.vars_saliendo = []

        símismo.modelo.vars_ingr = símismo.conex_entrando
        símismo.modelo.vars_egr = símismo.vars_saliendo

        símismo.sacar_vars()
        símismo.unidades_tiempo = símismo.modelo.unidades_tiempo

    def sacar_vars(símismo):
        variables = list(símismo.modelo.variables.keys())

        símismo.vars = variables
        for var in símismo.modelo.variables:
            símismo.unidades[var] = símismo.modelo.variables[var]['unidades']

    def iniciar_modelo(símismo):
        símismo.modelo.ejec()

    def incrementar(símismo, paso):
        símismo.modelo.incr(paso)

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


class ClaseModeloBF:
    def __init__(símismo):

        # Ejemplo de formato correcto para símismo.variables:
        # {'var1':
        #         {'var': 3,
        #          'unidades': 'kg/ha'},
        #  'var2':
        #         {'var': 2,
        #          'unidades': 'cm/día'}
        # }

        símismo.variables = NotImplemented
        símismo.unidades_tiempo = NotImplemented

        símismo.vars_ingr = {}
        símismo.vars_egr = []

    def ejec(símismo):
        raise NotImplementedError

    def incr(símismo, paso):
        """
        Esta función tiene que poner el diccionario símismo.variables a fecha.
        :param paso:
        :return:
        """
        raise NotImplementedError

    def actualizar(símismo, var, valor):
        símismo.variables[var]['var'] = valor
