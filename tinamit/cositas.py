import json
import os
import shutil
import tempfile
from datetime import datetime, date
from warnings import warn as avisar

import numpy as np
from chardet import UniversalDetector


def detectar_codif(archivo, máx_líneas=None, cortar=None):
    """
    Detecta la codificación de un fuente. (Necesario porque todavía existen programas dinosaurios que no entienden
    los milagros de unicódigo.)

    Parameters
    ----------
    archivo : str
        La dirección del fuente.
    máx_líneas : int
        El número máximo de líneas para pasar al detector. Por ejemplo, si únicamente la primera línea de tu documento
        tiene palabras (por ejemplo, un fuente .csv), no hay razón de seguir analizando las otras líneas.
    cortar : str
        Hasta dónde hay que leer cada línea. Es útil si tienes un csv donde únicamente la primera columna
        contiene texto.

    Returns
    -------
    str
        La codificación más probable.

    """

    detector = UniversalDetector()
    with open(archivo, 'rb') as d:
        for í, línea in enumerate(d.readlines()):

            if cortar is None or cortar.encode() not in línea:
                detector.feed(línea)  # Pasar la próxima línea al detector
            else:
                detector.feed(línea.split(cortar.encode())[0])

            # Parar si alcanzamos el máximo de líneas
            if máx_líneas is not None and í >= (máx_líneas - 1):
                break

            if detector.done:
                break  # Para si el detector ya está seguro

    detector.close()  # Cerrar el detector

    return detector.result['encoding']  # Devolver el resultado


def valid_nombre_arch(nombre):
    """
    Valida el nombre de un fuente.

    Parameters
    ----------
    nombre : str
        El nombre propuesto para el fuente.
    Returns
    -------
    str
        Un nombre de fuente válido.
    """

    for x in ['\\', '/', '|', ':' '*', '?', '"', '>', '<']:
        nombre = nombre.replace(x, '_')

    return nombre.strip()


def arch_más_recién(arch1, arch2):
    return os.path.getmtime(arch1) > os.path.getmtime(arch2)


def guardar_json(obj, arch):
    """
    Guarda un fuente json, sin riesgo de corrumpir el fuente si se interrumpe el programa mientras escribía al disco.

    Parameters
    ----------
    obj : list | dict
        Objeto compatible json.
    arch : str
        El fuente en el cual hay que guardar el objeto json.

    """
    nmbr, ext = os.path.splitext(arch)
    if not len(ext):
        arch = nmbr + '.json'

    contenido = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)
    guardar_archivo(arch, contenido=contenido)


def guardar_archivo(arch, contenido):
    """
    Guarda un documento de manera segura, sin riesgo de corrumpir el archivo existente si se interrumpe el proceso.

    Parameters
    ----------
    arch : str
        El archivo que hay que escribir.
    contenido : str
        El contenido deseado del archivo.

    """

    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as temp:
        # Escribimos primero a un fuente temporario para evitar de corrumpir nuestro fuente principal si el programa
        # se interrumpe durante la operación.
        temp.write(contenido)

        # Crear el directorio, si necesario
        direc = os.path.split(arch)[0]
        if len(direc) and not os.path.isdir(direc):  # pragma: sin cobertura
            os.makedirs(os.path.split(arch)[0])

    # Después de haber escrito el fuente, ya podemos cambiar el nombre sin riesgo.
    try:

        if os.path.splitdrive(temp.name)[0] == os.path.splitdrive(arch)[0]:
            os.replace(temp.name, arch)
        else:
            # En casos de documentos en distintos discos, debemos emplear `shutil` en vez.
            shutil.move(temp.name, arch)

    except (PermissionError, FileNotFoundError, OSError):  # pragma: sin cobertura
        # Necesario en el caso de corridas en paralelo en Windows. Sin este, la reimportación de Tinamït ocasionada
        # por varias corridas paralelas al mismo tiempo puede causar que el mismo documento se escriba por dos procesos
        # al mismo tiempo, el cual trava el sistema.
        avisar(arch)


def cargar_json(arch, codif='UTF-8'):
    """
    Cargar un fuente json.

    Parameters
    ----------
    arch : str
        El fuente en el cual se encuentra el objeto json.
    codif : str
        La codificación del fuente.

    Returns
    -------
    dict | list
        El objeto json.

    """

    nmbr, ext = os.path.splitext(arch)
    if not len(ext):
        arch = nmbr + '.json'

    with open(arch, 'r', encoding=codif) as d:
        return json.load(d)


def jsonificar(dic, redond=None):
    nuevo = {}
    for ll, v in dic.items():
        if isinstance(v, dict):
            nuevo[ll] = jsonificar(v, redond=redond)
        elif isinstance(v, np.ndarray):
            if redond:
                v = v.round(redond)
            nuevo[ll] = v.tolist()
        else:
            nuevo[ll] = v

    return nuevo


def numpyficar(dic):
    nuevo = {}
    for ll, v in dic.items():
        if isinstance(v, dict):
            nuevo[ll] = numpyficar(v)
        elif isinstance(v, list):
            nuevo[ll] = np.array(v)
        else:
            nuevo[ll] = v
    return nuevo


def _gen_fecha(f):
    if f is None:
        return
    elif isinstance(f, str):
        return datetime.strptime(f, '%Y-%m-%d')
    elif isinstance(f, datetime):
        return f
    elif isinstance(f, date):
        return datetime(f.year, f.month, f.day)
    else:
        raise TypeError(type(f))
