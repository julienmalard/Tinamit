import tkinter as tk
from tkinter import filedialog as diálogo
import webbrowser

from Interfaz import Formatos as Fm
from Interfaz import Traducciones as Trad
from Interfaz import Cajas as Cj

import MDS
import Biofísico
from Conectado import Conectado


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


        # Desactivar las ventanas no disponibles
        símismo.pantalla_central.desbloquear_caja(1)
        for i in [2, 3, 4]:
            símismo.pantalla_central.bloquear_caja(i)

        # Poner la primera ventana
        símismo.pantalla_central.caja_izq.bts[str(1)].seleccionar()
        símismo.pantalla_central.cajas_trabajo[str(1)].traer()
        símismo.pantalla_central.caja_trab_act = 1

        # Esconder la pantalla central y la pantalla de lenguas bajo la pantalla de inicio
        símismo.pantalla_central.caja.lower()
        símismo.pantalla_lengua.caja.lower()

        símismo.nombre_archivo_mds = None
        símismo.nombre_archivo_bf = None
        símismo.nombre_archivo_con = None
        símismo.mod_mds = None
        símismo.mod_bf = None
        símismo.modelo = None

    def acción_bt_empezar(símismo):
        símismo.pantalla_inicio.caja.destroy()

    @staticmethod
    def acción_bt_ayuda():
        webbrowser.open('Documentación.txt')

    def acción_bt_leng(símismo):
        símismo.pantalla_lengua.caja.lift()

    def acción_bt_regr_cent(símismo):
        símismo.pantalla_central.caja.lift()

    def cambiar_caja_trabajo(símismo, núm_nueva):
        símismo.pantalla_central.pasar_a_caja(núm_nueva)

    def ir_adelante(símismo):
        símismo.pantalla_central.ir_adelante()

    def ir_atrás(símismo):
        símismo.pantalla_central.ir_atrás()

    def buscar_mds(símismo):
        nombre_archivo_mds = diálogo.askopenfilename(filetypes=[('Modelos publicados VENSIM', '*.vpm')],
                                                     title='Cargar MDS')
        if nombre_archivo_mds:
            símismo.nombre_archivo_mds = nombre_archivo_mds
            try:
                símismo.mod_mds = MDS.EnvolturaMDS(programa_mds='VENSIM', ubicación_modelo=símismo.nombre_archivo_mds)
                símismo.pantalla_central.cajas_trabajo['1'].noerror('bt_cargar_mds')
            except AssertionError:
                símismo.pantalla_central.cajas_trabajo['1'].error('bt_cargar_mds')
                for i in [2, 3, 4]:
                    símismo.pantalla_central.bloquear_caja(i)
                símismo.mod_bf = None
        else:
            return FileNotFoundError('No se pudo cargar el archivo del MDS.')
        if símismo.mod_bf is not None:
            símismo.crear_conectado()

    def buscar_bf(símismo):
        nombre_archivo_bf = diálogo.askopenfilename(filetypes=[('Modelos Python', '*.py')],
                                                    title='Cargar modelo biofísico')
        if nombre_archivo_bf:
            símismo.nombre_archivo_bf = nombre_archivo_bf
            try:
                símismo.mod_bf = Biofísico.EnvolturaBF(ubicación_modelo=símismo.nombre_archivo_bf)
                símismo.pantalla_central.cajas_trabajo['1'].noerror('bt_cargar_bf')
            except AssertionError or AttributeError:
                símismo.pantalla_central.cajas_trabajo['1'].error('bt_cargar_bf')
                for i in [2, 3, 4]:
                    símismo.pantalla_central.bloquear_caja(i)
                símismo.mod_mds = None
        else:
            return FileNotFoundError('No se pudo cargar el archivo del MDS.')
        if símismo.mod_mds is not None:
            símismo.crear_conectado()

    def buscar_con(símismo):
        nombre_archivo_con = diálogo.askopenfilename(filetypes=[('Modelos conectados', '*.con')],
                                                     title='Cargar modelo conectado')
        if nombre_archivo_con:
            símismo.nombre_archivo_con = nombre_archivo_con
            símismo.pantalla_central.cajas_trabajo['1'].noerror('bt_cargar_con')
            try:
                símismo.crear_conectado()
            except AttributeError:
                símismo.pantalla_central.cajas_trabajo['1'].error('bt_cargar_con')
                for i in [2, 3, 4]:
                        símismo.pantalla_central.bloquear_caja(i)
                return FileNotFoundError('No se pudo cargar el archivo del MDS.')

    def crear_conectado(símismo):
        símismo.modelo = Conectado(archivo_mds=símismo.nombre_archivo_mds, archivo_biofísico=símismo.nombre_archivo_bf,
                                   mds=símismo.mod_mds, bf=símismo.mod_bf)
        símismo.pantalla_central.desbloquear_caja(2)

if __name__ == '__main__':
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()
