import tkinter as tk

from tinamit.NuveoConectado import Conectado
from tinamit.Interfaz import Cajas as Cj
from tinamit.Interfaz import Formatos as Fm
from tinamit.Interfaz import Traducciones as Trad


class Apli(tk.Frame):
    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')

        pariente.geometry('%ix%i' % (Fm.ancho_ventana, Fm.altura_ventana))
        pariente.configure(background=Fm.col_fondo)
        pariente.minsize(width=Fm.ancho_ventana, height=Fm.altura_ventana)

        símismo.Modelo = Conectado()

        símismo.DicLeng = Trad.Diccionario()
        símismo.Trads = símismo.DicLeng.trads_act
        símismo.receta = {'conexiones': símismo.Modelo.conexiones}

        símismo.CajaInic = Cj.CajaInic(símismo)
        símismo.CajaCentral = Cj.CajaCentral(símismo)
        símismo.CajaLenguas = Cj.CajaLeng(símismo)
        símismo.CajaCentral.lift()
        símismo.CajaInic.lift()
        símismo.pack()


def correr():
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()


if __name__ == '__main__':
    correr()
