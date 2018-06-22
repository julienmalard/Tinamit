parameters = [
    'Ptq - Aquifer total pore space',  # the most important for the water table depth (saturated zone)
    'Ptr - Root zone total pore space',  # unsaturated zone, important for the sanility
    # 'Ptx - Transition zone total pore space', #unsaturated zone
    'Kaq1 - Horizontal hydraulic conductivity 1',  # need to consider all four
    'Kaq2 - Horizontal hydraulic conductivity 2',
    'Kaq3 - Horizontal hydraulic conductivity 3',
    'Kaq4 - Horizontal hydraulic conductivity 4',
    # 'FsA - Water storage efficiency crop A', '#gaming variable''
    # 'FsB - Water storage efficiency crop B','#gaming variable''
    # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
    'Peq - Aquifer effective porosity',
    # # 'Per - Root zone effective porosity',
    'Pex - Transition zone effective porosity',
    # 'Gw - Groundwater extraction',
    # 'Lc - Canal percolation'
    'POH Kharif Tinamit',
    'POH rabi Tinamit',
    'Capacity per tubewell'
]

parametersNew = [
    'Ptq - Aquifer total pore space',  # the most important for the water table depth (saturated zone)
    'Ptr - Root zone total pore space',  # unsaturated zone, important for the sanility
    # 'Ptx - Transition zone total pore space', #unsaturated zone
    'Kaq - Horizontal hydraulic conductivity',
    # 'FsA - Water storage efficiency crop A', '#gaming variable''
    # 'FsB - Water storage efficiency crop B','#gaming variable''
    # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
    'Peq - Aquifer effective porosity',
    # # 'Per - Root zone effective porosity',
    'Pex - Transition zone effective porosity',
    # 'Gw - Groundwater extraction',
    # 'Lc - Canal percolation'
    'POH Kharif Tinamit',
    'POH rabi Tinamit',
    'Capacity per tubewell',
    # if don't need , please comment it
    'Dummy parameter'
]

parametersName4Plot = [
    'Ptq',  # the most important for the water table depth (saturated zone)
    'Ptr',  # unsaturated zone, important for the sanility
    # 'Ptx - Transition zone total pore space', #unsaturated zone
    'Kaq',
    # 'FsA - Water storage efficiency crop A', '#gaming variable''
    # 'FsB - Water storage efficiency crop B','#gaming variable''
    # 'FsU - Water storage efficiency non-irrigated', '#gaming variable''
    'Peq',
    # # 'Per - Root zone effective porosity',
    'Pex',
    # 'Gw - Groundwater extraction',
    # 'Lc - Canal percolation'
    'POH Kharif',
    'POH rabi',
    'Capacity per \ntubewell'
]

parameter_mapping = {'Ptq - s1':'Ptq',  # the most important for the water table depth (saturated zone)
                'Ptr - s1':'Ptr',  # unsaturated zone, important for the sanility
                'Kaq - s1':'Kaq',
                'Peq - s1':'Peq',
                'Pex - s1':'Pex',
                'Ptq - s2':'Ptq',  # the most important for the water table depth (saturated zone)
                'Ptr - s2':'Ptr',  # unsaturated zone, important for the sanility
                'Kaq - s2':'Kaq',
                'Peq - s2':'Peq',
                'Pex - s2':'Pex',
                'Ptq - s3':'Ptq',  # the most important for the water table depth (saturated zone)
                'Ptr - s3':'Ptr',  # unsaturated zone, important for the sanility
                'Kaq - s3':'Kaq',
                'Peq - s3':'Peq',
                'Pex - s3':'Pex',
                'Ptq - s4':'Ptq',  # the most important for the water table depth (saturated zone)
                'Ptr - s4':'Ptr',  # unsaturated zone, important for the sanility
                'Kaq - s4':'Kaq',
                'Peq - s4':'Peq',
                'Pex - s4':'Pex',
                'POH Kharif':'POH Kharif',
                'POH rabi':'POH rabi',
                'Capacity per tubewell':'Capacity per \ntubewell'}