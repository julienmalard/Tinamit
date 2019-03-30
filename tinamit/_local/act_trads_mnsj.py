import os
from subprocess import run

from tinamit import __file__ as dir_tinamit

leng_orig = 'es'
lenguas = {'ms', 'fr', 'ta', 'ur', 'nl'}

# El directorio de tinamit
dir_local = os.path.split(os.path.realpath(__file__))[0]

dir_base, pq = os.path.split(os.path.realpath(os.path.split(dir_tinamit)[0]))

dir_fuente = os.path.join(dir_base, pq, '_local', '_fuente')
lengs_ya = [x for x in os.listdir(dir_fuente) if os.path.isdir(os.path.join(dir_fuente, x))]
lengs_nuevas = lenguas.difference(lengs_ya)
lenguas.update(lengs_ya)

run('python setup.py extract_messages', cwd=dir_base)

for l in lengs_nuevas:
    run('python setup.py init_catalog -l {}'.format(l), cwd=dir_base)

for l in lengs_ya:
    run('python setup.py update_catalog -l {}'.format(l), cwd=dir_base)

# Mandar cambios locales al servidor Zanata
print('Mandando traducciones actualizadas localmente a Zanata...')
run('zanata po push --copytrans --import-po', input=b'y', cwd=dir_local)

# Traemos traducciones de Transifex y las mandamos a Zanata.
print('Actualizando con Transifex...')
run('tx pull -a -f', cwd=dir_fuente)
print('Mandando traducciones de Transifex a Zanata...')
run('zanata po push --copytrans --import-po', input=b'y', cwd=dir_local)

# Traemos las traducciones más recientes de Zanata
print('Verificando las traducciones más recientes en Zanata...')
run('zanata po pull', cwd=dir_local)

# Mandar los documentos de traducciones actualizados al servidor Transifex
print('Mandando todo a Transifex también...')
run('tx push -s -t', cwd=dir_local)

# Ver las estadísticas
print('Pidiendo estadísticas recientes de traducción (de Zanata)...')
run('zanata stats', cwd=dir_local)

# Compilar las traducciones actualizadas
run('python setup.py compile_catalog', cwd=dir_base)
