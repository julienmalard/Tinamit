import json

import numpy as np
from SALib.sample import morris
from SALib.sample import fast_sampler


def muestrear_paráms(config, método):
    """
    sampling data from the selected senc método
    Parameters
    ----------
    método: e.g., Morris
    config:

    Returns
    -------
    sampled data
    """
    if 'num_vars' in config and 'names' in config and 'bounds' in config:

        problem = {
            'num_vars': config['num_vars'],
            'names': config['names'],
            'bounds': config['bounds']}
    else:
        raise ValueError

    if método == 'Morris':
        mstr = morris_sample(problem, config)
    elif método == 'Fast':
        mstr = fast_sample(problem, config)
    else:
        raise ValueError

    return mstr


def morris_sample(problem, config):
    """
    Conduct Morris samling
    Parameters
    ----------
    problem
    config: ranges, names, number of params need to be defined

    Returns
    -------
    samplied data using Morris método
    """
    if 'num_sample' in config and 'num_level' in config:

        param_values = morris.sample(problem, config['num_sample'], num_levels=config['num_level'],
                                     grid_jump=config['grid_jump'] if 'grid_jump' in config else config[
                                                                                                     'num_level'] / 2,
                                     optimal_trajectories=config[
                                         'optimal_trajectories'] if 'optimal_trajectories' in config else None)
        return {'Morris': param_values}
    else:
        raise ValueError('Parameters error!')
        return


def fast_sample(problem, config):
    if 'num_sample' in config:
        return {'Fast': fast_sampler.sample(problem, config['num_sample'])}
    else:
        raise ValueError('parameter error!')
        return

def guardar_mstr_paráms(muestrear_paráms, archivo):
    mstr_json = {c: [p.tolist() for p in d] for c, d in muestrear_paráms.items()}

    with open(archivo, 'w', encoding='UTF-8') as d:
        json.dump(mstr_json, d, ensure_ascii=False)


def cargar_mstr_paráms(archivo):
    with open(archivo, encoding='UTF-8') as d:
        mstr_json = json.load(d)

    mstr = {c: [np.array(p) for p in d] for c, d in mstr_json.items()}
    return mstr

    # def muestrear_paráms(líms_paráms, mapa_paráms, método):


#     prob = None
#
#     if método == 'Morris':
#         mstr = morris.sample()
#     elif método == 'Fast':
#         pass
#     else:
#         raise ValueError
#
#     return mstr
#
# np.array([1]).tolist()

# def guardar_mstr_paráms(sample, archivo):
#
#     mstr_json = {c: {p: (v.tolist()) for p, v in d.items()} for c, d in sample.items()}
#
#     with open(archivo, 'w', encoding='UTF-8') as d:
#         json.dump(mstr_json, d, ensure_ascii=False)


# def cargar_mstr_paráms(archivo):
#
    # with open(archivo, encoding='UTF-8') as d:
    #     mstr_json = json.load(d)
#
#     mstr = {c: {p: np.array(v) for p, v in d.items()} for c, d in mstr_json.items()}
#     return mstr
