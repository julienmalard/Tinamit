import tkinter as tki
import webbrowser
from MDS import cargar_mds


def acción_bt_empezar():
    pass


def acción_bt_ayuda():
    webbrowser.open('Documentación.txt')


formato_botones = dict(relief='ridge', bg='white',  activebackground='#ccff66')

centr = tki.Tk()
centr.title('Tinamit')
centr.geometry('500x500')
centr.configure(background='white')


bt_empezar = tki.Button(text='Empezar', command=acción_bt_empezar(), **formato_botones)
bt_ayuda = tki.Button(text='Ayuda', command=acción_bt_ayuda(), **formato_botones)

bt_empezar.pack()
bt_ayuda.pack()

centr.mainloop()
