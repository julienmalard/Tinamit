import math as mat
try:
    import pymc3 as pm
    import theano.tensor as t
except ImportError:  # pragma: sin cobertura
    pm = t = None

# Funciones auxiliares para ecuaciones.

# Un diccionario con conversiones de funciones reconocidas. Si quieres activar más funciones, agregarlas aqui.
_dic_funs = {
    'mín': {'vensim': 'MIN', 'pm': pm.math.minimum if pm is not None else None, 'python': min},
    'máx': {'vensim': 'MAX', 'pm': pm.math.maximum if pm is not None else None, 'python': max},
    'abs': {'vensim': 'ABS', 'pm': pm.math.abs_ if pm is not None else None, 'python': abs},
    'exp': {'vensim': 'EXP', 'pm': pm.math.exp if pm is not None else None, 'python': mat.exp},
    'ent': {'vensim': 'INTEGER', 'pm': pm.math.floor if pm is not None else None, 'python': int},
    'rcd': {'vensim': 'SQRT', 'pm': pm.math.sqrt if pm is not None else None, 'python': mat.sqrt},
    'ln': {'vensim': 'LN', 'pm': pm.math.log if pm is not None else None, 'python': mat.log},
    'log': {'vensim': 'LOG', 'pm': None if pm is None else lambda x: pm.math.log(x) / mat.log(10), 'python': mat.log10},
    'sin': {'vensim': 'SIN', 'pm': pm.math.sin if pm is not None else None, 'python': mat.sin},
    'cos': {'vensim': 'COS', 'pm': pm.math.cos if pm is not None else None, 'python': mat.cos},
    'tan': {'vensim': 'TAN', 'pm': pm.math.tan if pm is not None else None, 'python': mat.tan},
    'sinh': {'vensim': 'SINH', 'pm': pm.math.sinh if pm is not None else None, 'python': mat.sinh},
    'cosh': {'vensim': 'COSH', 'pm': pm.math.cosh if pm is not None else None, 'python': mat.cosh},
    'tanh': {'vensim': 'TANH', 'pm': pm.math.tanh if pm is not None else None, 'python': mat.tanh},
    'asin': {'vensim': 'ARCSIN', 'pm': t.arcsin if t is not None else None, 'python': mat.asin},
    'acos': {'vensim': 'ARCCOS', 'pm': t.arccos if t is not None else None, 'python': mat.acos},
    'atan': {'vensim': 'ARCTAN', 'pm': t.arctan if t is not None else None, 'python': mat.atan},
    'si_sino': {'vensim': 'IF THEN ELSE', 'pm': pm.math.switch if pm is not None else None,
                'python': lambda cond, si, sino: si if cond else sino}
}

# Diccionario de operadores. Notar que algunos se traducen por funciones en PyMC3.
_dic_ops = {
    '>': {'vensim': '>', 'pm': pm.math.gt if pm is not None else None},
    '<': {'vensim': '<', 'pm': pm.math.lt if pm is not None else None},
    '>=': {'vensim': '>=', 'pm': pm.math.ge if pm is not None else None},
    '<=': {'vensim': '<=', 'pm': pm.math.le if pm is not None else None},
    '==': {'vensim': '=', 'pm': pm.math.eq if pm is not None else None},
    '!=': {'vensim': '<>', 'pm': pm.math.neq if pm is not None else None},
    '+': {'vensim': '+'},
    '-': {'vensim': '-'},
    '*': {'vensim': '*'},
    '^': {'vensim': '^'},
    '/': {'vensim': '/'}
}


def conv_fun(fun, dialecto_orig, dialecto_final):
    """
    Traduce una función a otro dialecto.

    Parameters
    ----------
    fun: str
        La función para traducir.
    dialecto_orig: str
        El dialecto original de la función.
    dialecto_final: str
        El dialecto final deseado.

    Returns
    -------
    str | Callable
        La función traducida.
    """

    if dialecto_final == dialecto_orig:
        return fun
    if dialecto_orig == 'tinamït':
        return _dic_funs[fun][dialecto_final]
    else:
        if dialecto_final == 'tinamït':
            return next(ll for ll, d in _dic_funs.items() if d[dialecto_orig] == fun)
        else:
            return next(d[dialecto_final] for ll, d in _dic_funs.items() if d[dialecto_orig] == fun)


def conv_op(oper, dialecto_orig, dialecto_final):
    """
    Traduce un operador a otro dialecto.

    Parameters
    ----------
    oper: str
        El operador para traducir.
    dialecto_orig: str
        El dialecto original del operador.
    dialecto_final: str
        El dialecto final deseado.

    Returns
    -------
    str | Callable
        El operador traducido.
    """

    if dialecto_final == dialecto_orig:
        return oper
    if dialecto_orig == 'tinamït':
        return _dic_ops[oper][dialecto_final]
    else:
        if dialecto_final == 'tinamït':
            return next(ll for ll, d in _dic_ops.items() if d[dialecto_orig] == oper)
        else:
            return next(d[dialecto_final] for ll, d in _dic_ops.items() if d[dialecto_orig] == oper)
