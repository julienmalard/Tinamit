from tinamit.Calib.ej.obs_patrón import read_obs_csv, read_obs_data, plot_pattern

# file_name = "D:\Thesis\data\organized obs values.xlsx"
# calib_file_csv = "D:\Thesis\data\\calib_poly.csv"
# valid_file_csv = "D:\Thesis\data\\valid_poly.csv"

# calib = "D:\Thesis\data\\cluster_calib.csv"
# valid = "D:\Thesis\data\\cluster_valid.csv"

calib = "D:\Thesis\data\\old\\calib.csv"
valid = "D:\Thesis\data\\old\\valid.csv"

total = "D:\Thesis\data\\total_obs.csv"
# res = read_obs_data(file_name, sheet_name='Sheet4')

# res = read_obs_data(file_name, sheet_name='Sheet4')
cluster_calib = read_obs_csv(calib)
cluster_valid = read_obs_csv(valid)
# obs_90_all = read_obs_csv(total)

ori_calib = read_obs_csv(calib)
ori_valid = read_obs_csv(valid)

# calib_obs_80 = read_obs_csv(calib_file_csv)
# valid_obs_80 = read_obs_csv(valid_file_csv)

# calib_obs = read_obs_data(calib, sheet_name='Sheet1')
# valid_obs = read_obs_data(valid, sheet_name='Sheet1')

# plot_pattern(valid_obs[1],
#              path="C:\\Users\gis_user\OneDrive - McGill University\Graduate study\Thesis\Project\paper draft 2\\data\\1989_2009\\valid\\")
