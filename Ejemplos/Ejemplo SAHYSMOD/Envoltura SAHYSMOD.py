import os
import re
from subprocess import run

from Biofísico import ClaseModeloBF

# Path to SAHYSMOD executable. Change as needed on your computer.
SAHYSMOD = ''

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
initial_data = ''


class Modelo(ClaseModeloBF):
    def __init__(símismo):
        super().__init__()

        # These attributes are needed for all ClaseModeloBF subclass implementations
        input_vals = símismo.gen_input_vals()  # Read input values from .inp file
        símismo.variables = dict([(nombre, {'var': input_vals[nombre][0],
                                            'unidades': dic['unidades']
                                            }
                                   )
                                  for (nombre, dic) in vars_SAHYSMOD.items()])

        símismo.unidades_tiempo = 'Season'

        # These attributes are specific to the SAHYSMOD wrapper
        current_dir = os.path.dirname(os.path.realpath(__file__))
        símismo.output = os.path.join(current_dir, 'SAHYSMOD.out')
        símismo.input = os.path.join(current_dir, 'TEMPLATE.inp')

        # This class will simulate on a seasonal time basis, but the SAHYSMOD executable must run for two half-years
        # at the same time. Therefore, we create an internal dictionary to store variable data for both half-years.
        # {'var 1': [season1value, season2value],
        #  'var 2': [season1value, season2value],
        #  ...
        #  }

        símismo.interal_data = dict([(var, [input_vals[var][0], input_vals[var][1]]) for var in símismo.variables])

        símismo.season = 0

    def ejec(símismo):
        pass  # No prior setup necessary

    def incr(símismo, paso):

        # Note: this subclass can only be used with a coupling time step of multiples of 1 year (two seasons).
        if not (int(paso/2) == paso/2):
            raise ValueError('Time step ("paso") must be multiples of one year (two seasons) for the SAHYSMOD model.')

        s = símismo.season

        # Save incoming coupled variables to the internal data
        for var in símismo.variables:
            if var in símismo.vars_ingr:
                símismo.interal_data[var][s] = símismo.variables[var]

        # Prepare the command
        args = dict(SAHYSMOD=SAHYSMOD, input=símismo.input, output=símismo.output)
        command = '{SAHYSMOD} {input} {output}'.format(**args)

        for _ in paso:

            # If we are in the first season of a year...
            if s == 0:

                # Create the data structure for the last two seasons.
                dic_data = dict([('%s_1' % x[i + 1]['code'], símismo.interal_data[x[0]][i])
                                 for x in vars_SAHYSMOD.items()
                                 for i in (0, 1)])

                # Create the appropriate input file:
                símismo.write_inp(file_path=símismo.input, output_file=símismo.output, dic_data=dic_data)

                # Run the command prompt command
                run(command)

                # Read the output
                símismo.read_out(file_path=símismo.output, dic_data=dict_read_out)

                for var in vars_SAHYSMOD:
                    símismo.interal_data[var] = dict_read_out[vars_SAHYSMOD[var]['code']]

            # Set the variables dictionary to the appropriate season data
            for var, dict_var in símismo.variables.items():
                if var in símismo.vars_egr:
                    símismo.variables[var]['var'] = símismo.interal_data[var][s]

            # Increment/reset the season
            s += 1
            s %= 2  # 2 seasons equals season 0 of the next year

        # Save the season for the next time.
        símismo.season = s

    # Some functions specific to the SAHYSMOD-specific wrapper
    @staticmethod
    def write_inp(file_path, output_file, dic_data):

        # Read the template CLI file
        with open(file_path) as d:
            template = d.readlines()

        # Fill in our data
        for n, line in enumerate(template):
            template[n] = line.format(**dic_data)

        # And save the input file
        with open(output_file, 'w') as d:
            d.write(''.join(template))

    @staticmethod
    def read_out(file_path, dic_data):
        """
        This function reads the last two seasons of a SAHYSMOD output file into a given diccionary.

        :param file_path: The file path at which the SAHYSMOD output file can be found
        :type file_path: str

        :param dic_data: A dictionary with the variables of interest as keys. Example:
          {'Dw': [None, None], 'Cqf': [None, None]}
          would read the variables Dw and Cqf from the last two seasons of the SAHYSMOD output
        :type dic_data: dict

        """

        with open(file_path, 'r') as d:

            # Skip unecessary lines before the year of interest
            l = ''
            while 'YEAR:      1' not in l:
                l = d.readline()

            for season in [0, 1]:  # Read output for the last two seasons of the output file

                season_output = []  # To hold the output file lines with the desired season

                # Keep on searching until we find the season we're looking for
                while 'Season:    %i' % (season + 1) not in l:
                    l = d.readline()

                # Copy all of the lines until we get to the end of the season
                l = d.readline()
                while '#' not in l:
                    season_output.append(l)
                    l = d.readline()

                # Search for the wariables we want:
                for var in dic_data:

                    for line in season_output:
                        print(1, var, line)
                        line += ' '
                        m = re.search('%s += +([^ ]*)' % var, line)
                        if m is not None:
                            if m == '-':
                                val = None
                            else:
                                try:
                                    val = float(m.group(1))
                                except ValueError:
                                    print(m.group(0))
                                    print(m.group(1))
                                    raise ValueError('The variable "%s" was not read from the SAHYSMOD output.' % var)

                            dic_data[var][season] = val

                            # If we've found the variable, stop looking for it.
                            break

    def gen_input_vals(símismo):
        dic_input_vals = {}

        with open(initial_data, 'r') as d:
            inp = d.readlines()

        with open(símismo.input) as d:
            template = d.readlines()

        for var, dic_var in vars_SAHYSMOD.items():
            n_line_1 = template.index('%s_1' % dic_var['code'])
            n_line_2 = template.index('%s_2' % dic_var['code'])
            val_season_1 = inp[n_line_1]
            val_season_2 = inp[n_line_2]
            dic_input_vals[var] = (val_season_1, val_season_2)

        return dic_input_vals

vars_SAHYSMOD = {'Total irrigation': {'code': 'It', 'unidades': 'm3/season/m2'},
                 'Canal irrigation': {'code': 'Is', 'unidades': 'm3/season/m2'},
                 'Crop A field irrigation': {'code': 'IaA', 'unidades': 'm3/season/m2'},
                 'Crop B field irrigation': {'code': 'IaB', 'unidades': 'm3/season/m2'},
                 'Irrigation efficiency crop A': {'code': 'FfA', 'unidades': 'Dmnl'},
                 'Irrigation efficiency crop B': {'code': 'FfB', 'unidades': 'Dmnl'},
                 'Total irrigation efficiency': {'code': 'FfT', 'unidades': 'Dmnl'},
                 'Water leaving by canal': {'code': 'Io', 'unidades': 'm3/season/m2'},
                 'Irrigation sufficiency crop A': {'code': 'JsA', 'unidades': 'Dmnl'},
                 'Irrigation sufficiency crop B': {'code': 'JsB', 'unidades': 'Dmnl'},
                 'Actual evapotranspiration nonirrigated': {'code': 'EaU', 'unidades': 'm3/season/m2'},
                 'Root zone percolation crop A': {'code': 'LrA', 'unidades': 'm3/season/m2'},
                 'Root zone percolation crop B': {'code': 'LrB', 'unidades': 'm3/season/m2'},
                 'Root zone percolation nonirrigated': {'code': 'LrU', 'unidades': 'm3/season/m2'},
                 'Total root zone percolation': {'code': 'LrT', 'unidades': 'm3/season/m2'},
                 'Capillary rise crop A': {'code': 'RrA', 'unidades': 'm3/season/m2'},
                 'Capillary rise crop B': {'code': 'RrB', 'unidades': 'm3/season/m2'},
                 'Capillary rise unirrigated': {'code': 'RrU', 'unidades': 'm3/season/m2'},
                 'Total capillary rise': {'code': 'RrT', 'unidades': 'm3/season/m2'},
                 'Trans zone horizontal incoming groundwater': {'code': 'Gti', 'unidades': 'm3/season/m2'},
                 'Trans zone horizontal outgoing groundwater': {'code': 'Gto', 'unidades': 'm3/season/m2'},
                 'Net vertical water table recharge': {'code': 'Qv', 'unidades': 'm'},
                 'Aquifer horizontal incoming groundwater': {'code': 'Gqi', 'unidades': '(m3/season/m2'},
                 'Aquifer horizontal outgoing groundwater': {'code': 'Gqo', 'unidades': '(m3/season/m2'},
                 'Net aquifer horizontal flow': {'code': 'Gaq', 'unidades': 'm3/season/m2'},
                 'Net horizontal groundwater flow': {'code': 'Gnt', 'unidades': 'm3/season/m2'},
                 'Total subsurface drainage': {'code': 'Gd', 'unidades': 'm3/season/m2'},
                 'Subsurface drainage above drains': {'code': 'Ga', 'unidades': 'm3/season/m2'},
                 'Subsurface drainage below drains': {'code': 'Gb', 'unidades': 'm3/season/m2'},
                 'Groundwater extraction': {'code': 'Gw', 'unidades': 'm3/season/m2'},
                 'Groundwater depth': {'code': 'Dw', 'unidades': 'm'},
                 'Water table elevation': {'code': 'Hw', 'unidades': 'm'},
                 'Subsoil hydraulic head': {'code': 'Hq', 'unidades': 'm'},
                 'Water table storage': {'code': 'Sto', 'unidades': 'm'},
                 'Surface water salt': {'code': 'Zs', 'unidades': 'm*dS/m'},
                 'Seasonal fraction area crop A': {'code': 'A', 'unidades': 'Dmnl'},
                 'Seasonal fraction area crop B': {'code': 'B', 'unidades': 'Dmnl'},
                 'Seasonal fraction area nonirrigated': {'code': 'U', 'unidades': 'Dmnl'},
                 'Fraction permanently unirrigated': {'code': 'Uc', 'unidades': 'Dmnl'},
                 'Land use key': {'code': 'Kr', 'unidades': 'Dmnl'},
                 'Root zone salinity crop A': {'code': 'CrA', 'unidades': 'dS / m'},
                 'Root zone salinity crop B': {'code': 'CrB', 'unidades': 'dS / m'},
                 'Root zone salinity unirrigated': {'code': 'CrU', 'unidades': 'dS / m'},
                 'Fully rotated land irrigated root zone salinity': {'code': 'Cr4', 'unidades': 'dS / m'},
                 'Key 1 non-permanently irrigated root zone salinity': {'code': 'C1*', 'unidades': 'dS / m'},
                 'Key 2 non-permanently irrigated root zone salinity': {'code': 'C2*', 'unidades': 'dS / m'},
                 'Key 3 non-permanently irrigated root zone salinity': {'code': 'C3*', 'unidades': 'dS / m'},
                 'Transition zone salinity': {'code': 'Cxf', 'unidades': 'dS / m'},
                 'Transition zone above-drain salinity': {'code': 'Cxa', 'unidades': 'dS / m'},
                 'Transition zone below-drain salinity': {'code': 'Cxb', 'unidades': 'dS / m'},
                 'Soil salinity': {'code': 'Cqf', 'unidades': 'dS / m'},
                 'Transition zone incoming salinity': {'code': 'Cti', 'unidades': 'dS / m'},
                 'Aquifer salinity': {'code': 'Cqi', 'unidades': 'dS / m'},
                 'Irrigation water salinity': {'code': 'Ci', 'unidades': 'dS / m'},
                 'Drainage salinity': {'code': 'Cd', 'unidades': 'ds / m'},
                 'Well water salinity': {'code': 'Cw', 'unidades': 'dS / m'}
                 }

dict_read_out = dict([(x['code'], [None, None]) for x in vars_SAHYSMOD.values()])
