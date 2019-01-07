from tinamit.Calib.ej.obs_patrón import *

# file_name = "D:\Gaby\organized obs values.xlsx"
file_name = "D:\Thesis\data\\organized obs values.xlsx"
res = read_obs_data(file_name, "Final")
split_data = split_obs_data(res[1])
kinds = ["previous", "nearest", "next"]
kinds_in_d = {}
for kind in kinds:
    kinds_in_d[kind] = interp_all_data(split_data, kind, 61)
print(kinds_in_d['previous'])
# write_excel(kinds_in_d, list(res[0]), "D:\Gaby\interpolated.xlsx")
# write_excel(kinds_in_d, list(res[0]), "D:\Thesis\data\interpolated.xlsx")

compute_superposition(kinds_in_d['previous'])
fited_behaviors = plot_pattern(kinds_in_d['previous'],
             path="C:\\Users\gis_user\OneDrive - McGill University\Graduate study\Thesis\Project\paper draft 2\\data\\")

print(fited_behaviors)
