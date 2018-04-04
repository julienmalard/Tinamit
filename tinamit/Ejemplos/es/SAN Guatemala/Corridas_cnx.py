from tinamit.Geog.Geog import Lugar
from tinamit.Conectado import Conectado

mod = Conectado()
mod.estab_bf('C:\\Users\\jmalar1\\PycharmProjects\\Tinamit\\tinamit\\EnvolturaBF\\es\\DSSAT\\envoltDSSAT_senc.py')
mod.estab_mds('Para Tinamït.vpm')

mod.conectar(var_mds='Rendimiento milpa', var_bf='Rendimiento', mds_fuente=False, conv=1/12)
mod.conectar(var_mds='Uso insumos químicos', var_bf='Químico', mds_fuente=True)
mod.conectar(var_mds='Uso insumos orgánicos', var_bf='Químico', mds_fuente=True)
mod.conectar(var_mds='Riego', var_bf='Riego', mds_fuente=True)

Tz_Ya = Lugar(lat=14.673, long=-91.145, elev=2050)
res = mod.simular_paralelo(tiempo_final=100, nombre_corrida='Conec', fecha_inic=1990, tcr=[0, 2.6, 4.5, 6.0, 8.5],
                           devolver=['Seguridad alimentaria', 'Rendimiento milpa', 'Pobreza',
                                     'Tecnificación agrícola', 'Emigración permanente'])
print(res)