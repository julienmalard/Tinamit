import os
import tkinter as tk
import pkg_resources


def imagen(nombre):
    archivo = pkg_resources.resource_filename('tinamit.Interfaz.Imágenes', archivos_imgs[nombre])
    img = tk.PhotoImage(file=archivo)
    return img

archivos_imgs = {'LogoInic': 'LogoInic.png',

                 'BtRegrCent_norm': 'BtRegrCent_norm.png',
                 'BtRegrCent_sel': 'BtRegrCent_sel.png',

                 'LogoCent': 'LogoCent.png',
                 'BtLeng_norm': 'BtLeng_norm.png',
                 'BtLeng_sel': 'BtLeng_sel.png',
                 'BtNuevo_norm': 'BtNuevo_norm.png',
                 'BtNuevo_sel': 'BtNuevo_sel.png',
                 'BtGuardar_norm': 'BtGuardar_norm.png',
                 'BtGuardar_sel': 'BtGuardar_sel.png',
                 'BtGuardarComo_norm': 'BtGuardarComo_norm.png',
                 'BtGuardarComo_sel': 'BtGuardarComo_sel.png',
                 'BtAbrir_norm': 'BtAbrir_norm.png',
                 'BtAbrir_sel': 'BtAbrir_sel.png',

                 'BtNavIzq_1_norm': 'BtNavIzq_1_norm.png',
                 'BtNavIzq_1_bloq': 'BtNavIzq_1_bloq.png',
                 'BtNavIzq_1_sel': 'BtNavIzq_1_sel.png',
                 'BtNavIzq_2_norm': 'BtNavIzq_2_norm.png',
                 'BtNavIzq_2_bloq': 'BtNavIzq_2_bloq.png',
                 'BtNavIzq_2_sel': 'BtNavIzq_2_sel.png',
                 'BtNavIzq_3_norm': 'BtNavIzq_3_norm.png',
                 'BtNavIzq_3_bloq': 'BtNavIzq_3_bloq.png',
                 'BtNavIzq_3_sel': 'BtNavIzq_3_sel.png',
                 'BtNavIzq_4_norm': 'BtNavIzq_4_norm.png',
                 'BtNavIzq_4_bloq': 'BtNavIzq_4_bloq.png',
                 'BtNavIzq_4_sel': 'BtNavIzq_4_sel.png',

                 'BtNavEtp_adel_norm': 'BtNavEtp_adel_norm.png',
                 'BtNavEtp_adel_bloq': 'BtNavEtp_adel_bloq.png',
                 'BtNavEtp_adel_sel': 'BtNavEtp_adel_sel.png',
                 'BtNavEtp_atrs_norm': 'BtNavEtp_atrs_norm.png',
                 'BtNavEtp_atrs_bloq': 'BtNavEtp_atrs_bloq.png',
                 'BtNavEtp_atrs_sel': 'BtNavEtp_atrs_sel.png',

                 'BtNavSub_adel_norm': 'BtNavSub_adel_norm.png',
                 'BtNavSub_adel_bloq': 'BtNavSub_adel_bloq.png',
                 'BtNavSub_adel_sel': 'BtNavSub_adel_sel.png',
                 'BtNavSub_atrs_norm': 'BtNavSub_atrs_norm.png',
                 'BtNavSub_atrs_bloq': 'BtNavSub_atrs_bloq.png',
                 'BtNavSub_atrs_sel': 'BtNavSub_atrs_sel.png',


                 'BtBorrarItema_norm': 'BtBorrarItema_norm.png',
                 'BtBorrarItema_sel': 'BtBorrarItema_sel.png',
                 'BtBorrarItema_bloq': 'BtBorrarItema_bloq.png',
                 'BtEditarItema_norm': 'BtEditarItema_norm.png',
                 'BtEditarItema_sel': 'BtEditarItema_sel.png',

                 'BtCasilla_norm': 'BtCasilla_norm.png',
                 'BtCasilla_sel': 'BtCasilla_sel.png',
                 'BtCasilla_bloq': 'BtCasilla_bloq.png',

                 'BtMarca_norm': 'BtMarca_norm.png',
                 'BtMarca_sel': 'BtMarca_sel.png',
                 'BtMarca_bloq': 'BtMarca_bloq.png',

                 'BtPlus_norm': 'BtPlus_norm.png',
                 'BtPlus_sel': 'BtPlus_sel.png',

                 'BtEscribIzqDer': 'BtEscribIzqDer.png',
                 'BtEscribDerIzq': 'BtEscribDerIzq.png',

                 'BtConecciónIzqDer': 'BtConecciónIzqDer.png',
                 'BtConecciónDerIzq': 'BtConecciónDerIzq.png',

                 'FlchConex_colaizq': 'FlchConex_colaizq.png',
                 'FlchConex_colader': 'FlchConex_colader.png',
                 'FlchConex_cbzizq': 'FlchConex_cbzizq.png',
                 'FlchConex_cbzder': 'FlchConex_cbzder.png'

                 }


def escalar_colores(color1, color2, n):

    def escalar(val1, val2, m):
            escl = [val1/256 + (val2/256 - val1/256)*i/(m-1) for i in range(m)]
            return escl

    r = escalar(color1[0], color2[0], n)
    v = escalar(color1[1], color2[1], n)
    a = escalar(color1[2], color2[2], n)

    return list(zip(r, v, a))


def inter_color(colores, p, tipo='rgb'):

    def interpol(val1, val2, u):
        return int(val1 + (val2 - val1)*u)

    def interpol_col(col1, col2, u):
        return tuple([interpol(col1[n], col2[n], u) for n in range(3)])

    pos = (p * (len(colores)-1)) % 1
    inic = max(0, int(pos) - 1)
    fin = inic + 1
    if fin >= len(colores):
        fin = len(colores) - 1
    col = interpol_col(colores[inic], colores[fin], u=pos)

    if tipo == 'rgb':
        col_final = col
    elif tipo == 'hex':
        col_final = '#%02x%02x%02x' % col
    else:
        raise KeyError

    return col_final
