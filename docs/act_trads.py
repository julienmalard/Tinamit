import os
from subprocess import run


"""
Este código aquí sirve para simplificar el proceso de manejo de traducciones. Correr este código actualizará las 
traducciones y en el servidor, y en la computadora.

Funciona también (probablemente) para coordinar traducciones entre Zanata y Transifex, porque todavía no he decidido
cuál es mejor. 
"""

# El directorio de la documentación
dir_docs = os.path.split(os.path.realpath(__file__))[0]

# Primero, actualizamos los archivos de documentos para traducir (.pot), basado en el código más recién del programa
print('Actualizando el proyecto...')
run('make gettext', cwd=dir_docs)

# Traemos traducciones de Transifex y las mandamos a Zanata.
print('Actualizando con Transifex...')
run('tx pull -a', cwd=dir_docs)
run('zanata po push --copytrans --import-po', input=b'y', cwd=dir_docs)

# Traer las traducciones más recientes de Zanata
print('Verificando las traducciones más recientes en Zanata...')
run('zanata po pull', cwd=dir_docs)

# Actualizamos traducciones ya hechas (documentos .po) con las nuevas cosas para traducir
print('Actualizando los archivos de traducciones locales...')
run('sphinx-intl update -p build/locale', cwd=dir_docs)

# Mandar los documentos de traducciones actualizados al servidor Zanata
print('Mandando los documentos de traducciones actualizados al servidor...')
run('zanata po push --copytrans', input=b'y', cwd=dir_docs)

# Mandar todo a Transifex también
print('Mandando todo a Transifex también...')
run('tx push -s -t', cwd=dir_docs)

# Ver las estadísticas
print('Pidiendo estadísticas recientes de traducción (de Zanata)...')
run('zanata stats', cwd=dir_docs)
