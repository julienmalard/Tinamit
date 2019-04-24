import json
import os


def verificar_leer_ingr(caso, cls):
    verificar_leer_arch(caso, cls.prb_ingreso())


def verificar_leer_egr(caso, cls):
    verificar_leer_arch(caso, cls.prb_egreso())


def verificar_leer_arch(caso, info_prb):
    if info_prb:
        arch, f_leer = info_prb
        dic = f_leer(arch)

        ref = _obt_ref(arch, dic)
        caso.assertListEqual(dic, ref)


def _obt_ref(arch, d_auto):
    dir_, nombre = os.path.split(arch)
    arch_ref = os.path.join(dir_, 'ref', nombre + '.json')

    if not os.path.isfile(arch_ref):
        json.dump(d_auto, arch_ref)

    return json.load(arch_ref)
