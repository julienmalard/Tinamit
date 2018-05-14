from tinamit.EnvolturaMDS.sintaxis import conv_fun
from tinamit.EnvolturaMDS.sintaxis import dic_funs_inv
from tinamit.EnvolturaMDS.sintaxis import dic_funs
from tinamit.EnvolturaMDS.sintaxis import Ecuación
from tinamit.EnvolturaMDS.sintaxis import _Transformador
from tinamit.EnvolturaMDS.sintaxis import cortar_líns
from tinamit.EnvolturaMDS.sintaxis import juntar_líns
from tinamit.EnvolturaMDS.sintaxis import sacar_arg
from tinamit.EnvolturaMDS.sintaxis import sacar_variables


class _Transformador(_Transformador):

    def num(x):
        return super().num()

    def neg(x):
        return super().neg()

    def var(x):
        return super().var()

    def nombre(x):
        return super().nombre()

    def cadena(x):
        return super().cadena()

    def func(x):
        return super().func()

    def pod(x):
        return super().pod()

    def mul(x):
        return super().mul()

    def div(x):
        return super().div()

    def suma(x):
        return super().suma()

    def sub(x):
        return super().sub()


class Ecuación(Ecuación):

    def variables(símismo):
        return super().variables()

    def gen_func_python(símismo, paráms):
        return super().gen_func_python(paráms=paráms)

    def gen_mod_bayes(símismo, paráms, líms_paráms, obs_x, obs_y, aprioris=None, binario=False):
        return super().gen_mod_bayes(paráms=paráms, líms_paráms=líms_paráms, obs_x=obs_x, obs_y=obs_y, aprioris=aprioris, binario=binario)

    def gen_texto(símismo, paráms=None):
        return super().gen_texto(paráms=paráms)

dic_funs = dic_funs

dic_funs_inv = dic_funs_inv
