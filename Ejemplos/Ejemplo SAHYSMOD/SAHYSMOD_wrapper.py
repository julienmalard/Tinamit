import os
import re
from subprocess import run

from Biofísico import ClaseModeloBF
import numpy as np

"""
How to use this SAHYSMOD wrapper for Tinamit:
    1. Set the SAHYSMOD path below according to your locale. You must have SAHYSMOD already installed on your computer.
    2. Create a SAHYSMOD input file set to run for one year according to the initial conditions for your model. As of
       now, Tinamit (and this wrapper) do not have spatial functionality, so make sure your model has only 1 internal
       polygon. If you'd like to contribute to adding spatial variability, we'd be forever grateful and will add your 
       name to the credits. Get in touch! (julien.malard@mail.mcgill.ca)
    3. Set the initial_data variable path below to the SAHYSMOD input file you just created.
    4. You're done! Start using Tinamit and use this python file's location as the biophysical model path.
     
"""

# Path to SAHYSMOD executable. Change as needed on your computer.
SAHYSMOD = ''

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
initial_data = 'C:\\Users\\iarna\\PyCharmProjects\\Tinamit\\Ejemplos\\Ejemplo SAHYSMOD\\INPUT_EXAMPLE.inp'


class Modelo(ClaseModeloBF):
    def __init__(self):
        super().__init__()

        # The following attributes are needed for all ClaseModeloBF subclass implementations. Don't change their names.
        self.variables = dict([(name, {'var': None,
                                       'unidades': dic['units']
                                       }
                                )
                               for (name, dic) in vars_SAHYSMOD.items()])

        self.unidades_tiempo = 'Months'
        
        # The following attributes are specific to the SAHYSMOD wrapper
        
        # This class will simulate on a seasonal time basis, but the SAHYSMOD executable must run for a full year
        # at the same time. Therefore, we create an internal dictionary to store variable data for all seasons in a
        # year.
        # {'code var 1': [season1value, season2value, ...],
        #  'code var 2': [season1value, season2value, ...],
        #  ...
        #  }
        self.internal_data = dict([(var, []) for var in self.variables
                                   if '#' in vars_SAHYSMOD[var]['code']])
        
        # Create some useful model attributes
        self.n_seasons = None  # Number of seasons per year
        self.len_seasons = []  # A list to store the length of each season, in months
        self.season = 0  # Current season number (Python numeration)
        self.month = 0  # Current month of the season

        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.output = os.path.join(current_dir, 'SAHYSMOD.out')
        self.input = os.path.join(current_dir, 'SAHYSMOD.inp')
        self.input_templ = os.path.join(current_dir, 'TEMPLATE.inp')

        # Prepare the command to the SAHYSMOD executable
        args = dict(SAHYSMOD=SAHYSMOD, input=self.input, output=self.output)
        self.command = '{SAHYSMOD} {input} {output}'.format(**args)

        # Read input values from .inp file
        self._read_input_vals()

    def ejec(símismo):
        pass  # No prior setup necessary. Including this function is necessary for all ClaseModeloBF subclasses

    def incr(self, paso):

        # Note: this subclass can only be used with a coupling time step multiple of 1 month.
        if not (int(paso) == paso):
            raise ValueError('Time step ("paso") must be a whole number.')

        m = self.month
        s = self.season
        y = 1  # The number of years to simulate.

        m += paso

        while m >= self.len_seasons[s]:
            m %= self.len_seasons[s]
            s += 1

        if s >= self.n_seasons:
            y += s // self.n_seasons
            s %= self.n_seasons

        # Save the season and month for the next time.
        self.month = m
        self.season = s

        # If this is the first month of the season, we change the variables dictionary values accordingly
        if m == 0:
            # Set the internal diccionary of values to this season's values
            for c in self.internal_data:
                # For every variable in the internal data dictionary (i.e., all variables that vary by season)

                var = codes_to_vars[c]  # Get the corresponding verbose variable name

                # Set the variables dictionary value to this season's value
                self.variables[var]['var'] = self.internal_data[c][s]

        # If this is the first season of the year, we also run a SAHYSMOD simulation
        if s == 0:

            # Create the appropriate input file:
            self._write_inp(n_year=y)

            # Run the command prompt command
            run(self.command)

            # Read the output
            self._read_out(n_year=y)

        # Save incoming coupled variables to the internal data
        for var in self.variables:
            if var in self.vars_ingr:
                self.internal_data[var][s] = self.variables[var]

    # Some internal functions specific to this SAHYSMOD wrapper
    def _write_inp(self, n_year):
        """
        This function writes a SAHYSMOD input file according to the model's current internal state (so that the
          simulation based on the input file will start with initial values corresponding to the model's present state).

        :param n_year: The number of years for which SAHYSMOD will be run.
        :type n_year: int

        """

        # Generate the dictionary of current variable values
        dic_data = dict([(vars_SAHYSMOD[k]['code'], v['var']) for (k, v) in self.variables.items()])
        dic_data.update(dict([(vars_SAHYSMOD[k]['code'], v) for (k, v) in self.internal_data.items()]))

        # Add basic data
        dic_data['n_years'] = n_year
        dic_data['n_seasons'] = self.n_seasons
        dic_data['months_per_season'] = '    '.join([str(x) for x in self.len_seasons])

        # Read the template CLI file
        with open(self.input_templ) as d:
            template = d.readlines()

        # Fill in our data
        input_file = []
        for n, line in enumerate(template):

            m = re.search(r'{([^}:]*)(:*.*?)}', line)
            if m is None:
                input_file.append(line)
                continue

            if '#' not in line:
                # If this is not a seasonal variable, simply add the line to the end of the input file
                input_file.append(line.format(**dic_data))

            else:
                # For every season, add the appropriate value of the variable
                for s in range(self.n_seasons):
                    line_s = line.replace('#', '#[%i]' % s)
                    input_file.append(line_s.format(**dic_data))

        # And save the input file
        with open(self.input, 'w') as d:
            d.write(''.join(input_file))

    def _read_out(self, n_year):
        """
        This function reads the last year of a SAHYSMOD output file.

        :param n_year: The number of years for which SAHYSMOD will be run.
        :type n_year: int

        """

        # A dictionary to hold the output values
        dic_data = dict([(k, -np.ones(self.n_seasons)) for k in SAHYSMOD_output_vars])

        with open(self.output, 'r') as d:

            # Skip unecessary lines before the year of interest
            l = ''
            while 'YEAR:      %i' % n_year not in l:
                l = d.readline()

            for season in range(self.n_seasons):  # Read output for the last year's seasons from the output file

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
                for cod in SAHYSMOD_output_vars:
                    var_out = cod.replace('#', '')

                    for line in season_output:

                        line += ' '
                        m = re.search('%s += +([^ ]*)' % var_out, line)

                        if m:
                            val = m.groups()[0]
                            if val == '-':
                                val = -1
                            else:
                                try:
                                    val = float(val)
                                except ValueError:
                                    raise ValueError('The variable "%s" was not read from the SAHYSMOD output.'
                                                     % var_out)

                            dic_data[cod][season] = val

                            # If we've found the variable, stop looking for it.
                            break

        # Save current season values
        for code, dic in dic_data.items():
            var = codes_to_vars[code]
            self.variables[var]['var'] = dic_data[code][0]

            # Save other season values
            if var in self.internal_data:
                self.internal_data[var] = dic_data[code]

        # Ajust for soil salinity of different crops
        kr = self.variables[codes_to_vars['Kr']]
        if kr == 0:
            u = 1 - dic_data['B'] - dic_data['A']
            soil_sal = dic_data['A'] * dic_data['CrA'] + dic_data['B'] * dic_data['CrB'] + u * dic_data['CrU']
        elif kr == 1:
            u = 1 - dic_data['B'] - dic_data['A']
            soil_sal = dic_data['CrU'] * u + dic_data['C1*'] * (1-u)
        elif kr == 2:
            soil_sal = dic_data['CrA'] * dic_data['A'] + dic_data['C2*'] * (1 - dic_data['A'])
        elif kr == 3:
            soil_sal = dic_data['CrB'] * dic_data['B'] + dic_data['C3*'] * (1 - dic_data['B'])
        elif kr == 4:
            soil_sal = dic_data['C4']
        for cr in ['CrA', 'CrB', 'CrU']:
            self.variables[codes_to_vars[cr]]['var'] = soil_sal[0]
            self.internal_data[codes_to_vars[cr]] = soil_sal

    def _read_input_vals(self):
        """
        This function will read the initial values for the model from a SAHYSMOD input (.inp) file and save the 
          relavant information to this model class's internal variables.
         
        """
        
        # Read the input file
        with open(initial_data, 'r') as d:
            inp = d.readlines()
        
        # Read the standard SAHYSMOD input template
        with open(self.input_templ) as d:
            template = d.readlines()
        
        # Save the number of seasons and length of each season
        self.n_seasons = int(inp[2].split()[1])
        self.len_seasons = [float(x) for x in inp[3].split()]
        
        # Make sure the number of season lengths equals the number of seasons.
        if self.n_seasons != len(self.len_seasons):
            raise ValueError('Error in the SAHYSMOD input file: the number of season lengths specified is not equal'
                             'to the number of seasons (lines 3 and 4).')
        
        n_i = 0  # To keep track of the line of the input file we are on
        
        # For every line in the template, extract the corresponding input file data
        for n_t, l in enumerate(template):

            # Search for a variable key in the template line
            m = re.search(r'{([^}:]*)(:*.*?)}', l)
            
            if m:
                # If we've found a key match, save the key (code) and verbose variable name.
                code = m.groups()[0]

                try:
                    var = codes_to_vars[code]
                except KeyError:
                    n_i += 1  # Increment the input file line number
                    continue

                if code not in SAHYSMOD_input_vars:
                    # If this variable key does not exist in the SAHYSMOD input variable list, move on to the next line.
                    n_i += 1  # Increment the input file line number
                    continue
                
                if '#' not in code:
                    # If this variable has one value per year, save it in the variable dictionary
                    self.variables[var]['var'] = float(inp[n_i])
                    n_i += 1  # Increment the input file line number

                else:
                    # If this variable has separate values for each season, save the first season's value in the 
                    # variable dictionary...

                    self.variables[var]['var'] = float(inp[n_i])
                    
                    # ... and save all the seasons' values in the internal data diccionary, for future reference.
                    for s in range(self.n_seasons):
                        self.internal_data[var].append(float(inp[n_i]))
                        n_i += 1

            else:
                n_i += 1


# A dictionary of SAHYSMOD variables. See the SAHYSMOD documentation for more details.
vars_SAHYSMOD = {'Rainfall': {'code': 'Pp#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Aquifer bottom level': {'code': 'BL', 'units': 'm', 'inp': True, 'out': False},
                 'Incoming canal salinity': {'code': 'Cic#', 'units': 'dS/m', 'inp': True, 'out': False},
                 'Aquifer inflow salinity': {'code': 'Cin', 'units': 'dS/m', 'inp': True, 'out': False},
                 'Aquifer thickness': {'code': 'Da', 'units': 'm', 'inp': True, 'out': False},
                 'Capillary rise critical depth': {'code': 'Dcr', 'units': 'm', 'inp': True, 'out': False},
                 'Subsurface drain depth': {'code': 'Dd', 'units': 'm', 'inp': True, 'out': False},
                 'Root zone thickness': {'code': 'Dr', 'units': 'm', 'inp': True, 'out': False},
                 'Transition zone thickness': {'code': 'Dx', 'units': 'm', 'inp': True, 'out': False},
                 'Potential ET crop A': {'code': 'EpA#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Potential ET crop B': {'code': 'EpB#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Potential ET non-irrigated': {'code': 'EpU#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Aquifer leaching efficienty': {'code': 'Flq', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Root zone leaching efficiency': {'code': 'Flr', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Transition zone leaching efficiency': {'code': 'Flx', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Drainage function reduction factor': {'code': 'Frd#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Water storage efficiency crop A': {'code': 'FsA#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Water storage efficiency crop B': {'code': 'FsB#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Water storage efficiency non-irrigated': {'code': 'FsU#', 'units': 'Dmnl',
                                                            'inp': True, 'out': False},
                 'Fraction well water to irrigation': {'code': 'Fw#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Subsurface drainage for irrigation': {'code': 'Gu#', 'units': 'm3/season/m2',
                                                        'inp': True, 'out': False},
                 'Groundwater extraction': {'code': 'Gw#', 'units': 'm3/season/m2', 'inp': True, 'out': True},
                 'Initial water level semi-confined': {'code': 'Hc', 'units': 'm', 'inp': True, 'out': False},
                 'Crop A field irrigation': {'code': 'IaA#', 'units': 'm3/season/m2', 'inp': True, 'out': True},
                 'Crop B field irrigation': {'code': 'IaB#', 'units': 'm3/season/m2', 'inp': True, 'out': True},
                 'Crop A paddy?': {'code': 'KcA#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Crop B paddy?': {'code': 'KcB#', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Subsurface drainage?': {'code': 'Kd', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Farmers\'s responses?': {'code': 'Kf', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Internal/external node index': {'code': 'Ki/e', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Horizontal hydraulic conductivity': {'code': 'Khor', 'units': 'm/day', 'inp': True, 'out': False},
                 'Semi-confined aquifer?': {'code': 'Ksc', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Land use key': {'code': 'Kr', 'units': 'Dmnl', 'inp': True, 'out': True},
                 'Vertical hydraulic conductivity semi-confined': {'code': 'Kver', 'units': 'm/day',
                                                                   'inp': True, 'out': False},
                 'Canal percolation': {'code': 'Lc#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Aquifer effective porosity': {'code': 'Peq', 'units': 'm/m', 'inp': True, 'out': False},
                 'Root zone effective porosity': {'code': 'Per', 'units': 'm/m', 'inp': True, 'out': False},
                 'Transition zone effective porosity': {'code': 'Pex', 'units': 'm/m', 'inp': True, 'out': False},
                 'Semi-confined aquifer storativity': {'code': 'Psq', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Aquifer total pore space': {'code': 'Ptq', 'units': 'm/m', 'inp': True, 'out': False},
                 'Root zone total pore space': {'code': 'Ptr', 'units': 'm/m', 'inp': True, 'out': False},
                 'Transition zone total pore space': {'code': 'Ptx', 'units': 'm/m', 'inp': True, 'out': False},
                 'Drain discharge to water table height ratio': {'code': 'QH1#', 'units': 'm/day/m',
                                                                 'inp': True, 'out': False},
                 'Drain discharge to sq. water table height ratio': {'code': 'QH2#', 'units': 'm/day/m2',
                                                                     'inp': True, 'out': False},
                 'Aquifer inflow': {'code': 'Qinf', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Aquifer outflow': {'code': 'Qout', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Scale': {'code': 'Scale', 'units': 'Dmnl', 'inp': True, 'out': False},
                 'Soil surface level': {'code': 'SL', 'units': 'm', 'inp': True, 'out': False},
                 'Surface inflow to non-irrigated': {'code': 'SiU#', 'units': 'm3/season/m2',
                                                     'inp': True, 'out': False},
                 'Surface outflow crop A': {'code': 'SoA#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Surface outflow crop B': {'code': 'SoB#', 'units': 'm3/season/m2', 'inp': True, 'out': False},
                 'Surface outflow non-irrigated': {'code': 'SoU#', 'units': 'm3/season/m2',
                                                   'inp': True, 'out': False},
                 'Season duration': {'code': 'Ts#', 'units': 'months', 'inp': True, 'out': False},

                 'Total irrigation': {'code': 'It', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Canal irrigation': {'code': 'Is', 'units': 'm3/season/m2', 'inp': False, 'out': True},

                 'Irrigation efficiency crop A': {'code': 'FfA', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Irrigation efficiency crop B': {'code': 'FfB', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Total irrigation efficiency': {'code': 'FfT', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Water leaving by canal': {'code': 'Io', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Irrigation sufficiency crop A': {'code': 'JsA', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Irrigation sufficiency crop B': {'code': 'JsB', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Actual evapotranspiration nonirrigated': {'code': 'EaU', 'units': 'm3/season/m2',
                                                            'inp': False, 'out': True},
                 'Root zone percolation crop A': {'code': 'LrA', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Root zone percolation crop B': {'code': 'LrB', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Root zone percolation nonirrigated': {'code': 'LrU', 'units': 'm3/season/m2',
                                                        'inp': False, 'out': True},
                 'Total root zone percolation': {'code': 'LrT', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Capillary rise crop A': {'code': 'RrA', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Capillary rise crop B': {'code': 'RrB', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Capillary rise non-irrigated': {'code': 'RrU', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Total capillary rise': {'code': 'RrT', 'units': 'm3/season/m2', 'inp': False, 'out': True},
                 'Trans zone horizontal incoming groundwater': {'code': 'Gti', 'units': 'm3/season/m2',
                                                                'inp': False, 'out': True},
                 'Trans zone horizontal outgoing groundwater': {'code': 'Gto', 'units': 'm3/season/m2',
                                                                'inp': False, 'out': True},
                 'Net vertical water table recharge': {'code': 'Qv', 'units': 'm', 'inp': False, 'out': True},
                 'Aquifer horizontal incoming groundwater': {'code': 'Gqi', 'units': 'm3/season/m2',
                                                             'inp': False, 'out': True},
                 'Aquifer horizontal outgoing groundwater': {'code': 'Gqo', 'units': 'm3/season/m2',
                                                             'inp': False, 'out': True},
                 'Net aquifer horizontal flow': {'code': 'Gaq', 'units': 'm3/season/m2',
                                                 'inp': False, 'out': True},
                 'Net horizontal groundwater flow': {'code': 'Gnt', 'units': 'm3/season/m2',
                                                     'inp': False, 'out': True},
                 'Total subsurface drainage': {'code': 'Gd', 'units': 'm3/season/m2',
                                               'inp': False, 'out': True},
                 'Subsurface drainage above drains': {'code': 'Ga', 'units': 'm3/season/m2',
                                                      'inp': True, 'out': True},
                 'Subsurface drainage below drains': {'code': 'Gb', 'units': 'm3/season/m2',
                                                      'inp': True, 'out': True},
                 'Groundwater depth': {'code': 'Dw', 'units': 'm', 'inp': False, 'out': True},
                 'Water table elevation': {'code': 'Hw', 'units': 'm', 'inp': True, 'out': True},
                 'Subsoil hydraulic head': {'code': 'Hq', 'units': 'm', 'inp': False, 'out': True},
                 'Water table storage': {'code': 'Sto', 'units': 'm', 'inp': False, 'out': True},
                 'Surface water salt': {'code': 'Zs', 'units': 'm*dS/m', 'inp': False, 'out': True},
                 'Seasonal fraction area crop A': {'code': 'A#', 'units': 'Dmnl', 'inp': True, 'out': True},
                 'Seasonal fraction area crop B': {'code': 'B#', 'units': 'Dmnl', 'inp': True, 'out': True},
                 'Seasonal fraction area nonirrigated': {'code': 'U', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Fraction permanently non-irrigated': {'code': 'Uc', 'units': 'Dmnl', 'inp': False, 'out': True},
                 'Root zone salinity crop A': {'code': 'CrA', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Root zone salinity crop B': {'code': 'CrB', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Root zone salinity non-irrigated': {'code': 'CrU', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Fully rotated land irrigated root zone salinity': {'code': 'Cr4', 'units': 'dS / m',
                                                                     'inp': False, 'out': True},
                 'Key 1 non-permanently irrigated root zone salinity': {'code': 'C1*', 'units': 'dS / m',
                                                                        'inp': False, 'out': True},
                 'Key 2 non-permanently irrigated root zone salinity': {'code': 'C2*', 'units': 'dS / m',
                                                                        'inp': False, 'out': True},
                 'Key 3 non-permanently irrigated root zone salinity': {'code': 'C3*', 'units': 'dS / m',
                                                                        'inp': False, 'out': True},
                 'Transition zone salinity': {'code': 'Cxf', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Transition zone above-drain salinity': {'code': 'Cxa', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Transition zone below-drain salinity': {'code': 'Cxb', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Soil salinity': {'code': 'Cqf', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Transition zone incoming salinity': {'code': 'Cti', 'units': 'dS / m', 'inp': False, 'out': True},
                 'Aquifer salinity': {'code': 'Cqi', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Irrigation water salinity': {'code': 'Ci#', 'units': 'dS / m', 'inp': True, 'out': True},
                 'Drainage salinity': {'code': 'Cd', 'units': 'ds / m', 'inp': False, 'out': True},
                 'Well water salinity': {'code': 'Cw', 'units': 'dS / m', 'inp': False, 'out': True}
                 }

# A dictionary to get the variable name from its SAHYSMOD code.
codes_to_vars = dict([(v['code'], k) for (k, v) in vars_SAHYSMOD.items()])

# A list containing only SAHYSMOD input variable codes
SAHYSMOD_input_vars = [v['code'] for v in vars_SAHYSMOD.values() if v['inp']]

# A list containing only SAHYSMOD output variable codes
SAHYSMOD_output_vars = [v['code'] for v in vars_SAHYSMOD.values() if v['out']]

if __name__ == '__main__':
    modelo = Modelo()
    print(modelo.internal_data)
    print(modelo.variables)
    modelo.incr(paso=1)
