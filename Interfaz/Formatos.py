

ancho_ventana = 800
altura_ventana = 600
dim_ventana = (ancho_ventana, altura_ventana)
formato_cajas = dict(bg='white')
emplacimiento_cajas_cent = dict(x=0, y=0, relheight=1, relwidth=1)


formato_logo_inic = dict(borderwidth=0, highlightthickness=0)
emplacimiento_logo_inic = dict(pady=(150, 0))
formato_bts_inic = dict(relief='ridge', bg='white', activebackground='#99ff33', activeforeground='white',
                        font=('arial', 20, 'bold'), height=3, width=13)
emplacimiento_bts_inic = dict(side='left', ipadx=5, ipady=5, padx=10, pady=10)

formato_bt_leng = dict(borderwidth=0, highlightthickness=0, bg='white', height=40, width=40)
emplacimiento_bt_leng = dict(relx=1, x=-60, rely=1, y=-60)
formato_logo_cent = dict(borderwidth=0, highlightthickness=0, height=60)
emplacimiento_logo_cent = dict(relx=0.5, x=-90, rely=0)
emplacimiento_caja_cabeza = dict(relx=0, rely=0, relwidth=1, height=80)

formato_lín_bts = dict(bd=0, highlightthickness=0, width=7, height=90)
emplacimiento_lín_bts = dict(side='top', pady=20)
formato_bts_cent = dict(bd=0, highlightthickness=0, relief='flat',
                        bg='white', activebackground='white', width=80, height=80)
emplacimiento_bts_cent = dict(side='top', ipadx=5, ipady=5, padx=10, pady=20)
color_bts = {'1': (179, 255, 102),
             '2': (128, 255, 0),
             '3': (102, 204, 0),
             '4': (128, 64, 0)}

formato_cajas_núm = dict(**formato_cajas)
emplacimiento_cajas_núm = dict(x=140, y=80, relheight=1, height=-100, relwidth=1, width=-170)
emplacimiento_cj_izq = dict(relx=0, y=80)

emplacimiento_bt_anterior = dict(relx=1, x=-60, rely=0)
emplacimiento_bt_siguiente = dict(relx=1, x=-60, rely=1, y=-60)
formato_bts_ant_sig = dict(bd=0, highlightthickness=0, relief='flat',
                           bg='white', activebackground='white', width=60, height=60)
