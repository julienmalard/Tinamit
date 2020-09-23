import os
import sys
from typing import Optional
from urllib.parse import urlparse

import asks
import tldextract
import trio

from tinamit3.modelo import Modelo

DIR_BASE = os.path.split(__file__)[0]
DIR_DESCARGAS = os.path.join(DIR_BASE, '_descargas')


def obt_exe(modelo: Modelo) -> Optional[str]:
    if not modelo.descargas:
        return

    exe = os.path.join(DIR_DESCARGAS, modelo.nombre + '.exe')

    if os.path.isfile(exe):
        return exe
    trio.run(descargar_modelo(modelo.descargas))
    assert os.path.isfile(exe), 'No se pudo descargar el modelo {}'.format(modelo)

    return exe


async def descargar_modelo(url):
    proveedor = _extraer_proveedor(url)

    if proveedor == 'github.com':
        instalador = InstaladorGitHub(url)
    else:
        raise ValueError('Proveedor desconocido: {}'.format(proveedor))
    await instalador.descargar()


def _extraer_proveedor(url):
    extraido = tldextract.extract('https://github.com/julienmalard/sahysmod-sourcecode')
    return '.'.join([extraido.domain, extraido.suffix])


class Instalador(object):
    _sinónimos = {
        'osx': 'darwin',
        'windows': 'win32'
    }

    def __init__(símismo, url: str):
        símismo.url = url

    async def obt_url_descarga(símismo) -> str:
        raise NotImplementedError

    def compatible(símismo, plataforma: str, versión: str):

        plataforma = plataforma.lower()
        if plataforma in símismo._sinónimos:
            return símismo._sinónimos[plataforma]
        return plataforma == sys.platform.lower()

    async def descargar(símismo, ubic_archivo):
        url = await símismo.obt_url_descarga()
        r = await asks.get(url, stream=True)

        with open(ubic_archivo, 'ab') as archivo:
            async with r.body:
                async for pedazobits in r.body:
                    archivo.write(pedazobits)


class InstaladorGitHub(Instalador):

    def __init__(símismo, url: str):
        super().__init__(url)
        partes = urlparse(símismo.url).path.split('/')
        símismo.dueño = partes[1]
        símismo.repo = partes[2]

    async def obt_url_descarga(símismo) -> str:
        url = f'https://api.github.com/repos/{símismo.dueño}/{símismo.repo}/releases'
        r = await asks.get(url)
        r = r.json()

        for v in r:
            for a in v['assets']:
                nombre = a['name']
                _, plataforma, n_versón = nombre.rsplit('-', maxsplit=2)
                if símismo.compatible(plataforma, n_versón):
                    url_final = a['browser_download_url']
                    return url_final

        raise ValueError()
