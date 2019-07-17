import tkinter as tk

from tinamit.conect import Conectado

from tinamit.interfaz import Cajas as Cj
from tinamit.interfaz import Formatos as Fm
from tinamit.interfaz import Traducciones as Trad


class Apli(tk.Frame):
    """
    Aquí creamos la aplicación centra para el IGU.
    """

    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')

        pariente.geometry('%ix%i' % (Fm.ancho_ventana, Fm.altura_ventana))
        pariente.configure(background=Fm.col_fondo)
        # pariente.minsize(width=Fm.ancho_ventana, height=Fm.altura_ventana)

        símismo.Modelo = Conectado()

        símismo.DicLeng = Trad.Diccionario()
        símismo.Trads = símismo.DicLeng.trads_act
        símismo.receta = {'conexiones': símismo.Modelo.conexiones,
                          'conv_tiempo': símismo.Modelo.conv_tiempo_mods}
        símismo.ubic_archivo = None

        símismo.CajaInic = Cj.CajaInic(símismo)
        símismo.CajaCentral = Cj.CajaCentral(símismo)
        símismo.CajaLenguas = Cj.CajaLeng(símismo)
        símismo.CajaCentral.lift()
        símismo.CajaInic.lift()
        símismo.pack()


def correr():
    """
    Esta función empieza el interfaz.
    """

    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.lift()
    apli.mainloop()


# Si este fuente se ejecuta directamente (y no se importa), empezar el IGU.
if __name__ == '__main__':
    correr()
