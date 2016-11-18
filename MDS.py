import ctypes
import struct

from warnings import warn as avisar


class EnvolturaMDS(object):
    def __init__(símismo, programa_mds, ubicación_modelo):
        símismo.programa = programa_mds.lower()
        símismo.dll = símismo.cargar_mds(símismo.programa, ubicación_modelo)
        símismo.vars_editables = []
        símismo.vars = []
        símismo.unidades = {}
        símismo.conex_entrando = {}
        símismo.vars_saliendo = []

        símismo.sacar_vars()

        símismo.unidades_tiempo = símismo.sacar_unidades_tiempo()

    @staticmethod
    def cargar_mds(programa, ubic_modelo):
        if programa == 'vensim':
            dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
            resultado = dll.vensim_command(('SPECIAL>LOADMODEL|%s' % ubic_modelo).encode())
            dll.vensim_be_quiet(2)

            todobien = (resultado == 1 and int(dll.vensim_check_status()) == 0)
        else:
            raise NotImplementedError('No se ha escrito una interfaz para este tipo de programa MDS. '
                                      'Quejarse al programador.')

        if todobien:
            return dll
        else:
            raise FileNotFoundError('No se pudo cargar el modelo ')

    def sacar_vars(símismo):
        if símismo.programa == 'vensim':
            tamaño_mem = 1000
            mem_inter = ctypes.create_string_buffer(tamaño_mem)
            resultado = símismo.dll.vensim_get_varnames('*', 0, mem_inter, tamaño_mem)
            if resultado <= 0:
                raise OSError('Error con VENSIM.')

            while resultado > tamaño_mem:
                tamaño_mem += 1000
                mem_inter = ctypes.create_string_buffer(tamaño_mem)
                resultado = símismo.dll.vensim_get_varnames(b'*', 0, mem_inter, tamaño_mem)
                if resultado < 0:
                    raise ChildProcessError('Error con VENSIM.')

            variables = [x for x in mem_inter.raw.decode().split('\x00') if x]
            for i in ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']:
                if i in variables:
                    variables.remove(i)

            # Sacar variables editables
            mem_inter = ctypes.create_string_buffer(tamaño_mem)
            resultado = símismo.dll.vensim_get_varnames(b'*', 12, mem_inter, tamaño_mem)
            if resultado < 0:
                raise ChildProcessError('Error con VENSIM.')

            editables = [x for x in mem_inter.raw.decode().split('\x00') if x]

            # Sacar las unidades de los variables
            def sacar_unid(variable):
                mem = ctypes.create_string_buffer(50)
                res = símismo.dll.vensim_get_varattrib(variable.encode(), 1, mem, 50)
                if res <= 0:
                    raise ChildProcessError('Error con VENSIM.')

                return mem.raw.decode().split('\x00')[0]

            unidades = {}
            for var in variables:
                unidades[var] = sacar_unid(var)

        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        símismo.vars = variables
        símismo.vars_editables = editables
        símismo.unidades = unidades

    def sacar_unidades_tiempo(símismo):
        if símismo.programa == 'vensim':
            mem_inter = ctypes.create_string_buffer(50)
            resultado = símismo.dll.vensim_get_varattrib(b'TIME STEP', 1, mem_inter, 50)
            if resultado < 0:
                raise OSError('Error con VENSIM.')
            unidades = mem_inter.raw.decode().split('\x00')[0]
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        return unidades

    def iniciar_modelo(símismo, tiempo_final, nombre=None):

        if nombre is None:
            nombre = 'Corrida Tinamit'

        if símismo.programa == 'vensim':
            símismo.dll.vensim_command(("SIMULATE>RUNNAME|%s" % nombre).encode())

            if tiempo_final is not None:
                símismo.dll.vensim_command(('SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', tiempo_final)).encode())

            resultado = símismo.dll.vensim_command(b"MENU>GAME")

            todobien = (resultado == 1)

        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        if not todobien:
            raise OSError('Error en comanda a %s para iniciar_modelo.' % símismo.programa)

    def incrementar(símismo, paso):
        if símismo.programa == 'vensim':
            símismo.dll.vensim_command(("GAME>GAMEINTERVAL|%i" % paso).encode())
            resultado = símismo.dll.vensim_command(b"GAME>GAMEON")
            funcionó = (resultado == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        return funcionó

    def leer_vals(símismo):
        egresos = {}

        if símismo.programa == 'vensim':
            todobien = True

            for var in símismo.vars_saliendo:
                mem_inter = ctypes.create_string_buffer(4)
                resultado = símismo.dll.vensim_get_val(var.encode(), mem_inter)

                val = struct.unpack('f', mem_inter)[0]
                egresos[var] = val

                if resultado != 1:
                    todobien = False

        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not todobien:
            raise ConnectionError('Error en comanda %s para actualizar_var.' % símismo.programa)
        return egresos

    def actualizar_vars(símismo, valores):
        if símismo.programa == 'vensim':
            todobien = True

            for var_propio, conex in símismo.conex_entrando.items():
                var_entr = conex['var']
                conv = conex['conv']
                if valores[var_entr] is not None:
                    valor = valores[var_entr] * conv
                    resultado = símismo.dll.vensim_command(('SIMULATE>SETVAL|%s = %f' % (var_propio, valor)).encode())
                else:
                    avisar('No encontramos valores iniciales para %s.' % var_entr)
                    resultado = 1

                if resultado != 1:
                    todobien = False

        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        if not todobien:
            raise ConnectionError('Error en comanda %s para actualizar_var.' % símismo.programa)

    def terminar_simul(símismo):
        if símismo.programa == 'vensim':
            funcionó = (símismo.dll.vensim_command(b"GAME>ENDGAME") == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda %s para terminar la simulación.' % símismo.programa)

    def verificar_vensim(símismo):
        """
        Esta función regresa el estatus de Vensim.
        :return: estatus número integral de código de estatus
        0 = Vensim está listo
        1 = Vensim está en una simulación activa
        2 = Vensim está en una simulación, pero no está respondiendo
        3 = Malas noticias
        4 = Error de memoria
        5 = Vensim está en modo de juego
        6 = Memoria no libre. Llamar vensim_command() debería de arreglarlo.
        16 += ver documentación de VENSIM para vensim_check_status() en la sección de DLL (Suplemento DSS)
        """
        estatus = int(símismo.dll.vensim_check_status())
        return estatus
