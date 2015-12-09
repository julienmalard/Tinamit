import tkinter as tk


class Botón(object):
    def __init__(símismo, pariente, comanda, img, img_sel=None, img_bloc=None, **kwargs):
        símismo.img = img
        símismo.img_sel = img_sel
        símismo.img_bloc = img_bloc

        símismo.bt = tk.Button(pariente, image=img, command=comanda, **kwargs)

        símismo.activado = True
        símismo.seleccionado = False

        if img_sel is not None:
            símismo.bt.bind('<Enter>', lambda event, b=símismo: b.colorar_sel())
            símismo.bt.bind('<Leave>', lambda event, b=símismo: b.descolorar_sel())

    def colorar_sel(símismo):
        if símismo.activado and not símismo.seleccionado:
            símismo.bt.configure(image=símismo.img_sel)

    def descolorar_sel(símismo):
        if símismo.activado and not símismo.seleccionado:
            símismo.bt.configure(image=símismo.img)

    def activar(símismo):
        símismo.activado = True
        símismo.bt.configure(image=símismo.img, cursor='arrow', state='normal')

    def desactivar(símismo):
        símismo.bt.configure(image=símismo.img_bloc, cursor='X_cursor', state='disabled')
        símismo.activado = False

    def seleccionar(símismo):
        símismo.bt.configure(image=símismo.img_sel, state='normal')
        símismo.seleccionado = True

    def deseleccionar(símismo):
        símismo.bt.configure(image=símismo.img, state='normal')
        símismo.seleccionado = False


class BotónIzq(Botón):
    def __init__(símismo, apli, pariente, lín, núm, img, img_sel, img_bloc, **kwargs):
        super().__init__(pariente=pariente, comanda=símismo.acción_bt_izq,
                         img=img, img_sel=img_sel, img_bloc=img_bloc, **kwargs)

        símismo.apli = apli
        símismo.lín = lín
        símismo.núm = núm

    def acción_bt_izq(símismo):
        símismo.apli.cambiar_caja_trabajo(símismo.núm)
