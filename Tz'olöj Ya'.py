from Central import conectar_modelos

modelo = conectar_modelos(ubicación_mds="F:\\Julien\\PhD\\Iximulew\\MDS 2015\\Tz'olöj Ya'\\Taller 12\\Prueba dll.vmf",
                          ubicación_biofísico=None)
# "F:\\Julien\\PhD\\Iximulew\\MDS 2015\\Tz'olöj Ya'\\Taller 12\\Prueba dll.vfm"

modelo.simular()