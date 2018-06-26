import os

# %% Buchiana 1
# %% Farida 2
# %% Jhang 3
# %% Chuharkana 4

soil_class = {

    # Buchiana
    '1': {
        'Ptq - Aquifer total pore space': [0.45, 0.55],  # the most important for the water table depth (saturated zone)
        'Ptr - Root zone total pore space': [0.45, 0.47],  # unsaturated zone, important for the sanility
        # 'Ptx - Transition zone total pore space':[0.43, 0.9], #unsaturated zone
        'Kaq': [26, 103],
        # 'FsA - Water storage efficiency crop A', '#gaming variable''
        # 'FsB - Water storage efficiency crop B','#gaming variable''
        # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
        'Peq - Aquifer effective porosity': [0.054, 0.302],
        # # 'Per - Root zone effective porosity':[0.31, 0.38],
        'Pex - Transition zone effective porosity': [0.065, 0.39],
        #'Gw - Groundwater extraction': [0.08, 0.35],
        # 'Lc - Canal percolation':
    },

    # Farida
     '2': {
        'Ptq - Aquifer total pore space': [0.44, 0.50],  # the most important for the water table depth (saturated zone)
        'Ptr - Root zone total pore space': [0.44, 0.46],  # unsaturated zone, important for the sanility
        # 'Ptx - Transition zone total pore space':[0.44, 0.9], #unsaturated zone
        'Kaq': [26, 120],
        # 'FsA - Water storage efficiency crop A', '#gaming variable''
        # 'FsB - Water storage efficiency crop B','#gaming variable''
        # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
        'Peq - Aquifer effective porosity': [0.054, 0.302],
        # # 'Per - Root zone effective porosity':[0.31, 0.38],
        'Pex - Transition zone effective porosity': [0.065, 0.39],
        #'Gw - Groundwater extraction': [0.08, 0.35],
        # 'Lc - Canal percolation':
    },

    # Jhang
    '3': {
        'Ptq - Aquifer total pore space': [0.45, 0.53],  # the most important for the water table depth (saturated zone)
        'Ptr - Root zone total pore space': [0.45, 0.53],  # unsaturated zone, important for the sanility
        # 'Ptx - Transition zone total pore space':[0.45, 0.9], #unsaturated zone
        'Kaq': [26, 158],
        # 'FsA - Water storage efficiency crop A', '#gaming variable''
        # 'FsB - Water storage efficiency crop B','#gaming variable''
        # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
        'Peq - Aquifer effective porosity': [0.054, 0.302],
        # # 'Per - Root zone effective porosity':[0.31, 0.38],
        'Pex - Transition zone effective porosity': [0.065, 0.39],
        #'Gw - Groundwater extraction': [0.08, 0.35],
        # 'Lc - Canal percolation':
    },

    # Chuharkana
    '4': {
        'Ptq - Aquifer total pore space': [0.43, 0.55],  # the most important for the water table depth (saturated zone)
        'Ptr - Root zone total pore space': [0.42, 0.52],  # unsaturated zone, important for the sanility
        # 'Ptx - Transition zone total pore space':[0.42, 0.9], #unsaturated zone
        'Kaq': [26, 52],
        # 'FsA - Water storage efficiency crop A', '#gaming variable''
        # 'FsB - Water storage efficiency crop B','#gaming variable''
        # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
        'Peq - Aquifer effective porosity': [0.054, 0.302],
        # # 'Per - Root zone effective porosity':[0.31, 0.38],
        'Pex - Transition zone effective porosity': [0.065, 0.39],
        #'Gw - Groundwater extraction': [0.08, 0.35],
        # 'Lc - Canal percolation':
    }
}

# print(soil_class[str(1)])

p_riv_class = ['head', 'head', 'head', 'head', 'head', 'head', 'head', 'head', 'head', 'head', 'head', 'head', 'head',
               'head', 'middle', 'middle', 'head', 'middle', 'Tail', 'middle', 'middle', 'middle', 'middle', 'middle',
               'middle', 'head', 'head', 'Tail', 'middle', 'middle', 'middle', 'middle', 'middle', 'Tail', 'Tail',
               'middle', 'Tail', 'Tail', 'Tail', 'Tail', 'head', 'Tail', 'Tail', 'head', 'Tail', 'head', 'middle',
               'Tail', 'middle', 'Tail', 'Tail', 'head', 'Tail', 'Tail', 'Tail', 'middle', 'head', 'head', 'head',
               'head', 'head', 'head', 'Tail', 'Tail', 'head', 'head', 'head', 'middle', 'middle', 'head', 'head',
               'middle', 'middle', 'Tail', 'head', 'head', 'middle', 'head', 'head', 'middle', 'middle', 'middle',
               'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle',
               'head', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle', 'middle',
               'middle', 'head', 'Tail', 'Tail', 'Tail', 'head', 'Tail', 'Tail', 'middle', 'middle', 'middle',
               'Tail', 'Tail', 'head', 'middle', 'middle', 'middle', 'Tail', 'Tail', 'middle', 'middle', 'Tail',
               'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'middle', 'middle', 'Tail', 'Tail', 'Tail', 'head',
               'head', 'middle', 'head', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail',
               'Tail', 'middle', 'middle', 'Tail', 'middle', 'head', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail',
               'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'middle', 'head', 'middle', 'middle', 'Tail', 'Tail',
               'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'head', 'Tail',
               'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'middle',
               'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'Tail', 'head', 'middle', 'Tail', 'Tail',
               'Tail', 'Tail', 'Tail']

p_soil_class = [1,
                1,
                2,
                2,
                3,
                2,
                2, #7
                2,
                3,
                2,
                3,
                3,
                2,
                2,
                3,
                3,#16
                1,
                2,
                3,
                2,
                2,
                3,#22
                1,
                1,
                2,
                2,
                1,
                3,
                1,
                2,
                2,
                3,
                3,
                3,
                3,
                1,
                1,
                2,
                2,
                3,
                3,
                2,
                2,
                1,
                2,
                3,
                3,
                1,
                2,
                3,
                2,
                1,
                2,
                2,
                3,
                3,
                2,
                2,
                3,
                3,
                2,
                2,
                2,
                2,
                2,
                1,
                2,
                3,
                2,
                3,
                3,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                3,
                3,
                3,
                3,
                2,
                1,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                3,
                1,
                3,
                3,
                3,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
                2,
                1,
                1,
                1,
                3,
                3,
                3,
                2,
                1,
                2,
                1,
                1,
                3,
                3,
                3,
                2,
                2,
                1,
                1,
                3,
                1,
                1,
                2,
                2,
                2,
                1,
                1,
                2,
                1,
                1,
                1,
                1,
                1,
                3,
                3,
                4,
                4,#143
                4,
                2,
                2,
                2,
                4,
                2,
                2,
                1,
                2,
                2,
                2,
                2,
                3,
                4,
                4,
                4,
                4,
                4,
                4,
                4,
                4,
                4,
                2,
                2,
                2,
                1,
                2,
                2,
                2,
                2,
                2,
                4,
                4,
                2,
                2,
                4,
                4,
                4,
                4,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                4,
                2,
                2,
                2,
                1,
                1,
                1,
                1,
                2,
                4,
                4,
                2,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
                1,
                1,
                1]
#print(p_soil_class[0], p_soil_class[10], p_soil_class[5])

p_neighbors = [
    # up, right, down, left
    [216, 279, 2, 217],
    [1, 278, 4, 218],
    [218, 4, 6, 219],
    [2, 277, 7, 3],
    [219, 6, 8, 220],
    [3, 7, 9, 5],
    [4, 276, 10, 6],
    [5, 9, 11, 221],
    [6, 10, 12, 8],
    [7, 275, 13, 9],
    [8, 12, 15, 222],
    [9, 13, 16, 11],
    [10, 274, 17, 12],
    [222, 15, 18, 223],
    [11, 16, 19, 14],
    [12, 17, 20, 15],
    [13, 273, 21, 16],
    [14, 19, 23, 224],
    [15, 20, 24, 18],
    [16, 21, 25, 19],
    [17, 272, 26, 20],
    [224, 23, 28, 225],
    [18, 24, 29, 22],
    [19, 25, 30, 23],
    [20, 26, 31, 24],
    [21, 27, 32, 25],
    [272, 271, 33, 26],
    [22, 29, 35, 226],
    [23, 30, 36, 28],
    [24, 31, 37, 29],
    [25, 32, 38, 30],
    [26, 33, 39, 31],
    [27, 270, 40, 32],
    [226, 35, 41, 227],
    [28, 36, 42, 34],
    [29, 37, 43, 35],
    [30, 38, 44, 36],
    [31, 39, 45, 37],
    [32, 40, 46, 38],
    [33, 269, 47, 39],
    [34, 42, 50, 228],
    [35, 43, 51, 41],
    [36, 44, 52, 42],
    [37, 45, 53, 43],
    [38, 46, 54, 44],
    [39, 47, 55, 45],
    [40, 48, 56, 46],
    [269, 268, 57, 47],
    [228, 50, 59, 229],
    [41, 51, 60, 49],
    [42, 52, 61, 50],
    [43, 53, 62, 51],
    [44, 54, 63, 52],
    [45, 55, 64, 53],
    [46, 56, 65, 54],
    [47, 57, 66, 55],
    [48, 267, 67, 56],
    [229, 59, 69, 230],
    [49, 60, 70, 58],
    [50, 61, 71, 59],
    [51, 62, 72, 60],
    [52, 63, 73, 61],
    [53, 64, 74, 62],
    [54, 65, 75, 63],
    [55, 66, 76, 64],
    [56, 67, 77, 65],
    [57, 266, 78, 66],
    [230, 69, 81, 231],
    [58, 70, 82, 68],
    [59, 71, 83, 69],
    [60, 72, 84, 70],
    [61, 73, 85, 71],
    [62, 74, 86, 72],
    [63, 75, 87, 73],
    [64, 76, 88, 74],
    [65, 77, 89, 75],
    [66, 78, 90, 76],
    [67, 79, 91, 77],
    [266, 265, 92, 78],
    [231, 81, 95, 232],
    [68, 82, 96, 80],
    [69, 83, 97, 81],
    [70, 84, 98, 82],
    [71, 85, 99, 83],
    [72, 86, 100, 84],
    [73, 87, 101, 85],
    [74, 88, 102, 86],
    [75, 89, 103, 87],
    [76, 90, 104, 88],
    [77, 91, 105, 89],
    [78, 92, 106, 90],
    [79, 93, 107, 91],
    [265, 264, 108, 92],
    [232, 95, 109, 233],
    [80, 96, 110, 94],
    [81, 97, 111, 95],
    [82, 98, 112, 96],
    [83, 99, 113, 97],
    [84, 100, 114, 98],
    [85, 101, 115, 99],
    [86, 102, 116, 100],
    [87, 103, 117, 101],
    [88, 104, 118, 102],
    [89, 105, 119, 103],
    [90, 106, 120, 104],
    [91, 107, 121, 105],
    [92, 108, 122, 106],
    [93, 263, 123, 107],
    [94, 110, 125, 234],
    [95, 111, 126, 109],
    [96, 112, 127, 110],
    [97, 113, 128, 111],
    [98, 114, 129, 112],
    [99, 115, 130, 113],
    [100, 116, 131, 114],
    [101, 117, 132, 115],
    [102, 118, 133, 116],
    [103, 119, 134, 117],
    [104, 120, 135, 118],
    [105, 121, 136, 119],
    [106, 122, 137, 120],
    [107, 123, 138, 121],
    [108, 262, 139, 122],
    [234, 125, 140, 235],
    [109, 126, 141, 124],
    [110, 127, 142, 125],
    [111, 128, 143, 126],
    [112, 129, 144, 127],
    [113, 130, 145, 128],
    [114, 131, 146, 129],
    [115, 132, 147, 130],
    [116, 133, 148, 131],
    [117, 134, 149, 132],
    [118, 135, 150, 133],
    [119, 136, 151, 134],
    [120, 137, 152, 135],
    [121, 138, 153, 136],
    [122, 139, 154, 137],
    [123, 261, 155, 138],
    [124, 141, 156, 236],
    [125, 142, 157, 140],
    [126, 143, 158, 141],
    [127, 144, 159, 142],
    [128, 145, 160, 143],
    [129, 146, 161, 144],
    [130, 147, 162, 145],
    [131, 148, 163, 146],
    [132, 149, 164, 147],
    [133, 150, 165, 148],
    [134, 151, 166, 149],
    [135, 152, 167, 150],
    [136, 153, 168, 151],
    [137, 154, 169, 152],
    [138, 155, 170, 153],
    [139, 260, 171, 154],
    [140, 157, 172, 237],
    [141, 158, 173, 156],
    [142, 159, 174, 157],
    [143, 160, 175, 158],
    [144, 161, 176, 159],
    [145, 162, 177, 160],
    [146, 163, 178, 161],
    [147, 164, 179, 162],
    [148, 165, 180, 163],
    [149, 166, 181, 164],
    [150, 167, 182, 165],
    [151, 168, 183, 166],
    [152, 169, 184, 167],
    [153, 170, 185, 168],
    [154, 171, 186, 169],
    [155, 259, 258, 170],
    [156, 173, 187, 238],
    [157, 174, 188, 172],
    [158, 175, 189, 173],
    [159, 176, 190, 174],
    [160, 177, 191, 175],
    [161, 178, 192, 176],
    [162, 179, 193, 177],
    [163, 180, 194, 178],
    [164, 181, 195, 179],
    [165, 182, 196, 180],
    [166, 183, 197, 181],
    [167, 184, 198, 182],
    [168, 185, 199, 183],
    [169, 186, 200, 184],
    [170, 258, 201, 185],
    [172, 188, 240, 239],
    [173, 189, 241, 187],
    [174, 190, 242, 188],
    [175, 191, 243, 189],
    [176, 192, 244, 190],
    [177, 193, 245, 191],
    [178, 194, 202, 192],
    [179, 195, 203, 193],
    [180, 196, 204, 194],
    [181, 197, 205, 195],
    [182, 198, 206, 196],
    [183, 199, 207, 197],
    [184, 200, 208, 198],
    [185, 201, 209, 199],
    [186, 257, 210, 200],
    [193, 203, 246, 245],
    [194, 204, 247, 202],
    [195, 205, 248, 203],
    [196, 206, 249, 204],
    [197, 207, 211, 205],
    [198, 208, 212, 206],
    [199, 209, 213, 207],
    [200, 210, 214, 208],
    [201, 256, 215, 209],
    [206, 212, 250, 249],
    [207, 213, 251, 211],
    [208, 214, 252, 212],
    [209, 215, 253, 213],
    [210, 255, 254, 214],
]

All_Classes = ['H1', 'H2', 'H3', 'M1', 'M2', 'M3', 'M4', 'T1', 'T2', 'T3', 'T4']

H1 = [0, 1, 16, 26, 43, 51, 65, 107, 135, 136, 138, 168, 184, 208]
H2 = [2, 3, 5, 6, 7, 9, 12, 13, 25, 56, 57, 60, 61, 64, 66, 74, 75, 77, 78, 92, 103, 115, 154]
H3 = [4, 8, 10, 11, 40, 45, 58, 59, 69, 70]
H4 = []
M1 = [22, 23, 28, 35, 84, 94, 98, 99, 100, 116, 117, 131, 137, 150, 198, 209]
M2 = [17, 19, 20, 24, 29, 30, 48, 68, 71, 72, 76, 83, 85, 86, 88, 89, 90, 91, 101, 102, 121, 122, 130, 151, 153, 167, 169, 170] #deleted poly_87
M3 = [14, 15, 21, 31, 32, 46, 55, 67, 79, 80, 81, 82, 93, 95, 96, 97, 110, 111, 112, 118]
M4 = [87] #87
T1 = [36, 47, 108, 109, 114, 123, 124, 126, 127, 132, 134, 182, 183, 185, 197, 199, 200, 205, 206, 207, 212, 213, 214]
T2 = [37, 38, 41, 42, 44, 50, 52, 53, 62, 63, 73, 104, 105, 106, 113, 128, 129, 133, 144, 145, 146, 148, 149, 152, 165, 166, 171, 172, 173, 176, 177, 186, 187, 188, 189, 190, 191, 192, 194, 195, 196, 201, 204, 210, 211]
T3 = [18, 27, 33, 34, 39, 49, 54, 119, 120, 125, 139, 140, 155]
T4 = [141, 142, 143, 147, 156, 157, 158, 159, 160, 161, 162, 163, 164, 174, 175, 178, 179, 180, 181, 193, 202, 203]


def get_p_soil_class(poly_id, location = -1):
    if poly_id == None or poly_id > 215 or poly_id < 0:
        print('Error: poly_id is not valid!')
        return None
    if location == -1:
        return soil_class[str(p_soil_class[poly_id])]
    else:
        # the real polygon start with 1, so there needs minus 1
        neighbor = p_neighbors[poly_id][location] - 1
        if neighbor > 214:
            neighbor = poly_id

        #print(poly_id, neighbor, location)
        return soil_class[str(p_soil_class[neighbor])]

def get_soil_type(poly_id, location = -1):
    if poly_id == None or poly_id > 215 or poly_id < 0:
        print('Error: poly_id is not valid!')
        return None
    if location == -1:
        return p_soil_class[poly_id]
    else:
        # the real polygon start with 1, so there needs -1
        neighbor = p_neighbors[poly_id][location] - 1
        if neighbor > 214:
            neighbor = poly_id
        #print(poly_id, neighbor, location)
        return p_soil_class[neighbor]

def local_data_prepare(mstr_paráms, is_dummy=False, n_poly=215):
    """
    transform sampled data into Tinamit matrix
    :param mstr_paráms: {Ns * 23}
    :param is_dummy: if is_dummy add dummy variable
    :param n_poly: num of the polygons in the study area
    :return: list_dic_set [8*215 + 3*215]
    """

    def data_transform(sample):
        sampling = {}  # from 23*215 to 11*215
        for i, name in enumerate(P.parameters):  # give index to 11 param names
            if name.startswith('Kaq'):
                if name.endswith('1'):
                    sampling[name] = [(sample[(SC.get_soil_type(j, 0) - 1) * 5 + parameters.index(
                        'Kaq - Horizontal hydraulic conductivity')] +
                                       sample[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                                           'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                                      range(n_poly)]
                if name.endswith('2'):
                    sampling[name] = [
                        (sample[(SC.get_soil_type(j, 1) - 1) * 5 + parameters.index(
                            'Kaq - Horizontal hydraulic conductivity')] +
                         sample[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                             'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                        range(n_poly)]

                if name.endswith('3'):
                    sampling[name] = [
                        (sample[(SC.get_soil_type(j, 2) - 1) * 5 + parameters.index(
                            'Kaq - Horizontal hydraulic conductivity')] +
                         sample[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                             'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                        range(n_poly)]

                if name.endswith('4'):
                    sampling[name] = [
                        (sample[(SC.get_soil_type(j, 3) - 1) * 5 + parameters.index(
                            'Kaq - Horizontal hydraulic conductivity')] +
                         sample[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                             'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                        range(n_poly)]
            else:
                if parameters.index(name) <= 4:  # 4 means the first 5 BF params
                    sampling[name] = [
                        sample[(SC.get_soil_type(j) - 1) * 5 + parameters.index(name)] for j in
                        range(n_poly)]
                elif parameters.index(name) <= 7 and parameters.index(name) > 4:
                    sampling[name] = [
                        sample[15 + parameters.index(name)] for j in
                        range(n_poly)]
                else:
                    pass
        return sampling  # {11 * 215}

    sampling_parameters_set = []  # Ns*11*215 Tinamit format as Tinamit only consider Kaq1234
    if is_dummy:
        parameters = P.parametersNew_dummy
    else:
        parameters = P.parametersNew
    # for each sample from Ns,
    for k, v in mstr_paráms.items():
        for sam in v:  # sam: each 23 of the Ns
            sampling_parameters_set.append(data_transform(sam))

    lista_mds = ['POH Kharif Tinamit', 'POH rabi Tinamit', 'Capacity per tubewell']
    list_dic_set = [{'bf': {ll: v for ll, v in s.items() if ll not in lista_mds},
                     'mds': {ll: v for ll, v in s.items() if ll in lista_mds}} for s in sampling_parameters_set]
    return list_dic_set
    # list_dic_set [8*215 + 3*215]