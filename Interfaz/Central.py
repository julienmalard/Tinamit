import tkinter as tk
from tkinter import filedialog as diálogo
import webbrowser

from Interfaz import Formatos as Fm, Gráficos as Gr, Pantallas as Pants

from MDS import cargar_mds


class Apli(tk.Frame):
    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')
        pariente.geometry('%ix%i' % Fm.dim_ventana)
        pariente.configure(background='white')

        símismo.imgs = Gr.cargar_imágenes()

        símismo.pantalla_inicio = Pants.PantallaInicio(apli=símismo, imgs=símismo.imgs)
        símismo.pantalla_central = Pants.PantallaCentral(apli=símismo, imgs=símismo.imgs)
        símismo.pantalla_lengua = Pants.PantallaLengua(apli=símismo, imgs=símismo.imgs)

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
                print(nombre_archivo_mds)
                símismo.nombre_archivo_mds = nombre_archivo_mds
            else:
                print('¡Error!')
                return FileNotFoundError('No se pudo cargar el archivo del MDS.')

    def buscar_bf(símismo):
        nombre_archivo_bf = diálogo.askopenfilename(filetypes=[('Modelos Python', '*.py')],
                                                     title='Cargar modelo biofísico')
        if nombre_archivo_bf:
            print(nombre_archivo_bf)
            símismo.nombre_archivo_bf = nombre_archivo_bf
        else:
            print('¡Error!')
            return FileNotFoundError('No se pudo cargar el archivo del MDS.')

    def buscar_con(símismo):
        nombre_archivo_con = diálogo.askopenfilename(filetypes=[('Modelos Python', '*.py')],
                                                     title='Cargar modelo conectado')
        if nombre_archivo_con:
            print(nombre_archivo_con)
            símismo.nombre_archivo_con = nombre_archivo_con
        else:
            print('¡Error!')
            return FileNotFoundError('No se pudo cargar el archivo del MDS.')


if __name__ == '__main__':
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()
