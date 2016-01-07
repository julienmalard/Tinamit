import tkinter as tk


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
color_bts = {'1': '#%02x%02x%02x' % (179, 255, 102),
             '2': '#%02x%02x%02x' % (128, 255, 0),
             '3': '#%02x%02x%02x' % (102, 204, 0),
             '4': '#%02x%02x%02x' % (128, 64, 0)}
color_error = '#%02x%02x%02x' % (255, 128, 128)

formato_cajas_trab = dict(**formato_cajas)
emplacimiento_cajas_trab = dict(x=140, y=80, relheight=1, height=-100, relwidth=1, width=-170)
emplacimiento_cj_izq = dict(relx=0, y=80)

emplacimiento_bt_anterior = dict(relx=1, x=-60, rely=0)
emplacimiento_bt_siguiente = dict(relx=1, x=-60, rely=1, y=-60)
formato_bts_ant_sig = dict(bd=0, highlightthickness=0, relief='flat',
                           bg='white', activebackground='white', width=60, height=60)

emplacimiento_caja_cargar_mds = dict(x=0, y=0, relwidth=0.5, width=-10, relheight=0.5, height=-10)
emplacimiento_caja_cargar_bf = dict(relx=0.5, y=0, x=+10, relwidth=0.5, width=-10, relheight=0.5, height=-10)
emplacimiento_lín_vert_med = dict(relx=0.5, y=0, width=1, relheight=0.5, height=-10)
emplacimiento_lín_hor = dict(relx=0, rely=0.5, relwidth=1, height=1)
emplacimiento_caja_cargar_conectado = dict(x=0, rely=0.5, y=+10, relwidth=1, relheight=0.5, height=-10)

formato_etiq_cargar_mod = dict(bg='white', font=('arial', 20, 'bold'), fg=color_bts['1'])
formato_etiq_sino = dict(bg='white', font=('arial', 20, 'bold'), fg=color_bts['1'])
formato_etiq_cargar_con = dict(bg='white', font=('arial', 20, 'bold'), fg=color_bts['1'])
formato_bts_cargar = dict(relief='ridge', bg='white', activebackground='#99ff33', activeforeground='white',
                          font=('arial', 20, 'bold'), height=2, width=10, wraplength=150)
emplacimiento_bts_cargar_mod = dict(relx=0.5, rely=0.5, y=10, anchor=tk.CENTER)
