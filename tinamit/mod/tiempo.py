from datetime import datetime, date, timedelta


class EjeTiempo(object):
    def __init__(símismo, t_inic, n_pasos, paso, unid_paso, paso_guardar=None):
        símismo.t_inic = t_inic

        símismo.paso = paso
        símismo.n_pasos = n_pasos
        símismo.unid_paso = unid_paso
        símismo.paso_guardar = paso_guardar

    def avanzar(símismo):



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
