import tkinter as tk
import Formatos as fm


class BotónIzq(object):
    def __init__(símismo, apli, pariente, lín, i, img, img_sel, img_bloc):
        
        símismo.bt = tk.Button(pariente, command=símismo.acción_bt_izq, **fm.formato_bts_cent)
        símismo.apli = apli
        símismo.imagen = img
        símismo.im_sel = img_sel
        símismo.im_bloc = img_bloc
        símismo.lín = lín
        símismo.núm = i
        
    def acción_bt_izq(símismo):
        if símismo.apli.caja_activa.núm is not símismo.núm:
            símismo.apli.intercambiar(símismo.apli.caja_activa,
                                      símismo.apli.caja_pantalla_central.cajas_trabajo[str(símismo.núm)])
            símismo.apli.caja_activa = símismo.apli.pantalla_central.cajas_trabajo[str(símismo.núm)]
