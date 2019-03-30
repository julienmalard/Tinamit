from datetime import datetime, date, timedelta


class Tiempo(object):
    def __init__(símismo, n_días, f_inic=None, paso=1):
        símismo._f_inic = _gen_fecha(f_inic)
        símismo._día = 0
        símismo.paso = paso
        símismo._n_días = n_días

    def n_pasos(símismo):
        return len(símismo.eje)

    def avanzar(símismo):
        símismo._día += símismo.paso
        return símismo._día <= símismo._n_días

    def fecha(símismo):
        if símismo._f_inic is not None:
            return símismo._f_inic + timedelta(days=símismo._día)

    def día(símismo):
        return símismo._día

    def reinic(símismo):
        símismo._día = 0

    def __len__(símismo):
        return len(símismo.eje)


def _gen_fecha(f):
    if f is None:
        return
    elif isinstance(f, str):
        return datetime.strptime(str, '%Y-%m-%d')
    elif isinstance(f, date):
        return f
    elif isinstance(f, datetime):
        return f.date()
    else:
        raise TypeError(type(f))
