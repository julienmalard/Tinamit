from tinamit.Calib.ej.obs_patrón import read_obs_csv, read_obs_data

# file_name = "D:\Thesis\data\organized obs values.xlsx"
file_name_csv = "D:\Thesis\data\\obs.csv"

# res = read_obs_data(file_name, sheet_name='Sheet4')

# res = read_obs_data(file_name, sheet_name='Sheet4')

res = read_obs_csv(file_name_csv)
# for obs_p, ts in res[1].items():
#     ts[np.where(ts == 'None')] = np.nan

# split_data = split_obs_data(res[1])
# kinds = ["previous", "nearest", "next"]
# kinds_in_d = {}
# for kind in kinds:
#     kinds_in_d[kind] = interp_all_data(split_data, kind, 61)
# print(kinds_in_d['previous'])
# write_excel(kinds_in_d, list(res[0]), "D:\Gaby\interpolated.xlsx")
# write_excel(kinds_in_d, list(res[0]), "D:\Thesis\data\interpolated.xlsx")
# bd = kinds_in_d['previous']

# best_behaviors, d_calib, d_numero= compute_superposition(kinds_in_d['previous'])

# np.save("D:\Thesis\pythonProject\localuse\Dt\Calib\\", best_behaviors)
# np.save("D:\Thesis\pythonProject\localuse\Dt\Calib\\", d_calib)
# fited_behaviors = plot_pattern(kinds_in_d['previous'],
#              path="C:\\Users\gis_user\OneDrive - McGill University\Graduate study\Thesis\Project\paper draft 2\\data\\")

# print(fited_behaviors)
