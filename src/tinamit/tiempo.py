from datetime import datetime, date
from typing import Union, Optional, List

import pandas as pd

_conv_unids = {
    "año": {"delta": "years", "freq": "Y"},
    "mes": {"delta": "months", "freq": "M"},
    "semana": {"delta": "weeks", "freq": "W"},
    "día": {"delta": "days", "freq": "D"},
    "hora": {"delta": "hours", "freq": "H"},
    "minuto": {"delta": "minutes", "freq": "T"},
    "secundo": {"delta": "seconds", "freq": "S"},
    "microsecundo": {"delta": "microseconds", "freq": "U"},
    "nanosecundo": {"delta": "nanoseconds", "freq": "N"}
}


class EspecTiempo(object):
    def __init__(
            símismo,
            n_pasos: int,
            f_inic: Optional[Union[str, datetime, date, pd.Timestamp]] = None
    ):
        símismo.n_pasos = n_pasos
        símismo.f_inic: pd.Timestamp = pd.Timestamp(f_inic or datetime.now())


class Tiempo(object):
    def __init__(
            símismo,
            n_pasos: int,
            unids: Union[str, "UnidTiempo"],
            f_inic: pd.Timestamp
    ):
        símismo.n_pasos = n_pasos
        símismo.unids: UnidTiempo = unids if isinstance(unids, UnidTiempo) else UnidTiempo[unids]

        símismo.f_inic = f_inic
        símismo.eje = pd.date_range(símismo.f_inic, periods=n_pasos + 1, freq=símismo.unids.unid_freq)
        símismo.paso: int = 0

    def incr(símismo, n_pasos: int):
        símismo.paso = min(símismo.paso + n_pasos, símismo.n_pasos)

    def finalizar(símismo):
        símismo.paso = símismo.n_pasos

    @property
    def ahora(símismo) -> pd.Timestamp:
        return símismo.eje[símismo.paso]

    @property
    def terminado(símismo) -> bool:
        return símismo.paso == símismo.n_pasos


class UnidTiempo(object):
    def __init__(símismo, base: str, n: int = 1):
        símismo.base = base
        símismo.n = n

        try:
            símismo.unid_delta = _conv_unids[símismo.base.lower()]["delta"]
            símismo.unid_freq = _conv_unids[símismo.base.lower()]["freq"]
            símismo.unid_retallo = str(símismo.n) + símismo.unid_freq
        except KeyError:
            raise ValueError(
                "Unidad de tiempo `{u}` desconocida. Debe ser una de:\n\t* {l}".format(
                    u=símismo.base, l="\n\t* ".join(_conv_unids)
                )
            )

    def gen_tiempo(símismo, tiempo: Tiempo):
        n_pasos = conv_tiempo(tiempo.n_pasos, de=tiempo.unids, a=símismo, t=tiempo.f_inic)
        return Tiempo(
            n_pasos=n_pasos,
            unids=símismo,
            f_inic=tiempo.f_inic
        )


def conv_tiempo(n: int, de: UnidTiempo, a: UnidTiempo, t: pd.Timestamp) -> int:
    dif = t + pd.offsets.DateOffset(**{de.unid_delta: n * de.n}) - t
    return round(getattr(dif, a.unid_delta) / a.n)


def calc_tiempo_común(tiempos: List[UnidTiempo]) -> UnidTiempo:
    return sorted(tiempos, key=lambda x: conv_tiempo(
        1, de=x, a=UnidTiempo("nanosecundo"), t=pd.Timestamp(2000, 1, 1)
    ))[-1]


def gen_tiempo(tiempo: Union[int, EspecTiempo], unid_tiempo: Union[str, UnidTiempo]) -> Tiempo:
    if not isinstance(tiempo, EspecTiempo):
        tiempo = EspecTiempo(tiempo)

    return Tiempo(
        n_pasos=tiempo.n_pasos,
        unids=unid_tiempo,
        f_inic=tiempo.f_inic
    )
