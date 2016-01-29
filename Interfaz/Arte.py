import tkinter as tk


def imagen(nombre):
    archivo = archivos_imgs[nombre]
    img = tk.PhotoImage(file=archivo)
    
    return img

raíz_imgs = 'Imágenes\\'
archivos_imgs = {'LogoInic': '%sLogoInic.png' % raíz_imgs,

                 'BtRegrCent_norm': '%sBtRegrCent_norm.png' % raíz_imgs,
                 'BtRegrCent_sel': '%sBtRegrCent_sel.png' % raíz_imgs,

                 'LogoCent': '%sLogoCent.png' % raíz_imgs,
                 'BtLeng_norm': '%sBtLeng_norm.png' % raíz_imgs,
                 'BtLeng_sel': '%sBtLeng_sel.png' % raíz_imgs,
                 'BtNavIzq_1_norm': '%sBtNavIzq_1_norm.png' % raíz_imgs,
                 'BtNavIzq_1_bloq': '%sBtNavIzq_1_bloq.png' % raíz_imgs,
                 'BtNavIzq_1_sel': '%sBtNavIzq_1_sel.png' % raíz_imgs,
                 'BtNavIzq_2_norm': '%sBtNavIzq_2_norm.png' % raíz_imgs,
                 'BtNavIzq_2_bloq': '%sBtNavIzq_2_bloq.png' % raíz_imgs,
                 'BtNavIzq_2_sel': '%sBtNavIzq_2_sel.png' % raíz_imgs,
                 'BtNavIzq_3_norm': '%sBtNavIzq_3_norm.png' % raíz_imgs,
                 'BtNavIzq_3_bloq': '%sBtNavIzq_3_bloq.png' % raíz_imgs,
                 'BtNavIzq_3_sel': '%sBtNavIzq_3_sel.png' % raíz_imgs,
                 'BtNavIzq_4_norm': '%sBtNavIzq_4_norm.png' % raíz_imgs,
                 'BtNavIzq_4_bloq': '%sBtNavIzq_4_bloq.png' % raíz_imgs,
                 'BtNavIzq_4_sel': '%sBtNavIzq_4_sel.png' % raíz_imgs,

                 'BtNavEtp_adel_norm': '%sBtNavEtp_adel_norm.png' % raíz_imgs,
                 'BtNavEtp_adel_bloq': '%sBtNavEtp_adel_bloq.png' % raíz_imgs,
                 'BtNavEtp_adel_sel': '%sBtNavEtp_adel_sel.png' % raíz_imgs,
                 'BtNavEtp_atrs_norm': '%sBtNavEtp_atrs_norm.png' % raíz_imgs,
                 'BtNavEtp_atrs_bloq': '%sBtNavEtp_atrs_bloq.png' % raíz_imgs,
                 'BtNavEtp_atrs_sel': '%sBtNavEtp_atrs_sel.png' % raíz_imgs,

                 'BtNavSub_adel_norm': '%sBtNavSub_adel_norm.png' % raíz_imgs,
                 'BtNavSub_adel_bloq': '%sBtNavSub_adel_bloq.png' % raíz_imgs,
                 'BtNavSub_adel_sel': '%sBtNavSub_adel_sel.png' % raíz_imgs,
                 'BtNavSub_atrs_norm': '%sBtNavSub_atrs_norm.png' % raíz_imgs,
                 'BtNavSub_atrs_bloq': '%sBtNavSub_atrs_bloq.png' % raíz_imgs,
                 'BtNavSub_atrs_sel': '%sBtNavSub_atrs_sel.png' % raíz_imgs,


                 'BtBorrarItema_norm': '%sBtBorrarItema_norm.png' % raíz_imgs,
                 'BtBorrarItema_sel': '%sBtBorrarItema_sel.png' % raíz_imgs,
                 'BtBorrarItema_bloq': '%sBtBorrarItema_bloq.png' % raíz_imgs,
                 'BtEditarItema_norm': '%sBtEditarItema_norm.png' % raíz_imgs,
                 'BtEditarItema_sel': '%sBtEditarItema_sel.png' % raíz_imgs,

                 'BtCasilla_norm': '%sBtCasilla_norm.png' % raíz_imgs,
                 'BtCasilla_sel': '%sBtCasilla_sel.png' % raíz_imgs,
                 'BtCasilla_bloq': '%sBtCasilla_bloq.png' % raíz_imgs

                 }


def escalar_colores(color1, color2, n):

    def escalar(val1, val2, m):
            escl = [val1/256 + (val2/256 - val1/256)*i/(m-1) for i in range(m)]
            return escl

    r = escalar(color1[0], color2[0], n)
    v = escalar(color1[1], color2[1], n)
    a = escalar(color1[2], color2[2], n)

    return list(zip(r, v, a))
