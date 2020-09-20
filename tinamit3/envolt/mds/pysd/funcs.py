import os
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


def gen_vars_pysd(archivo) -> Dict[str, Variable]:
    mod = gen_mod_pysd(archivo)
