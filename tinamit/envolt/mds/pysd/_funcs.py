import os
from ast import literal_eval

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


def obt_paso_mod_pysd(mod):
    doc = mod.components.time_step.__doc__
    partes = doc.split()
    return decodar(partes[partes.index('Units:')+1])


def decodar(tx):
    return literal_eval(tx).decode('unicode_escape')
