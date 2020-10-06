from __future__ import annotations

import os
import sys
from numbers import Number
from typing import List, Optional, Union
from urllib.parse import urlparse

import asks
import semantic_version as sv
import tldextract
import trio

DIR_BASE = os.path.split(__file__)[0]
DIR_DESCARGAS = os.path.join(DIR_BASE, '_descargas')


def obt_exe(
        nombre: str,
        url: Union[str, Instalador],
        versión: Optional[Union[str, Number]] = None
) -> Optional[str]:
    versión = str(versión) if versión else '*'
    try:
        ver_sem = sv.SimpleSpec(versión)
    except ValueError:
        ver_sem = False

    if ver_sem:
        if not url:
            raise ValueError('Repositorio de descargas no definido para modelo {}.'.format(nombre))

        v_local = mejor_instalada(nombre, ver_sem)
        if not v_local:
            proveedor = url if isinstance(url, Instalador) else gen_instalador(nombre, url)
            v_local = trio.run(proveedor.instalar, sv.SimpleSpec(versión))

        archivo = v_local.archivo

    else:
        archivo = versión
        if not os.path.isfile(archivo):
            raise FileNotFoundError(archivo)

    return archivo


def gen_instalador(nombre: str, url: str) -> Instalador:
    proveedor = _extraer_proveedor(url)
    if proveedor == 'github.com':
        return InstaladorGitHub(nombre, url)
    else:
        raise ValueError('Proveedor desconocido: {}'.format(proveedor))


def _extraer_proveedor(url: str) -> str:
    extraido = tldextract.extract(url)
    return '.'.join([extraido.domain, extraido.suffix])


def instaladas(nombre: str, espec_versión: Optional[Union[str, sv.SimpleSpec]] = None) -> List[VersiónLocal]:
    v = sv.SimpleSpec(str(espec_versión or '*'))

    dir_local = _obt_dir_local(nombre)
    lista = []
    if os.path.isdir(dir_local):
        lista = [VersiónLocal(nombre, x) for x in os.listdir(dir_local)]

    return [x for x in lista if x in v]


def mejor_instalada(nombre: str, espec_versión: sv.SimpleSpec) -> Optional[VersiónLocal]:
    _instaladas = instaladas(nombre, espec_versión)
    if _instaladas:
        return sorted(_instaladas)[-1]


def _obt_dir_local(nombre: str) -> str:
    return os.path.join(DIR_DESCARGAS, nombre)


def _obt_archivo_local(nombre: str, versión: str) -> str:
    return os.path.join(_obt_dir_local(nombre), versión)


class VersiónLocal(sv.Version):
    def __init__(símismo, nombre: str, versión: str):
        símismo.nombre = nombre
        símismo.versión = versión
        símismo.archivo = _obt_archivo_local(nombre, versión)
        super().__init__(versión)


class VersiónDescargable(sv.Version):
    def __init__(símismo, nombre: str, plataforma: str, versión: str, url: str):
        símismo.nombre = nombre
        símismo.url = url

        _sinónimos = {
            'osx': 'darwin',
            'windows': 'win32'
        }
        plataforma = plataforma.lower()
        símismo.plataforma = _sinónimos[plataforma].lower() if plataforma in _sinónimos else plataforma

        super().__init__(str(sv.Version.coerce(versión)))

    def compatible(símismo, espec_versión: sv.SimpleSpec):
        return símismo.plataforma == sys.platform.lower() and símismo in espec_versión

    async def instalar(símismo, forzar: bool = False) -> VersiónLocal:
        arch_local = _obt_archivo_local(símismo.nombre, str(símismo))
        if forzar or not os.path.isfile(arch_local):

            r = await asks.get(símismo.url, stream=True)
            async with await trio.open_file(arch_local, 'ab') as d:
                async with r.body:
                    async for pedazobits in r.body:
                        d.write(pedazobits)

            if not os.path.isfile(arch_local):
                raise FileNotFoundError(
                    'No se pudo descargar el modelo {n}, versión {v}'.format(n=símismo.nombre, v=símismo)
                )

        return VersiónLocal(símismo.nombre, str(símismo))


class Instalador(object):
    def __init__(símismo, nombre: str, url: str):
        símismo.nombre = nombre
        símismo.url = url

    async def instalar(símismo, versión: sv.SimpleSpec) -> VersiónLocal:
        disponibles = await símismo.disponibles()
        compatibles = sorted([x for x in disponibles if x.compatible(versión)])

        if compatibles:
            return await compatibles[-1].instalar()
        raise ValueError('Versión compatible no encontrada para {n}, versión {v}.'.format(n=símismo.nombre, v=versión))

    async def actualizar(símismo):
        return await símismo.instalar(sv.SimpleSpec('*'))

    async def disponibles(símismo) -> List[VersiónDescargable]:
        raise NotImplementedError


class InstaladorGitHub(Instalador):
    def __init__(símismo, nombre: str, url: str):
        super().__init__(nombre, url)
        partes = urlparse(símismo.url).path.split('/')
        símismo.dueño = partes[1]
        símismo.repo = partes[2]

    async def disponibles(símismo) -> List[VersiónDescargable]:
        l_final = []

        url = f'https://api.github.com/repos/{símismo.dueño}/{símismo.repo}/releases'
        resp = await asks.get(url)
        resp = resp.json()

        for v in resp:
            for arch in v['assets']:
                nombre_arch = arch['name']
                _, plataforma, versión = nombre_arch.rsplit('-', maxsplit=2)
                l_final.append(VersiónDescargable(
                    símismo.nombre,
                    plataforma=plataforma,
                    versión=versión,
                    url=arch['browser_download_url']
                ))

        return l_final
