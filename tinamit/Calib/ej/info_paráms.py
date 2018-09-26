import numpy as np

from tinamit.Calib.ej.soil_class import p_soil_class, all_soil_class, p_neighbors


def gen_mapa_kaq(location, all_soil_class, neighbors):
    if location < 0 or location > 3:
        raise ValueError("Location out of scope")
    return [(all_soil_class[i], all_soil_class[neighbor[location] - 1]) for i, neighbor in enumerate(neighbors)]


mapa_paráms = {
    'Ptq - Aquifer total pore space': np.array(p_soil_class),
    'Ptr - Root zone total pore space': np.array(p_soil_class),
    'Kaq': {
        'transf': 'prom',
        'mapa': {
            'Kaq1 - Horizontal hydraulic conductivity 1': gen_mapa_kaq(0, all_soil_class, p_neighbors), #average(self, upper)
            'Kaq2 - Horizontal hydraulic conductivity 2': gen_mapa_kaq(1, all_soil_class, p_neighbors),
            'Kaq3 - Horizontal hydraulic conductivity 3': gen_mapa_kaq(2, all_soil_class, p_neighbors),
            'Kaq4 - Horizontal hydraulic conductivity 4': gen_mapa_kaq(3, all_soil_class, p_neighbors)
        }
    },
    'Peq - Aquifer effective porosity': np.array(p_soil_class),
    'Pex - Transition zone effective porosity': np.array(p_soil_class)
}


líms_paráms = {
    'Ptq - Aquifer total pore space': [(0.368, 0.506), (0.368, 0.551), (0.374, 0.500), (0.375, 0.551)],
    'Ptr - Root zone total pore space': [(0.375, 0.551), (0.350, 0.555), (0.351, 0.555), (0.332, 0.464)],
    'Kaq': [(26, 103), (26, 120), (26, 158), (26, 52)],
    'Peq - Aquifer effective porosity': [(0.1, 0.33)] * 4,
    'Pex - Transition zone effective porosity': [(0.01, 0.33)] * 4,
    'POH Kharif Tinamit': (355, 450),
    'POH rabi Tinamit': (235, 300),
    'Capacity per tubewell': (100.8, 201.6),
}

# 'Gw - Groundwater extraction': [(0.08, 0.35)]
#GW6, Per