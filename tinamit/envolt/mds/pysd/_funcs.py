import os

import pysd
from tinamit.cositas import arch_más_recién


def gen_mod_pysd(archivo):
    nmbr, ext = os.path.splitext(archivo)

    arch_py = nmbr + '.py'
    if os.path.isfile(arch_py) and arch_más_recién(arch_py, archivo):
        return pysd.load(nmbr + '.py')
    else:
        return pysd.read_vensim(archivo) if ext == '.mdl' else pysd.read_xmile(archivo)


def obt_paso_mod_pysd(archivo):
    # Inelegante, seguro, pero por el momento inevitable con PySD
    with open(archivo, 'r', encoding='UTF-8') as d:
        f = d.readline()
        while f != 'def time_step():\n':
            f = d.readline()
        while not f.strip().startswith('Units:'):
            f = d.readline()
    return f.split(':')[1].strip()
