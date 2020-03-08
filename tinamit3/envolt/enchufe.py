import json
import socket
from abc import abstractmethod
from struct import pack

import numpy as np

from tinamit3.mod import Modelo
from tinamit3.mod.simul import SimulModelo


class ModeloEnchufe(Modelo):
    @property
    def unids(símismo):
        pass


class SimulEnchufe(SimulModelo):
    HUÉSPED = '127.0.0.1'

    def __init__(símismo, modelo):

        símismo._enchufe = e = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        e.bind((símismo.HUÉSPED, 0))
        símismo.puerto = e.getsockname()[1]
        e.listen()
        símismo.con, puerto_recib = e.accept()

        símismo.proceso = símismo.iniciar_proceso()

    @abstractmethod
    def iniciar_proceso(símismo):
        pass

    def cambiar_var(símismo, var):
        MensajeMandar(símismo.con, variable=str(var), valor=var.valor).mandar()

    def leer_var(símismo, var):
        val = MensajeLeer(símismo.con, var).mandar()

    def incrementar(símismo, rbnd):
        for paso in rbnd:
            MensajeIncrementar(símismo.con, pasos=paso.n_pasos).mandar()

    def cerrar(símismo):
        try:
            símismo._enchufe.close()
        finally:
            try:
                símismo.con.close()
            finally:
                if símismo.proceso.poll() is None:
                    avisar(_(
                        'Proceso de modelo {} todavía estaba corriendo al final de la simulación.'
                    ).format(símismo))
                    símismo.proceso.kill()



class Mensaje(object):
    def __init__(símismo, con, contenido):
        símismo.con = con
        símismo.contenido = contenido if isinstance(contenido, )

    @property
    def tipo(símismo):
        raise NotImplementedError

    def _encabezado(símismo):
        return {'tipo': símismo.tipo}

    def mandar(símismo):
        encabezado = símismo._encabezado()
        encabezado_bytes = json.dumps(encabezado, ensure_ascii=False).encode('utf8')

        # Mandar tmñ encabezado
        símismo.con.sendall(pack('!i', len(encabezado_bytes)))
        if not símismo.con.recv(4) == 0:
            raise ConnectionError

        # Mandar encabezado json
        símismo.conn.sendall(encabezado_bytes)
        if not símismo.con.recv(4) == 0:
            raise ConnectionError

        # Mandar contenido
        contenido = símismo.contenido.encode('uft8')
        if contenido:
            símismo.con.sendall(contenido)

        return símismo._procesar()


class MensajeMandar(Mensaje):
    tipo = 'MANDAR'

    def __init__(símismo, enchufe, variable, valor):
        símismo.variable = variable
        símismo.valor = valor
        super().__init__(enchufe)

    def _contenido(símismo):
        return símismo.valor.to_bytes()


class MensajeLeer(Mensaje):
    tipo = 'LEER'

    def __init__(símismo, enchufe, variable):
        símismo.variable = variable
        super().__init__(enchufe)

    def _contenido(símismo):
        return símismo.variable

    def _procesar(símismo):
        return RecepciónVariable(símismo.enchufe).recibir()


class MensajeIncrementar(Mensaje):
    tipo = 'AVANZAR'

    def __init__(símismo, enchufe, pasos):
        símismo.pasos = pasos
        super().__init__(enchufe)

    def _contenido(símismo):
        return símismo.pasos


class Recepción(object):
    def __init__(símismo, con):
        símismo.con = con

    def recibir(símismo):
        tmñ = símismo.con.recv(4)
        encabezado = json.loads(símismo.con.recv(tmñ).decode('utf8'))
        contenido = símismo.con.recv(encabezado['tamaño'])
        return símismo._procesar(encabezado, contenido)

    def _procesar(símismo, encabezado, contenido):
        raise NotImplementedError


class RecepciónVariable(Recepción):

    def _procesar(símismo, encabezado, contenido):
        forma = encabezado['forma']
        return np.frombuffer(contenido).reshape(forma)
