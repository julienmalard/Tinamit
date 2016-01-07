import ctypes
import struct


class EnvolturaMDS(object):
    def __init__(símismo, programa_mds, ubicación_modelo):
        símismo.programa = programa_mds.lower()
        símismo.dll = cargar_mds(símismo.programa, ubicación_modelo)
        símismo.vars = símismo.sacar_vars()
        símismo.vars_entrando = {}
        símismo.vars_saliendo = []

    def sacar_vars(símismo):
        if símismo.programa == 'vensim':
            mem_inter = ctypes.create_string_buffer(1000000)
            símismo.intentar_función(símismo.dll.vensim_get_varnames,
                                     ['*', 0, mem_inter, 1000000]
                                     )
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        variables = [x for x in mem_inter.raw.decode().split('\x00') if x]

        return variables

    def iniciar_modelo(símismo, tiempo_final):
        if símismo.programa == 'vensim':
            if tiempo_final is not None:
                for v in [b'TIEMPO FINAL', b'FINAL TIME']:
                    símismo.intentar_función(símismo.dll.vensim_command,
                                             [b'SIMULATE>SETVAL|%s = %s' % (v, str(tiempo_final).encode())]
                                             )
            símismo.intentar_función(símismo.dll.vensim_start_simulation,
                                     [1, 0, 1]
                                     )
            todobien = símismo.verificar_vensim() == 1
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        if not todobien:
            raise ConnectionError('Error en comanda %s para iniciar_modelo.' % símismo.programa)

    def incrementar(símismo, paso):
        if símismo.programa == 'vensim':
            símismo.intentar_función(símismo.dll.vensim_continue_simulation,
                                     [paso]
                                     )
            funcionó = símismo.verificar_vensim()
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        return funcionó

    def leer_vals(símismo):
        egresos = {}

        if símismo.programa == 'vensim':
            for var in símismo.vars_saliendo:
                mem_inter = ctypes.create_string_buffer(4)
                símismo.intentar_función(símismo.dll.vensim_get_val,
                                         [var.encode(), mem_inter]
                                         )
                val = struct.unpack('f', mem_inter)[0]
                egresos[var] = val
            todobien = símismo.verificar_vensim()
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not todobien:
            raise ConnectionError('Error en comanda %s para actualizar_var.' % símismo.programa)
        return egresos

    def actualizar_vars(símismo, valores):
        if símismo.programa == 'vensim':
            for var_mds in símismo.vars_entrando:
                valor = valores[símismo.vars_entrando[var_mds]]
                símismo.intentar_función(símismo.dll.vensim_command,
                                         [b'SIMULATE>SETVAL|%s = %s' %
                                          (var_mds.encode(), str(valor).encode())]
                                         )
            todobien = símismo.verificar_vensim()
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)

        if not todobien:
            raise ConnectionError('Error en comanda %s para actualizar_var.' % símismo.programa)

    def terminar_simul(símismo):
        if símismo.programa == 'vensim':
            funcionó = (símismo.dll.vensim_finish_simulation() == 1)
        else:
            raise NotImplementedError('Falta implementar el programa de MDS %s.' % símismo.programa)
        if not funcionó:
            raise ConnectionError('Error en comanda %s para terminar_simul.' % símismo.programa)

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

    @staticmethod
    def intentar_función(función, parámetros):
        try:
            resultado = función(*parámetros)
        except ValueError:
            resultado = None

        return resultado


def cargar_mds(programa_mds, ubicación_modelo):
        if programa_mds == 'vensim':
            dll = ctypes.cdll.LoadLibrary('C:\\Windows\\System32\\vendll32.dll')

            try:
                dll.vensim_command(b'SPECIAL>LOADMODEL|%s' % ubicación_modelo.encode())
            except ValueError:
                pass

            todobien = (int(dll.vensim_check_status()) == 0)
        else:
            raise NotImplementedError('No se ha escrito una interfaz para este tipo de programa MDS. '
                                      'Quejarse al programador.')

        if todobien:
            return dll
        else:
            raise FileNotFoundError('No se pudo cargar el modelo ')
