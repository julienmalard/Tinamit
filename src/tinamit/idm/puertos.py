import json
import socket
from numbers import Number
from struct import pack, unpack
from typing import Optional, Union, Any, Dict

import numpy as np


class IDMEnchufes(object):

    def __init__(símismo, dirección: str = '127.0.0.1', puerto: int = 0):
        símismo.enchufe = enchf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        enchf.bind((dirección, puerto))

        símismo.dirección, símismo.puerto = enchf.getsockname()
        enchf.listen()

        símismo.activo: bool = False
        símismo.con: Optional[socket.socket] = None

    def activar(símismo):
        símismo.con, dir_ = símismo.enchufe.accept()
        símismo.activo = True

    def cambiar(símismo, variable: str, valor: Union[np.ndarray, Number]):
        MensajeCambiar(símismo.con, variable=variable, valor=valor).mandar()

    def recibir(símismo, variable: str) -> np.ndarray:
        return MensajeRecibir(símismo.con, variable).mandar()

    def incrementar(símismo, n_pasos):
        MensajeIncrementar(símismo.con, pasos=n_pasos).mandar()

    def finalizar(símismo):
        símismo.incrementar(0)

    def cerrar(símismo):
        MensajeCerrar(símismo.con).mandar()
        try:
            símismo.con.close()
        finally:
            símismo.enchufe.close()
        símismo.activo = False

    def __enter__(símismo):
        return símismo

    def __exit__(símismo, *args):
        if símismo.activo:
            símismo.cerrar()


class Mensaje(object):

    def __init__(símismo, conex: socket.socket, contenido: bytes = None):
        símismo.conex = conex
        símismo.contenido = contenido

    @property
    def tipo(símismo):
        raise NotImplementedError

    def _encabezado(símismo) -> Dict:
        return {'tipo': símismo.tipo, 'tamaño': len(símismo.contenido) if símismo.contenido else 0}

    def mandar(símismo) -> Any:
        encabezado = símismo._encabezado()
        encabezado_bytes = json.dumps(encabezado, ensure_ascii=False).encode('utf8')

        # Mandar tmñ encabezado
        símismo.conex.sendall(pack('i', len(encabezado_bytes)))

        # Mandar encabezado json
        símismo.conex.sendall(encabezado_bytes)

        # Mandar contenido
        if símismo.contenido:
            símismo.conex.sendall(símismo.contenido)

        return símismo._procesar_respuesta()

    def _procesar_respuesta(símismo) -> Any:
        pass


class MensajeCambiar(Mensaje):
    tipo = 'cambiar'

    def __init__(símismo, enchufe, variable: str, valor: Union[np.ndarray, Number]):
        símismo.variable = variable
        símismo.valor = valor if isinstance(valor, np.ndarray) else np.array(valor)

        super().__init__(enchufe, contenido=símismo.valor.tobytes())

    def _encabezado(símismo) -> Dict:
        return {
            'var': símismo.variable,
            'tipo_cont': str(símismo.valor.dtype),
            'forma': símismo.valor.shape,
            **super()._encabezado()
        }


class MensajeRecibir(Mensaje):
    tipo = 'leer'

    def __init__(símismo, conex: socket.socket, variable: str):
        símismo.variable = variable
        super().__init__(conex)

    def _encabezado(símismo):
        return {'var': símismo.variable, **super()._encabezado()}

    def _procesar_respuesta(símismo) -> Any:
        return RecepciónVariable(símismo.conex).recibir()


class MensajeIncrementar(Mensaje):
    tipo = 'incr'

    def __init__(símismo, enchufe: socket.socket, pasos: int):
        símismo.pasos = pasos

        super().__init__(enchufe)

    def _encabezado(símismo) -> Dict:
        encab = super()._encabezado()

        encab['n_pasos'] = símismo.pasos

        return encab


class MensajeCerrar(Mensaje):
    tipo = 'cerrar'

    def __init__(símismo, con: socket.socket):
        super().__init__(con)


class Recepción(object):
    def __init__(símismo, con: socket.socket):
        símismo.con = con

    def recibir(símismo) -> Any:
        tmñ = unpack('i', símismo.con.recv(4))[0]

        encabezado = json.loads(símismo.con.recv(tmñ).decode('utf8'))

        contenido = símismo.con.recv(encabezado['tamaño'])

        return símismo._procesar(encabezado, contenido)

    def _procesar(símismo, encabezado: Dict, contenido: bytes):
        raise NotImplementedError


class RecepciónVariable(Recepción):
    def _procesar(símismo, encabezado: Dict, contenido: bytes):
        return np.frombuffer(contenido, dtype=encabezado['tipo_cont']).reshape(encabezado['forma'])
