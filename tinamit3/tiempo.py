from datetime import datetime, date


class Tiempo(object):
    def __init__(símismo):
        pass


class TiempoCaléndrico(object):
    def __init__(símismo):
        pass



class EspecTiempo(object):
    """
    Objeto para especificar opciones de tiempo para la simulación.
    """
    def __init__(símismo, n_pasos, f_inic=None, tmñ_paso=1, guardar=1, intercambiar=1):
        """

        Parameters
        ----------
        n_pasos: int
            El número de pasos en la simulación.
        f_inic: str or datetime.datetime or datetime.date
            La fecha inicial, si hay.
        tmñ_paso: int
            El tamaño de cada paso.
        guardar:
            La frecuencia para guardar resultados.
        intercambiar:
            La frecuencia para intercambiar valores entre modelos (solamente para modelos conectados).
        """

        if (int(tmñ_paso) != tmñ_paso) or (tmñ_paso < 1):
            raise ValueError(_('`tmñ_paso` debe ser un número entero superior a 0.'))
        símismo.f_inic = _gen_fecha(f_inic)

        símismo.tmñ_paso = tmñ_paso
        símismo.n_pasos = n_pasos
        símismo.guardar = guardar
        símismo.intercambiar = intercambiar

    def gen_tiempo(símismo, unid_paso):
        """
        Genera un objeto :class:`Tiempo` con las especificaciones.

        Parameters
        ----------
        unid_paso: str
            La unidad de paso de la simulación.

        Returns
        -------
        Tiempo

        """
        if símismo.f_inic:
            return TiempoCaléndrico(t=símismo, unid_paso=unid_paso)
        else:
            return Tiempo(t=símismo, unid_paso=unid_paso)



def _gen_fecha(f):
    if f is None:
        return
    elif isinstance(f, str):
        return datetime.strptime(f, '%Y-%m-%d')
    elif isinstance(f, datetime):
        return f
    elif isinstance(f, date):
        return datetime(f.year, f.month, f.day)
    else:
        raise TypeError(type(f))
