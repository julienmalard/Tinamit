from tinamit.BF import EnvolturaBF

if __name__ == '__main__':
    from tinamit.Geog.Geog import Lugar

    mod = EnvolturaBF('DSSAT.py')
    mod.inic_vals_vars({'Irrigación': 0.5, 'Orgánico': 0.1, 'Químico': 0.7})
    Tz_Ya = Lugar(lat=14.673, long=-91.145, elev=2050)
    mod.simular(tiempo_final=48, nombre_corrida='Prueba', fecha_inic=2050, lugar=Tz_Ya,
                tcr=8.5, clima=True, recalc_clima=True)
