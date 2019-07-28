import os

import numpy as np
import shapefile as sf
from matplotlib import colors, cm
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from matplotlib.axes import Axes
import matplotlib.pyplot as dib
from tinamit.config import _
from tinamit.cositas import detectar_codif

from ..mod import ResultadosSimul, ResultadosGrupo


def dibujar_mapa(formas, archivo=None, título=None, fig=None):
    """
    Dibuja un mapa.

    Parameters
    ----------
    formas: list of Forma
        Las formas para incluir.
    archivo: str
        Dónde hay que guardar el gráfico. Si es ``None``, no se guardará el gráfico.
    título: str
        El título del mapa.
    fig: matplotlib.Figure
        Figura para dibujar el mapa.

    Returns
    -------
    tuple[Figure, Axes]
        La figura y sus ejes.
    """

    formas = [formas] if isinstance(formas, Forma) else formas

    if not fig:
        fig = Figura()
        TelaFigura(fig)
    ejes = fig.add_subplot(111)
    ejes.set_aspect('equal')

    for frm in formas:
        frm.dibujar(ejes, fig)
    if título is not None:
        ejes.set_title(título)
    if archivo:
        fig.savefig(archivo, dpi=500)

    return fig, ejes


def dibujar_mapa_de_res(
        forma_dinámica, res, var, t, escala=None, título='', directorio=None, otras_formas=None
):
    """
    Dibujar los resultados de una simulación en un mapa.

    Parameters
    ----------
    forma_dinámica: FormaDinámica
        La forma cuyos colores variarán según los resultados.
    res: ResultadosSimul or ResultadosGrupo
        Los resultados para dibujar.
    var: str
        El variable de interés.
    t: int or tuple or range or list
        Los tiempos a los cuales queremos graficar los resultados.
    escala: tuple
        El rango para aplicar colores. Si es ``None``, se aplicará según los datos de los resultados.
    título: str
        El título del gráfico.
    directorio: str
        Dónnde hay que guardar el gráfico.
    otras_formas: list of FormaEstática or FormaEstática
        Las otras formas (estáticas) para incluir en el gráfico.

    """
    título = título or res.nombre
    otras_formas = otras_formas or []
    if isinstance(otras_formas, FormaEstática):
        otras_formas = [otras_formas]

    def _extr_i(matr, i):
        return matr[i] if isinstance(i, int) else matr.sel(**{_('fecha'): i}).values

    if isinstance(res, ResultadosSimul):
        res_var = res[var].vals
        unids = res[var].var.unid

        escala = escala or (np.min(res_var.values), np.max(res_var.values))

        def _extr_res_i(i):
            return _extr_i(res_var, i)

    else:

        unids = list(res.values())[0][var].var.unid

        todos_vals = np.array([res_lg[var].vals for res_lg in res.values()])
        escala = escala or (np.min(todos_vals), np.max(todos_vals))

        def _extr_res_i(i):
            return {lg: _extr_i(res_lg[var].vals, i) for lg, res_lg in res.items()}

    if isinstance(t, int):
        pasos = range(t, t + 1)
    else:
        pasos = t

    for i_p in pasos:
        título_i = '{}_{}'.format(título, i_p)
        res_i = _extr_res_i(i_p)
        forma_dinámica.estab_valores(res_i, escala_valores=escala, unidades=unids)

        arch_i = os.path.join(directorio, título_i) if directorio is not None else None
        fig_i = None if directorio else dib.figure()
        dibujar_mapa([forma_dinámica, *otras_formas], archivo=arch_i, título=título_i, fig=fig_i)


class Forma(object):
    """
    Clase pariente para todas las formas que se pueden dibujar.
    """
    def __init__(símismo, archivo, llenar, alpha):
        codif = detectar_codif(os.path.splitext(archivo)[0] + '.dbf')
        símismo.forma = sf.Reader(archivo, encoding=codif)
        símismo.llenar = llenar
        símismo.alpha = alpha

    def dibujar(símismo, ejes, fig):
        """
        Agrega la forma a la figura.

        Parameters
        ----------
        ejes:
            Los ejes de la figura.
        fig:
            La figura.

        """
        raise NotImplementedError

    def _dibujar_frm(símismo, ejes, color):
        for i, frm in enumerate(símismo.forma.shapes()):
            puntos = frm.points
            partes = frm.parts

            for ip, i0 in enumerate(partes):  # Para cada parte del imagen

                if ip < len(partes) - 1:
                    i1 = partes[ip + 1] - 1
                else:
                    i1 = len(puntos)

                seg = puntos[i0:i1 + 1]
                x_lon = np.zeros((len(seg), 1))
                y_lat = np.zeros((len(seg), 1))
                for j in range(len(seg)):
                    x_lon[j] = seg[j][0]
                    y_lat[j] = seg[j][1]

                clr = color[i] if isinstance(color, np.ndarray) else color
                if símismo.llenar:
                    ejes.fill(x_lon, y_lat, color=clr, alpha=símismo.alpha)
                else:
                    ejes.plot(x_lon, y_lat, color=clr, alpha=símismo.alpha)


class FormaEstática(Forma):
    """
    Clase de base para formas estáticas en el mapa, cuyos colores no cambian.
    """

    def __init__(símismo, archivo, color, llenar, alpha):
        símismo.color = color
        super().__init__(archivo, llenar=llenar, alpha=alpha)

    def dibujar(símismo, ejes, fig):
        símismo._dibujar_frm(ejes, color=símismo.color)


class FormaDinámica(Forma):
    """
    Forma cuyos colores se asignan según valores numéricos.
    """

    def __init__(símismo, archivo, escala_colores=None, llenar=True, alpha=1):
        """

        Parameters
        ----------
        archivo: str
            El archivo ``.shp``.
        escala_colores: list or tuple or str or int or None
            Lista de dos colores para establecer una escala de colores. Si es un solo color, se agregará el color
            blanco. Si es ``-1``, se inverserán los colores automáticos.
        llenar: bool
            Si hay que llenar la forma o simplement delinear su contorno.
        alpha: float or int
            La opacidad del interior de la forma. Solamente aplica si ``llenar`` est ``False``.
        """
        super().__init__(archivo, llenar=llenar, alpha=alpha)

        símismo.escala_colores = símismo._resolver_colores(escala_colores)
        símismo.valores = np.full(len(símismo.forma.shapes()), np.nan)
        símismo.unidades = None
        símismo.escala = None

    def estab_valores(símismo, valores, escala_valores=None, unidades=None):
        """
        Establece los valores para colorar.

        Parameters
        ----------
        valores: np.ndarray or dict
            Los valores para dibujar. Debe ser del mismo tamaño que el archivo ``.shp`` en ``archivo``.
        escala_valores: tuple or list or None
            La escala para el rango de colores. Si es ``None``, se ajustará el rango según de los valores dados.
        unidades: str, optional
            Las unidades.
        """
        símismo.unidades = unidades

        símismo._llenar_valores(valores)

        if escala_valores is None:
            if np.all(np.isnan(símismo.valores)):
                escala_valores = (0, 1)
            else:
                escala_valores = (np.nanmin(símismo.valores), np.nanmax(símismo.valores))
                if escala_valores[0] == escala_valores[1]:
                    escala_valores = (escala_valores[0] - 0.5, escala_valores[0] + 0.5)

        símismo.escala = escala_valores

    def dibujar(símismo, ejes, fig):
        vals_norm = (símismo.valores - símismo.escala[0]) / (símismo.escala[1] - símismo.escala[0])

        d_clrs = _gen_d_mapacolores(colores=símismo.escala_colores)

        mapa_color = colors.LinearSegmentedColormap('mapa_color', d_clrs)
        norm = colors.Normalize(vmin=símismo.escala[0], vmax=símismo.escala[1])
        cpick = cm.ScalarMappable(norm=norm, cmap=mapa_color)
        cpick.set_array(np.array([]))

        v_cols = mapa_color(vals_norm)
        v_cols[np.isnan(vals_norm)] = 1

        símismo._dibujar_frm(ejes=ejes, color=v_cols)

        if símismo.unidades is not None:
            fig.colorbar(cpick, label=símismo.unidades)
        else:
            fig.colorbar(cpick)

    @staticmethod
    def _resolver_colores(colores):
        if colores is None:
            return ['#FF6666', '#FFCC66', '#00CC66']
        elif colores == -1:
            return ['#00CC66', '#FFCC66', '#FF6666']
        elif isinstance(colores, str):
            return ['#FFFFFF', colores]
        return colores

    def _extraer_col(símismo, col):
        nombres_attr = [field[0] for field in símismo.forma.fields[1:]]
        try:
            return [x.record[nombres_attr.index(col)] for x in símismo.forma.shapeRecords()]
        except ValueError:
            raise ValueError(_('La columna "{}" no existe en la base de datos.').format(col))

    def _llenar_valores(símismo, valores):
        raise NotImplementedError


class FormaDinámicaNumérica(FormaDinámica):
    """
    Forma dinámica cuyos valores se asignan a los polígonos de la forma ``.shp`` por su orden en la matriz de valores.
    """

    def __init__(símismo, archivo, col_id=None, escala_colores=None, llenar=True, alpha=1):
        """

        Parameters
        ----------
        archivo: str
            El archivo ``.shp``.
        col_id: str, optional
            La columna con el número de cada polígono en la forma ``.shp``. Si es ``None``, se asiñará número según
            su orden en la forma ``.shp``.
        escala_colores: list or tuple or str or int or None
            Lista de dos colores para establecer una escala de colores. Si es un solo color, se agregará el color
            blanco. Si es ``-1``, se inverserán los colores automáticos.
        llenar: bool
            Si hay que llenar la forma o simplement delinear su contorno.
        alpha: float or int
            La opacidad del interior de la forma. Solamente aplica si ``llenar`` est ``False``.
        """
        super().__init__(archivo, escala_colores, llenar, alpha)

        if col_id is not None:
            ids = np.array(símismo._extraer_col(col_id))
            símismo.ids = ids - np.min(ids)
        else:
            símismo.ids = None

    def _llenar_valores(símismo, valores):
        if símismo.ids is None:
            símismo.valores[:] = valores
        else:
            símismo.valores[:] = valores[símismo.ids]


class FormaDinámicaNombrada(FormaDinámica):
    """
    Forma dinámica cuyos valores se asignan a los polígonos de la forma ``.shp`` por su llave en el diccionario de
    valores.
    """

    def __init__(símismo, archivo, col_id, escala_colores=None, llenar=True, alpha=1):
        """

        Parameters
        ----------
        archivo: str
            La archivo ``.shp``.
        col_id: str
            La columna en el archivo ``.shp`` con el nomrbe de cada polígono.
        escala_colores: list or tuple or str or int or None
            Lista de dos colores para establecer una escala de colores. Si es un solo color, se agregará el color
            blanco. Si es ``-1``, se inverserán los colores automáticos.
        llenar: bool
            Si hay que llenar la forma o simplement delinear su contorno.
        alpha: float or int
            La opacidad del interior de la forma. Solamente aplica si ``llenar`` est ``False``.
        """
        super().__init__(archivo, escala_colores, llenar, alpha)
        símismo.ids = [str(x) for x in símismo._extraer_col(col_id)]

    def _llenar_valores(símismo, valores):
        símismo.valores[:] = np.nan
        for id_, val in valores.items():
            i = símismo.ids.index(id_)
            símismo.valores[i] = val


class Agua(FormaEstática):
    """
    Representa áreas de agua.
    """

    def __init__(símismo, archivo, llenar=True):
        """

        Parameters
        ----------
        archivo: str
            El archivo ``.shp``.
        llenar: bool
            Si hay que llenar el cuerpo de agua o no.
        """
        super().__init__(archivo=archivo, color='#13A6DD', llenar=llenar, alpha=0.5)


class Bosque(FormaEstática):
    """
    Representa áreas con bosque.
    """

    def __init__(símismo, archivo):
        super().__init__(archivo=archivo, color='#33A02C', llenar=True, alpha=0.7)


class Calle(FormaEstática):
    """
    Representa calles.
    """

    def __init__(símismo, archivo):
        super().__init__(archivo=archivo, color='#585763', llenar=False, alpha=1)


class Ciudad(FormaEstática):
    """
    Representa áreas urbanas.
    """

    def __init__(símismo, archivo):
        super().__init__(archivo=archivo, color='#FB9A99', llenar=True, alpha=1)


class OtraForma(FormaEstática):
    """
    Representa otras áreas no representadas por las otras formas disonibles.
    """

    def __init__(símismo, archivo):
        super().__init__(archivo=archivo, color='#FFECB3', llenar=True, alpha=1)


def _hex_a_rva(hx):
    """
    Convierte colores RVA a Hex.

    Parameters
    ----------
    hx: str
        El valor hex.

    Returns
    -------
    tuple
        El valor rva.
    """
    return tuple(int(hx.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


def _gen_d_mapacolores(colores):
    """
    Genera un diccionario de mapa de color para MatPlotLib.

    Parameters
    ----------
    colores: list
        Una lista de colores

    Returns
    -------
    dict
        Un diccionario para MatPlotLib
    """

    clrs_rva = [_hex_a_rva(x) for x in colores]
    # noinspection PyTypeChecker
    n_colores = len(colores)

    dic_c = {'red': tuple((round(i / (n_colores - 1), 2), clrs_rva[i][0] / 255, clrs_rva[i][0] / 255) for i in
                          range(0, n_colores)),
             'green': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][1] / 255, clrs_rva[i][1] / 255) for i in
                 range(0, n_colores)),
             'blue': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][2] / 255, clrs_rva[i][2] / 255) for i in
                 range(0, n_colores))}

    return dic_c
