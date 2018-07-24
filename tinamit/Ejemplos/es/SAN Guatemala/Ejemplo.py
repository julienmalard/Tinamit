import os
import shutil

import numpy as np

from tinamit import guardar_json, cargar_json
from tinamit.Análisis.Datos import MicroDatos, Datos, SuperBD
from tinamit.EnvolturasMDS import generar_mds
from tinamit.Geog.Geog import Geografía

if __name__ == '__main__':  # Necesario para paralelización en Windows
    c = lambda x: os.path.join('C:\\Users\\jmalar1\\Documents\\Julien\\Bases de datos\\Iximulew', x)
    # EnvolturasMDS es una función que genera una instancia de ModeloMDS, tal como VENSIM
    modelo = generar_mds(archivo='Para Tinamït.mdl')
    print('vars', modelo.variables.keys())
    print('internos', modelo.internos)  # variables internos al EnvolturasMDS (p. ej., TIMESTEP y TIME en VENSIM)
    print('auxiliares', modelo.auxiliares)
    print('flujos', modelo.flujos)
    print('niveles', modelo.niveles)
    print('constantes', modelo.constantes)
    # print('vacíos', modelo.vacíos())

    geog = Geografía('Iximulew')
    geog.espec_estruct_geog(archivo='Geografía Iximulew.csv')

    ENCOVI_ind_2011 = MicroDatos('ENCOVI ind 2011', fuente=c('ENCOVIs\\2011\\BD Personas_final.csv'),
                                 tiempo=2011,
                                 lugar='munidept')
    ENCOVI_hog_2011 = MicroDatos('ENCOVI hog 2011', fuente=c('ENCOVIs\\2011\\BD Hogares_final.csv'), tiempo=2011,
                                 lugar='munidept')
    ENCOVI_reg_2011 = Datos('ENCOVI reg 2011', fuente=c('ENCOVIs\\2011\\BD regional_final.csv'), tiempo=2011,
                            lugar='id')

    datos_muni = Datos('Datos municipales', fuente=c('Datos muni\\Datos Muni Iximulew.csv'), tiempo='Año',
                       lugar='Código_lugar')
    datos_pob = Datos('Población', fuente=c('Población\\Población INE.csv'), tiempo='Año', lugar='Código')
    datos_tierra = Datos('Uso tierra', fuente=c('Uso de tierra\\Uso de tierra.csv'), tiempo='Año', lugar='Código')
    datos_superficie = Datos('Superficie', fuente=c('Uso de tierra\\Superficie.csv'), tiempo=None, lugar='Código')

    #
    bd = SuperBD('BD Iximulew', bds=[ENCOVI_hog_2011, ENCOVI_ind_2011, ENCOVI_reg_2011, datos_muni,
                                     datos_pob, datos_tierra, datos_superficie], geog=geog)
    bd.espec_var('Seguridad alimentaria', var_bd='SA_0', bds=ENCOVI_hog_2011)
    bd.espec_var('Seguridad alimentaria', var_bd='SA_0.fam', bds=ENCOVI_ind_2011)
    bd.espec_var('Seguridad alimentaria', var_bd='hog.SA_0', bds=ENCOVI_reg_2011)
    bd.espec_var('Educación formal', var_bd='educación.adultos', bds=ENCOVI_hog_2011)
    bd.espec_var('Educación formal', var_bd='educación', bds=ENCOVI_ind_2011)
    bd.espec_var('Educación sexual', var_bd='educación.sexual', bds=ENCOVI_ind_2011)
    bd.espec_var('Fertilidad', var_bd='fertilidad', bds=ENCOVI_ind_2011)
    bd.espec_var('Calidad de la dieta', var_bd='inv.défic.shannon.calidad.dieta', bds=ENCOVI_hog_2011)
    bd.espec_var('Cantidad de alimentos', var_bd='cantidad.dieta', bds=ENCOVI_hog_2011)

    # bd.espec_var('Ingresos salarial', var_bd='Ingresos.de.salario', cód_vacío='NA')
    # bd.espec_var('Ingresos agrícolas', var_bd='Ingresos.agrícolas', cód_vacío='NA')
    # bd.espec_var('Ingresos familiares', var_bd='Ingresos', cód_vacío='NA')
    bd.espec_var('Comercialización', var_bd='hog.prc.tierra.comercial', bds=ENCOVI_reg_2011)
    # bd.espec_var('Producción autoconsumo', var_bd='Producción.autoconsumo', cód_vacío='NA')
    bd.espec_var('Tamaño familia', var_bd='tamaño.familia', bds=ENCOVI_hog_2011)
    # bd.espec_var('Repetición escolar', var_bd='Repetición.escolar', cód_vacío='NA')
    bd.espec_var('Enfermedades infantiles', var_bd='enfermedades.infantiles.fam', bds=ENCOVI_hog_2011)
    bd.espec_var('Enfermedades infantiles', var_bd='ind.enfermedades.infantiles', bds=ENCOVI_reg_2011)
    bd.espec_var('Acceso agua potable', var_bd='disponibilidad.agua', bds=ENCOVI_hog_2011)
    bd.espec_var('Tratamiento agua', var_bd='tratamiento.agua', bds=ENCOVI_hog_2011)
    bd.espec_var('Higiene', var_bd='sanitación', bds=ENCOVI_hog_2011)

    bd.espec_var('Consumo leña por hogar', var_bd='talla.árb', bds=ENCOVI_hog_2011)
    bd.espec_var('Población', var_bd='Población', bds=datos_pob)
    bd.espec_var('Infraestructura vial', var_bd='Densidad vial (km/km2)', bds=datos_muni)
    bd.espec_var('Desnutrición crónica infantil', var_bd='Desntr_crón_inft', bds=datos_muni)

    bd.espec_var('Costumbre de consumo', var_bd='prc.dieta.hort', bds=ENCOVI_hog_2011)
    bd.espec_var('Superficie municipio', var_bd='Superficie (ha)', bds=datos_superficie)
    bd.espec_var('Fracción tierras a hortalizas', var_bd='prc.tierra.hortalizas', bds=ENCOVI_hog_2011)
    bd.espec_var('Fracción infantes inicial', var_bd='ind.edad.0.a.4', bds=ENCOVI_reg_2011)
    bd.espec_var('Fracción niños inicial', var_bd='ind.edad.5.a.14', bds=ENCOVI_reg_2011)
    bd.espec_var('Fracción adultos inicial', var_bd='ind.edad.15.a.54', bds=ENCOVI_reg_2011)

    bd.espec_var('Comercialización', var_bd='hog.prc.tierra.comercial', bds=ENCOVI_reg_2011)
    bd.espec_var('Comercialización', var_bd='prc.tierra.comercial', bds=ENCOVI_hog_2011)
    bd.espec_var('Riego', var_bd='riego', bds=ENCOVI_hog_2011)
    bd.espec_var('Uso insumos orgánicos', var_bd='uso.orgánico', bds=ENCOVI_hog_2011)
    bd.espec_var('Uso insumos químicos', var_bd='uso.abono.químico', bds=ENCOVI_hog_2011)

    bd.espec_var('Ingresos netos familiares', var_bd='hog.ingresos.per.cáp', bds=ENCOVI_reg_2011)
    bd.espec_var('Pobreza', var_bd='hog.brecha.pobr.gastos', bds=ENCOVI_reg_2011)
    bd.espec_var('Pobreza', var_bd='brecha.pobr.gastos', bds=ENCOVI_hog_2011)
    bd.espec_var('Desempleo', var_bd='ind.desempleo', bds=ENCOVI_reg_2011)

    # bd.espec_var('Tecnificación agrícola', var_bd='hog.tecni.agri', bds=ENCOVI_reg_2011)
    bd.espec_var('Tecnificación agrícola', var_bd='tecni.agri', bds=ENCOVI_hog_2011)
    bd.espec_var('Costos insumos', var_bd='costos.insumos.agri', bds=ENCOVI_hog_2011)
    bd.espec_var('Rendimiento milpa', var_bd='rendimiento.maíz', bds=ENCOVI_hog_2011)
    bd.espec_var('Gastos en enfermedades', var_bd='gastos.enfermedades.fam', bds=ENCOVI_hog_2011)
    bd.espec_var('Comida comprada', var_bd='cantidad.dieta.comp', bds=ENCOVI_hog_2011)
    bd.espec_var('Producción milpa', var_bd='prod.maíz', bds=ENCOVI_hog_2011)

    bd.espec_var('Producción hortalizas consumida', var_bd='dieta.hort.auto', bds=ENCOVI_hog_2011)
    bd.espec_var('Desempleo', var_bd='ind.desempleo', bds=ENCOVI_reg_2011)
    bd.espec_var('Emigración permanente', var_bd='migr.perm', bds=ENCOVI_reg_2011)
    bd.espec_var('Acceso a crédito', var_bd='acceso.prést', bds=ENCOVI_hog_2011)
    bd.espec_var('Acceso a crédito', var_bd='hog.acceso.prést', bds=ENCOVI_reg_2011)
    bd.espec_var('Tierra por familia', var_bd='tierra.agri', bds=ENCOVI_hog_2011)
    bd.espec_var('Tierra por familia', var_bd='tierra.agri.fam', bds=ENCOVI_ind_2011)
    bd.espec_var('Trabajo parcela', var_bd='trabajo.parcela', bds=ENCOVI_ind_2011)
    bd.espec_var('Demanda de trabajo', var_bd='demanda.trabajo', bds=ENCOVI_ind_2011)
    bd.espec_var('Trabajo infantil', var_bd='trabajo.infantil', bds=ENCOVI_hog_2011)
    bd.espec_var('Salario', var_bd='salario.hora.prom', bds=ENCOVI_ind_2011)
    bd.espec_var('Mortalidad infantil', var_bd='mortalidad.infantil', bds=ENCOVI_hog_2011)
    bd.espec_var('Atraso escolar', var_bd='atraso.escolar.fam', bds=ENCOVI_hog_2011)
    bd.espec_var('Disponibilidad trabajo', var_bd='ind.horas.trabajo', bds=ENCOVI_reg_2011)
    bd.espec_var('Producción hortalizas', var_bd='valor.econ.hort', bds=ENCOVI_hog_2011)
    bd.espec_var('Rendimiento hortalizas', var_bd='rendimiento.econ.hort', bds=ENCOVI_hog_2011)
    bd.espec_var('Educación inicial', var_bd='educación.adultos', bds=ENCOVI_hog_2011)

    conex = ConexDatos(bd=bd, modelo=modelo)
    conex.no_calibrados()

    _ = bd.obt_datos(l_vars=['Desnutrición crónica infantil'], tiempos=1986)


    def np_a_lista(d, d_f=None):
        if d_f is None:
            d_f = {}

        for ll, v in d.items():
            if isinstance(v, dict):
                d_f[ll] = {}
                np_a_lista(d=v, d_f=d_f[ll])
            elif isinstance(v, np.ndarray):
                d_f[ll] = v.tolist()
            elif isinstance(v, str):
                d_f[ll] = v
            else:
                try:
                    if v is None or np.any(np.isnan(v)):
                        d_f[ll] = 'None'
                    else:
                        d_f[ll] = v
                except TypeError:
                    d_f[ll] = 'None'

        return d_f


    def act_calib(cnx):

        if os.path.isfile(os.path.join(os.path.split(__file__)[0], 'calib.json')):
            shutil.copyfile(os.path.join(os.path.split(__file__)[0], 'calib.json'),
                            os.path.join(os.path.split(__file__)[0], 'calib2.json'))
            dic = cargar_json(os.path.join(os.path.split(__file__)[0], 'calib.json'))
            dic.update(cnx.dic_calibs)
        else:
            dic = cnx.dic_calibs

        guardar_json(np_a_lista(dic), arch=os.path.join(os.path.split(__file__)[0], 'calib.json'))

    # #1/(b*Educación formal+b2*Educación sexual+a)+c', paráms=['a', 'b', 'b2', 'c'],
    # #                   líms_paráms=[(0, None), (0, 50), (0, 50), (0, None)]
    # #_ = conex.calib_var('Demanda de trabajo',
    # #                    ec='a*((Tierra por familia+c)^b)',
    # #                    paráms=['a', 'b', 'c'],
    # #                    líms_paráms=[(0, None), (-10, 0), (0, 10)], por='Territorio', aprioris=True)
    # #
    # #_ = conex.calib_var('Venta de tierra',
    # #                    ec='máx(a*Pobreza)+b, Tierra por familia)',
    # #                    paráms=['a', 'b'],
    # #                    líms_paráms=[(0, None)] * 2, por='Territorio', aprioris=True)

    # _ = conex.estim_constante(const='Fracción infantes inicial', líms=(0, 1), por='Territorio', regional=True)
    # _ = conex.estim_constante(const='Fracción niños inicial', líms=(0, 1), por='Territorio', regional=True)
    # _ = conex.estim_constante(const='Fracción adultos inicial', líms=(0, 1), por='Territorio', regional=True)
    # _ = conex.estim_constante(const='Consumo leña por hogar', líms=(0, None), por='Territorio')
    # _ = conex.estim_constante(const='Infraestructura vial', líms=(0, None), regional=True)
    # _ = conex.estim_constante(const='Costumbre de consumo', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Educación sexual', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Superficie municipio', líms=(0, None), regional=True)
    # _ = conex.estim_constante(const='Fracción tierras a hortalizas', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Tratamiento agua', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Acceso agua potable', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Higiene', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Uso insumos orgánicos', líms=(0, 1), por='Territorio')
    # _ = conex.estim_constante(const='Disponibilidad trabajo', líms=(0, None), por='Territorio', regional=True)

    # conex.espec_inicial('Desnutrición inicial', var='Desnutrición crónica infantil')
    # conex.espec_inicial('Población inicial', var='Población')
    # conex.espec_inicial('Pobreza inicial', var='Pobreza')
    # #
    # # # act_calib(conex)
    # #
    # _ = conex.calib_var('Fertilidad', ec='1/(b*Educación formal+b2*Educación sexual+a)+c', paráms=['a', 'b', 'b2', 'c'],
    #                      líms_paráms=[(0, None), (0, 50), (0, 50), (0, None)], por='Territorio', aprioris=True)
    #
    # _ = conex.calib_var('Desnutrición crónica infantil',
    #                     ec='1/(exp(-a9*Seguridad alimentaria-a10*Enfermedades infantiles-b6)+ 1)', paráms=['a9', 'a10', 'b6'],
    #                     líms_paráms=[(-10, 10), (-10, 10), (-10, 10)],
    #                     por='Territorio', aprioris=True, regional=True)
    #
    # _ = conex.calib_var('Seguridad alimentaria', ec='1/(1 + b4*exp(-a2*Calidad de la dieta+a3*Cantidad de alimentos))',
    #                     paráms=['b4', 'a2', 'a3'],
    #                     líms_paráms=[(0, None), (0, None), (0, 10e-5)],
    #                     por='Territorio', aprioris=True, regional=False)
    # # '1/((a2*Calidad de la dieta+a3*Cantidad de alimentos)^a4*b4 + 1)'
    # act_calib(conex)
    #
    # _ = conex.calib_var('Enfermedades infantiles',
    #                     ec='1/(1 + exp(-a5*Tratamiento agua-a6*Acceso agua potable-a7*Seguridad alimentaria-a8*Higiene - b5))',
    #                     paráms=['a5', 'a6', 'a7', 'a8', 'b5'],
    #                     líms_paráms=[(-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10)], por='Territorio',
    #                     aprioris=True)
    #
    # _ = conex.calib_var('Pobreza', ec='a11/(Ingresos netos familiares)', paráms=['a11'],
    #                     líms_paráms=[(0, None)], por='Territorio', aprioris=True, regional=True)
    #
    # _ = conex.calib_var('Rendimiento milpa',
    #                     ec='c2/(1 + exp(-a16*Riego-a17*Uso insumos orgánicos-a18*Uso insumos químicos - b9))',
    #                     paráms=['a16', 'a17', 'a18', 'b9', 'c2'],
    #                     líms_paráms=[(-10, 50), (-10, 50), (-10, 50), (-10, 50), (0, 60000)], por='Territorio',
    #                     aprioris=True)  # MUY LENTO. ... bueno, no siempre.
    #
    # act_calib(conex)
    #
    # _ = conex.calib_var('Calidad de la dieta',
    #                     ec='1/(1 + exp(-a12*Pobreza - a13*Producción hortalizas consumida- a14*Educación formal-b7))',
    #                     paráms=['a12', 'a13', 'a14', 'b7'],
    #                     líms_paráms=[(-1e-2, 1e-2), (-1e-2, 1e-2), (-1, 1), (-10, 10)],
    #                     por='Territorio', aprioris=True)  # MUY LENTO... de verdad. Pero un poco más rápido para territorios.
    #
    # _ = conex.calib_var('Gastos en enfermedades', ec='a15*Enfermedades infantiles^b8', paráms=['a15', 'b8'],
    #                     líms_paráms=[(0, None), (0, 10)], por='Territorio', aprioris=True)
    #
    # _ = conex.calib_var('Comercialización',
    #                     ec='1/(1 + exp(-a19*Infraestructura vial -a20*Población/Superficie municipio-b10))',
    #                     paráms=['a19', 'a20', 'b10'],
    #                     líms_paráms=[(-10, 10)] * 3, por='Territorio',
    #                     aprioris=True, regional=True)  # Muy lento únicamente para terr. 1 (hacia rápido para Ixml)
    #
    # act_calib(conex)
    #
    # _ = conex.calib_var('Tecnificación agrícola',
    #                      ec='exp(a22*Acceso a crédito + a23*Pobreza + a24*Comercialización)',
    #                      paráms=['a22', 'a23', 'a24'],
    #                      líms_paráms=[(-9, 9), (-1e-2, 1e-2), (-9, 9)], por='Territorio', aprioris=True)
    # act_calib(conex)
    #
    # _ = conex.calib_var('Tecnificación agrícola',
    #                     # ec='exp(a*Pobreza + a2*Comercialización)+b',
    #                     ec='c4/(1 + exp(-a22*Pobreza -a23*Comercialización-a24*Acceso a crédito -b17))',
    #                     paráms=['a22', 'a23', 'a24', 'b17', 'c4'],
    #                     líms_paráms=[(-1e-2, 1e-2), (-20, 20), (-10, 10), (-10, 10), (0, 5e5)], por='Territorio',
    #                     aprioris=True)
    #
    # _ = conex.calib_var('Emigración permanente',
    #                     ec='1/(1 + exp(-a28*Desempleo-b14))',
    #                     paráms=['a28', 'b14'],
    #                     líms_paráms=[(-1e-1, 1e-1), (-10, 10)], por='Territorio', regional=True, aprioris=True)
    # act_calib(conex)
    #
    # _ = conex.calib_var('Comida comprada',
    #                     ec='c3/(1 + exp(-a25*Pobreza - a26*Producción milpa/Tamaño familia-b12))',
    #                     paráms=['a25', 'a26', 'b12', 'c3'],
    #                     líms_paráms=[(-1e-2, 1e-2), (-1e-2, 1e-2), (-10, 10), (0, 1000)], por='Territorio',
    #                     aprioris=True)
    #
    # act_calib(conex)
    #
    # _ = conex.calib_var('Acceso a crédito',
    #                     ec='1/(1 + exp(-a21*Tierra por familia-b11))',
    #                     paráms=['a21', 'b11'],
    #                     líms_paráms=[(-1e-1, 1e-1), (-10, 10)], por='Territorio', aprioris=True)
    #
    # _ = conex.calib_var('Riego',
    #                     ec='1/(1 + exp(a30*Tecnificación agrícola-b16))',
    #                     paráms=['a30', 'b16'],
    #                     líms_paráms=[(-1e-4, 1e-4), (-10, 10)], binario=False, por='Territorio', aprioris=True)
    #
    # act_calib(conex)
    #
    # _ = conex.calib_var('Uso insumos químicos',
    #                     ec='1/(1 + exp(-a27*Tecnificación agrícola-b13))',
    #                     paráms=['a27', 'b13'],
    #                     líms_paráms=[(-1e-2, 1e-2), (-10, 10)], por='Territorio', aprioris=True)
    #
    # _ = conex.calib_var('Costos insumos',
    #                     ec='a29*Uso insumos químicos+b15',
    #                     paráms=['a29', 'b15'],
    #                     líms_paráms=[(0, None)] * 2, por='Territorio', aprioris=True)
    #
    # act_calib(conex)

    # _ = conex.calib_var('Salario',
    #                     ec='c5/(1+exp(-a31*Educación formal -b18))',
    #                     paráms=['a31', 'b18', 'c5'],
    #                     líms_paráms=[(0, None), (0, None), (0, None)], por='Territorio', aprioris=True)
    # act_calib(conex)

    # _ = conex.calib_var('Trabajo infantil',
    #                     ec='c6/(1+exp(-a32*Pobreza -a33*Tamaño familia-b19))',
    #                     paráms=['a32', 'a33', 'b19', 'c6'],
    #                     líms_paráms=[(-1e-2, 1e-2), (0, None), (0, None), (0, None)], por='Territorio', aprioris=True)
    # act_calib(conex)

    # _ = conex.calib_var('Mortalidad infantil',
    #                     ec='a1*Seguridad alimentaria+b3',
    #                     paráms=['a1', 'b3'],
    #                     líms_paráms=[(0, None), (0, None)], por='Territorio', aprioris=True)
    # act_calib(conex)

    # _ = conex.calib_var('Atraso escolar',
    #                     ec='c7/(1+exp(-a34*Trabajo infantil -a35*Pobreza-a36*Enfermedades infantiles-a37*Seguridad alimentaria-b20))',
    #                     paráms=['a34', 'a35', 'a36', 'a37', 'b20', 'c7'],
    #                     líms_paráms=[(0, 10), (0, 1e-2), (0, 10), (-10, 0), (0, 10), (0, 20)], por='Territorio', aprioris=True)
    # act_calib(conex)

    # _ = conex.calib_var('Producción hortalizas consumida',
    #                     ec='c8/(1+exp(-a38*Producción hortalizas -a39*Costumbre de consumo-b21))',
    #                     paráms=['a38', 'a39', 'b21', 'c8'],
    #                     líms_paráms=[(-1e-5, 1e-5), (-10, 10), (0, 10), (0, None)], por='Territorio', aprioris=True)
    # act_calib(conex)

    # _ = conex.calib_var('Rendimiento hortalizas',
    #                     ec='c9/(1+exp(-a40*Riego -a41*Uso insumos químicos-b22))',
    #                     paráms=['a40', 'a41', 'b22', 'c9'],
    #                     líms_paráms=[ (-10, 10), (-10, 10),  (-10, 10), (0, None)], por='Territorio', aprioris=True)
    # act_calib(conex)
    # _ = conex.estim_constante(const='Educación inicial', líms=(0, 1), por='Territorio')
    # act_calib(conex)

    raise SystemExit(0)
    # Gráfico de "caja" con incertidumbre
    bd.graficar_hist(var='ISA', fechas=2011, cód_lugar='0708', bd_datos=None)
    bd.graficar_hist(var='ISA', fechas=2011, lugar=['Iximulew', "Tz'olöj Ya'", 'Concepción'])  # Da lo mismo al antecedente

    # Gráfico de línea con tiempo en el eje x e incertidumbre mostrada
    bd.graficar_hist(var='Población', años=(2000, None), cód_lugar='0112')

    # Varias "cajas" en el mismo gráfico (eje x = lugares)
    bd.graficar_hist(var='Población', fechas=2011, cód_lugar=['0112', 1204])

    # Varias líneas en el mismo gráfico (eje x = tiempo)
    bd.graficar_hist(var='Población', fechas=None, cód_lugar=['0112', 1204])

    # Gráfico de un variable contra el otro
    bd.graf_comparar(var_x='Sueldo', var_y='Educación', escala='individual', datos=None)
    # اعداد.comparar(var_x='Lluvia', var_y='Rendimiento', var_z='Suelo', escala='individual')

    bd.guardar(proyecto='')
    bd.cargar(fuente='')
    bd.cambiar_datos(nombre_datos, nueva_ubic)

    control = Control(bd=bd, modelo=modelo, fuente='')

    control.conectar_var_ind(datos=ENCOVI_hog_2011, var_bd='', var_modelo='', transformación='promedio')
    control.conectar_var_ind(datos=ENCOVI_hog_2011, var_bd='', var_modelo='', transformación='máximo')
    control.conectar_var_reg(datos=datos_desnutr, var_bd='Desnutr_crón_inft', var_modelo='', calc_error='porcentaje')

    control.comparar(var_mod_x='', var_mod_y='', escala='individual')  # llama BasedeDatos.comparar()
    control.estimar(constante='Desnutrición', escala='individual')  # Mal ejemplo
    control.estimar(constante='Rendimiento potencial', manera='inversa')  # Estima por aproximación
    control.estimados()

    control.calibrar_ec(var='Sueldo', relación='logística', cód_lugar='0112', años=None)
    control.calibrar_ec(var='Sueldo', cód_lugar='0113', años=None)  # Toma la relación existente
    control.calibrados()

    var = control.detalles_var(var='')  # Llama Modelo.var()
    modelo.parientes(var='')
    modelo.hijos(var='')
    eq_var = var.eq
    eq = control.eq(var='Sueldo')
    eq_var is eq
    eq.paráms()  # Dic de parám, distribución y valor
    control.calibrar_ec(var='', años=None, escala='Municipio', cód_lugar='0112')
    control.graficar_ec(var='', var_y=None, var_z=None, datos=None,
                        años=None)  # Grafica los datos (اعداد.relación) y la línea, con incertdumbre, de la ecuación calibrada

    control.guardar_incert_paráms(archivo='')  # Dic. de var, parám, y distribución
    control.cargar_incert_paráms(fuente='')
    control.gen_doc_incert(fuente='')  # Formato de especicificaciones de corridas de incertidumbre VENSIM/otro

    control.escribir_modelo(archivo='')
    control.correr(nombre_corrida='')
    control.analizar_incert(nombre_corrida='',
                            manera='natural')  # Utilizando la función de incertidumbre del programa de EnvolturasMDS
    control.visualizar_corrida(var='')

    control.validar_MDS(año_inic=None, cód_lugar=['0112'], n_reps=100)  # Genera los análises de Barlas, gráficos, etc.
    control.validar_conectado(conectado=ObjDeModeloConectado)

    control.guardar(proyecto='')
    control.cargar(fuente='')

    otro_modelo = mds(archivo_mds='')
    control.agregar_modelo(otro_modelo)
    control.recalibrar_ecs(cód_lugar='0113')  # Calibrar todas las equationes y constantes anteriormente calibradas

    control.guardar(proyecto='otro fuente')
