import os
from ast import literal_eval
from typing import Dict

import pysd

from tinamit3.utils import arch_más_recién
from tinamit3.variables import Variable


def gen_mod_pysd(archivo):
    nmbr, ext = os.path.splitext(archivo)

    if ext.lower() == '.py':
        return pysd.load(archivo)

    arch_py = nmbr + '.py'
    if os.path.isfile(arch_py) and arch_más_recién(arch_py, archivo):
        return pysd.load(nmbr + '.py')
    else:
        return pysd.read_vensim(archivo) if ext.lower() == '.mdl' else pysd.read_xmile(archivo)


def decodar(tx: str) -> str:
    if tx.startswith('b\''):
        return literal_eval(tx).decode('unicode_escape')
    return tx


def obt_unid_t_mod_pysd(mod: pysd.functions.Model) -> str:
    doc = mod.components.time_step.__doc__
    partes = doc.split()
    return decodar(partes[partes.index('Units:') + 1])


def gen_vars_pysd(mod: pysd.functions.Model) -> Dict[str, Variable]:
    return
