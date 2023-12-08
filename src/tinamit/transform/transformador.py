class Transformador(object):
    def __init__(símismo, f: Callable[[xr.DataArray], xr.DataArray]):
        símismo.f = f

    def __call__(símismo, val: xr.DataArray) -> xr.DataArray:
        return símismo.f(val)

    def __add__(símismo, otro: Callable):
        return Transformador(f=lambda x: símismo.f(otro(x)))


