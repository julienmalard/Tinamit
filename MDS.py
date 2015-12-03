import ctypes


class CoberturaMDS(object):
    def __init__(símismo, programa_mds, ubicación_modelo):
        símismo.programa = programa_mds.lower()
        símismo.dll = símismo.cargar_mds(símismo.programa, ubicación_modelo)
        símismo.vars = símismo.sacar_vars()
        símismo.vars_entrando = {}
        símismo.vars_saliendo = []

    def sacar_vars(símismo):
        variables = []
        if símismo.programa == 'vensim':

            funcionó = símismo.dll.vensim_get_varnames('*', 0, buff, 10000)
            if funcionó != -1:
                variables = leer(buff)

        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para iniciar_modelo.')

        return variables

    def conectar(símismo, var_mds, var_bf):
        símismo.vars_entrando[var_mds] = var_bf
        símismo.vars_saliendo.append(var_mds)

    def iniciar_modelo(símismo, tiempo_final):
        if tiempo_final is not None:
            if símismo.programa == 'vensim':
                for v in [b'TIEMPO FINAL', b'FINAL TIME']:
                    símismo.dll.vensim_command(b'SIMULATE>SETVAL|%s = %s' %
                                               (v, str(tiempo_final).encode())
                                               )

            funcionó = (símismo.dll.vensim_start_simulation(1, 0, 1) == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para iniciar_modelo.')

    def incrementar(símismo, paso):
        if símismo.programa == 'vensim':
            funcionó = (símismo.dll.vensim_continute_simulation(paso) == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para incrementar.')

    def leer_vals(símismo):
        funcionó = False
        egresos = {}
        for var in símismo.vars_saliendo:
            if símismo.programa == 'vensim':
                buff =
                funcionó = (símismo.dll.vensim_get_val(var.encode(), buff) == 1)
                # Para hacer: verificar el uso de val y de funcionó aquí
                val = leer(buff)
                egresos[var] = val
            else:
                raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para leer_vals.')

        return egresos

    def actualizar_vars(símismo, valores):
        if símismo.programa == 'vensim':
            funcionó = False
            for variables in símismo.vars_entrando.items():
                var_mds = variables[0]
                valor = valores[variables[1]]
                funcionó = (símismo.dll.vensim_command(b'SIMULATE>SETVAL|%s = %s' %
                                                       (var_mds.encode, valor.encode)) == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para actualizar_var.')

    def terminar_simul(símismo):
        if símismo.programa == 'vensim':
            funcionó = (símismo.dll.vensim_finish_simul() == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda Vensim para terminar_simul.')

    @staticmethod
    def cargar_mds(programa_mds, ubicación_modelo):
        if programa_mds == 'vensim':
            dll = ctypes.cdll.LoadLibrary('C:\\Windows\\System32\\vendll32.dll')
            cargado = dll.vensim_command(b'SPECIAL>LOADMODEL|%s' % ubicación_modelo.encode()) == 1
        else:
            raise NotImplementedError('No se ha escrito una interfaz para este tipo de programa MDS. '
                                      'Quejarse al programador.')

        if cargado:
            return dll
        else:
            raise FileNotFoundError('No se pudo cargar el modelo ')