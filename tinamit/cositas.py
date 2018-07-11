import json
import os
import tempfile

from chardet import UniversalDetector


def detectar_codif(archivo, máx_líneas=None):
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

    Returns
    -------
    str
        La codificación más probable.

    """

    detector = UniversalDetector()
    for í, línea in enumerate(open(archivo, 'rb').readlines()):

        detector.feed(línea)  # Pasar la próxima línea al detector

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

    for x in ['\\', '/', '\|', ':' '*', '?', '"', '>', '<']:
        nombre = nombre.replace(x, '_')

    return nombre.strip()


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
    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as temp:
        # Escribimos primero a un fuente temporario para evitar de corrumpir nuestro fuente principal si el programa
        # se interrumpe durante la operación.
        json.dump(obj, temp, ensure_ascii=False, sort_keys=True, indent=2)

        # Crear el directorio, si necesario
        direc = os.path.split(arch)[0]
        if len(direc) and not os.path.isdir(direc):
            os.makedirs(os.path.split(arch)[0])

    # Después de haber escrito el fuente, ya podemos cambiar el nombre sin riesgo.
    try:
        os.replace(temp.name, arch)
    except PermissionError:
        # Necesario en el caso de corridas en paralelo en Windows. Sin este, la reimportación de Tinamït ocasionada
        # por varias corridas paralelas al mismo tiempo puede causar que el mismo documento se escriba por dos procesos
        # al mismo tiempo, el cual trava el sistema.
        pass


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

    with open(arch, 'r', encoding=codif) as d:
        return json.load(d)
