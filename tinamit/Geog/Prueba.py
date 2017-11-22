import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from numpy.random import randn
import matplotlib.colors as colors
from matplotlib.colorbar import ColorbarBase

# Make plot with vertical (default) colorbar
fig, ax = plt.subplots()

datos = np.random.random(200)*100
escala = [0, 25, 100]
unidades='dS/m'

clrs = ['#FF6666', '#FFCC66', '#00CC66']
n_colores = len(clrs)

def hex_a_rva(hex):
    return tuple(int(hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

clrs_rva = [hex_a_rva(x) for x in clrs]

dic_c = {'red': tuple((round(i/(n_colores-1), 2), clrs_rva[i][0]/255, clrs_rva[i][0]/255) for i in range(0, n_colores)),
         'green': tuple(
             (round(i / (n_colores-1), 2), clrs_rva[i][1] / 255, clrs_rva[i][1] / 255) for i in range(0, n_colores)),
         'blue': tuple(
             (round(i / (n_colores-1), 2), clrs_rva[i][2] / 255, clrs_rva[i][2] / 255) for i in range(0, n_colores))}

mapa_color = colors.LinearSegmentedColormap('mapa_color', dic_c)
norm = colors.Normalize(vmin=escala[0], vmax=escala[1])
cpick = cm.ScalarMappable(norm=norm,cmap=mapa_color)
cpick.set_array([])
plt.colorbar(cpick,label=unidades)
plt.show()
input()