import os

EJE_TIEMPO = 't'


def arch_más_recién(arch1: str, arch2: str) -> bool:
    return os.path.getmtime(arch1) > os.path.getmtime(arch2)
