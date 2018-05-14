from tinamit.Geog.Geog import Geografía
from tinamit.Geog.Geog import Lugar
from tinamit.Geog.Geog import conv_vars

conv_vars = conv_vars


class Lugar(Lugar):

    def observar_diarios(símismo, archivo, cols_datos, c_fecha, conv):
        return super().observar_diarios(archivo=archivo, cols_datos=cols_datos, c_fecha=c_fecha, conv=conv)

    def observar_mensuales(símismo, archivo, cols_datos, meses, años, conv):
        return super().observar_mensuales(archivo=archivo, cols_datos=cols_datos, meses=meses, años=años, conv=conv)

    def observar_anuales(símismo, archivo, cols_datos, años, conv):
        return super().observar_anuales(archivo=archivo, cols_datos=cols_datos, años=años, conv=conv)

    def prep_datos(símismo, fecha_inic, fecha_final, tcr, prefs=None, lím_prefs=False, regenerar=False):
        return super().prep_datos(fecha_inic=fecha_inic, fecha_final=fecha_final, tcr=tcr, prefs=prefs, lím_prefs=lím_prefs, regenerar=regenerar)

    def devolver_datos(símismo, vars_clima, f_inic, f_final):
        return super().devolver_datos(vars_clima=vars_clima, f_inic=f_inic, f_final=f_final)

    def comb_datos(símismo, vars_clima, combin, f_inic, f_final):
        return super().comb_datos(vars_clima=vars_clima, combin=combin, f_inic=f_inic, f_final=f_final)


class Geografía(Geografía):

    def dibujar(símismo, archivo, valores=None, título=None, unidades=None, colores=None, escala_num=None):
        return super().dibujar(archivo=archivo, valores=valores, título=título, unidades=unidades, colores=colores, escala_num=escala_num)

    def agregar_forma(símismo, archivo, nombre=None, tipo=None, alpha=None, color=None, llenar=None):
        return super().agregar_forma(archivo=archivo, nombre=nombre, tipo=tipo, alpha=alpha, color=color, llenar=llenar)

    def agregar_frm_regiones(símismo, archivo, col_id=None, col_orden=None, escala_geog=None):
        return super().agregar_frm_regiones(archivo=archivo, col_id=col_id, col_orden=col_orden, escala_geog=escala_geog)

    def agregar_info_regiones(símismo, archivo, col_cód, orden_jer=None, grupos=None):
        return super().agregar_info_regiones(archivo=archivo, col_cód=col_cód, orden_jer=orden_jer, grupos=grupos)

    def leer_archivo_info_reg(símismo, archivo, orden_jer, col_cód, grupos=None):
        return super().leer_archivo_info_reg(archivo=archivo, orden_jer=orden_jer, col_cód=col_cód, grupos=grupos)

    def obt_lugares_en(símismo, escala=None, en=None, por=None):
        return super().obt_lugares_en(escala=escala, en=en, por=por)

    def obt_en_grupo(símismo, tipo_grupo, grupos):
        return super().obt_en_grupo(tipo_grupo=tipo_grupo, grupos=grupos)
