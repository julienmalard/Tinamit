import os
from subprocess import run


"""
Este código aquí sirve para simplificar el proceso de manejo de traducciones. Correr este código actualizará las 
traducciones y en el servidor, y en la computadora.
"""

# El directorio de la documentación
dir_docs = os.path.split(os.path.realpath(__file__))[0]

# Primero, actualizamos los archivos de documentos para traducir (.pot), basado en el código más recién del programa
print('Actualizando el proyecto...')
run('make gettext', cwd=dir_docs)

# Traer las traducciones más recientes de Zanara
print('Verificando las traducciones más recientes...')
run('zanata po pull', cwd=dir_docs)

# Actualizamos traducciones ya hechas (documentos .po) con las nuevas cosas para traducir
print('Actualizando los archivos de traducciones locales...')
run('sphinx-intl update -p build/locale', cwd=dir_docs)

# Mandar los documentos de traducciones actualizados al servidor Zanata
print('Mandando los documentos de traducciones actualizados al servidor...')
run('zanata po push --copytrans', cwd=dir_docs)

# Ver las estadísticas
print('Pidiendo estadísticas recientes de traducción...')
run('zanata stats', cwd=dir_docs)
