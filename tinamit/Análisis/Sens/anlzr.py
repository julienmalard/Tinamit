
def anlzr_sens(líms_paráms, mstr_paráms, var_egr, método):
    prob = None
    sens = {}
    sens['prom'] = _calc_sens(prob, mstr=mstr_paráms, egr=None, método=método)
    sens['ajst'] = _calc_sens(prob, mstr=mstr_paráms, egr=None, método=método)

    return sens

def _calc_sens(prob, mstr, egr, método):

    if método == 'morris':
        sens = None
    elif método == 'fast':
        sens = None
    else:
        raise ValueError
    return sens

