import tkinter as tk
import webbrowser
import Formatos as fm
from MDS import cargar_mds


class Apli(tk.Frame):
    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')
        pariente.geometry('%ix%i' % fm.dimensiones_ventana)
        pariente.configure(background='white')

        símismo.img_logo = tk.PhotoImage(file='Interfaz\\Imágenes\\Logo.png')
        símismo.img_logo_cent = tk.PhotoImage(file='Interfaz\\Imágenes\\Logo_cent.png')
        símismo.img_bt_1 = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_1.png')
        símismo.img_bt_2 = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_2.png')
        símismo.img_bt_3 = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_3.png')
        símismo.img_bt_4 = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_4.png')
        símismo.img_bt_1_sel = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_1_sel.png')
        símismo.img_bt_2_sel = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_2_sel.png')
        símismo.img_bt_3_sel = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_3_sel.png')
        símismo.img_bt_4_sel = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_4_sel.png')
        símismo.img_bt_1_bloc = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_1_bloc.png')
        símismo.img_bt_2_bloc = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_2_bloc.png')
        símismo.img_bt_3_bloc = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_3_bloc.png')
        símismo.img_bt_4_bloc = tk.PhotoImage(file='Interfaz\\Imágenes\\Botón_4_bloc.png')
        símismo.img_ulew = tk.PhotoImage(file='Interfaz\\Imágenes\\Ulew.png')

        símismo.crear_pantalla_inicio()

    def crear_pantalla_inicio(símismo):
        # Los formatos para los objetos en esta pantalla


        # La caja principal que contiene todo visible en esta pantalla
        símismo.caja_pantalla_inic = tk.Frame(height=600, width=800, **fm.formato_cajas)

        # El logo 'Tinamit'

        símismo.logo_inic = tk.Label(símismo.caja_pantalla_inic, image=símismo.img_logo, **fm.formato_logo_inic)

        # Una caja para los dos botones, tanto como los botones sí mismos
        símismo.caja_bts_inic = tk.Frame(símismo.caja_pantalla_inic, **fm.formato_cajas)
        símismo.bt_empezar = tk.Button(símismo.caja_bts_inic, text='Empezar', command=símismo.acción_bt_empezar,
                                       **fm.formato_bts_inic)
        símismo.bt_ayuda = tk.Button(símismo.caja_bts_inic, text='Ayuda', command=símismo.acción_bt_ayuda,
                                     **fm.formato_bts_inic)
        for i in [símismo.bt_empezar, símismo.bt_ayuda]:
            i.bind('<Enter>', lambda event, b=i: b.configure(bg='#ccff66'))
            i.bind('<Leave>', lambda event, b=i: b.configure(bg='white'))

        # Dibujar todo
        símismo.logo_inic.pack(fm.emplacimiento_logo_inic)
        símismo.bt_empezar.pack(fm.emplacimiento_bts_inic)
        símismo.bt_ayuda.pack(fm.emplacimiento_bts_inic)
        símismo.caja_bts_inic.pack(pady=20)
        símismo.caja_pantalla_inic.pack(**fm.emplacimiento_cajas_cent)

    def acción_bt_empezar(símismo):
        símismo.caja_pantalla_inic.pack_forget()
        símismo.crear_pantalla_central()

    @staticmethod
    def acción_bt_ayuda():
        webbrowser.open('Documentación.txt')

    def crear_pantalla_central(símismo):

        # La caja principal que contiene todo visible en esta pantalla
        símismo.caja_pantalla_central = tk.Frame(**fm.formato_cajas)

        #
        símismo.caja_cabeza = tk.Frame(símismo.caja_pantalla_central, **fm.formato_cajas)
        símismo.logo_cent = tk.Label(símismo.caja_cabeza, image=símismo.img_logo_cent, **fm.formato_logo_cent)
        símismo.bt_leng = tk.Button(símismo.caja_cabeza, image=símismo.img_ulew, **fm.formato_bt_leng)

        #
        símismo.caja_izq = tk.Frame(símismo.caja_pantalla_central, **fm.formato_cajas)

        #
        símismo.caja_líneas_izq = tk.Frame(símismo.caja_izq, **fm.formato_cajas)
        símismo.lín_1 = tk.Label(símismo.caja_líneas_izq, **fm.formato_lín_bts)
        símismo.lín_1.col = '#%02x%02x%02x' % fm.color_bt_1
        símismo.lín_2 = tk.Label(símismo.caja_líneas_izq, **fm.formato_lín_bts)
        símismo.lín_2.col = '#%02x%02x%02x' % fm.color_bt_2
        símismo.lín_3 = tk.Label(símismo.caja_líneas_izq, **fm.formato_lín_bts)
        símismo.lín_3.col = '#%02x%02x%02x' % fm.color_bt_3
        símismo.lín_4 = tk.Label(símismo.caja_líneas_izq, **fm.formato_lín_bts)
        símismo.lín_4.col = '#%02x%02x%02x' % fm.color_bt_4

        #
        símismo.caja_bts_izq = tk.Frame(símismo.caja_izq, **fm.formato_cajas)
        símismo.bt_1 = tk.Button(símismo.caja_bts_izq, image=símismo.img_bt_1, command=símismo.acción_bt_1,
                                 **fm.formato_bts_cent)
        símismo.bt_1.imagen = símismo.img_bt_1
        símismo.bt_1.im_sel = símismo.img_bt_1_sel
        símismo.bt_1.im_bloc = símismo.img_bt_1_bloc
        símismo.bt_1.lín = símismo.lín_1
        símismo.bt_2 = tk.Button(símismo.caja_bts_izq, image=símismo.img_bt_2, command=símismo.acción_bt_2,
                                 **fm.formato_bts_cent)
        símismo.bt_2.imagen = símismo.img_bt_2
        símismo.bt_2.im_sel = símismo.img_bt_2_sel
        símismo.bt_2.im_bloc = símismo.img_bt_2_bloc
        símismo.bt_2.lín = símismo.lín_2
        símismo.bt_3 = tk.Button(símismo.caja_bts_izq, image=símismo.img_bt_3, command=símismo.acción_bt_3,
                                 **fm.formato_bts_cent)
        símismo.bt_3.imagen = símismo.img_bt_3
        símismo.bt_3.im_sel = símismo.img_bt_3_sel
        símismo.bt_3.im_bloc = símismo.img_bt_3_bloc
        símismo.bt_3.lín = símismo.lín_3
        símismo.bt_4 = tk.Button(símismo.caja_bts_izq, image=símismo.img_bt_4, command=símismo.acción_bt_4,
                                 **fm.formato_bts_cent)
        símismo.bt_4.imagen = símismo.img_bt_4
        símismo.bt_4.im_sel = símismo.img_bt_4_sel
        símismo.bt_4.im_bloc = símismo.img_bt_4_bloc
        símismo.bt_4.lín = símismo.lín_4

        # Desactivar los botones no disponibles
        símismo.desactivar_bt(símismo.bt_2)
        símismo.desactivar_bt(símismo.bt_3)
        símismo.desactivar_bt(símismo.bt_4)
        símismo.activar_bt(símismo.bt_1)

        # Dibujar todo
        símismo.logo_cent.pack(**fm.emplacimiento_logo_cent)
        símismo.bt_leng.pack(**fm.emplacimiento_bt_leng)
        símismo.caja_cabeza.pack(**fm.emplacimiento_caja_cabeza)

        for l in [símismo.lín_1, símismo.lín_2, símismo.lín_3, símismo.lín_4]:
            l.pack(**fm.emplacimiento_lín_bts)

        símismo.caja_líneas_izq.pack(side='right')

        for b in [símismo.bt_1, símismo.bt_2, símismo.bt_3, símismo.bt_4]:
            b.pack(fm.emplacimiento_bts_cent)
        símismo.caja_bts_izq.pack(side='right')
        símismo.caja_izq.pack(side='left', expand=False)

        # Crear las otras cajas
        símismo.caja_1 = tk.Frame(símismo.caja_pantalla_central)
        prueba = tk.Label(símismo.caja_1, text='prueba')
        prueba.pack()
        símismo.caja_1.pack(**fm.emplacimiento_cajas_núm)

        símismo.caja_pantalla_central.pack(**fm.emplacimiento_cajas_cent)



    def acción_bt_1(símismo):
        if símismo.caja_activa is not símismo.caja_1:
            símismo.intercambiar(símismo.caja_activa, símismo.caja_1)
        símismo.caja_activa = símismo.caja_1

    def acción_bt_2(símismo):
        if símismo.caja_activa is not símismo.caja_2:
            símismo.intercambiar(símismo.caja_activa, símismo.caja_2)
        símismo.caja_activa = símismo.caja_2

    def acción_bt_3(símismo):
        if símismo.caja_activa is not símismo.caja_3:
            símismo.intercambiar(símismo.caja_activa, símismo.caja_3)
        símismo.caja_activa = símismo.caja_3

    def acción_bt_4(símismo):
        if símismo.caja_activa is not símismo.caja_4:
            símismo.intercambiar(símismo.caja_activa, símismo.caja_4)
        símismo.caja_activa = símismo.caja_4

    @staticmethod
    def desactivar_bt(botón):
        botón.configure(image=botón.im_bloc, state='disabled')
        botón.lín.configure(bg='#C3C3C3')

    @staticmethod
    def activar_bt(botón):
        botón.configure(image=botón.imagen, state='normal')
        botón.lín.configure(bg=botón.lín.col)


if __name__ == '__main__':
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()
