import pandas as pd


class MiModelo(Modelo):
    def __init__(símismo, archivo):
        variables = leer_variables(archivo)
        super().__init__(variables)


mod = MiModelo()
mod.variables
mod.simular(10)

mod.simular(externos={
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': xr.DataArray()
})

mod = Conectado([Modelo1, Modelo2], conexiones=[
    Conex('var', 'var', Modelo1, Modelo2, transf=1.5),
    Conex('var1', 'var2', Modelo1, Modelo2, transf=RenombrarEjes('eje1', 'eje2'))
])
mod.simular(10)

ValsExternos = Externos({
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': xr.DataArray()
})
mod = Conectado([Modelo1, Externos])
mod.simular(10)
