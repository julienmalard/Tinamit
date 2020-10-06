from datetime import datetime, date
from typing import Union, Optional, List

import numpy as np
import pandas as pd

_conv_unids = {
    "año": {"delta": "years", "freq_pd": "Y", "freq_np": "Y"},
    "mes": {"delta": "months", "freq_pd": "M", "freq_np": "M"},
    "semana": {"delta": "weeks", "freq_pd": "W", "freq_np": "W"},
    "día": {"delta": "days", "freq_pd": "D", "freq_np": "D"},
    "hora": {"delta": "hours", "freq_pd": "H", "freq_np": "h"},
    "minuto": {"delta": "minutes", "freq_pd": "T", "freq_np": "m"},
    "secundo": {"delta": "seconds", "freq_pd": "S", "freq_np": "s"},
    "microsecundo": {"delta": "microseconds", "freq_pd": "U", "freq_np": "us"},
    "nanosecundo": {"delta": "nanoseconds", "freq_pd": "N", "freq_np": "ns"}
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

        freq = pd.DateOffset(**{símismo.unids.unid_delta: símismo.unids.n})
        símismo.eje = pd.date_range(símismo.f_inic, periods=n_pasos + 1, freq=freq)
        símismo.paso: int = 0

    def incr(símismo, n_pasos: int):
        símismo.paso = min(símismo.paso + n_pasos, símismo.n_pasos)

    def finalizar(símismo):
        símismo.paso = símismo.n_pasos

    @property
    def ahora(símismo) -> pd.Timestamp:
        return símismo.eje[símismo.paso]

    @property
    def próximo(símismo) -> pd.Timestamp:
        if símismo.terminado:
            raise ValueError('Tiempo ya finnalizado.')
        return símismo.eje[símismo.paso + 1]

    @property
    def terminado(símismo) -> bool:
        return símismo.paso == símismo.n_pasos


class UnidTiempo(object):
    def __init__(símismo, base: str, n: int = 1):
        símismo.base = base
        símismo.n = n

        try:
            base = símismo.base.lower()
            símismo.unid_delta = _conv_unids[base]["delta"]
            símismo.unid_freq_pd = _conv_unids[base]["freq_pd"]
            símismo.unid_freq_np = _conv_unids[base]["freq_np"]
        except KeyError:
            raise ValueError(
                "Unidad de tiempo `{u}` desconocida. Debe ser una de:\n\t* {l}".format(
                    u=símismo.base, l="\n\t* ".join(_conv_unids)
                )
            )
        símismo.unid_retallo = str(símismo.n) + símismo.unid_freq_pd

    def gen_tiempo(símismo, tiempo: Tiempo):
        n_pasos = conv_tiempo(tiempo.n_pasos, de=tiempo.unids, a=símismo, t=tiempo.f_inic)
        return Tiempo(
            n_pasos=n_pasos,
            unids=símismo,
            f_inic=tiempo.f_inic
        )


def conv_tiempo(n: int, de: UnidTiempo, a: UnidTiempo, t: pd.Timestamp) -> int:
    dif = t + pd.offsets.DateOffset(**{de.unid_delta: n * de.n}) - t

    return round(dif / np.timedelta64(1, a.unid_freq_np) / a.n)


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
