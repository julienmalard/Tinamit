import json
import socket
from struct import pack, unpack
from typing import Dict, Any, Optional

import numpy as np
import trio


class IDMEnchufesAsinc(object):

    def __init__(símismo, dirección: str = '127.0.0.1', puerto: int = 0):

        símismo.dirección: str = dirección
        símismo.puerto: int = puerto
        símismo.activo = False
        símismo.conectado = False

        símismo.enchufe = None
        símismo.con = None

    async def conectar(símismo):
        símismo.enchufe = trio.socket.socket()
        await símismo.enchufe.bind((símismo.dirección, str(símismo.puerto)))

        símismo.dirección, símismo.puerto = símismo.enchufe.getsockname()
        símismo.enchufe.listen()
        símismo.conectado = True

    async def activar(símismo):
        símismo.con, dir_ = await símismo.enchufe.accept()
        símismo.activo = True

    async def cambiar(símismo, variable: str, valor):
        await MensajeCambiar(símismo.con, variable=variable, valor=valor).mandar()

    async def recibir(símismo, variable: str) -> np.ndarray:
        return await MensajeRecibir(símismo.con, variable).mandar()

    async def incrementar(símismo, n_pasos: int):
        await MensajeIncrementar(símismo.con, pasos=n_pasos).mandar()

    async def finalizar(símismo):
        await símismo.incrementar(0)

    async def cerrar(símismo):
        await MensajeCerrar(símismo.con).mandar()
        try:
            símismo.con.close()
        finally:
            símismo.enchufe.close()
        símismo.activo = False

    async def __aenter__(símismo):
        return símismo

    async def __aexit__(símismo, *args):
        if símismo.activo:
            await símismo.cerrar()


class Mensaje(object):

    def __init__(símismo, conex, contenido: bytes = None):
        símismo.conex = conex
        símismo.contenido = contenido

    @property
    def tipo(símismo):
        raise NotImplementedError

    def _encabezado(símismo) -> Dict:
        return {'tipo': símismo.tipo, 'tamaño': len(símismo.contenido) if símismo.contenido else 0}

    async def mandar(símismo) -> Any:
        encabezado = símismo._encabezado()
        encabezado_bytes = json.dumps(encabezado, ensure_ascii=False).encode('utf8')

        # Mandar tmñ encabezado
        await símismo.conex.send(pack('i', len(encabezado_bytes)))

        # Mandar encabezado json
        await símismo.conex.send(encabezado_bytes)

        # Mandar contenido
        if símismo.contenido:
            await símismo.conex.send(símismo.contenido)

        return await símismo._procesar_respuesta()

    async def _procesar_respuesta(símismo):
        pass


class MensajeCambiar(Mensaje):
    tipo = 'cambiar'

    def __init__(símismo, enchufe, variable: str, valor: np.ndarray):
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

    def __init__(símismo, conex: socket, variable: str):
        símismo.variable = variable
        super().__init__(conex)

    def _encabezado(símismo) -> Dict:
        return {'var': símismo.variable, **super()._encabezado()}

    async def _procesar_respuesta(símismo) -> Any:
        return await RecepciónVariable(símismo.conex).recibir()


class MensajeIncrementar(Mensaje):
    tipo = 'incr'

    def __init__(símismo, enchufe, pasos: int):
        símismo.pasos = pasos

        super().__init__(enchufe)

    def _encabezado(símismo) -> Dict:
        encab = super()._encabezado()

        encab['n_pasos'] = símismo.pasos

        return encab


class MensajeCerrar(Mensaje):
    tipo = 'cerrar'

    def __init__(símismo, con):
        super().__init__(con)


class Recepción(object):
    def __init__(símismo, con):
        símismo.con = con

    async def recibir(símismo) -> Any:
        tmñ = unpack('i', await símismo.con.recv(4))[0]

        datos = await símismo.con.recv(tmñ)
        encabezado = json.loads(datos.decode('utf8'))

        contenido = await símismo.con.recv(encabezado['tamaño'])

        return símismo._procesar(encabezado, contenido)

    def _procesar(símismo, encabezado, contenido) -> Any:
        raise NotImplementedError


class RecepciónVariable(Recepción):
    def _procesar(símismo, encabezado: Dict, contenido: bytes) -> np.ndarray:
        return np.frombuffer(contenido, dtype=encabezado['tipo_cont']).reshape(encabezado['forma'])
