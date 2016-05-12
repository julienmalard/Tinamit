import os
import re
from subprocess import run

from Biofísico import ClaseModeloBF

# Path to SAHYSMOD executable. Change as needed on your computer
SAHYSMOD = ''


class Modelo(ClaseModeloBF):
    def __init__(símismo):
        super().__init__()

        # These attributes are needed for all ClaseModeloBF subclass implementations
        símismo.variables = {'Groundwater Depth': {'var': 1,
                                                   'unidades': 'm'
                                                   },

                             'Soil Salinity': {'var': 0,
                                               'unidades': 'dS/m'
                                               },

                             'Groundwater Extraction': {'var': 0,
                                                        'unidades': 'm/season'
                                                        }
                             }

        símismo.unidades_tiempo = 'Season'

        # These attributes are specific to the SAHYSMOD wrapper
        current_dir = os.path.dirname(os.path.realpath(__file__))
        símismo.output = os.path.join(current_dir, 'SAHYSMOD.out')
        símismo.input = os.path.join(current_dir, 'TEMPLATE.inp')

        # This class will simulate on a seasonal time basis, but the SAHYSMOD executable must run for two half-years
        # at the same time. Therefore, we create an internal diccionario to store variable data for both half-years.
        # {'var 1': [season1value, season2value],
        #  'var 2': [season1value, season2value],
        #  ...
        #  }

        símismo.interal_data = dict([(var, [símismo.variables[var]['var']]*2) for var in símismo.variables])

        símismo.season = 0

    def ejec(símismo):
        pass  # No prior setup necessary

    def incr(símismo, paso):
        # Note: this subclass can only be used with a coupling time step of 0.5 years
        assert paso == 0.5

        s = símismo.season

        # Save incoming coupled variables to the internal data
        símismo.interal_data['Groundwater Extraction'][s] = símismo.variables['Groundwater Extraction']

        if s == 0:

            dic_data = dict(GwWS1=símismo.interal_data['Groundwater Extraction'][0],
                            GwWS2=símismo.interal_data['Groundwater Extraction'][1])

            # Create the appropriate input file:
            símismo.write_inp(file_path=símismo.input, output_file=símismo.output, dic_data=dic_data)

            # Prepare the command
            args = dict(SAHYSMOD=SAHYSMOD, input=símismo.input, output=símismo.output)
            command = '{SAHYSMOD} {input} {output}'.format(**args)

            # Run the command prompt command
            run(command)

            # Read the output
            data_out = {'Dw': [None, None], 'Cqf': [None, None]}
            símismo.read_out(file_path=símismo.output, dic_data=data_out)

            símismo.interal_data['Groundwater Ddepth'] = data_out['Dw']
            símismo.interal_data['Groundwater Ddepth'] = data_out['Cqf']

            # Increment the season
            s = 1

            # Set the variables dictionary to the appropriate season data
            símismo.variables['Groundwater Depth']['var'] = símismo.interal_data['Groundwater Depth'][s]
            símismo.variables['Soil Salinity']['var'] = símismo.interal_data['Soil Salinity'][s]

            # Increment/reset the season
            s += 1
            s %= 2  # 2 seasons equals season 0 of the next year
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

        :param file_path:


        :param dic_data: A dictionario with the variables of interest as keys. Example:
          {'Dw': [None, None], 'Cqf': [None, None]}
          would read the variables Dw and Cqf from the last two seasons of the SAHYSMOD output

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

                            try:
                                val = float(m.group(1))
                            except ValueError:
                                print(m.group(0))
                                print(m.group(1))
                                raise ValueError('The variable "%s" was not read from the SAHYSMOD output.' % var)

                            dic_data[var][season] = val

                            # If we've found the variable, stop looking for it.
                            break
