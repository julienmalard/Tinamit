from unittest import TestCase

import pandas as pd
import xarray as xr

from fnt.tinamit3 import Conectado
from fnt.tinamit3 import ConexiónVars
from fnt.tinamit3.envolt.clima import Clima
from fnt.tinamit3.externos import Externos
from fnt.tinamit3 import GrupoCombinador
from fnt.tinamit3.modelo import Modelo
from fnt.tinamit3.resultados import RenombrarEjes


class PruebaModelo(TestCase):
    pass


class PruebaExterno(TestCase):
    pass


class PruebaClima(TestCase):
    pass


class PruebaConectado(TestCase):
    pass


class MiModelo(Modelo):
    def __init__(símismo, archivo):
        variables = leer_variables(archivo)
        super().__init__(variables)


mod = MiModelo()
mod.variables
mod.simular(10)

externos = Externos({
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': pd.DataFrame([1, 2, 3], index=[0, 2, 3]),
    'e': xr.DataArray()
})

mod.simular(10, extras=[externos])

mod.conectar_clima('Lluvia', 'lluvia')

mod.simular(50, extras=Clima('8.5'))

simul = mod.iniciar(10, extras=externos)
simul.incr(2)
simul.cerrar()
res = simul.resultados()

mod2 = Conectado("conectado", [Modelo1, Modelo2], conex=[
    ConexiónVars('var', 'var', Modelo1, Modelo2, transf=1.5),
    ConexiónVars('var1', 'var2', Modelo1, Modelo2, transf=RenombrarEjes({'eje1': 'eje2'}))
])
mod2.simular(10)

ValsExternos = Externos({
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': xr.DataArray()
})
mod = Conectado("otro conectado", [Modelo1])
mod.simular(10, extras=[ValsExternos])

Geografía().simular(mod)

GrupoCombinador([ValsExternos], [Clima(x) for x in {'0', '2.6', '4.5', '6.0', '8.5'}]).simular(mod, 100)
