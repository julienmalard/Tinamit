from tinamit.BF import EnvolturaBF


if __name__ == '__main__':
    from tinamit.Geog.Geog import Lugar
    mod = EnvolturaBF('DSSAT.py')
    mod.inic_vals({'Irrigación': 0.5, 'Orgánico': 0.1, 'Químico': 0.7})
    Tz_Ya = Lugar(lat=14.673, long=-91.145, elev=2050)
    mod.simular(tiempo_final=50, nombre_corrida='Prueba', fecha_inic=2000, lugar=Tz_Ya,
                tcr=8.5, clima=True, recalc=True)