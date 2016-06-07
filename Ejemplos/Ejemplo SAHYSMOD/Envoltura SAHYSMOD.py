import os
import re
from subprocess import run

from Biofísico import ClaseModeloBF

# Path to SAHYSMOD executable. Change as needed on your computer.
SAHYSMOD = ''

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
inicial_data = ''


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

                # Increment the season
                s = 1

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

        with open(inicial_data, 'r') as d:
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

vars_SAHYSMOD = {'var1': {'code': 'It', 'unidades': ''},
                 'var1': {'code': 'Is', 'unidades': ''},
                 'var1': {'code': 'IaA', 'unidades': ''},
                 'var1': {'code': 'IaB', 'unidades': ''},
                 'var1': {'code': 'FfA', 'unidades': ''},
                 'var1': {'code': 'FfB', 'unidades': ''},
                 'var1': {'code': 'FfT', 'unidades': ''},
                 'var1': {'code': 'Io', 'unidades': ''},
                 'var1': {'code': 'JsA', 'unidades': ''},
                 'var1': {'code': 'JsB', 'unidades': ''},
                 'var1': {'code': 'EaU', 'unidades': ''},
                 'var1': {'code': 'LrA', 'unidades': ''},
                 'var1': {'code': 'LrB', 'unidades': ''},
                 'var1': {'code': 'LrU', 'unidades': ''},
                 'var1': {'code': 'LrT', 'unidades': ''},
                 'var1': {'code': 'RrA', 'unidades': ''},
                 'var1': {'code': 'RrB', 'unidades': ''},
                 'var1': {'code': 'RrU', 'unidades': ''},
                 'var1': {'code': 'RrT', 'unidades': ''},
                 'var1': {'code': 'Gti', 'unidades': ''},
                 'var1': {'code': 'Gto', 'unidades': ''},
                 'var1': {'code': 'Qv', 'unidades': ''},
                 'var1': {'code': 'Gqi', 'unidades': ''},
                 'var1': {'code': 'Gqo', 'unidades': ''},
                 'var1': {'code': 'Gaq', 'unidades': ''},
                 'var1': {'code': 'Gnt', 'unidades': ''},
                 'var1': {'code': 'Gd', 'unidades': ''},
                 'var1': {'code': 'Ga', 'unidades': ''},
                 'var1': {'code': 'Gb', 'unidades': ''},
                 'var1': {'code': 'Gw', 'unidades': ''},
                 'var1': {'code': 'Dw', 'unidades': ''},
                 'var1': {'code': 'Hw', 'unidades': ''},
                 'var1': {'code': 'Hq', 'unidades': ''},
                 'var1': {'code': 'Sto', 'unidades': ''},
                 'var1': {'code': 'Zs', 'unidades': ''},
                 'var1': {'code': 'A', 'unidades': ''},
                 'var1': {'code': 'B', 'unidades': ''},
                 'var1': {'code': 'U', 'unidades': ''},
                 'var1': {'code': 'Uc', 'unidades': ''},
                 'var1': {'code': 'Kr', 'unidades': ''},
                 'var1': {'code': 'CrA', 'unidades': ''},
                 'var1': {'code': 'CrB', 'unidades': ''},
                 'var1': {'code': 'CrU', 'unidades': ''},
                 'var1': {'code': 'Cr4', 'unidades': ''},
                 'var1': {'code': 'C1*', 'unidades': ''},
                 'var1': {'code': 'C2*', 'unidades': ''},
                 'var1': {'code': 'C3*', 'unidades': ''},
                 'var1': {'code': 'Cxf', 'unidades': ''},
                 'var1': {'code': 'Cxa', 'unidades': ''},
                 'var1': {'code': 'Cxb', 'unidades': ''},
                 'var1': {'code': 'Cqf', 'unidades': ''},
                 'var1': {'code': 'Cti', 'unidades': ''},
                 'var1': {'code': 'Cqi', 'unidades': ''},
                 'var1': {'code': 'Ci', 'unidades': ''},
                 'var1': {'code': 'Cd', 'unidades': ''},
                 'var1': {'code': 'Cw', 'unidades': ''}
                 }

dict_read_out = dict([(x['code'], [None, None]) for x in vars_SAHYSMOD.values()])
