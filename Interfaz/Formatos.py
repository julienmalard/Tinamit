import tkinter as tk

dimensiones_ventana = (800, 600)
formato_cajas = dict(bg='white')
emplacimiento_cajas_cent = dict(fill=tk.X)


formato_logo_inic = dict(borderwidth=0, highlightthickness=0)
emplacimiento_logo_inic = dict(pady=(150, 0))
formato_bts_inic = dict(relief='ridge', bg='white', activebackground='#99ff33', activeforeground='white',
                        font=('arial', 20, 'bold'), height=3, width=13)
emplacimiento_bts_inic = dict(side='left', ipadx=5, ipady=5, padx=10, pady=10)

formato_logo_cent = dict(borderwidth=0, highlightthickness=0)
emplacimiento_logo_cent = dict(side='left', padx=(250, 0))
formato_bt_leng= dict(borderwidth=0, highlightthickness=0)
emplacimiento_bt_leng = dict(side='right')
emplacimiento_caja_cabeza = dict(side='top', fill=tk.X)

formato_lín_bts = dict(height=7)
emplacimiento_lín_bts = dict(side='top', pady=7)
emplacimiento_bts_cent = dict(side='top', ipadx=5, ipady=5, padx=10, pady=10)
formato_bts_cent = dict(relief='flat', bg='white', activebackground='white')
color_bt_1 = (179, 255, 102)
color_bt_2 = (128,255,0)
color_bt_3 = (102, 204, 0)
color_bt_4 = (128, 64, 0)

formato_cajas_núm = dict(**formato_cajas)
emplacimiento_cajas_núm = dict(side='left', expand=True, padx=20, pady=20, fill=tk.BOTH)
