## obeserved data detection ##
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

file_name = "D:\Gaby\organized obs values.xlsx"

def read_obs_data(file_name, sheet_name=None):
    res = pd.read_excel(file_name, sheet_name=sheet_name)

    obs_data = {}
    for row in res.values:
        obs_data[row[1]] = row[2:]
    return res.columns[3:], obs_data

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

res = read_obs_data(file_name, "Final")
split_data= split_obs_data(res[1])
kinds = ["previous", "nearest", "next"]
kinds_in_d = {}
for kind in kinds:
    kinds_in_d[kind] = interp_all_data(split_data, kind, 60)

write_excel(kinds_in_d, list(res[0]), "D:\Gaby\interpolated.xlsx")
print()