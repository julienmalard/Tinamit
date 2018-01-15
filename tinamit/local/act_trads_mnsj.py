from subprocess import run
import os
from tinamit import __file__ as dir_tinamit

leng_orig = 'es'
lenguas = {'ms', 'fr', 'ta', 'ur', 'nl'}

# El directorio de tinamit
dir_local = os.path.split(os.path.realpath(__file__))[0]

dir_base, pq = os.path.split(os.path.realpath(os.path.split(dir_tinamit)[0]))

dir_fuente = os.path.join(dir_base, pq, 'local', '_fuente')
lengs_ya = [x for x in os.listdir(dir_fuente) if os.path.isdir(os.path.join(dir_fuente, x))]
lengs_nuevas = lenguas.difference(lengs_ya)
lenguas.update(lengs_ya)

run('python setup.py extract_messages', cwd=dir_base)

for l in lengs_nuevas:
    run('python setup.py init_catalog -l {}'.format(l), cwd=dir_base)

for l in lengs_ya:
    run('python setup.py update_catalog -l {}'.format(l), cwd=dir_base)

run('python setup.py compile_catalog', cwd=dir_base)
