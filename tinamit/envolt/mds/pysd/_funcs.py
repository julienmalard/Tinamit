import os

import pysd
from tinamit.cositas import arch_más_recién


def gen_mod_pysd(archivo):
    nmbr, ext = os.path.splitext(archivo)

    if ext == '.py':
        return pysd.load(archivo)

    arch_py = nmbr + '.py'
    if os.path.isfile(arch_py) and arch_más_recién(arch_py, archivo):
        return pysd.load(nmbr + '.py')
    else:
        return pysd.read_vensim(archivo) if ext == '.mdl' else pysd.read_xmile(archivo)


def obt_paso_mod_pysd(archivo):
    # Inelegante, seguro, pero por el momento inevitable con PySD
    with open(archivo, 'r', encoding='UTF-8') as d:
        buscando = False
        for f in d:
            if f == 'def time_step():\n':
                buscando = True
            if buscando and f.strip().startswith('Units:'):
                return f.split(':')[1].strip()

    raise ValueError()
