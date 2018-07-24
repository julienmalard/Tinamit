import tkinter as tk

import pkg_resources

from tinamit import cargar_json
from tinamit.Interfaz import Traducciones as Trad

# Una función para modificar los formatos según la dirección del texto de la lengua
direc = pkg_resources.resource_filename('tinamit.Interfaz', 'Trads.json')
arch_config = pkg_resources.resource_filename('tinamit.Interfaz', 'Config.json')
Trad.Diccionario()
dic = cargar_json(direc)
leng = cargar_json(arch_config)['leng_act']
IzqaDerech = dic['Lenguas'][leng]['IzqaDerech']


def gen_formato(formato):
    if IzqaDerech:
        return formato
    else:
        if isinstance(formato, str):
            invers = [('e', 'w'), ('ne', 'nw'), ('se', 'sw'), ('right', 'left'), ('izquierda', 'derecha')]
            for inver in invers:
                if formato == inver[0]:
                    formato = inver[1]
                    break
                elif formato == inver[1]:
                    formato = inver[0]

        if isinstance(formato, dict):
            formato = formato.copy()
            invers = [('e', 'w'), ('ne', 'nw'), ('se', 'sw'), ('right', 'left')]
            if 'x' in formato.keys():
                if 'relx' not in formato.keys():
                    formato['relx'] = 0
            if 'x' in formato.keys() or 'relx' in formato.keys():
                if 'anchor' not in formato.keys():
                    formato['anchor'] = tk.NW

            for ll, v in formato.items():
                if ll == 'x':
                    formato[ll] = -v
                if ll == 'relx':
                    formato[ll] = (1 - v)
                    continue
                for inver in invers:
                    if v == inver[0]:
                        formato[ll] = inver[1]
                        continue
                    elif v == inver[1]:
                        formato[ll] = inver[0]

        return formato


# Parámetros generales
col_fondo = 'white'  # El color de fondo del interfaz
color_bts = {'1': '#%02x%02x%02x' % (218, 242, 142),
             '2': '#%02x%02x%02x' % (181, 230, 29),
             '3': '#%02x%02x%02x' % (102, 204, 0),
             '4': '#%02x%02x%02x' % (128, 64, 0)}
color_gris = '#C3C3C3'
col_1 = color_bts['3']
col_2 = '#cc9900'
col_3 = color_bts['2']
col_4 = color_bts['1']
col_5 = '#33cc33'
fuente = 'Comic Sans MS'
formato_cajas = dict(bg=col_fondo, borderwidth=0, highlightthickness=0)
formato_botones = dict(borderwidth=0, highlightthickness=0)
formato_etiq = dict(bg=col_fondo)

formato_bts_norm = dict(activebackground=col_1, bg=col_3, fg='#000000', **formato_botones)
formato_bts_sel = dict(bg=col_1)

# Ventana central
ancho_ventana = 1100
altura_ventana = 800

# Caja inicial
formato_CjInic = dict(bg=col_fondo)
ubic_CjInic = dict(x=0, y=0, relwidth=1, relheight=1)
formato_LogoInic = dict(borderwidth=0, highlightthickness=0)
ubic_LogoInic = dict(side='top', pady=(175, 50))
formato_BtsInic = dict(font=(fuente, 25, 'bold'), height=2, width=13, **formato_bts_norm)

ubic_BtsInic = dict(side='left', ipadx=5, ipady=5, padx=10, pady=10)

# Caja lenguas
ubic_CjLeng = dict(relx=0, y=0, relwidth=1, relheight=1)
ubic_BtRegrCent = dict(x=20, y=20)
ubic_CbzLeng = dict(relx=0.5, y=20, anchor=tk.N)
formato_CbzLeng = dict(font=(fuente, 40, 'bold'), fg=col_1, **formato_etiq)

ubic_CjCentLeng = dict(relx=0.5, rely=0, x=0, y=100, relheight=1, height=-150, relwidth=1, anchor=tk.N)
formato_LínVert = dict(bd=0, highlightthickness=0, bg=col_5)
ubic_LínVert1 = dict(relx=1 / 3, rely=0.05, y=20, width=1, relheight=1, anchor=tk.N)
ubic_LínVert2 = dict(relx=2 / 3, rely=0.05, y=20, width=1, relheight=1, anchor=tk.N)

ubic_CjIzqLeng = dict(relx=(1 / 3) / 2, rely=0.05, y=20, relwidth=1 / 3, width=-10, relheight=1, anchor=tk.N)
ubic_CjMedLeng = dict(relx=1 / 3 + (1 / 3) / 2, rely=0.05, y=20, relwidth=1 / 3, width=-10, relheight=1, anchor=tk.N)
ubic_CjDerchLeng = dict(relx=2 / 3 + (1 / 3) / 2, rely=0.05, y=20, relwidth=1 / 3, width=-10, relheight=1, anchor=tk.N)

formato_EtiqLengCentro = dict(font=(fuente, 30, 'bold'), fg=col_5, **formato_etiq)
formato_EtiqLengLados = dict(font=(fuente, 20, 'bold'), fg=col_3, **formato_etiq)
ubic_EtiqCbzColsLeng = dict(relx=0.5, rely=0, y=50, anchor=tk.S)

formato_CjLstLengCentro = dict(highlightthickness=1, highlightbackground=col_5, bg=col_fondo)
formato_CjLstLengLados = dict(highlightthickness=1, highlightbackground=col_3, bg=col_fondo)
ubic_LstsLeng = dict(relx=0.5, rely=0, y=75, width=300, relheight=1, height=-150, anchor=tk.N)
ubic_LstsLeng_bajo = dict(relx=0.5, rely=0, y=75 + 20, width=300, relheight=1, height=-150 - 20, anchor=tk.N)
ubic_CjAñadirLeng = dict(relx=0, rely=0, x=20, y=60, height=20, anchor=tk.NW)
ubic_CjCamposAñLeng = dict(side='left', padx=2)
formato_cj_etiq_nombre_leng = dict(height=25, **formato_cajas)
formato_etiq_nombre_leng = dict(anchor=tk.W, **formato_etiq)
ubic_etiq_nombre_leng = dict(side='left')
ancho_etiq_nombre_largo = 160
ancho_etiq_nombre_estr = 80
ubic_IzqLstLeng = dict(side='left', padx=5)
ubic_EtiqNombreLstLeng = dict(side='left')
ubic_DerLstLeng = dict(side='right', padx=5)
ubic_CjCentLstLeng = dict(side='left', padx=0)
colores_prog_leng = [(152, 103, 52), (181, 230, 29)]
dim_barra_prog_leng = (20, 55)
ubic_BtsAñadirLeng = dict(side='right', padx=2)
ubic_CentralItemaLstLeng = dict(side='left')

formato_CjEditLeng = dict(highlightthickness=1, highlightbackground=col_5, bg=col_fondo)
ubic_CjEditLeng = dict(relx=0.5, rely=0, y=10, relheight=1, width=600, height=-20, anchor=tk.N)
formato_EtiqCbzEditLeng = dict(font=(fuente, 40, 'bold'), fg=col_2, **formato_etiq)
ubic_CjCbzCjEditLeng = dict(side='top', pady=0, fill=tk.X)
ubic_CjNomEditLeng = dict(side='top', pady=0, fill=tk.X)
formato_EtiqLengBase = dict(font=(fuente, 20, 'bold'), fg=col_5, **formato_etiq)
formato_EtiqLengEdit = dict(font=(fuente, 20, 'bold'), fg=col_3, **formato_etiq)
ubic_EtiqLengs = dict(side='left', padx=5, pady=5, fill=tk.BOTH, expand=True)

formato_LínHor = dict(bd=0, highlightthickness=0, bg=col_3, height=1)
ubic_LínHorCjEditLeng = dict(side='top', fill=tk.X)
ubic_CjCentrCjEditLeng = dict(side='top', fill=tk.BOTH, expand=True)

formato_LstEditLeng = dict(highlightthickness=0, highlightbackground=col_3, bg=col_fondo)
ubic_LstEditLeng = dict(relx=0, rely=0, relheight=1, width=ubic_CjEditLeng['width'], anchor=tk.NW)

ubic_CjBtsCjEditLeng = dict(side='top', pady=20, fill=tk.X)
formato_CjLengTxOrig = dict(bg=col_fondo, highlightthickness=1, highlightbackground=col_5)
formato_EtiqLengTxOrig = dict(font=(fuente, '14', 'bold'), fg=col_5, bg=col_fondo,
                              width=20, wraplength=240, anchor=tk.W, justify=tk.LEFT)
ubic_CjTxOrigTradLeng = dict(side='left', padx=5, pady=5, fill=tk.Y, expand=True)
formato_CampoTexto = dict(font=(fuente, '14', 'bold'), bg=col_fondo,
                          highlightthickness=1, highlightbackground=col_3, highlightcolor=col_5,
                          width=25, height=3, wrap=tk.WORD, relief=tk.FLAT)
ubic_CamposLeng = dict(side='left', padx=25, pady=25, expand=True)

formato_CajaAvisoReinic = dict(highlightthickness=3, highlightbackground=col_2, bg=col_fondo)
ubic_CjAvisoReinic = dict(relx=0.5, rely=0.5, width=350, height=200, anchor=tk.CENTER)
formato_EtiqLengReinic = dict(font=(fuente, 14), fg=col_2, wraplength=275, **formato_etiq)
ubic_etiq_aviso_inic_leng = dict(side='top', pady=(20, 0))
formato_BtAvisoInic = dict(borderwidth=0, highlightthickness=0, activebackground='#ffdb4d',
                           font=(fuente, 20, 'bold'), height=1, width=9, wraplength=170)  # Formatos generales
formato_BtAvisoInic_norm = dict(bg='#ffe580', fg='#000000', **formato_BtAvisoInic)
formato_BtAvisoInic_sel = dict(bg='#ffdb4d')
ubic_bt_aviso_inic_leng = dict(side='bottom', pady=(0, 20))

formato_EtiqLengBorrar = dict(font=(fuente, 14), fg=col_2, wraplength=275, **formato_etiq)
ubic_etiq_aviso_borrar_leng = dict(side='top', pady=(20, 0))

ubic_bts_aviso_borrar_leng = dict(side='left', padx=25)
ubic_cj_bts_aviso_borrar_leng = dict(side='bottom', pady=(0, 20))

# Caja central
formato_CjCent = dict(bg=col_fondo)
ubic_CjCent = dict(x=0, y=0, relwidth=1, relheight=1)

# Caja cabeza
formato_CjCabeza = dict(height=110, **formato_cajas)
ubic_CjCabeza = dict(side='top', fill=tk.X, anchor=tk.N)

ubic_BtsArchivo = dict(x=20, rely=0.5, anchor=tk.W)
ubic_BtNuevo = dict(row=0, column=0, padx=5, pady=5)
ubic_BtGuardar = dict(row=0, column=1, padx=5, pady=5)
ubic_BtAbrir = dict(row=1, column=0, padx=5, pady=5)
ubic_BtGuardarComo = dict(row=1, column=1, padx=5, pady=5)

formato_LogoCabz = dict(borderwidth=0, highlightthickness=0, height=65)
ubic_LogoCabz = dict(relx=0.5, rely=0.5, anchor=tk.CENTER)

formato_BtLeng = dict(height=40, width=40, **formato_botones)
ubic_BtLeng = dict(relx=1, rely=0.5, x=-20, anchor=tk.E)

# Botones izquierda
ubic_CjIzq = dict(side='top', fill=tk.Y, expand=True, anchor=tk.W)
formato_BtsNavIzq = dict(width=86, height=86, borderwidth=0, highlightthickness=0)
ubic_CjBtNavIzq = dict(side='top', padx=10, pady=15, expand=True)
ubic_BtNavIzq = dict(side='left', padx=10)
formato_lín_bts = dict(highlightthickness=0, width=7, height=120)
ubic_LínNavIzq = dict(side='right', padx=10)
formato_LínIzq = dict(bd=0, highlightthickness=0, width=2, bg='black')
ubic_LínIzq = dict(side='right', pady=(0, 20), fill=tk.Y, expand=True)

# Caja Contenedora de cajas etapas
ubic_CjContCjEtps = dict(side='right', fill=tk.BOTH, expand=True, anchor=tk.NW)

# Cajas etapas
ubic_CjEtp = dict(relx=0, rely=0, relwidth=1, relheight=1)
ubic_BtNavEtp_adel = dict(rely=1, relx=0.52, anchor=tk.S)
ubic_BtNavEtp_atrs = dict(rely=0, relx=0.52, anchor=tk.N)
formato_BtsNavEtapa = dict(width=270, height=35, bg=col_fondo, borderwidth=0, highlightthickness=0)
formato_EncbzCjEtp = dict(font=(fuente, 35, 'bold'), fg=col_1, **formato_etiq)
ubic_EncbzCjEtp = dict(relx=0, rely=0, x=20)

# Cajas sub etapas
ubic_CjSubEtp = dict(relx=0, rely=0, y=2 * formato_BtsNavEtapa['height'],
                     relwidth=1, relheight=1,
                     height=-3 * formato_BtsNavEtapa['height'])
formato_EncbzCjSubEtp = dict(font=(fuente, 20, 'bold'), fg=col_2, **formato_etiq)
ubic_EncbzCjSubEtp = dict(relx=0, rely=0, x=30)

ubic_BtNavSub_adel = dict(relx=1, rely=0.5, anchor=tk.E)
ubic_BtNavSub_atrs = dict(relx=0, rely=0.5, anchor=tk.W)
formato_BtsNavSub = dict(width=25, height=205, bg=col_fondo, borderwidth=0, highlightthickness=0)
formato_etiq_error = dict(bg='#ffffe5', fg='#ff0000', font=(fuente, '12'), wraplength=350, padx=10, pady=10)
formato_etiq_todobien = dict(bg='#f2ffcc', fg='#2eb82e', font=(fuente, '12'), wraplength=350, padx=10, pady=10)

# Listas
formato_CjLstItemas = dict(highlightthickness=1, highlightbackground=col_1, bg=col_fondo)
formato_TlLstItemas = dict(bg=col_fondo, highlightthickness=0)
formato_EtiqEncbzLst = dict(bg=col_4, fg=col_1, font=(fuente, 14, 'bold'), anchor=tk.W)
ubic_ColsEncbzLst = dict(y=0, relheight=1, anchor=tk.NW)
ubic_EncbzLstItemas = dict(x=0, y=0, relx=0, rely=0, height=25, relwidth=1, anchor=tk.NW)
ubic_TlLstItemas = dict(x=0, y=0, relx=0, rely=0, relheight=1, relwidth=1, anchor=tk.NW)
ubic_BaraDesp = dict(side="right", fill="y")
ubic_CjTl = dict(anchor=tk.NW)

formato_secciones_itemas = dict(height=20, **formato_cajas)
ubic_CjItemas = dict(side='top', pady=2, fill=tk.X, expand=True)
ancho_cj_bts_itemas = 85
ubic_CjColsItemas = dict(side='left', fill=tk.BOTH, expand=True)
ubic_BtsItemas = dict(side='left', padx=5)
ubic_CjBtsItemas = dict(side='right')
ubic_EtiqItemas = dict(side='left', anchor=tk.W)
fuente_etiq_itema_sel = (fuente, 14, 'bold')
fuente_etiq_itema_norm = (fuente, 14)
formato_texto_itemas = dict(font=(fuente, 14), fg='#000000', **formato_etiq)
ubic_ColsItemasEdit = dict(y=0, relheight=1, anchor=tk.NW)

# Controles
formato_EtiqCtrl = dict(bg=col_fondo, fg=col_3, font=(fuente, 20, 'bold'))
formato_EtiqCtrl_bloq = dict(fg='#999999')

formato_MnMn = dict(bg=col_fondo, relief='flat', bd=0, activebackground=col_4, activeforeground='#000000',
                    disabledforeground='#cccccc', font=(fuente, '13'))
formato_BtMn = dict(bg=col_fondo, highlightthickness=1, highlightbackground=col_3, highlightcolor=col_3,
                    relief='flat', activebackground=col_4, font=(fuente, '13'),
                    anchor=tk.W)
formato_BtMn_bloq = dict(highlightbackground='#999999')

ubic_EtiqMenú = dict(side='left', padx=20)
ubic_Menú = dict(side='left')

ubic_EtiqIngrNúm = dict(side='left', padx=20)
ubic_IngrNúm = dict(side='left')

formato_lín_escl = dict(fill=col_1, outline=col_1, disabledfill='#cccccc', disabledoutline='#cccccc')
ubic_Escl = dict(side='left')
ubic_CampoIngrEscl = dict(side='left', padx=10)
formato_EtiqNúmEscl = dict(font={fuente, 6}, fg=col_1, **formato_etiq)
ubic_EtiqNúmEscl = dict(side='left')
ubic_EtiqEscl = dict(side='left', padx=20)

formato_CampoIngr = dict(bg=col_fondo, highlightthickness=1, highlightbackground=col_3,
                         relief='flat', highlightcolor=col_3, font=(fuente, '13'))
formato_CampoIngr_error = dict(highlightthickness=2, highlightbackground='#ff0000')

formato_BtGuardar_norm = dict(bg='#6ac86a', fg='#ffffff', borderwidth=0, highlightthickness=0,
                              activebackground='#3ea73e', activeforeground='#ffffff',
                              font=(fuente, 15, 'bold'), width=10)
formato_BtGuardar_sel = dict(bg='#3ea73e', fg='#ffffff')
formato_BtGuardars_bloq = dict(bg='#ecf8ec', disabledforeground='#ffffff')
formato_BtBorrar_norm = dict(bg='#ff6233', fg='#ffffff', borderwidth=0, highlightthickness=0,
                             activebackground='#e63500', activeforeground='#ffffff',
                             font=(fuente, 15, 'bold'), width=10)
formato_BtBorrar_sel = dict(bg='#e63500', fg='#ffffff')
formato_BtBorrars_bloq = dict(bg='#ffebe5', disabledforeground='#ffffff')
ubic_BtsGrupo = dict(side='left', expand=True)
ubic_CjBtsGrupoCtrl = dict(side='top', padx=20, fill=tk.X, expand=True)

# Caja subetapa 1.1

ubic_caja_cargar_mds = dict(x=0, rely=0.2, relwidth=0.5, width=-10, height=250)
ubic_caja_cargar_bf = dict(relx=0.5, rely=0.2, x=+10, relwidth=0.5, width=-10, height=250)

formato_bts_cargar = dict(font=(fuente, 20, 'bold'), height=3, width=15, wraplength=300, **formato_bts_norm)
ubic_bts_cargar_mod = dict(relx=0.5, rely=0.3, y=10, anchor=tk.CENTER)
ubic_EtiqCargarMod = dict(side='bottom', pady=20)

# Caja subetapa 2.1
ubic_CjLstConecciones = dict(relx=0.5, rely=0, y=50, width=0.8 * ancho_ventana, height=150, anchor=tk.N)
anchos_cols_listacon = [0.40, 0.40, 0.20]
formato_etiq_conversión = dict(width=7, anchor=tk.W, **formato_texto_itemas)

ubic_CjBajoConex = dict(relx=0, rely=0, x=10, y=10, relwidth=1, relheight=.8, width=-20, anchor=tk.NW)

ubic_CjCtrlsConectar = dict(relx=0.5, rely=0, y=200, relwidth=1, width=-20, height=150, anchor=tk.N)
ancho_MnVars = 10
formato_EtiqsUnid = dict(font=(fuente, 13, 'italic'), fg='#d9b38c', bg=col_fondo)
ubic_EtiqsUnid = dict(side='top', anchor=tk.E)
ubic_CjsCtrlsConectar = dict(side='left', padx=20, pady=20, expand=True, anchor=tk.N)
ubic_CjMedCtrlsConectar = dict(side='left', padx=20, pady=30, expand=True, anchor=tk.N)
ubic_CtrlsConectar = dict(side='top')

ubic_CjBtsConectar = dict(relx=0.5, rely=0, y=340, width=400, anchor=tk.N)

# Caja subetapa 3.1
formato_etiqs_ctrls_tiempo = dict(font=(fuente, '13'), fg='#000000', bg=col_fondo)
ubic_CjCtrlsTiempo = dict(relx=0.5, rely=0.2, width=600, anchor=tk.CENTER)
ubic_CtrlsUnidTiempo = dict(side='left', padx=5)
ubic_CtrlsTiempo = dict(side='top', pady=10)

formato_bt_simular = dict(font=(fuente, 20, 'bold'), height=3, width=15, wraplength=300, **formato_bts_norm)
ubic_bt_simular = dict(side='top')
ubic_cj_bt_simular = dict(relx=0.5, rely=0.4, anchor=tk.N)
ubic_cj_corrida = dict(relx=0.5, rely=0.8, anchor=tk.N)
formato_CjSimulando = dict(height=50, width=350, **formato_cajas)
ubic_CjSimulando = dict(side='top', pady=20)
formato_etiq_simulando = dict(width=20, height=2, font=(fuente, 15, 'bold'), **formato_etiq)
ubic_EtiqSimulando = dict(relx=0, rely=0.5, anchor=tk.W)
