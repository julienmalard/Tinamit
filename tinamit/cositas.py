import json
import os
import tempfile

from chardet import UniversalDetector


def detectar_codif(archivo, máx_líneas=None):
    """
    Detecta la codificación de un archivo. (Necesario porque todavía existen programas dinosaurios que no entienden
    los milagros de unicódigo.)

    Parameters
    ----------
    archivo : str
        La dirección del archivo.
    máx_líneas : int
        El número máximo de líneas para pasar al detector. Por ejemplo, si únicamente la primera línea de tu documento
        tiene palabras (por ejemplo, un archivo .csv), no hay razón de seguir analizando las otras líneas.

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

        if detector.done: break  # Para si el detector ya está seguro

    detector.close()  # Cerrar el detector

    return detector.result['encoding']  # Devolver el resultado


def valid_nombre_arch(nombre):
    """
    Valida el nombre de un archivo.

    Parameters
    ----------
    nombre : str
        El nombre propuesto para el archivo.
    Returns
    -------
    str
        Un nombre de archivo válido.
    """

    for x in ['\\', '/', '\|', ':' '*', '?', '"', '>', '<']:
        nombre = nombre.replace(x, '_')

    return nombre.strip()


def guardar_json(obj, arch):
    """
    Guarda un archivo json, sin riesgo de corrumpir el archivo si se interrumpe el programa mientras escribía al disco.

    Parameters
    ----------
    obj : list | dict
        Objeto compatible json.
    arch : str
        El archivo en el cual hay que guardar el objeto json.

    """

    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as temp:
        # Escribimos primero a un archivo temporario para evitar de corrumpir nuestro archivo principal si el programa
        # se interrumpe durante la operación.
        json.dump(obj, temp, ensure_ascii=False, sort_keys=True, indent=2)

        # Crear el directorio, si necesario
        direc = os.path.split(arch)[0]
        if len(direc) and not os.path.isdir(direc):
            os.makedirs(os.path.split(arch)[0])

    # Después de haber escrito el archivo, ya podemos cambiar el nombre sin riesgo.
    os.replace(temp.name, arch)


def cargar_json(arch, codif='UTF-8'):
    """
    Cargar un archivo json.

    Parameters
    ----------
    arch : str
        El archivo en el cual se encuentra el objeto json.
    codif : str
        La codificación del archivo.

    Returns
    -------
    dict | list
        El objeto json.

    """

    with open(arch, 'r', encoding=codif) as d:
        return json.load(d)
