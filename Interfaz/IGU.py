import tkinter as tk

from Interfaz import Formatos as Fm
from Interfaz import Traducciones as Trad
from Interfaz import Cajas as Cj


class Apli(tk.Frame):
    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')

        pariente.geometry('%ix%i' % (Fm.ancho_ventana, Fm.altura_ventana))
        pariente.configure(background=Fm.col_fondo)
        pariente.minsize(width=Fm.ancho_ventana, height=Fm.altura_ventana)

        símismo.modelo = None

        símismo.DicLeng = Trad.Diccionario()
        símismo.Trads = símismo.DicLeng.trads_act

        símismo.CajaInic = Cj.CajaInic(símismo)
        símismo.CajaCentral = Cj.CajaCentral(símismo)
        símismo.CajaLenguas = Cj.CajaLeng(símismo)
        símismo.CajaCentral.lift()
        símismo.CajaInic.lift()
        símismo.pack()


if __name__ == '__main__':
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()
