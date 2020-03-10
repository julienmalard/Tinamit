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
        raise NotImplementedError


class SimulEnchufe(SimulModelo):
    HUÉSPED = '127.0.0.1'

    def __init__(símismo, modelo):
        super().__init__(modelo)

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
        MensajeCambiar(símismo.con, variable=str(var), valor=var.valor).mandar()

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
                MensajeCerrar().mandar()
                if símismo.proceso.poll() is None:
                    avisar(_(
                        'Proceso de modelo {} todavía estaba corriendo al final de la simulación.'
                    ).format(símismo))
                    símismo.proceso.kill()


class Mensaje(object):
    def __init__(símismo, con, contenido=''):
        símismo.con = con
        símismo.contenido = contenido if isinstance(contenido, bytes) else contenido.encode('utf8')

    @property
    def tipo(símismo):
        raise NotImplementedError

    def _encabezado(símismo):
        return {'tipo': símismo.tipo, 'tamaño': len(símismo.contenido)}

    def mandar(símismo):
        encabezado = símismo._encabezado()
        encabezado_bytes = json.dumps(encabezado, ensure_ascii=False).encode('utf8')

        # Mandar tmñ encabezado
        símismo.con.sendall(pack('i', len(encabezado_bytes)))
        if not símismo.con.recv(4) == 0:
            raise ConnectionError

        # Mandar encabezado json
        símismo.con.sendall(encabezado_bytes)
        if not símismo.con.recv(4) == 0:
            raise ConnectionError

        # Mandar contenido
        if símismo.contenido:
            símismo.con.sendall(símismo.contenido)

        return símismo._procesar_respuesta()

    def _procesar_respuesta(símismo):
        pass


class MensajeCambiar(Mensaje):
    tipo = 'cambiar'

    def __init__(símismo, enchufe, variable, valor):
        símismo.variable = variable
        super().__init__(enchufe, contenido=valor.to_bytes())

    def _encabezado(símismo):
        encab = super()._encabezado()
        encab['var'] = str(símismo.variable)
        encab['matr'] = símismo.variable.esmatriz
        return encab


class MensajeLeer(Mensaje):
    tipo = 'leer'

    def __init__(símismo, con, variable):
        símismo.variable = variable
        super().__init__(con)

    def _encabezado(símismo):
        encab = super()._encabezado()
        encab['var'] = str(símismo.variable)
        return encab

    def _procesar_respuesta(símismo):
        val = RecepciónVariable(símismo.con).recibir()
        if símismo.variable.esmatriz:
            if isinstance(val, np.ndarray):
                val = val.reshape(símismo.variable.forma)
            else:
                val = np.full(símismo.variable.forma, val)
        elif isinstance(val, np.ndarray):
            raise TypeError
        return val


class MensajeIncrementar(Mensaje):
    tipo = 'incr'

    def __init__(símismo, enchufe, pasos):
        símismo.pasos = pasos
        super().__init__(enchufe)

    def _encabezado(símismo):
        encab = super()._encabezado()
        encab['n_pasos'] = símismo.pasos
        return encab


class MensajeCerrar(Mensaje):
    tipo = 'cerrar'


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
        return np.frombuffer(contenido)
