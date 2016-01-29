import tkinter as tk
from tkinter import filedialog as diálogo

from Interfaz import CajasGenéricas as CjG
from Interfaz import Botones as Bt
from Interfaz import Formatos as Fm
from Interfaz import ControlesGenéricos as CtrG
from Interfaz import Controles as Ctrl

from Modelo import Modelo


class CajaSubEtp11(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['Cargardatos'], núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        cj_bts = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.bt_cargar_bd = Bt.BotónTexto(cj_bts, texto=apli.Trads['BasedeDatos'],
                                             comanda=símismo.acción_bt_cargar_bd,
                                             formato_norm=Fm.formato_BtsCarg_norm, formato_sel=Fm.formato_BtsCarg_sel,
                                             ubicación=Fm.ubic_BtsCarg, tipo_ubic='pack')
        símismo.bt_cargar_pr = Bt.BotónTexto(cj_bts, texto=apli.Trads['ProyectoExistente'],
                                             comanda=símismo.acción_bt_cargar_pr,
                                             formato_norm=Fm.formato_BtsCarg_norm, formato_sel=Fm.formato_BtsCarg_sel,
                                             ubicación=Fm.ubic_BtsCarg, tipo_ubic='pack')
        cj_bts.place(**Fm.ubic_CjBtsCarg)

        símismo.EtiqErrCargarBD = tk.Label(símismo, text='Error cargando la base de datos', **Fm.formato_etiq_error)

        símismo.CjAct = CjG.CajaActivable(símismo, ubicación=Fm.ubic_CjFechaHora, tipo_ubic='place')

        cj_mn_col_fecha = tk.Frame(símismo.CjAct, **Fm.formato_cajas)
        símismo.MnColFecha = CtrG.Menú(cj_mn_col_fecha, nombre=apli.Trads['ColumnaFecha'], opciones='',
                                       comanda=símismo.acción_mn_col_fecha,
                                       ubicación=Fm.ubic_MnCol, tipo_ubic='pack')
        cj_mn_col_fecha.pack(**Fm.ubic_CjMnCol)

        cj_mn_col_hora = tk.Frame(símismo.CjAct, **Fm.formato_cajas)
        símismo.MnColHora = CtrG.Menú(cj_mn_col_hora, nombre=apli.Trads['ColumnaHora'], opciones='',
                                      comanda=símismo.acción_mn_col_hora,
                                      ubicación=Fm.ubic_MnCol, tipo_ubic='pack')
        cj_mn_col_hora.pack(**Fm.ubic_CjMnCol)

        símismo.CjAct.especificar_objetos([símismo.MnColHora, símismo.MnColFecha])

        símismo.EtiqErrColFecha = tk.Label(cj_mn_col_fecha,
                                           text=apli.Trads['ErrorCargarFecha'],
                                           **Fm.formato_etiq_error)

        símismo.EtiqErrColHora = tk.Label(cj_mn_col_hora,
                                          text=apli.Trads['ErrorCargarHora'],
                                          **Fm.formato_etiq_error)

        símismo.MnColFecha.estab_exclusivo(símismo.MnColHora)
        símismo.CjAct.bloquear()

    def acción_bt_cargar_bd(símismo):
        apli = símismo.apli
        archivo_bd = diálogo.askopenfilename(filetypes=[(apli.Trads['FormatoComas'], '*.csv'),
                                                        (apli.Trads['FormatoTexto'], '*.txt')],
                                             title=apli.Trads['CargarBaseDatos'])
        try:
            símismo.Modelo = Modelo(archivo_bd)
            símismo.apli.modelo = símismo.Modelo
            cols_bd = símismo.Modelo.base_central.nombres_cols
            símismo.EtiqErrCargarBD.pack_forget()
        except (ValueError, FileNotFoundError):
            símismo.EtiqErrCargarBD.pack(**Fm.ubic_EtiqErrCargarBD)
            return

        símismo.CjAct.desbloquear()
        símismo.MnColFecha.refrescar(opciones=cols_bd, texto_opciones=cols_bd)
        símismo.MnColHora.refrescar(opciones=cols_bd, texto_opciones=cols_bd)

    def acción_bt_cargar_pr(símismo):
        apli = símismo.apli
        archivo_bd = diálogo.askopenfilename(filetypes=[(apli.Trads['ProyectoKutuj'], '*.kut')],
                                             title=apli.Trads['CargarProyecto'])
        # para hacer: hacer más cosas aquí

    def acción_mn_col_fecha(símismo, col):
        try:
            símismo.Modelo.base_central.estab_col_fecha(col)
            símismo.EtiqErrColFecha.pack_forget()
        except ValueError:
            símismo.EtiqErrColFecha.pack(**Fm.ubic_EtiqErrCol)

        if símismo.verificar_completo():
            símismo.pariente.desbloquear_subcajas([2])
        else:
            símismo.pariente.bloquear_subcajas([2])

    def acción_mn_col_hora(símismo, col):
        try:
            símismo.Modelo.base_central.estab_col_hora(col)
            símismo.EtiqErrColHora.pack_forget()
        except ValueError:
            símismo.EtiqErrColHora.pack(**Fm.ubic_EtiqErrCol)

        if símismo.verificar_completo():
            símismo.pariente.desbloquear_subcajas([2])
        else:
            símismo.pariente.bloquear_subcajas([2])

    def verificar_completo(símismo):
        if len(símismo.Modelo.base_central.fechas) and len(símismo.Modelo.base_central.tiempos):
            return True
        else:
            return False


class CajaSubEtp12(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='Especificar variables', núm=2, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_ctrls = tk.Frame(cj_bajo, **Fm.formato_cajas)
        ingr_nombre = CtrG.IngrTexto(cj_ctrls, 'Nombre:', ubicación=Fm.ubic_CtrlsVarBD, tipo_ubic='pack')

        símismo.MnCol = CtrG.Menú(cj_ctrls, nombre='Columna:', opciones='',
                                  ubicación=Fm.ubic_CtrlsVarBD, tipo_ubic='pack')

        escl_fecha_inic = CtrG.Escala(cj_bajo, texto='Día inicio año', límites=(1, 365), valor_inicial=1, prec='ent',
                                      ubicación=Fm.ubic_escl_fecha_inic, tipo_ubic='place')

        menú_transform = CtrG.Menú(cj_ctrls, nombre='Transformación:',
                                   opciones=['sumar', 'máx', 'mín', 'prom'],
                                   texto_opciones=['Sumar', 'Máximo', 'Mínimo', 'Promedio'],
                                   ubicación=Fm.ubic_CtrlsVarBD, tipo_ubic='pack')

        menú_interpol = CtrG.Menú(cj_ctrls, nombre='Interpolación:',
                                  opciones=['trap', 'ninguno'],
                                  texto_opciones=['Trapezoidal', 'Ninguno'],
                                  inicial='trap',
                                  ubicación=Fm.ubic_CtrlsVarBD, tipo_ubic='pack')

        cj_bts = tk.Frame(cj_ctrls, **Fm.formato_cajas)

        bt_guardar = Bt.BotónTexto(cj_bts, texto='Guardar',
                                   ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto='Borrar',
                                  ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )
        cj_bts.pack(**Fm.ubic_CjBtsGrupoCtrl)

        dic_controles = {'Nombre': ingr_nombre, 'Columna': símismo.MnCol, 'Fecha_inic': escl_fecha_inic,
                         'Transformación': menú_transform, 'Interpol': menú_interpol}

        símismo.gráfico = Ctrl.GráfVarBD(cj_bajo, ubicación=Fm.ubic_GráficoVarsBD, tipo_ubic='place')
        símismo.lista = Ctrl.ListaVarsBD(símismo, ubicación=Fm.ubic_CjLstVarsBD, tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsVarBD(
                apli=apli, controles=dic_controles, gráfico=símismo.gráfico,
                lista=símismo.lista,
                bt_guardar=bt_guardar, bt_borrar=bt_borrar
        )
        cj_ctrls.place(**Fm.ubic_CjCtrlsVarsBD)
        cj_bajo.place(**Fm.ubic_CjBajoSE12)

    def acción_desbloquear(símismo):
        símismo.Modelo = símismo.apli.modelo
        bd = símismo.Modelo.base_central
        cols_potenciales = bd.nombres_cols.copy()
        cols_potenciales.remove(bd.id_cols['fecha'])
        cols_potenciales.remove(bd.id_cols['tiempo'])
        símismo.MnCol.refrescar(opciones=cols_potenciales, texto_opciones=cols_potenciales)
        símismo.lista.objetos = símismo.apli.modelo.base_central.vars

        símismo.verificar_completo()

    def verificar_completo(símismo):
        if len(símismo.apli.modelo.base_central.vars) > 0:
            símismo.pariente.desbloquear_cajas([2])
            return True
        else:
            símismo.pariente.bloquear_cajas([2])
            return False


class CajaSubEtp21(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='¿Qué quieres predecir?', núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        cj_ctrls = tk.Frame(símismo, **Fm.formato_cajas)
        ingr_nombre = CtrG.IngrTexto(cj_ctrls, 'Nombre:', ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        símismo.MnVarBD = CtrG.Menú(cj_ctrls, nombre='A base de:', opciones='',
                                    ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        menú_calc = CtrG.Menú(cj_ctrls, nombre='Calculado con:',
                              opciones=['val_tot', 'val_prom', 'núm_días', 'núm_días_consec'],
                              texto_opciones=['Valor total', 'Valor promedio', 'No. días', 'No. días consecutivos'],
                              inicial='val_tot',
                              ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        cj_filtr_val = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        menú_filtr_val = CtrG.Menú(cj_filtr_val, nombre='Con valores:',
                                   opciones=['ninguno', 'igual', 'sup', 'inf', 'entre'],
                                   texto_opciones=['Sin límites', 'Igual a', 'Superior a', 'Inferior a', 'Entre'],
                                   inicial='ninguno',
                                   ubicación=Fm.ubic_CtrlsFltrValY, tipo_ubic='pack',
                                   ancho=7)
        cj_1_filtro = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        ingr_fltr_único = CtrG.IngrNúm(cj_1_filtro, límites=None, prec='dec',
                                       ubicación=Fm.ubic_CtrlsFltrValY, ancho=5,
                                       tipo_ubic='pack')
        cj_2_filtros = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        ingr_fltr_1 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
                                   ubicación=Fm.ubic_CtrlsFltrValY, ancho=3,
                                   tipo_ubic='pack')
        etiq_2_filtrs = tk.Label(cj_2_filtros, text='y', **Fm.formato_EtiqCtrl)
        etiq_2_filtrs.pack(**Fm.ubic_CtrlsFltrValY)
        ingr_fltr_2 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
                                   ubicación=Fm.ubic_CtrlsFltrValY, ancho=3,
                                   tipo_ubic='pack')

        símismo.ops_cj_ingr_fltr_val = {
            '': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
            'ninguno': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
            'igual': cj_1_filtro,
            'sup': cj_1_filtro,
            'inf': cj_1_filtro,
            'entre': cj_2_filtros
        }

        símismo.cj_ingr_fltr_val = símismo.ops_cj_ingr_fltr_val['']

        cj_fltr_tmp = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        etiq_filtr_tiempo = tk.Label(cj_fltr_tmp, text='En el periodo desde:', **Fm.formato_EtiqCtrl)
        cj_tmp_inic = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        ingr_fltr_tp_inic = CtrG.IngrNúm(cj_tmp_inic, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
                                         ubicación=Fm.ubic_CtrlsFltrTmpY, tipo_ubic='pack', orden='ingr')
        menú_fltr_tp_inic = CtrG.Menú(cj_tmp_inic, nombre=None,
                                      opciones=['rel', 'abs'],
                                      texto_opciones=['desde hoy', 'del año'], inicial='abs',
                                      ubicación=Fm.ubic_CtrlsFltrTmpY, tipo_ubic='pack', ancho=7)
        etiq_hasta = tk.Label(cj_tmp_inic, text='hasta', **Fm.formato_EtiqCtrl)
        etiq_hasta.pack(**Fm.ubic_CtrlsFltrTmpY)

        cj_tmp_fin = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        ingr_fltr_tp_fin = CtrG.IngrNúm(cj_tmp_fin, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
                                        ubicación=Fm.ubic_CtrlsFltrTmpY, tipo_ubic='pack', orden='ingr')
        menú_fltr_tp_fin = CtrG.Menú(cj_tmp_fin, nombre=None,
                                     opciones=['rel', 'abs'],
                                     texto_opciones=['desde hoy', 'del año'], inicial='rel',
                                     ubicación=Fm.ubic_CtrlsFltrTmpY, tipo_ubic='pack', ancho=7)

        cj_bts = tk.Frame(cj_ctrls, **Fm.formato_cajas)

        bt_guardar = Bt.BotónTexto(cj_bts, texto='Guardar',
                                   ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto='Borrar',
                                  ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )

        dic_controles = {'Nombre': ingr_nombre, 'VarBD': símismo.MnVarBD, 'MétodoCalc': menú_calc,
                         'FiltroVal': menú_filtr_val,
                         'FiltroValÚn': ingr_fltr_único, 'FitroValEntre1': ingr_fltr_1, 'FitroValEntre2': ingr_fltr_2,
                         'FiltroTmpInic': ingr_fltr_tp_inic, 'RefTmpInic': menú_fltr_tp_inic,
                         'FiltroTmpFin': ingr_fltr_tp_fin, 'RefTmpFin': menú_fltr_tp_fin}

        símismo.gráfico = Ctrl.GráfVarY(símismo, ubicación=Fm.ubic_GráficoVarsY, tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsVarY(pariente=símismo, apli=apli, controles=dic_controles,
                                                    gráfico=símismo.gráfico,
                                                    bt_guardar=bt_guardar, bt_borrar=bt_borrar)
        cj_filtr_val.pack(**Fm.ubic_CtrlsVarY)

        etiq_filtr_tiempo.pack(**Fm.ubic_CtrlsVarY)
        cj_tmp_inic.pack(**Fm.ubic_CtrlsVarY)
        cj_tmp_fin.pack(**Fm.ubic_CtrlsVarY)
        cj_fltr_tmp.pack(**Fm.ubic_cj_fltr_tmpY)

        cj_bts.pack(**Fm.ubic_CjBtsGrupoCtrl)

        cj_ctrls.place(**Fm.ubic_CjCtrlsVarsY)

    def acción_desbloquear(símismo):
        símismo.Modelo = símismo.apli.modelo
        cols = [v.nombre for ll, v in símismo.Modelo.base_central.vars.items()]
        símismo.MnVarBD.refrescar(opciones=cols)

        símismo.verificar_completo()

    def verificar_completo(símismo):
        if símismo.apli.modelo.config.varY is not None:
            símismo.pariente.desbloquear_subcajas([2])
        else:
            símismo.pariente.bloquear_subcajas([2])

    def cambió_filtro_val(símismo, val):
        if símismo.cj_ingr_fltr_val is not símismo.ops_cj_ingr_fltr_val[val]:
            símismo.cj_ingr_fltr_val.pack_forget()
            símismo.cj_ingr_fltr_val = símismo.ops_cj_ingr_fltr_val[val]
            símismo.cj_ingr_fltr_val.pack(**Fm.ubic_CtrlsFltrValY)


class CajaSubEtp22(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='¿Con qué lo vas a predecir?', núm=2, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_ctrls = tk.Frame(cj_bajo, **Fm.formato_cajas)
        ingr_nombre = CtrG.IngrTexto(cj_ctrls, 'Nombre:', ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        símismo.MnVarBD = CtrG.Menú(cj_ctrls, nombre='A base de:', opciones='',
                                    ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        menú_calc = CtrG.Menú(cj_ctrls, nombre='Calculado con:',
                              opciones=['val_tot', 'val_prom', 'núm_días', 'núm_días_consec'],
                              texto_opciones=['Valor total', 'Valor promedio', 'No. días', 'No. días consecutivos'],
                              inicial='val_tot',
                              ubicación=Fm.ubic_CtrlsVarX, tipo_ubic='pack')

        cj_filtr_val = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        menú_filtr_val = CtrG.Menú(cj_filtr_val, nombre='Con valores:',
                                   opciones=['ninguno', 'igual', 'sup', 'inf', 'entre'],
                                   texto_opciones=['Sin límites', 'Igual a', 'Superior a', 'Inferior a', 'Entre'],
                                   inicial='ninguno',
                                   ubicación=Fm.ubic_CtrlsFltrValX, tipo_ubic='pack',
                                   ancho=7)
        cj_1_filtro = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        ingr_fltr_único = CtrG.IngrNúm(cj_1_filtro, límites=None, prec='dec',
                                       ubicación=Fm.ubic_CtrlsFltrValX, ancho=5,
                                       tipo_ubic='pack')
        cj_2_filtros = tk.Frame(cj_filtr_val, **Fm.formato_cajas)
        ingr_fltr_1 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
                                   ubicación=Fm.ubic_CtrlsFltrValX, ancho=3,
                                   tipo_ubic='pack')
        etiq_2_filtrs = tk.Label(cj_2_filtros, text='y', **Fm.formato_EtiqCtrl)
        etiq_2_filtrs.pack(**Fm.ubic_CtrlsFltrValX)
        ingr_fltr_2 = CtrG.IngrNúm(cj_2_filtros, límites=None, prec='dec',
                                   ubicación=Fm.ubic_CtrlsFltrValX, ancho=3,
                                   tipo_ubic='pack')

        símismo.ops_cj_ingr_fltr_val = {
            '': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
            'ninguno': tk.Frame(cj_filtr_val, **Fm.formato_cajas),
            'igual': cj_1_filtro,
            'sup': cj_1_filtro,
            'inf': cj_1_filtro,
            'entre': cj_2_filtros
        }

        símismo.cj_ingr_fltr_val = símismo.ops_cj_ingr_fltr_val['']

        cj_fltr_tmp = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        etiq_filtr_tiempo = tk.Label(cj_fltr_tmp, text='En el periodo desde:', **Fm.formato_EtiqCtrl)
        cj_tmp_inic = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        ingr_fltr_tp_inic = CtrG.IngrNúm(cj_tmp_inic, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
                                         ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', orden='ingr')
        menú_fltr_tp_inic = CtrG.Menú(cj_tmp_inic, nombre=None,
                                      opciones=['rel', 'abs'],
                                      texto_opciones=['desde hoy', 'del año'], inicial='abs',
                                      ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', ancho=7)
        etiq_hasta = tk.Label(cj_tmp_inic, text='hasta', **Fm.formato_EtiqCtrl)
        etiq_hasta.pack(**Fm.ubic_CtrlsFltrTmpX)

        cj_tmp_fin = tk.Frame(cj_fltr_tmp, **Fm.formato_cajas)
        ingr_fltr_tp_fin = CtrG.IngrNúm(cj_tmp_fin, nombre='días', límites=(-365, 365), prec='ent', val_inic=0,
                                        ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', orden='ingr')
        menú_fltr_tp_fin = CtrG.Menú(cj_tmp_fin, nombre=None,
                                     opciones=['rel', 'abs'],
                                     texto_opciones=['desde hoy', 'del año'], inicial='rel',
                                     ubicación=Fm.ubic_CtrlsFltrTmpX, tipo_ubic='pack', ancho=7)

        cj_bts = tk.Frame(cj_ctrls, **Fm.formato_cajas)

        bt_guardar = Bt.BotónTexto(cj_bts, texto='Guardar',
                                   ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto='Borrar',
                                  ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )

        dic_controles = {'Nombre': ingr_nombre, 'VarBD': símismo.MnVarBD, 'MétodoCalc': menú_calc,
                         'FiltroVal': menú_filtr_val,
                         'FiltroValÚn': ingr_fltr_único, 'FitroValEntre1': ingr_fltr_1, 'FitroValEntre2': ingr_fltr_2,
                         'FiltroTmpInic': ingr_fltr_tp_inic, 'RefTmpInic': menú_fltr_tp_inic,
                         'FiltroTmpFin': ingr_fltr_tp_fin, 'RefTmpFin': menú_fltr_tp_fin}

        símismo.gráfico = Ctrl.GráfVarX(cj_bajo, ubicación=Fm.ubic_GráficoVarsX, tipo_ubic='place')
        símismo.lista = Ctrl.ListaVarsX(símismo, ubicación=Fm.ubic_CjLstVarsX, tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsVarX(pariente=símismo, apli=apli, controles=dic_controles,
                                                    gráfico=símismo.gráfico,
                                                    lista=símismo.lista, bt_guardar=bt_guardar, bt_borrar=bt_borrar)
        cj_filtr_val.pack(**Fm.ubic_CtrlsVarX)

        etiq_filtr_tiempo.pack(**Fm.ubic_CtrlsVarX)
        cj_tmp_inic.pack(**Fm.ubic_CtrlsVarX)
        cj_tmp_fin.pack(**Fm.ubic_CtrlsVarX)
        cj_fltr_tmp.pack(**Fm.ubic_cj_fltr_tmpX)

        cj_bts.pack(**Fm.ubic_CjBtsGrupoCtrl)

        cj_ctrls.place(**Fm.ubic_CjCtrlsVarsX)
        cj_bajo.place(**Fm.ubic_CjBajoSE22)

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


class CajaSubEtp31(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='Sería útil calibrar...', núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = None

        símismo.bt = Bt.BotónTexto(símismo, texto='Calibrar modelo',
                                   formato_norm=Fm.formato_BtCalib_norm, formato_sel=Fm.formato_BtCalib_sel,
                                   comanda=símismo.acción_bt_calibrar,
                                   ubicación=Fm.ubic_BtCalib, tipo_ubic='place')

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


class CajaSubEtp32(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre='...y aún mejor validar', núm=2, total=total)
        símismo.apli = apli


class CajaSubEtp41(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli


class CajaSubEtp51(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
