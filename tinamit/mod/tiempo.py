from datetime import datetime, date, timedelta

from tinamit.config import _
from tinamit.unids.conv import convertir


class EjeTiempo(object):
    def __init__(símismo, t, unid_paso):
        if not isinstance(t, EspecTiempo):
            t = EspecTiempo(t)

        símismo.t_inic = t.t_inic
        símismo.tmñ_paso = t.tmñ_paso
        símismo.n_pasos = t.n_pasos
        símismo.paso_guardar = t.paso_guardar

        símismo.unid_paso = unid_paso

        símismo._convs = {}

        símismo.í = 0

    def fecha(símismo):
        if isinstance(símismo.t_inic, int):
            return None
        return símismo.t_inic + timedelta(**{_a_unid_python(símismo.unid_paso): símismo.í})

    def t_guardar(símismo):
        return not (símismo.í % símismo.paso_guardar)

    def pasos_avanzados(símismo, unid=None):
        if unid:
            if isinstance(símismo.t_inic, int):
                return símismo._obt_fact_conv(unid) * símismo.tmñ_paso
            else:
                raise NotImplementedError  # para hacer
        return símismo.tmñ_paso

    def avanzar(símismo):
        if símismo.í < símismo.n_pasos:
            símismo.í += símismo.tmñ_paso
            return símismo.í
        return False

    def _obt_fact_conv(símismo, unid):

        # Evitar buscar la misma unidad 2 veces porque la búsqueda puede ser lenta.
        try:
            return símismo._convs[unid]
        except KeyError:
            fact = convertir(de=símismo.unid_paso, a=unid, val=1)
            símismo._convs[unid] = fact
            return fact

    def __len__(símismo):
        return símismo.n_pasos + 1


class EspecTiempo(object):
    def __init__(símismo, n_pasos, t_inic=0, tmñ_paso=1, paso_guardar=None):
        símismo.t_inic = t_inic if isinstance(t_inic, int) else _gen_fecha(t_inic)

        símismo.tmñ_paso = tmñ_paso
        símismo.n_pasos = n_pasos
        símismo.paso_guardar = paso_guardar or tmñ_paso


def _gen_fecha(f):
    if f is None:
        return
    elif isinstance(f, str):
        return datetime.strptime(str, '%Y-%m-%d')
    elif isinstance(f, datetime):
        return f
    elif isinstance(f, date):
        return datetime(f.year, f.month, f.day)
    else:
        raise TypeError(type(f))


def _a_unid_python(unid):
    unid = unid.lower()
    aceptables = ['año', 'mes', 'día', 'hora', 'minuto', 'secundo']
    for u in aceptables:
        if unid == u:
            return unid
        try:
            factor = convertir(de=unid, a=u)
            if factor == 1:
                return u
        except (ValueError, KeyError):
            pass
    raise ValueError(
        _('La unidad de tiempo "{}" no se pudo convertir a años, meses, días, horas, minutos o secundos.').format(unid))
