from Incertidumbre.Modelo import mds
from Incertidumbre.Controles import Control
from Incertidumbre.Datos import DatosIndividuales, DatosRegión, Geografía, BaseDeDatos

modelo = mds(archivo_mds='')  # MDS es una función que genera una instancia de ModeloMDS, tal como VENSIM
print(modelo.vars)
print(modelo.internos)  # variables internos al MDS (p. ej., TIMESTEP y TIME en VENSIM)
print(modelo.auxiliares)
print(modelo.flujos)
print(modelo.niveles)
print(modelo.constantes)
modelo.vacíos()

datos_ind = DatosIndividuales(archivo_csv='', año=2011, col_cód_lugar='Código')

# datos_ind = DatosIndividuales(fuente='')
# datos_ind.estab_tiempo(col='año')

geog = Geografía(archivo='ubicación.csv',
                 orden=['Departamiento', 'Municipio'],
                 col_cód='Código')

datos_ind.datos_irreg(var='')
datos_ind.limpiar(var='', rango=(), tipo='valor')  # Hace cambios al csv
datos_ind.limpiar(var='', rango=(0, 0.90))

datos_ind.guardar_datos()  # Guarda el csv

datos_muni = DatosRegión(archivo_csv='')
datos_ind.estab_año(col='año')

bd = BaseDeDatos(datos=[datos_ind, datos_muni], geog=geog)

bd.renombrar_var(datos=datos_ind, var='P01221', nuevo_nombre='Insegurdad Alimentaria')  # puro ejemplo

# Gráfico de "caja" con incertidumbre
bd.graficar(var='Inseguridad Alimentaria', años=2011, cód_lugar='0112', datos=None)
bd.graficar(var='Inseguridad Alimentaria', años=2011, lugar=['Iximulew', "Tz'olöj Ya'", 'Concepción'])  # Da lo mismo al antecedente

# Gráfico de línea con tiempo en el eje x e incertidumbre mostrada
bd.graficar(var='Población', años=(2000, None), cód_lugar='0112')

# Varias "cajas" en el mismo gráfico (eje x = lugar)
bd.graficar(var='Población', años=2011, cód_lugar=['0112', 1204])

# Varias líneas en el mismo gráfico (eje x = tiempo)
bd.graficar(var='Población', años=None, cód_lugar=['0112', 1204])

# Gráfico de un variable contra el otro
bd.comparar(var_x='Sueldo', var_y='Educación', escala='individual', datos=None)
# bd.comparar(var_x='Lluvia', var_y='Rendimiento', var_z='Suelo', escala='individual')

bd.guardar(archivo='')
bd.cargar(fuente='')
bd.cambiar_datos(nombre_datos, nueva_ubic)

control = Control(bd=bd, modelo=modelo, fuente='')

control.conectar_vars(datos=datos_ind, var_bd='', var_modelo='', transformación='promedio')
control.conectar_vars(datos=datos_ind, var_bd='', var_modelo='', transformación='máximo')

control.comparar(var_mod_x='', var_mod_y='')  # llama BasedeDatos.comparar()
control.estimar(constante='Desnutrición')  # Mal ejemplo
control.estimar(constante='Rendimiento potencial', manera='inversa')  # Estima por aproximación
control.estimados()

control.calibrar_eq(var='Sueldo', relación='logística', cód_lugar=0112, años=None)
control.calibrar_eq(var='Sueldo', cod_lugar=0113, años=None)  # Toma la relación existente
control.calibrados()

var = control.detalles_var(var='')  # Llama Modelo.var()
var.parientes
var.hijos
eq_var = var.eq
eq = control.eq(var='Sueldo')
eq_var is eq
eq.paráms()  # Dic de parám, distribución y valor
control.calibrar_parám_eq(var='', paráms=[''], años=None, cód_lugar=0112)
control.graficar_eq(var='', var_y=None, var_z=None, datos=None, años=None)  # Grafica los datos (bd.relación) y la línea, con incertdumbre, de la ecuación calibrada


control.guardar_incert_paráms(archivo='')  # Dic. de var, parám, y distribución
control.cargar_incert_paráms(fuente='')
control.gen_doc_incert(fuente='')  # Formato de especicificaciones de corridas de incertidumbre VENSIM/otro

control.escribir_modelo(archivo='')
control.correr(nombre_corrida='')
control.analizar_incert(nombre='', manera='Natural')  # Utilizando la función de incertidumbre del programa de MDS
control.visualizar_corrida(var='')

control.validar_MDS(año_inic=None, cód_lugar=[0112], n_reps=100)  # Genera los análises de Barlas, gráficos, etc.
control.validar_conectado(conectado=ObjDeModeloConectado)

control.guardar(archivo='')
control.cargar(fuente='')


otro_modelo = mds(fuente='')
control.estab_modelo(otro_modelo)
control.calibrar_eqs(cód_lugar=0113)  # Calibrar todas las equationes y constantes anteriormente calibradas

control.guardar(archivo='otro archivo')