## obeserved data detection ##
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from tinamit.Análisis.Sens.behavior import superposition, find_best_behavior, predict


def read_obs_data(file_name, sheet_name=None):
    res = pd.read_excel(file_name, sheet_name=sheet_name)

    obs_data = {}
    for row in res.values:
        obs_data[row[1]] = row[2:]
    return res.columns[2:len(res.columns) - 1], obs_data

def split_obs_data(obs_data):
    split_data = {}
    for key, val in obs_data.items():
        split_data[key] = [(x, y) for x, y in enumerate(val) if y != "None" and not np.isnan(y)]
    return split_data


def interpolate_data(points, kind, length):
    x = [point[0] for point in points]
    y = [point[1] for point in points]
    f = interp1d(x, y, kind=kind)(range(length))
    interpolated_data = []
    for i in range(length):
        if i in x:
            interpolated_data.append((i, y[x.index(i)]))
        else:
            interpolated_data.append((i, f[i]))

    return interpolated_data

def interp_all_data(split_data, kind, length):
    int_all_data = {}
    for key, val in split_data.items():
        interpolated_data = interpolate_data(val, kind, length)
        int_all_data[key] = [point[1] for point in interpolated_data]

    return int_all_data

def write_excel(data, columns, file):
    with pd.ExcelWriter(file,
                        engine='xlsxwriter') as writer:
        for kind, val in data.items():
            df = pd.DataFrame(data=list(val.values()), columns=columns)
            df.to_excel(writer, kind)

def compute_superposition(interploated_data):
    best_behaviors = {}
    for poly, data in interploated_data.items():
        print(f"Polygon {poly} is under processing!")
        re = superposition(range(len(data)), data)
        best_behaviors[poly] = find_best_behavior(re[0])[0]
    return best_behaviors

def plot_pattern(interploated_data, path):
    fited_behaviors={poly: [] for poly in interploated_data}
    for poly, data in interploated_data.items():
        print(f"Polygon {poly} is under processing!")
        plt.plot(data)
        re = superposition(range(len(data)), data)
        gof_dict = find_best_behavior(re[0])[1]
        fited_behaviors[poly].append(gof_dict[0])
        m = 1
        while m < len(gof_dict):
            if gof_dict[m][1] - gof_dict[0][1] > 10:
                break
            else:
                fited_behaviors[poly].append(gof_dict[m])
            m += 1
        for tup_patt in fited_behaviors[poly]:
            plt.plot(predict(range(len(data)), re[0][tup_patt[0]]['bp_params'], tup_patt[0]))
        plt.savefig(path+f'{poly}-{fited_behaviors[poly][0][0]}')
        plt.close()

    return fited_behaviors