import os
from subprocess import run, Popen, PIPE


"""
Este código aquí sirve para simplificar el proceso de manejo de traducciones. Correr este código actualizará las 
traducciones y en el servidor, y en la computadora.

Funciona también (probablemente) para coordinar traducciones entre Zanata y Transifex, porque todavía no he decidido
cuál es mejor. 
"""

proyecto_transifex = 'tinamit'
leng_orig = 'es'
lenguas = ['ms', 'yo', 'fa', 'fr', 'ta', 'ur', 'nl']

# El directorio de la documentación
dir_docs = os.path.split(os.path.realpath(__file__))[0]

# Primero, actualizamos los archivos de documentos para traducir (.pot), basado en el código más recién del programa
print('Actualizando el proyecto...')
run('make gettext', cwd=dir_docs)
l_lengs = '-l ' + ' -l '.join(lenguas)

# Actualizamos traducciones ya hechas (documentos .po) con las nuevas cosas para traducir
run('sphinx-intl update -p build/locale {}'.format(l_lengs), cwd=dir_docs)

p = Popen('tx init',stdin=PIPE, cwd='C:\\Users\\jmalar1\\PycharmProjects\\Tinamit\\docs', shell=True)
p.stdin.write(b'y\n')
p.stdin.flush()
p.stdin.write(b'\n')
p.stdin.flush()

run('sphinx-intl update-txconfig-resources --pot-dir build/locale --transifex-project-name {}'
    .format(proyecto_transifex), cwd=dir_docs)

archivo_config_tx = os.path.join(dir_docs, '.tx', 'config')
final = []
with open(archivo_config_tx, mode='r') as d:
    for l in d.readlines():
        if l == 'source_lang = en\n':
            final.append('source_lang = {}\n'.format(leng_orig))
        else:
            final.append(l)

with open(archivo_config_tx, mode='w') as d:
    d.truncate()
    d.writelines(final)


# Mandar cambios locales al servidor Zanata
print('Mandando los documentos de traducciones actualizados al servidor...')
run('zanata po push --copytrans', input=b'y', cwd=dir_docs)

# Traemos traducciones de Transifex y las mandamos a Zanata.
print('Actualizando con Transifex...')
run('tx pull -a', cwd=dir_docs)
run('zanata po push --copytrans --import-po', input=b'y', cwd=dir_docs)

# Traemos las traducciones más recientes de Zanata
print('Verificando las traducciones más recientes en Zanata...')
run('zanata po pull', cwd=dir_docs)

# Mandar los documentos de traducciones actualizados al servidor Zanata
print('Mandando los documentos de traducciones actualizados al servidor...')
run('zanata po push --copytrans', input=b'y', cwd=dir_docs)

# Mandar todo a Transifex también
print('Mandando todo a Transifex también...')
run('tx push -s -t', cwd=dir_docs)

# Ver las estadísticas
print('Pidiendo estadísticas recientes de traducción (de Zanata)...')
run('zanata stats', cwd=dir_docs)
