import tkinter as tk
from tkinter import filedialog as diálogo

from Interfaz import CajasGenéricas as CjG
from Interfaz import Botones as Bt
from Interfaz import Formatos as Fm
from Interfaz import ControlesGenéricos as CtrG
from Interfaz import Controles as Ctrl
from Interfaz import Arte as Art

from Conectado import Conectado
from MDS import EnvolturaMDS
from Biofísico import EnvolturaBF


class CajaSubEtp11(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        símismo.receta = {}

        caja_mds = tk.Frame(símismo, **Fm.formato_cajas)
        lín_vert = tk.Label(símismo, bg='black')
        caja_bf = tk.Frame(símismo, **Fm.formato_cajas)
        lín_hor = tk.Frame(símismo, bg='black')
        caja_con = tk.Frame(símismo, **Fm.formato_cajas)

        etiq_mds = tk.Label(caja_mds, text=apli.Trads['MDS'], **Fm.formato_etiq_cargar_mod)
        Bt.BotónTexto(caja_mds, texto='Cargar', comanda=símismo.buscar_mds,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_bts_cargar_mod, tipo_ubic='place')
        símismo.EtiqErrCargarMDS = tk.Label(caja_mds, text=apli.Trads['ErrorCargarMDS'],
                                            **Fm.formato_etiq_error)

        etiq_bf = tk.Label(caja_bf, text=apli.Trads['ModeloBiofísico'], **Fm.formato_etiq_cargar_mod)
        Bt.BotónTexto(caja_bf, texto=apli.Trads['Cargar'], comanda=símismo.buscar_bf,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_bts_cargar_mod, tipo_ubic='place')
        símismo.EtiqErrCargarBf = tk.Label(caja_bf, text=apli.Trads['ErrorCargarBf'],
                                           **Fm.formato_etiq_error)

        etiq_sino = tk.Label(caja_con, text=apli.Trads['O...'], **Fm.formato_etiq_sino)
        etiq_con = tk.Label(caja_con, text=apli.Trads['CargarModeloConectado'], **Fm.formato_etiq_cargar_con)

        etiq_sino.pack(**Fm.ubic_etiqs_sino_con)
        etiq_con.pack(**Fm.ubic_etiqs_sino_con)
        Bt.BotónTexto(caja_con, texto='Modelo conectado', comanda=símismo.buscar_con,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación={}, tipo_ubic='pack')
        símismo.EtiqErrCargarMod = tk.Label(caja_con, text=apli.Trads['ErrorCreandoMod'],
                                            **Fm.formato_etiq_error)

        etiq_mds.place(**Fm.ubic_etiqs_bts_cargar)
        etiq_bf.place(**Fm.ubic_etiqs_bts_cargar)

        caja_mds.place(**Fm.ubic_caja_cargar_mds)
        lín_vert.place(**Fm.ubic_lín_vert_med)
        caja_bf.place(**Fm.ubic_caja_cargar_bf)
        lín_hor.place(**Fm.ubic_lín_hor)
        caja_con.place(**Fm.ubic_caja_cargar_conectado)

    def buscar_mds(símismo):
        apli = símismo.apli
        nombre_archivo_mds = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelospublicadosVENSIM'], '*.vpm')],
                                                     title=apli.Trads['CargarMDS'])
        if nombre_archivo_mds:
            rec = símismo.receta
            rec['mds'] = nombre_archivo_mds

            try:
                EnvolturaMDS(programa_mds='VENSIM', ubicación_modelo=rec['mds'])
                símismo.EtiqErrCargarMDS.pack_forget()
            except (FileNotFoundError, AssertionError):
                símismo.EtiqErrCargarMDS.pack(**Fm.ubic_EtiqErrCargarMod)
                return

            símismo.verificar_completo()

    def buscar_bf(símismo):
        apli = símismo.apli
        nombre_archivo_bf = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelosPython'], '*.py')],
                                                    title=apli.Trads['CargarModeloBF'])
        if nombre_archivo_bf:
            rec = símismo.receta
            rec['bf'] = nombre_archivo_bf

            try:
                EnvolturaBF(ubicación_modelo=rec['bf'])
                símismo.EtiqErrCargarBf.pack_forget()
            except (FileNotFoundError, AssertionError):
                símismo.EtiqErrCargarBf.pack(**Fm.ubic_EtiqErrCargarMod)
                return

            símismo.verificar_completo()

    def buscar_con(símismo):
        apli = símismo.apli
        nombre_archivo_con = diálogo.askopenfilename(filetypes=[(apli.Trads['ArchivoTinamit'], '*.tin')],
                                                     title=apli.Trads['CargarModeloConectado'])
        if nombre_archivo_con:
            rec = símismo.receta
            rec['nombre_archivo_bf'] = nombre_archivo_con

    def verificar_completo(símismo):
        rec = símismo.receta
        if 'mds' in rec.keys() and 'bf' in rec.keys():
            try:
                símismo.apli.modelo = Conectado(archivo_mds=rec['mds'],
                                                archivo_biofísico=rec['bf'])
                símismo.Modelo = símismo.apli.modelo
                símismo.pariente.desbloquear_cajas([2])
            except (FileNotFoundError, AssertionError):
                símismo.EtiqErrCargarMod.pack(**Fm.ubic_EtiqErrCargarMod)
                símismo.pariente.bloquear_cajas([2])
                return

            símismo.EtiqErrCargarMod.pack_forget()
            símismo.pariente.desbloquear_cajas([2])

        else:
            símismo.pariente.bloquear_cajas([2])
            return False


class CajaSubEtp21(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_ctrls = tk.Frame(cj_bajo, bg='red')

        cj_izq = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsMDS = CtrG.Menú(cj_izq, nombre=apli.Trads['MDS'], opciones='', ancho=Fm.ancho_MnVars,
                                      ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')

        cj_med = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        bt_dir = Bt.BotónAltern(cj_med, formato=Fm.formato_botones,
                                img_1=Art.imagen('BtConecciónIzqDer'), img_2=Art.imagen('BtConecciónDerIzq'),
                                ubicación=Fm.ubic_ObjCjCentrCtrl, tipo_ubic='pack')
        símismo.factor_conv = CtrG.IngrNúm(cj_med, límites=(0, None), val_inic=1, prec='dec', nombre=apli.Trads['X'],
                                           ubicación=Fm.ubic_ObjCjCentrCtrl, tipo_ubic='pack')

        cj_derech = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsBf = CtrG.Menú(cj_derech, nombre=apli.Trads['Biofísico'], opciones='', ancho=Fm.ancho_MnVars,
                                     ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')

        cj_bts = tk.Frame(cj_bajo, **Fm.formato_cajas)

        bt_guardar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Guardar'],
                                   ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Borrar'],
                                  ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )

        cj_izq.pack(**Fm.ubic_CtrlsConectar)
        cj_med.pack(**Fm.ubic_CtrlsConectar)
        cj_derech.pack(**Fm.ubic_CtrlsConectar)

        dic_controles = {'VarMDS': símismo.MnVarsMDS, 'DirIzqDer': bt_dir, 'Conversión': símismo.factor_conv,
                         'VarBf': símismo.MnVarsBf}

        símismo.lista = Ctrl.ListaConexiónes(símismo, ubicación=Fm.ubic_CjLstConecciones, tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsConex(
                apli=apli, controles=dic_controles,
                lista=símismo.lista,
                bt_guardar=bt_guardar, bt_borrar=bt_borrar
        )

        cj_ctrls.place(**Fm.ubic_CjCtrlsConectar)
        cj_bts.place(**Fm.ubic_CjBtsConectar)
        cj_bajo.place(**Fm.ubic_CjBajoConex)

    def acción_desbloquear(símismo):
        símismo.Modelo = símismo.apli.modelo
        vars_mds = símismo.Modelo.mds.sacar_vars()
        vars_bf = símismo.Modelo.bf.sacar_vars()

        símismo.MnVarsMDS.refrescar(opciones=vars_mds)
        símismo.MnVarsBf.refrescar(opciones=vars_bf)

        símismo.verificar_completo()

    def verificar_completo(símismo):
        if len(símismo.Modelo.bf.vars_entrando) or len(símismo.Modelo.mds.vars_entrando):
            símismo.pariente.desbloquear_cajas([2])
            return True
        else:
            símismo.pariente.bloquear_cajas([2])
            return False


class CajaSubEtp31(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='¿Con qué lo vas a predecir?', núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        # cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)
        #
        # cj_ctrls = tk.Frame(cj_bajo, **Fm.formato_cajas)
        # ingr_nombre = CtrG.IngrTexto(cj_ctrls, 'Nombre:', ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')
        #
        # símismo.MnVarBD = CtrG.Menú(cj_ctrls, nombre='A base de:', opciones='',
        #                             ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')
        #
        # menú_calc = CtrG.Menú(cj_ctrls, nombre='Calculado con:',
        #                       opciones=['val_tot', 'val_prom', 'núm_días', 'núm_días_consec'],
        #                       texto_opciones=['Valor total', 'Valor promedio', 'No. días', 'No. días consecutivos'],
        #                       inicial='val_tot',
        #                       ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')
        #
        # cj_filtr_val = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        # menú_filtr_val = CtrG.Menú(cj_filtr_val, nombre='Con valores:',
        #                            opciones=['ninguno', 'igual', 'sup', 'inf', 'entre'],
        #                            texto_opciones=['Sin límites', 'Igual a', 'Superior a', 'Inferior a', 'Entre'],
        #                            inicial='ninguno',
        #                            ubicación=Fm.ubic_CtrlsFltrValX, tipo_ubic='pack',
        #                            ancho=7)
        # cj_1_filtro = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        # ingr_fltr_único = CtrG.IngrNúm(cj_1_filtro, límites=None, prec='dec',
        #                                ubicación=Fm.ubic_CtrlsFltrValX, ancho=5,
        #                                tipo_ubic='pack')
        # cj_2_filtros = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        # ingr_fltr_1 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
        #                            ubicación=Fm.ubic_CtrlsFltrValX, ancho=3,
        #                            tipo_ubic='pack')
        # etiq_2_filtrs = tk.Label(cj_2_filtros, text='y', **Fm.formato_EtiqCtrl)
        # etiq_2_filtrs.pack(**Fm.ubic_CtrlsFltrValX)
        # ingr_fltr_2 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
        #                            ubicación=Fm.ubic_CtrlsFltrValX, ancho=3,
        #                            tipo_ubic='pack')
        #
        # símismo.ops_cj_ingr_fltr_val = {
        #     '': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
        #     'ninguno': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
        #     'igual': cj_1_filtro,
        #     'sup': cj_1_filtro,
        #     'inf': cj_1_filtro,
        #     'entre': cj_2_filtros
        # }
        #
        # símismo.cj_ingr_fltr_val = símismo.ops_cj_ingr_fltr_val['']
        #
        # cj_fltr_tmp = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        # etiq_filtr_tiempo = tk.Label(cj_fltr_tmp, text='En el periodo desde:', **Fm.formato_EtiqCtrl)
        # cj_tmp_inic = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        # ingr_fltr_tp_inic = CtrG.IngrNúm(cj_tmp_inic, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
        #                                  ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', orden='ingr')
        # menú_fltr_tp_inic = CtrG.Menú(cj_tmp_inic, nombre=None,
        #                               opciones=['rel', 'abs'],
        #                               texto_opciones=['desde hoy', 'del año'], inicial='abs',
        #                               ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', ancho=7)
        # etiq_hasta = tk.Label(cj_tmp_inic, text='hasta', **Fm.formato_EtiqCtrl)
        # etiq_hasta.pack(**Fm.ubic_CtrlsFltrTmpX)
        #
        # cj_tmp_fin = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        # ingr_fltr_tp_fin = CtrG.IngrNúm(cj_tmp_fin, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
        #                                 ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', orden='ingr')
        # menú_fltr_tp_fin = CtrG.Menú(cj_tmp_fin, nombre=None,
        #                              opciones=['rel', 'abs'],
        #                              texto_opciones=['desde hoy', 'del año'], inicial='rel',
        #                              ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', ancho=7)
        #
        # cj_bts = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        #
        # bt_guardar = Bt.BotónTexto(cj_bts, texto='Guardar',
        #                            ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
        #                            formato_norm=Fm.formato_BtGuardar_norm,
        #                            formato_sel=Fm.formato_BtGuardar_sel,
        #                            formato_bloq=Fm.formato_BtGuardars_bloq,
        #                            )
        # bt_borrar = Bt.BotónTexto(cj_bts, texto='Borrar',
        #                           ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
        #                           formato_norm=Fm.formato_BtBorrar_norm,
        #                           formato_sel=Fm.formato_BtBorrar_sel,
        #                           formato_bloq=Fm.formato_BtBorrars_bloq,
        #                           )
        #
        # dic_controles = {'Nombre': ingr_nombre, 'VarBD': símismo.MnVarBD, 'MétodoCalc': menú_calc,
        #                  'FiltroVal': menú_filtr_val,
        #                  'FiltroValÚn': ingr_fltr_único, 'FitroValEntre1': ingr_fltr_1, 'FitroValEntre2': ingr_fltr_2,
        #                  'FiltroTmpInic': ingr_fltr_tp_inic, 'RefTmpInic': menú_fltr_tp_inic,
        #                  'FiltroTmpFin': ingr_fltr_tp_fin, 'RefTmpFin': menú_fltr_tp_fin}
        #
        # símismo.gráfico = Ctrl.GráfVarX(cj_bajo, ubicación=Fm.ubic_GráficoVarsX, tipo_ubic='place')
        # símismo.lista = Ctrl.ListaVarsX(símismo, ubicación=Fm.ubic_CjLstVarsX, tipo_ubic='place')
        #
        # símismo.grupo_controles = Ctrl.GrpCtrlsVarX(pariente=símismo, apli=apli, controles=dic_controles,
        #                                             gráfico=símismo.gráfico,
        #                                             lista=símismo.lista, bt_guardar=bt_guardar, bt_borrar=bt_borrar)
        # cj_filtr_val.pack(**Fm.ubic_CtrlsVarX)
        #
        # etiq_filtr_tiempo.pack(**Fm.ubic_CtrlsVarX)
        # cj_tmp_inic.pack(**Fm.ubic_CtrlsVarX)
        # cj_tmp_fin.pack(**Fm.ubic_CtrlsVarX)
        # cj_fltr_tmp.pack(**Fm.ubic_cj_fltr_tmpX)
        #
        # cj_bts.pack(**Fm.ubic_CjBtsGrupoCtrl)
        #
        # cj_ctrls.place(**Fm.ubic_CjCtrlsVarsX)
        # cj_bajo.place(**Fm.ubic_CjBajoSE22)

    def acción_desbloquear(símismo):
        símismo.lista.objetos = símismo.apli.modelo.config.varsX
        símismo.Modelo = símismo.apli.modelo
        cols = [v.nombre for ll, v in símismo.Modelo.base_central.vars.items()]
        símismo.MnVarBD.refrescar(opciones=cols)

        símismo.verificar_completo()

    def verificar_completo(símismo):
        if len(símismo.apli.modelo.config.varsX) > 0:
            símismo.pariente.desbloquear_cajas([3])
        else:
            símismo.pariente.bloquear_cajas([3])

    def cambió_filtro_val(símismo, val):
        if símismo.cj_ingr_fltr_val is not símismo.ops_cj_ingr_fltr_val[val]:
            símismo.cj_ingr_fltr_val.pack_forget()
            símismo.cj_ingr_fltr_val = símismo.ops_cj_ingr_fltr_val[val]
            símismo.cj_ingr_fltr_val.pack(**Fm.ubic_CtrlsFltrValX)


class CajaSubEtp41(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='Sería útil calibrar...', núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        # símismo.bt = Bt.BotónTexto(símismo, texto='Calibrar modelo',
        #                            formato_norm=Fm.formato_BtCalib_norm, formato_sel=Fm.formato_BtCalib_sel,
        #                            comanda=símismo.acción_bt_calibrar,
        #                            ubicación=Fm.ubic_BtCalib, tipo_ubic='place')

    def acción_bt_calibrar(símismo):
        símismo.Modelo.config.calibrar()
        símismo.verificar_completo()

    def acción_desbloquear(símismo):
        símismo.Modelo = símismo.apli.modelo
        símismo.verificar_completo()

    def verificar_completo(símismo):
        if símismo.Modelo.config.pesos_vars is not None:
            símismo.pariente.desbloquear_subcajas([2])
        else:
            símismo.pariente.bloquear_subcajas([2])
