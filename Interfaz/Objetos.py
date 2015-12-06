import tkinter as tk
import Formatos as fm


class BotónIzq(object):
    def __init__(símismo, apli, pariente, lín, i, img, img_sel, img_bloc):
        
        símismo.bt = tk.Button(pariente, command=símismo.acción_bt_izq, **fm.formato_bts_cent)
        símismo.apli = apli
        símismo.img = img
        símismo.img_sel = img_sel
        símismo.img_bloc = img_bloc
        símismo.lín = lín
        símismo.núm = i
        
    def acción_bt_izq(símismo):
        símismo.apli.cambiar_caja_trabajo(símismo.núm)
