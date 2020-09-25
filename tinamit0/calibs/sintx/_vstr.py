from lark import Tree
from lark.lexer import Token
from lark.visitors import Transformer_InPlace, Visitor
from ._vstr_transf import VstrATx


class TrnsfSubstNmbrs(Transformer_InPlace):
    def __init__(símismo, subst):
        símismo.subst = subst
        super().__init__()

    def var(símismo, x):
        try:
            sub = símismo.subst[x[0]]
            if isinstance(sub, str):
                return Tree('var', Token('NOMBRE', sub))
            else:
                return sub
        except KeyError:
            return Tree('var', x)


class VstrSacarVars(Visitor):
    def __init__(símismo):
        símismo.c_vars = set()

    def var(símismo, x):
        símismo.c_vars.add(str(x.children[0]))

    def __call__(símismo, árbol):
        símismo.c_vars.clear()
        símismo.visit(árbol)
        return símismo.c_vars


class VstrExtrArgs(Visitor):
    def __init__(símismo, f, i, dial):
        símismo.f = f
        símismo.i = i
        símismo.dial = dial
        símismo.args_f = None

    def func(símismo, x):
        if x.children[0] == símismo.f:
            símismo.args_f = [
                VstrATx(dialecto=símismo.dial).convertir(e) for e in x.children[1].children[:símismo.i]
            ]

    def __call__(símismo, árbol):
        símismo.args_f = None
        símismo.visit(árbol)
        return símismo.args_f


class VstrCoefDe(Visitor):
    def __init__(símismo):
        símismo.coef = None
        símismo.inv = None
        símismo.vr = None
        símismo.error = False
        símismo.núm = 0
        símismo.l_vars = []

    def _valid_consist(símismo, coef, inv):
        if símismo.coef is None:
            símismo.coef = coef
            símismo.inv = inv
        else:
            if símismo.coef != coef or símismo.inv != inv:
                símismo.error = True
        símismo.núm += 1

    def prod(símismo, x):
        coef = None
        op = x.children[1].children[0]
        args = [x.children[0], x.children[2]]
        for i, a in enumerate(args):
            if a.data == 'neg':
                a = a.children[0]
            if a.data == 'var':
                a = a.children[0]
            else:
                return

            args[i] = a

        if op == '*':
            inv = False

            if args[0] == símismo.vr and args[1] not in símismo.l_vars:
                coef = str(args[1])
            elif args[1] == símismo.vr and args[0] not in símismo.l_vars:
                coef = str(args[0])
        else:
            inv = True
            if args[0] == símismo.vr and args[1] not in símismo.l_vars:
                coef = str(args[1])
            elif args[1] == símismo.vr and args[0] not in símismo.l_vars:
                coef = str(args[0])

        if coef is not None:
            símismo._valid_consist(coef, inv)

    def __call__(símismo, árbol, var, l_vars=None):
        símismo.núm = 0
        símismo.vr = var
        símismo.coef = símismo.inv = None
        símismo.l_vars = [] if l_vars is None else l_vars
        símismo.visit(árbol)
        if símismo.error or símismo.coef is None:
            return None
        elif not (símismo.núm == VstrContarVar(símismo.coef)(árbol) == VstrContarVar(símismo.vr)(árbol)):
            return None
        else:
            return símismo.coef, símismo.inv


class VstrContarVar(Visitor):
    def __init__(símismo, var):
        símismo.vr = var
        símismo.cnt = 0

    def var(símismo, x):
        if x.children[0] == símismo.vr:
            símismo.cnt += 1

    def __call__(símismo, árbol):
        símismo.cnt = 0
        símismo.visit(árbol)
        return símismo.cnt
