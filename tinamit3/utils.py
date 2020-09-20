import os

EJE_TIEMPO = 't'

def arch_más_recién(arch1, arch2):
    return os.path.getmtime(arch1) > os.path.getmtime(arch2)
