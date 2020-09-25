from tinamit.config import _

from ._funcs import conv_fun


class VstrAPyMC3(object):
    def __init__(símismo, d_vars_pm, obs_x, í_datos, dialecto='tinamït'):
        símismo.d_vars_pm = d_vars_pm
        símismo.í_datos = í_datos
        símismo.obs_x = obs_x

        símismo.dialecto = dialecto

    def func(símismo, x):
        fun = conv_fun(x.children[0], símismo.dialecto, 'pm')  # Traducir la función a PyMC3
        args = [símismo.convertir(a) for a in
                x.children[1].children]  # Recursar a través de los argumentos de la función

        # Devolver la función dinámica
        return fun(*args)

    def neg(símismo, x):
        return -símismo.convertir(x.children[0])

    def var(símismo, x):
        v = str(x.children[0])
        try:
            if símismo.í_datos is None:
                return símismo.d_vars_pm[v]
            else:
                return símismo.d_vars_pm[v][símismo.í_datos]

        except KeyError:
            # Si el variable no es un parámetro calibrable, debe ser un valor observado
            try:
                return símismo.obs_x[v].values

            except KeyError:
                raise ValueError(_('El variable "{}" no es un parámetro, y no se encuentra'
                                   'en la base de datos observados tampoco.').format(v))

    def num(símismo, x):
        return float(x.children[0])

    def prod(símismo, x):
        # Recursar a través de los componentes del operador ahora. Es importante hacerlo antes de
        # las expresiones ``lambda``; sino se llamará `transformar()` sí mismo cada vez que se llama
        # la función generada.
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '*':
            return comp_1 * comp_2
        elif op == '/':
            return comp_1 / comp_2
        else:
            raise ValueError(op)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '+':
            return comp_1 + comp_2
        elif op == '-':
            return comp_1 - comp_2
        else:
            raise ValueError(op)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[1])
        return comp_1 ** comp_2

    def comp(símismo, x):
        import pymc3 as pm

        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '>':
            return pm.math.gt(comp_1, comp_2)
        elif op == '<':
            return pm.math.lt(comp_1, comp_2)
        elif op == '>=':
            return pm.math.ge(comp_1, comp_2)
        elif op == '<=':
            return pm.math.le(comp_1, comp_2)
        elif op == '==':
            return pm.math.eq(comp_1, comp_2)
        elif op == '!=':
            return pm.math.neq(comp_1, comp_2)
        else:
            # Si no sabemos lo que tenemos, hay error.
            raise ValueError(op)

    def op_comp(símismo, x):
        return str(x.children[0])

    def convertir(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class VstrAPy(object):
    def __init__(símismo, l_prms, dialecto):
        símismo.l_prms = l_prms
        símismo.dialecto = dialecto

    def func(símismo, x):
        fun = conv_fun(x.children[0], símismo.dialecto, 'python')  # Traducir la función a Python
        comp = [símismo.convertir(a) for a in
                x.children[1].children]  # Recursar a través de los argumentos de la función

        # Devolver la función dinámica
        return lambda p, vr: fun(*[a(p=p, vr=vr) for a in comp])

    def neg(símismo, x):
        comp = símismo.convertir(x.children[0])
        return lambda p, vr: -comp(p=p, vr=vr)

    def var(símismo, x):
        v = str(x.children[0])
        try:
            # Si el variable existe en la lista de parámetros, obtenerlo de `p`.
            í_var = símismo.l_prms.index(v)

            return lambda p, vr: p[í_var]

        except ValueError:
            # Si el variable no es un parámetro calibrable, debe ser un valor observado.
            return lambda p, vr: vr[v]

    def num(símismo, x):
        return lambda p, vr: float(x.children[0])

    def prod(símismo, x):
        # Recursar a través de los componentes del operador ahora. Es importante hacerlo antes de
        # las expresiones ``lambda``; sino se llamará `transformar()` sí mismo cada vez que se llama
        # la función generada.
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '*':
            return lambda p, vr: comp_1(p=p, vr=vr) * comp_2(p=p, vr=vr)
        elif op == '/':
            return lambda p, vr: comp_1(p=p, vr=vr) / comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '+':
            return lambda p, vr: comp_1(p=p, vr=vr) + comp_2(p=p, vr=vr)
        elif op == '-':
            return lambda p, vr: comp_1(p=p, vr=vr) - comp_2(p=p, vr=vr)
        else:
            raise ValueError(op)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[1])
        return lambda p, vr: comp_1(p=p, vr=vr) ** comp_2(p=p, vr=vr)

    def comp(símismo, x):
        comp_1 = símismo.convertir(x.children[0])
        comp_2 = símismo.convertir(x.children[2])
        op = símismo.convertir(x.children[1])

        if op == '>':
            return lambda p, vr: comp_1(p=p, vr=vr) > comp_2(p=p, vr=vr)
        elif op == '<':
            return lambda p, vr: comp_1(p=p, vr=vr) < comp_2(p=p, vr=vr)
        elif op == '>=':
            return lambda p, vr: comp_1(p=p, vr=vr) >= comp_2(p=p, vr=vr)
        elif op == '<=':
            return lambda p, vr: comp_1(p=p, vr=vr) <= comp_2(p=p, vr=vr)
        elif op == '==':
            return lambda p, vr: comp_1(p=p, vr=vr) == comp_2(p=p, vr=vr)
        elif op == '!=':
            return lambda p, vr: comp_1(p=p, vr=vr) != comp_2(p=p, vr=vr)
        else:
            # Si no sabemos lo que tenemos, hay error.
            raise ValueError(op)

    def op_comp(símismo, x):
        return str(x.children[0])

    def convertir(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)


class VstrATx(object):
    def __init__(símismo, dialecto):
        símismo.dialecto = dialecto

    def func(símismo, x):
        args = [símismo.convertir(a) for a in x.children[1].children]
        if len(args) != 1:
            return str(x.children[0]) + '(' + ', '.join(args) + ')'
        elif len(args) == 1:
            return str(x.children[0]) + '(' + args[0] + ')'

    def neg(símismo, x):
        return '-' + símismo.convertir(x.children[0])

    def var(símismo, x):
        return str(x.children[0])

    def num(símismo, x):
        return str(x.children[0])

    def prod(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_prod(símismo, x):
        return str(x.children[0])

    def suma(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_suma(símismo, x):
        return str(x.children[0])

    def pod(símismo, x):
        return símismo.convertir(x.children[0]) + '^' + símismo.convertir(x.children[1])

    def comp(símismo, x):
        return ''.join(símismo.convertir(a) for a in x.children)

    def op_comp(símismo, x):
        return str(x.children[0])

    def convertir(símismo, árbol):
        if hasattr(símismo, árbol.data):
            return getattr(símismo, árbol.data)(árbol)
        else:
            raise TypeError(árbol.data)
