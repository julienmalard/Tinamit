import os
from subprocess import run
import numpy as np
from tinamit import obt_val_config
from tinamit.BF import ModeloBF


class ModeloSWAT(ModeloBF):
    """
    This is Wrapper for SWAT.
    """

    def __init__(self, textinout_path, swat_exe=None):
        """
        This function initializes the SWAT wrapper.
        You must have SWAT already installed on your computer or the SWAT executable.

        :param textinout_path: The path to SWAT Project TextInOut folder
        :type textinout_path: str

        :param swat_exe: The path to the SWAT executable.
        :type swat_exe: str
        """

        self.initargs = (textinout_path, swat_exe)

        # Find the SWAT executable path, if necessary.
        if swat_exe is None:
            swat_exe = obt_val_config('exe_swat', mnsj='Specify the location of your SWAT executable.')
        self.swat_exe = swat_exe

        # Time step of the model
        self.timestep = None

        # Set the working directory, which is basically the same as Textinout Path
        self.working_dir = textinout_path

        # Prepare the command to the SWAT executable
        # This is prepared later on in the function "iniciar_modelo"
        self.command = None

        # Initialise as the parent class.
        super().__init__()

    def inic_vars(self):
        """
        This function initializes the variable and variable type dictionaries.
        """

        self.variables.clear()

        for name, dic in vars_SWAT.items():
            self.variables[name] = {'val': None,
                                    'unidades': None,
                                    'ingreso': dic['inp'],
                                    'egreso': dic['out'],
                                    'dims': (None,)  # This will be changed later for multidimensional variables.
                                    }

        self.hru_params = read_hru_details(self.working_dir)

        # Number of sub-basins in the model
        self.nsub = self.hru_params["no_sub"]

        # Number of hrus in the model (determining from the number of mgt parameter files)
        self.nhru = self.hru_params["no_hru"]

        self.leer_vals_inic()

    def iniciar_modelo(self, tiempo_final, nombre_corrida):
        """
        This function doesn't do anything of much importance.
        It:
        1) Determines the time step;
        2) Reads the HRU details;
        3) Determines the number of sub-basins and HRUs in the SWAT project.
        4) Creates a run command for running SWAT

        The input arguments are not used and are passed to parent class.
        """

        # Determining the time step
        self.timestep = self.obt_unidad_tiempo()

        # Reading HRU details
        self.hru_params = read_hru_details(self.working_dir)

        # Number of sub-basins in the model
        self.nsub = self.hru_params["no_sub"]

        # Number of hrus in the model (determining from the number of mgt parameter files)
        self.nhru = self.hru_params["no_hru"]

        # Create the run command (for later use)
        args = dict(SWAT=self.swat_exe, work_dir=self.working_dir)
        self.command = '"{SWAT}" "{work_dir}"'.format(**args)

        # Initialise as the parent class.
        super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cambiar_vals_modelo_interno(self, valores):
        """
        This function update the values of the SWAT parameters.
        It:
        1) Updates the parameters in file.cio for next run;
        2) Updates the parameters in basin.bsn based on variables dictionary;
        3) Updates the parameters in .mgt files based on variables dictionary;

        .: param valores: A dictionary of variables and values ​​to change
        .: type valores: dict

        """

        # Updating the values of variables dictionary as per valores
        for code in valores:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = valores[code]
            else:
                self.variables[code]["val"] = valores[code]

        # Updating file.cio

        # Reading the file.cio for present values of the variables
        setup_vars = read_file_cio(self.working_dir)
        runtype = setup_vars["IPRINT"]

        # Update the start and end of simulation
        if runtype == 0:  # monthly run

            # Here we need to check if it is a leap year
            current_run_year = setup_vars['IYR'] + setup_vars['NYSKIP']

            # Determining if leap year
            if current_run_year % 4 == 0 and current_run_year % 100 != 0:
                leap_year = True
            elif current_run_year % 400 == 0:
                leap_year = True
            elif current_run_year % 4 != 0:
                leap_year = False

            if leap_year:  # If it is leap year
                start_month = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]
                end_month = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
            else:
                start_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
                end_month = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

            # Identify the current month

            if setup_vars['IDAF'] in start_month:

                current_month = start_month.index(setup_vars['IDAF'])

                if current_month < 11:  # if the current month is not December
                    next_month = current_month + 1
                    setup_vars['IDAF'] = start_month[next_month]
                    setup_vars['IDAL'] = end_month[next_month]

                else:
                    setup_vars['IYR'] += 1  # Update year by one
                    setup_vars['IDAF'] = 1  # Set starting month to 1 (of next year)
                    setup_vars['IDAL'] = 31  # Set last month to 1 (as we want to run for one month)

            else:
                print("The begin day (IDAF) of simulation is not correct - Check file.cio")

        elif runtype == 1:  # daily run

            # Here we need to check if it is a leap year
            current_run_year = setup_vars['IYR'] + setup_vars['NYSKIP']

            # Determining if leap year
            if current_run_year % 4 == 0 and current_run_year % 100 != 0:

                leap_year = True

            elif current_run_year % 400 == 0:
                leap_year = True

            elif current_run_year % 4 != 0:
                leap_year = False

            if leap_year:  # If it is leap year
                if setup_vars['IDAF'] == 366:  # Last day of the year
                    setup_vars['IYR'] += 1  # Update the year
                    setup_vars['IDAF'] = 1
                    setup_vars['IDAL'] = 1
                else:  # Any other day of the year
                    setup_vars['IDAF'] += 1
                    setup_vars['IDAL'] += 1

            else:  # Not a leap year
                if setup_vars['IDAF'] == 365:  # Last day of the year
                    setup_vars['IYR'] += 1
                    setup_vars['IDAF'] = 1
                    setup_vars['IDAL'] = 1
                else:
                    setup_vars['IDAF'] += 1
                    setup_vars['IDAL'] += 1

        elif runtype == 2:  # annual run
            setup_vars['IYR'] += 1
            setup_vars['IDAF'] = 1
            current_run_year = setup_vars['IYR'] + setup_vars['NYSKIP']

            # Determining if leap year
            if current_run_year % 4 == 0 and current_run_year % 100 != 0:

                leap_year = True

            elif current_run_year % 400 == 0:
                leap_year = True

            elif current_run_year % 4 != 0:
                leap_year = False

            if leap_year:
                setup_vars['IDAL'] = 366

            else:
                setup_vars['IDAL'] = 365

        # Updating these values in variable dictionary
        for code in setup_vars:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = setup_vars[code]
            else:
                self.variables[code]["val"] = setup_vars[code]

            self.variables[code]["dims"] = (1,)

        # Writing the file.cio with updated values
        write_file_cio(self.working_dir, self.variables)

        # Updating basin.bsn file
        write_bsn_file(self.working_dir, self.variables)

        # Updating .mgt files
        write_mgt_file(self.working_dir, self.variables, self.hru_params)

        # Updating .hru files
        write_hru_file(self.working_dir, self.variables, self.hru_params)

        # Updating .pnd files
        write_pnd_file(self.working_dir, self.variables, self.hru_params)

        # Updating .rte files
        write_rte_file(self.working_dir, self.variables, self.hru_params)

        # Updating .gw files
        write_gw_file(self.working_dir, self.variables, self.hru_params)

        # Updating .sdr files
        write_sdr_file(self.working_dir, self.variables, self.hru_params)

        # Updating .sep files
        write_sep_file(self.working_dir, self.variables, self.hru_params)

        # Updating .sol files
        write_sol_file(self.working_dir, self.variables, self.hru_params)

    def incrementar(self, paso):
        """
        This function runs the swat model for a time step.
        Currently it works of paso = 1

        :param paso: El número de pasos
        :type paso: int
        """

        # Command to run the model
        run(self.swat_exe, cwd=self.working_dir)

    def leer_vals(self):
        """
        This function reads the outputs of the SWAT.
        For now, it reads only reach outputs from output.rch for the last time step

        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.
        """

        flow_out_data = read_reach_output(self.working_dir, self.nsub)

        for code in flow_out_data:
            val = flow_out_data[code]
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = val
            else:
                self.variables[code]["val"] = val
            self.variables[code]["dims"] = flow_out_data[code].shape

    def cerrar_modelo(self):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        pass

    def obt_unidad_tiempo(self):
        """
        This function finds out what time step the model is set up for.
        It reads the variables "IPRINT" from file.cio
        IPRINT  | Time Step
        0       |   Month
        1       |   Day
        2       |   Year

        :return: runtype
        :rtype: int
        """

        # Reading the file.cio for present values of the variables
        file_cio_data = read_file_cio(self.working_dir)

        # Read the timestep
        runtype = file_cio_data['IPRINT']

        if runtype == 0:
            return "Month"
        elif runtype == 1:
            return "Day"
        elif runtype == 2:
            return "Year"

    def leer_vals_inic(self):
        """
        This function reads the values of the SWAT parameters
        For now, it works only for basins.bsn and mgt files parameters
        """

        # Read file.cio parameters
        file_cio_vars = read_file_cio(self.working_dir)

        # Writing the values of file.cio parameters in variables dictionary
        for code in file_cio_vars:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = file_cio_vars[code]
            else:
                self.variables[code]["val"] = file_cio_vars[code]
            if isinstance(file_cio_vars[code], np.ndarray):
                dims = file_cio_vars[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading basin parameters
        bsn_params = read_bsn_file(self.working_dir)

        # Writing the values of basin parameters in variables dictionary
        for code in bsn_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = bsn_params[code]
            else:
                self.variables[code]["val"] = bsn_params[code]
            if isinstance(bsn_params[code], np.ndarray):
                dims = bsn_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading mgt files parameters
        mgt_params = read_mgt_file(self.working_dir, self.hru_params)

        # Writing the values of mgt parameters in variables dictionary
        for code in mgt_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = mgt_params[code]
            else:
                self.variables[code]["val"] = mgt_params[code]
            if isinstance(mgt_params[code], np.ndarray):
                dims = mgt_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading hru files parameters
        hru_file_params = read_hru_file(self.working_dir, self.hru_params)

        # Writing the values of mgt parameters in variables dictionary
        for code in hru_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = hru_file_params[code]
            else:
                self.variables[code]["val"] = hru_file_params[code]
            if isinstance(hru_file_params[code], np.ndarray):
                dims = hru_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading pnd files parameters
        pnd_file_params = read_pond_file(self.working_dir, self.hru_params)

        # Writing the values of mgt parameters in variables dictionary
        for code in pnd_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = pnd_file_params[code]
            else:
                self.variables[code]["val"] = pnd_file_params[code]
            if isinstance(pnd_file_params[code], np.ndarray):
                dims = pnd_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading rte files parameters
        rte_file_params = read_rte_file(self.working_dir, self.hru_params)

        # Writing the values of rte parameters in variables dictionary
        for code in rte_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = rte_file_params[code]
            else:
                self.variables[code]["val"] = rte_file_params[code]
            if isinstance(rte_file_params[code], np.ndarray):
                dims = rte_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading gw files parameters
        gw_file_params = read_gw_file(self.working_dir, self.hru_params)

        # Writing the values of gw parameters in variables dictionary
        for code in gw_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = gw_file_params[code]
            else:
                self.variables[code]["val"] = gw_file_params[code]
            if isinstance(gw_file_params[code], np.ndarray):
                dims = gw_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading sdr files parameters
        sdr_file_params = read_sdr_file(self.working_dir, self.hru_params)

        # Writing the values of sdr parameters in variables dictionary
        for code in sdr_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = sdr_file_params[code]
            else:
                self.variables[code]["val"] = sdr_file_params[code]
            if isinstance(sdr_file_params[code], np.ndarray):
                dims = sdr_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading sep files parameters
        sep_file_params = read_sep_file(self.working_dir, self.hru_params)

        # Writing the values of sep parameters in variables dictionary
        for code in sep_file_params:
            if isinstance(self.variables[code]["val"], np.ndarray):
                self.variables[code]["val"][:] = sep_file_params[code]
            else:
                self.variables[code]["val"] = sep_file_params[code]
            if isinstance(sep_file_params[code], np.ndarray):
                dims = sep_file_params[code].shape
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Reading sol files parameters
        sol_file_params = read_sol_file(self.working_dir, self.hru_params)

        # Writing the values of sol parameters in variables dictionary
        for code in sol_file_params:
            if isinstance(self.variables[code]["val"], list):
                self.variables[code]["val"][:] = sol_file_params[code]
            else:
                self.variables[code]["val"] = sol_file_params[code]
            if isinstance(sol_file_params[code], list):
                dims = len(sol_file_params[code])
            else:
                dims = (1,)
            self.variables[code]["dims"] = dims

        # Writing the dims of flowout parameters in variables dictionary
        for code in SWAT_output_vars:
            self.variables[code]["dims"] = (self.nsub,)

    def __getinitargs__(self):
        return self.initargs


# A dictionary of SWAT variables. See the SWAT documentation for more details.
vars_SWAT = {'RCH': {'code': 'RCH', 'file': 'rch', 'inp': False, 'out': True},
             'GIS': {'code': 'GIS', 'file': 'rch', 'inp': False, 'out': True},
             'MON': {'code': 'MON', 'file': 'rch', 'inp': False, 'out': True},
             'AREA': {'code': 'AREA', 'file': 'rch', 'inp': False, 'out': True},
             'FLOW_IN': {'code': 'FLOW_IN', 'file': 'rch', 'inp': False, 'out': True},
             'FLOW_OUT': {'code': 'FLOW_OUT', 'file': 'rch', 'inp': False, 'out': True, 'dims': (8, 1)},
             'EVAP': {'code': 'EVAP', 'file': 'rch', 'inp': False, 'out': True},
             'TLOSS': {'code': 'TLOSS', 'file': 'rch', 'inp': False, 'out': True},
             'SED_IN': {'code': 'SED_IN', 'file': 'rch', 'inp': False, 'out': True},
             'SED_OUT': {'code': 'SED_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'SEDCONC': {'code': 'SEDCONC', 'file': 'rch', 'inp': False, 'out': True},
             'ORGN_IN': {'code': 'ORGN_IN', 'file': 'rch', 'inp': False, 'out': True},
             'ORGN_OUT': {'code': 'ORGN_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'ORGP_IN': {'code': 'ORGP_IN', 'file': 'rch', 'inp': False, 'out': True},
             'ORGP_OUT': {'code': 'ORGP_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'NO3_IN': {'code': 'NO3_IN', 'file': 'rch', 'inp': False, 'out': True},
             'NO3_OUT': {'code': 'NO3_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'NH4_IN': {'code': 'NH4_IN', 'file': 'rch', 'inp': False, 'out': True},
             'NH4_OUT': {'code': 'NH4_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'NO2_IN': {'code': 'NO2_IN', 'file': 'rch', 'inp': False, 'out': True},
             'NO2_OUT': {'code': 'NO2_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'MINP_IN': {'code': 'MINP_IN', 'file': 'rch', 'inp': False, 'out': True},
             'MINP_OUT': {'code': 'MINP_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'ALGAE_IN': {'code': 'ALGAE_IN', 'file': 'rch', 'inp': False, 'out': True},
             'ALGAE_OUT': {'code': 'ALGAE_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'CBOD_IN': {'code': 'CBOD_IN', 'file': 'rch', 'inp': False, 'out': True},
             'CBOD_OUT': {'code': 'CBOD_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'DISOX_IN': {'code': 'DISOX_IN', 'file': 'rch', 'inp': False, 'out': True},
             'DISOX_OUT': {'code': 'DISOX_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'SOLPST_IN': {'code': 'SOLPST_IN', 'file': 'rch', 'inp': False, 'out': True},
             'SOLPST_OUT': {'code': 'SOLPST_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'SORPST_IN': {'code': 'SORPST_IN', 'file': 'rch', 'inp': False, 'out': True},
             'SORPST_OUT': {'code': 'SORPST_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'REACTPST': {'code': 'REACTPST', 'file': 'rch', 'inp': False, 'out': True},
             'VOLPST': {'code': 'VOLPST', 'file': 'rch', 'inp': False, 'out': True},
             'SETTLPST': {'code': 'SETTLPST', 'file': 'rch', 'inp': False, 'out': True},
             'RESUSP_PST': {'code': 'RESUSP_PST', 'file': 'rch', 'inp': False, 'out': True},
             'DIFFUSEPST': {'code': 'DIFFUSEPST', 'file': 'rch', 'inp': False, 'out': True},
             'REACBEDPST': {'code': 'REACBEDPST', 'file': 'rch', 'inp': False, 'out': True},
             'BURYPST': {'code': 'BURYPST', 'file': 'rch', 'inp': False, 'out': True},
             'BED_PST': {'code': 'BED_PST', 'file': 'rch', 'inp': False, 'out': True},
             'BACTP_OUT': {'code': 'BACTP_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'BACTLP_OUT': {'code': 'BACTLP_OUT', 'file': 'rch', 'inp': False, 'out': True},
             'CMETAL#1': {'code': 'CMETAL#1', 'file': 'rch', 'inp': False, 'out': True},
             'CMETAL#2': {'code': 'CMETAL#2', 'file': 'rch', 'inp': False, 'out': True},
             'CMETAL#3': {'code': 'CMETAL#3', 'file': 'rch', 'inp': False, 'out': True},
             'TOT_N': {'code': 'TOT_N', 'file': 'rch', 'inp': False, 'out': True},
             'TOT_P': {'code': 'TOT_P', 'file': 'rch', 'inp': False, 'out': True},
             'NO3CONC': {'code': 'NO3CONC', 'file': 'rch', 'inp': False, 'out': True},
             'SFTMP': {'code': 'SFTMP', 'file': 'bsn', 'inp': True, 'out': False},
             'SMTMP': {'code': 'SMTMP', 'file': 'bsn', 'inp': True, 'out': False},
             'SMFMX': {'code': 'SMFMX', 'file': 'bsn', 'inp': True, 'out': False},
             'SMFMN': {'code': 'SMFMN', 'file': 'bsn', 'inp': True, 'out': False},
             'TIMP': {'code': 'TIMP', 'file': 'bsn', 'inp': True, 'out': False},
             'SNOCOVMX': {'code': 'SNOCOVMX', 'file': 'bsn', 'inp': True, 'out': False},
             'SNO50COV': {'code': 'SNO50COV', 'file': 'bsn', 'inp': True, 'out': False},
             'IPET': {'code': 'IPET', 'file': 'bsn', 'inp': True, 'out': False},
             'PETFILE': {'code': 'PETFILE', 'file': 'bsn', 'inp': True, 'out': False},
             'ESCO': {'code': 'ESCO', 'file': 'bsn', 'inp': True, 'out': False},
             'EPCO': {'code': 'EPCO', 'file': 'bsn', 'inp': True, 'out': False},
             'EVLAI': {'code': 'EVLAI', 'file': 'bsn', 'inp': True, 'out': False},
             'FFCB': {'code': 'FFCB', 'file': 'bsn', 'inp': True, 'out': False},
             'IEVENT': {'code': 'IEVENT', 'file': 'bsn', 'inp': True, 'out': False},
             'ICRK': {'code': 'ICRK', 'file': 'bsn', 'inp': True, 'out': False},
             'SURLAG': {'code': 'SURLAG', 'file': 'bsn', 'inp': True, 'out': False},
             'ADJ_PKR': {'code': 'ADJ_PKR', 'file': 'bsn', 'inp': True, 'out': False},
             'PRF_BSN': {'code': 'PRF_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'SPCON': {'code': 'SPCON', 'file': 'bsn', 'inp': True, 'out': False},
             'SPEXP': {'code': 'SPEXP', 'file': 'bsn', 'inp': True, 'out': False},
             'RCN': {'code': 'RCN', 'file': 'bsn', 'inp': True, 'out': False},
             'CMN': {'code': 'CMN', 'file': 'bsn', 'inp': True, 'out': False},
             'N_UPDIS': {'code': 'N_UPDIS', 'file': 'bsn', 'inp': True, 'out': False},
             'P_UPDIS': {'code': 'P_UPDIS', 'file': 'bsn', 'inp': True, 'out': False},
             'NPERCO': {'code': 'NPERCO', 'file': 'bsn', 'inp': True, 'out': False},
             'PPERCO': {'code': 'PPERCO', 'file': 'bsn', 'inp': True, 'out': False},
             'PHOSKD': {'code': 'PHOSKD', 'file': 'bsn', 'inp': True, 'out': False},
             'PSP': {'code': 'PSP', 'file': 'bsn', 'inp': True, 'out': False},
             'RSDCO': {'code': 'RSDCO', 'file': 'bsn', 'inp': True, 'out': False},
             'PERCOP': {'code': 'PERCOP', 'file': 'bsn', 'inp': True, 'out': False},
             'ISUBWQ': {'code': 'ISUBWQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WDPQ': {'code': 'WDPQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WGPQ': {'code': 'WGPQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WDLPQ': {'code': 'WDLPQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WGLPQ': {'code': 'WGLPQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WDPS': {'code': 'WDPS', 'file': 'bsn', 'inp': True, 'out': False},
             'WGPS': {'code': 'WGPS', 'file': 'bsn', 'inp': True, 'out': False},
             'WDLPS': {'code': 'WDLPS', 'file': 'bsn', 'inp': True, 'out': False},
             'WGLPS': {'code': 'WGLPS', 'file': 'bsn', 'inp': True, 'out': False},
             'BACTKDQ': {'code': 'BACTKDQ', 'file': 'bsn', 'inp': True, 'out': False},
             'THBACT': {'code': 'THBACT', 'file': 'bsn', 'inp': True, 'out': False},
             'WOF_P': {'code': 'WOF_P', 'file': 'bsn', 'inp': True, 'out': False},
             'WOF_LP': {'code': 'WOF_LP', 'file': 'bsn', 'inp': True, 'out': False},
             'WDPF': {'code': 'WDPF', 'file': 'bsn', 'inp': True, 'out': False},
             'WGPF': {'code': 'WGPF', 'file': 'bsn', 'inp': True, 'out': False},
             'WDLPF': {'code': 'WDLPF', 'file': 'bsn', 'inp': True, 'out': False},
             'WGLPF': {'code': 'WGLPF', 'file': 'bsn', 'inp': True, 'out': False},
             'ISED_DET': {'code': 'ISED_DET', 'file': 'bsn', 'inp': True, 'out': False},
             'IRTE': {'code': 'IRTE', 'file': 'bsn', 'inp': True, 'out': False},
             'MSK_CO1': {'code': 'MSK_CO1', 'file': 'bsn', 'inp': True, 'out': False},
             'MSK_CO2': {'code': 'MSK_CO2', 'file': 'bsn', 'inp': True, 'out': False},
             'MSK_X': {'code': 'MSK_X', 'file': 'bsn', 'inp': True, 'out': False},
             'IDEG': {'code': 'IDEG', 'file': 'bsn', 'inp': True, 'out': False},
             'IWQ': {'code': 'IWQ', 'file': 'bsn', 'inp': True, 'out': False},
             'WWQFILE': {'code': 'WWQFILE', 'file': 'bsn', 'inp': True, 'out': False},
             'TRNSRCH': {'code': 'TRNSRCH', 'file': 'bsn', 'inp': True, 'out': False},
             'EVRCH': {'code': 'EVRCH', 'file': 'bsn', 'inp': True, 'out': False},
             'IRTPEST': {'code': 'IRTPEST', 'file': 'bsn', 'inp': True, 'out': False},
             'ICN': {'code': 'ICN', 'file': 'bsn', 'inp': True, 'out': False},
             'CNCOEF': {'code': 'CNCOEF', 'file': 'bsn', 'inp': True, 'out': False},
             'CDN': {'code': 'CDN', 'file': 'bsn', 'inp': True, 'out': False},
             'SDNCO': {'code': 'SDNCO', 'file': 'bsn', 'inp': True, 'out': False},
             'BACT_SWF': {'code': 'BACT_SWF', 'file': 'bsn', 'inp': True, 'out': False},
             'BACTMX': {'code': 'BACTMX', 'file': 'bsn', 'inp': True, 'out': False},
             'BACTMINLP': {'code': 'BACTMINLP', 'file': 'bsn', 'inp': True, 'out': False},
             'BACTMINP': {'code': 'BACTMINP', 'file': 'bsn', 'inp': True, 'out': False},
             'WDLPRCH': {'code': 'WDLPRCH', 'file': 'bsn', 'inp': True, 'out': False},
             'WDPRCH': {'code': 'WDPRCH', 'file': 'bsn', 'inp': True, 'out': False},
             'WDLPRES': {'code': 'WDLPRES', 'file': 'bsn', 'inp': True, 'out': False},
             'WDPRES': {'code': 'WDPRES', 'file': 'bsn', 'inp': True, 'out': False},
             'TB_ADJ': {'code': 'TB_ADJ', 'file': 'bsn', 'inp': True, 'out': False},
             'DEPIMP_BSN': {'code': 'DEPIMP_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'DDRAIN_BSN': {'code': 'DDRAIN_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'TDRAIN_BSN': {'code': 'TDRAIN_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'GDRAIN_BSN': {'code': 'GDRAIN_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'CN_FROZ': {'code': 'CN_FROZ', 'file': 'bsn', 'inp': True, 'out': False},
             'DORM_HR': {'code': 'DORM_HR', 'file': 'bsn', 'inp': True, 'out': False},
             'SMXCO': {'code': 'SMXCO', 'file': 'bsn', 'inp': True, 'out': False},
             'FIXCO': {'code': 'FIXCO', 'file': 'bsn', 'inp': True, 'out': False},
             'NFIXMX': {'code': 'NFIXMX', 'file': 'bsn', 'inp': True, 'out': False},
             'ANION_EXCL_BSN': {'code': 'ANION_EXCL_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'CH_ONCO_BSN': {'code': 'CH_ONCO_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'CH_OPCO_BSN': {'code': 'CH_OPCO_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'HLIFE_NGW_BSN': {'code': 'HLIFE_NGW_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'RCN_SUB_BSN': {'code': 'RCN_SUB_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'BC1_BSN': {'code': 'BC1_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'BC2_BSN': {'code': 'BC2_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'BC3_BSN': {'code': 'BC3_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'BC4_BSN': {'code': 'BC4_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'DECR_MIN': {'code': 'DECR_MIN', 'file': 'bsn', 'inp': True, 'out': False},
             'ICFAC': {'code': 'ICFAC', 'file': 'bsn', 'inp': True, 'out': False},
             'RSD_COVCO': {'code': 'RSD_COVCO', 'file': 'bsn', 'inp': True, 'out': False},
             'VCRIT': {'code': 'VCRIT', 'file': 'bsn', 'inp': True, 'out': False},
             'CSWAT': {'code': 'CSWAT', 'file': 'bsn', 'inp': True, 'out': False},
             'RES_STLR_CO': {'code': 'RES_STLR_CO', 'file': 'bsn', 'inp': True, 'out': False},
             'BFLO_DIST 0-1 (1': {'code': 'BFLO_DIST 0-1 (1', 'file': 'bsn', 'inp': True, 'out': False},
             'IUH': {'code': 'IUH', 'file': 'bsn', 'inp': True, 'out': False},
             'UHALPHA': {'code': 'UHALPHA', 'file': 'bsn', 'inp': True, 'out': False},
             'EROS_SPL': {'code': 'EROS_SPL', 'file': 'bsn', 'inp': True, 'out': False},
             'RILL_MULT': {'code': 'RILL_MULT', 'file': 'bsn', 'inp': True, 'out': False},
             'EROS_EXPO': {'code': 'EROS_EXPO', 'file': 'bsn', 'inp': True, 'out': False},
             'SUBD_CHSED': {'code': 'SUBD_CHSED', 'file': 'bsn', 'inp': True, 'out': False},
             'C_FACTOR': {'code': 'C_FACTOR', 'file': 'bsn', 'inp': True, 'out': False},
             'CH_D50': {'code': 'CH_D50', 'file': 'bsn', 'inp': True, 'out': False},
             'SIG_G': {'code': 'SIG_G', 'file': 'bsn', 'inp': True, 'out': False},
             'RE_BSN': {'code': 'RE_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'SDRAIN_BSN': {'code': 'SDRAIN_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'DRAIN_CO_BSN': {'code': 'DRAIN_CO_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'PC_BSN': {'code': 'PC_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'LATKSATF_BSN': {'code': 'LATKSATF_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'ITDRN': {'code': 'ITDRN', 'file': 'bsn', 'inp': True, 'out': False},
             'IWTDN': {'code': 'IWTDN', 'file': 'bsn', 'inp': True, 'out': False},
             'SOL_P_MODEL': {'code': 'SOL_P_MODEL', 'file': 'bsn', 'inp': True, 'out': False},
             'IABSTR': {'code': 'IABSTR', 'file': 'bsn', 'inp': True, 'out': False},
             'IATMODEP': {'code': 'IATMODEP', 'file': 'bsn', 'inp': True, 'out': False},
             'R2ADJ_BSN': {'code': 'R2ADJ_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'SSTMAXD_BSN': {'code': 'SSTMAXD_BSN', 'file': 'bsn', 'inp': True, 'out': False},
             'ISMAX': {'code': 'ISMAX', 'file': 'bsn', 'inp': True, 'out': False},
             'IROUTUNIT': {'code': 'IROUTUNIT', 'file': 'bsn', 'inp': True, 'out': False},
             'NMGT': {'code': 'NMGT', 'file': 'mgt', 'inp': True, 'out': False},
             'IGRO': {'code': 'IGRO', 'file': 'mgt', 'inp': True, 'out': False},
             'PLANT_ID': {'code': 'PLANT_ID', 'file': 'mgt', 'inp': True, 'out': False},
             'LAI_INIT': {'code': 'LAI_INIT', 'file': 'mgt', 'inp': True, 'out': False},
             'BIO_INIT': {'code': 'BIO_INIT', 'file': 'mgt', 'inp': True, 'out': False},
             'PHU_PLT': {'code': 'PHU_PLT', 'file': 'mgt', 'inp': True, 'out': False},
             'BIOMIX': {'code': 'BIOMIX', 'file': 'mgt', 'inp': True, 'out': False},
             'CN2': {'code': 'CN2', 'file': 'mgt', 'inp': True, 'out': False},
             'USLE_P': {'code': 'USLE_P', 'file': 'mgt', 'inp': True, 'out': False},
             'BIO_MIN': {'code': 'BIO_MIN', 'file': 'mgt', 'inp': True, 'out': False},
             'FILTERW': {'code': 'FILTERW', 'file': 'mgt', 'inp': True, 'out': False},
             'IURBAN': {'code': 'IURBAN', 'file': 'mgt', 'inp': True, 'out': False},
             'URBLU': {'code': 'URBLU', 'file': 'mgt', 'inp': True, 'out': False},
             'IRRSC': {'code': 'IRRSC', 'file': 'mgt', 'inp': True, 'out': False},
             'IRRNO': {'code': 'IRRNO', 'file': 'mgt', 'inp': True, 'out': False},
             'FLOWMIN': {'code': 'FLOWMIN', 'file': 'mgt', 'inp': True, 'out': False},
             'DIVMAX': {'code': 'DIVMAX', 'file': 'mgt', 'inp': True, 'out': False},
             'FLOWFR': {'code': 'FLOWFR', 'file': 'mgt', 'inp': True, 'out': False},
             'DDRAIN': {'code': 'DDRAIN', 'file': 'mgt', 'inp': True, 'out': False},
             'TDRAIN': {'code': 'TDRAIN', 'file': 'mgt', 'inp': True, 'out': False},
             'GDRAIN': {'code': 'GDRAIN', 'file': 'mgt', 'inp': True, 'out': False},
             'NROT': {'code': 'NROT', 'file': 'mgt', 'inp': True, 'out': False},
             'NBYR': {'code': 'NBYR', 'file': 'file.cio', 'inp': True, 'out': False},
             'IYR': {'code': 'IYR', 'file': 'file.cio', 'inp': True, 'out': False},
             'IDAF': {'code': 'IDAF', 'file': 'file.cio', 'inp': True, 'out': False},
             'IDAL': {'code': 'IDAL', 'file': 'file.cio', 'inp': True, 'out': False},
             'IGEN': {'code': 'IGEN', 'file': 'file.cio', 'inp': True, 'out': False},
             'PCPSIM': {'code': 'PCPSIM', 'file': 'file.cio', 'inp': True, 'out': False},
             'IDT': {'code': 'IDT', 'file': 'file.cio', 'inp': True, 'out': False},
             'IDIST': {'code': 'IDIST', 'file': 'file.cio', 'inp': True, 'out': False},
             'REXP': {'code': 'REXP', 'file': 'file.cio', 'inp': True, 'out': False},
             'NRGAGE': {'code': 'NRGAGE', 'file': 'file.cio', 'inp': True, 'out': False},
             'NRTOT': {'code': 'NRTOT', 'file': 'file.cio', 'inp': True, 'out': False},
             'NRGFIL': {'code': 'NRGFIL', 'file': 'file.cio', 'inp': True, 'out': False},
             'TMPSIM': {'code': 'TMPSIM', 'file': 'file.cio', 'inp': True, 'out': False},
             'NTGAGE': {'code': 'NTGAGE', 'file': 'file.cio', 'inp': True, 'out': False},
             'NTTOT': {'code': 'NTTOT', 'file': 'file.cio', 'inp': True, 'out': False},
             'NTGFIL': {'code': 'NTGFIL', 'file': 'file.cio', 'inp': True, 'out': False},
             'SLRSIM': {'code': 'SLRSIM', 'file': 'file.cio', 'inp': True, 'out': False},
             'NSTOT': {'code': 'NSTOT', 'file': 'file.cio', 'inp': True, 'out': False},
             'RHSIM': {'code': 'RHSIM', 'file': 'file.cio', 'inp': True, 'out': False},
             'NHTOT': {'code': 'NHTOT', 'file': 'file.cio', 'inp': True, 'out': False},
             'WINDSIM': {'code': 'WINDSIM', 'file': 'file.cio', 'inp': True, 'out': False},
             'NWTOT': {'code': 'NWTOT', 'file': 'file.cio', 'inp': True, 'out': False},
             'FCSTYR': {'code': 'FCSTYR', 'file': 'file.cio', 'inp': True, 'out': False},
             'FCSTDAY': {'code': 'FCSTDAY', 'file': 'file.cio', 'inp': True, 'out': False},
             'FCSTCYCLES': {'code': 'FCSTCYCLES', 'file': 'file.cio', 'inp': True, 'out': False},
             'SLRFILE': {'code': 'SLRFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'RHFILE': {'code': 'RHFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'WNDFILE': {'code': 'WNDFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'FCSTFILE': {'code': 'FCSTFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'BSNFILE': {'code': 'BSNFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'PLANTDB': {'code': 'PLANTDB', 'file': 'file.cio', 'inp': True, 'out': False},
             'TILLDB': {'code': 'TILLDB', 'file': 'file.cio', 'inp': True, 'out': False},
             'PESTDB': {'code': 'PESTDB', 'file': 'file.cio', 'inp': True, 'out': False},
             'FERTDB': {'code': 'FERTDB', 'file': 'file.cio', 'inp': True, 'out': False},
             'URBANDB': {'code': 'URBANDB', 'file': 'file.cio', 'inp': True, 'out': False},
             'ISPROJ': {'code': 'ISPROJ', 'file': 'file.cio', 'inp': True, 'out': False},
             'ICLB': {'code': 'ICLB', 'file': 'file.cio', 'inp': True, 'out': False},
             'CALFILE': {'code': 'CALFILE', 'file': 'file.cio', 'inp': True, 'out': False},
             'IPRINT': {'code': 'IPRINT', 'file': 'file.cio', 'inp': True, 'out': False},
             'NYSKIP': {'code': 'NYSKIP', 'file': 'file.cio', 'inp': True, 'out': False},
             'ILOG': {'code': 'ILOG', 'file': 'file.cio', 'inp': True, 'out': False},
             'IPRP': {'code': 'IPRP', 'file': 'file.cio', 'inp': True, 'out': False},
             'IPHR': {'code': 'IPHR', 'file': 'file.cio', 'inp': True, 'out': False},
             'ISTO': {'code': 'ISTO', 'file': 'file.cio', 'inp': True, 'out': False},
             'ISOL': {'code': 'ISOL', 'file': 'file.cio', 'inp': True, 'out': False},
             'I_SUBW': {'code': 'I_SUBW', 'file': 'file.cio', 'inp': True, 'out': False},
             'IA_B': {'code': 'IA_B', 'file': 'file.cio', 'inp': True, 'out': False},
             'IHUMUS': {'code': 'IHUMUS', 'file': 'file.cio', 'inp': True, 'out': False},
             'ITEMP': {'code': 'ITEMP', 'file': 'file.cio', 'inp': True, 'out': False},
             'ISNOW': {'code': 'ISNOW', 'file': 'file.cio', 'inp': True, 'out': False},
             'IMGT': {'code': 'IMGT', 'file': 'file.cio', 'inp': True, 'out': False},
             'IWTR': {'code': 'IWTR', 'file': 'file.cio', 'inp': True, 'out': False},
             'ICALEN': {'code': 'ICALEN', 'file': 'file.cio', 'inp': True, 'out': False},
             'CANMX': {'code': 'CANMX', 'file': 'hru', 'inp': True, 'out': False},
             'CF': {'code': 'CF', 'file': 'hru', 'inp': True, 'out': False},
             'CFDEC': {'code': 'CFDEC', 'file': 'hru', 'inp': True, 'out': False},
             'CFH': {'code': 'CFH', 'file': 'hru', 'inp': True, 'out': False},
             'DEP_IMP': {'code': 'DEP_IMP', 'file': 'hru', 'inp': True, 'out': False},
             'DIS_STREAM': {'code': 'DIS_STREAM', 'file': 'hru', 'inp': True, 'out': False},
             'EPCO_hru': {'code': 'EPCO_hru', 'file': 'hru', 'inp': True, 'out': False},
             'ERORGN': {'code': 'ERORGN', 'file': 'hru', 'inp': True, 'out': False},
             'ERORGP': {'code': 'ERORGP', 'file': 'hru', 'inp': True, 'out': False},
             'ESCO_hru': {'code': 'ESCO_hru', 'file': 'hru', 'inp': True, 'out': False},
             'EVPOT': {'code': 'EVPOT', 'file': 'hru', 'inp': True, 'out': False},
             'FLD_FR': {'code': 'FLD_FR', 'file': 'hru', 'inp': True, 'out': False},
             'HRU_FR': {'code': 'HRU_FR', 'file': 'hru', 'inp': True, 'out': False},
             'HRU_SLP': {'code': 'HRU_SLP', 'file': 'hru', 'inp': True, 'out': False},
             'LAT_SED': {'code': 'LAT_SED', 'file': 'hru', 'inp': True, 'out': False},
             'LAT_TTIME': {'code': 'LAT_TTIME', 'file': 'hru', 'inp': True, 'out': False},
             'N_LAG': {'code': 'N_LAG', 'file': 'hru', 'inp': True, 'out': False},
             'N_LN': {'code': 'N_LN', 'file': 'hru', 'inp': True, 'out': False},
             'N_LNCO': {'code': 'N_LNCO', 'file': 'hru', 'inp': True, 'out': False},
             'N_REDUC': {'code': 'N_REDUC', 'file': 'hru', 'inp': True, 'out': False},
             'ORGN_CON': {'code': 'ORGN_CON', 'file': 'hru', 'inp': True, 'out': False},
             'ORGP_CON': {'code': 'ORGP_CON', 'file': 'hru', 'inp': True, 'out': False},
             'OV_N': {'code': 'OV_N', 'file': 'hru', 'inp': True, 'out': False},
             'POT_FR': {'code': 'POT_FR', 'file': 'hru', 'inp': True, 'out': False},
             'POT_K': {'code': 'POT_K', 'file': 'hru', 'inp': True, 'out': False},
             'POT_NO3L': {'code': 'POT_NO3L', 'file': 'hru', 'inp': True, 'out': False},
             'POT_NSED': {'code': 'POT_NSED', 'file': 'hru', 'inp': True, 'out': False},
             'POT_SOLP': {'code': 'POT_SOLP', 'file': 'hru', 'inp': True, 'out': False},
             'POT_TILE': {'code': 'POT_TILE', 'file': 'hru', 'inp': True, 'out': False},
             'POT_VOL': {'code': 'POT_VOL', 'file': 'hru', 'inp': True, 'out': False},
             'POT_VOLX': {'code': 'POT_VOLX', 'file': 'hru', 'inp': True, 'out': False},
             'R2ADJ': {'code': 'R2ADJ', 'file': 'hru', 'inp': True, 'out': False},
             'RIP_FR': {'code': 'RIP_FR', 'file': 'hru', 'inp': True, 'out': False},
             'RSDIN': {'code': 'RSDIN', 'file': 'hru', 'inp': True, 'out': False},
             'SED_CON': {'code': 'SED_CON', 'file': 'hru', 'inp': True, 'out': False},
             'SLSOIL': {'code': 'SLSOIL', 'file': 'hru', 'inp': True, 'out': False},
             'SLSUBBSN': {'code': 'SLSUBBSN', 'file': 'hru', 'inp': True, 'out': False},
             'SOLN_CON': {'code': 'SOLN_CON', 'file': 'hru', 'inp': True, 'out': False},
             'SOLP_CON': {'code': 'SOLP_CON', 'file': 'hru', 'inp': True, 'out': False},
             'SURLAG_hru': {'code': 'SURLAG_hru', 'file': 'hru', 'inp': True, 'out': False},
             'PND_FR': {'code': 'PND_FR', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_PSA': {'code': 'PND_PSA', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_PVOL': {'code': 'PND_PVOL', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_ESA': {'code': 'PND_ESA', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_EVOL': {'code': 'PND_EVOL', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_VOL': {'code': 'PND_VOL', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_SED': {'code': 'PND_SED', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_NSED': {'code': 'PND_NSED', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_K': {'code': 'PND_K', 'file': 'pnd', 'inp': True, 'out': False},
             'IFLOD1': {'code': 'IFLOD1', 'file': 'pnd', 'inp': True, 'out': False},
             'IFLOD2': {'code': 'IFLOD2', 'file': 'pnd', 'inp': True, 'out': False},
             'NDTARG': {'code': 'NDTARG', 'file': 'pnd', 'inp': True, 'out': False},
             'PSETLP1': {'code': 'PSETLP1', 'file': 'pnd', 'inp': True, 'out': False},
             'PSETLP2': {'code': 'PSETLP2', 'file': 'pnd', 'inp': True, 'out': False},
             'NSETLP1': {'code': 'NSETLP1', 'file': 'pnd', 'inp': True, 'out': False},
             'NSETLP2': {'code': 'NSETLP2', 'file': 'pnd', 'inp': True, 'out': False},
             'CHLAP': {'code': 'CHLAP', 'file': 'pnd', 'inp': True, 'out': False},
             'SECCIP': {'code': 'SECCIP', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_NO3': {'code': 'PND_NO3', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_SOLP': {'code': 'PND_SOLP', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_ORGN': {'code': 'PND_ORGN', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_ORGP': {'code': 'PND_ORGP', 'file': 'pnd', 'inp': True, 'out': False},
             'PND_D50': {'code': 'PND_D50', 'file': 'pnd', 'inp': True, 'out': False},
             'IPND1': {'code': 'IPND1', 'file': 'pnd', 'inp': True, 'out': False},
             'IPND2': {'code': 'IPND2', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_FR': {'code': 'WET_FR', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_NSA': {'code': 'WET_NSA', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_NVOL': {'code': 'WET_NVOL', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_MXSA': {'code': 'WET_MXSA', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_MXVOL': {'code': 'WET_MXVOL', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_VOL': {'code': 'WET_VOL', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_SED': {'code': 'WET_SED', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_NSED': {'code': 'WET_NSED', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_K': {'code': 'WET_K', 'file': 'pnd', 'inp': True, 'out': False},
             'PSETLW1': {'code': 'PSETLW1', 'file': 'pnd', 'inp': True, 'out': False},
             'PSETLW2': {'code': 'PSETLW2', 'file': 'pnd', 'inp': True, 'out': False},
             'NSETLW1': {'code': 'NSETLW1', 'file': 'pnd', 'inp': True, 'out': False},
             'NSETLW2': {'code': 'NSETLW2', 'file': 'pnd', 'inp': True, 'out': False},
             'CHLAW': {'code': 'CHLAW', 'file': 'pnd', 'inp': True, 'out': False},
             'SECCIW': {'code': 'SECCIW', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_NO3': {'code': 'WET_NO3', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_SOLP': {'code': 'WET_SOLP', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_ORGN': {'code': 'WET_ORGN', 'file': 'pnd', 'inp': True, 'out': False},
             'WET_ORGP': {'code': 'WET_ORGP', 'file': 'pnd', 'inp': True, 'out': False},
             'PNDEVCOEFF': {'code': 'PNDEVCOEFF', 'file': 'pnd', 'inp': True, 'out': False},
             'WETEVCOEFF': {'code': 'WETEVCOEFF', 'file': 'pnd', 'inp': True, 'out': False},
             'CHW2': {'code': 'CHW2', 'file': 'rte', 'inp': True, 'out': False},
             'CHD': {'code': 'CHD', 'file': 'rte', 'inp': True, 'out': False},
             'CH_S2': {'code': 'CH_S2', 'file': 'rte', 'inp': True, 'out': False},
             'CH_L2': {'code': 'CH_L2', 'file': 'rte', 'inp': True, 'out': False},
             'CH_N2': {'code': 'CH_N2', 'file': 'rte', 'inp': True, 'out': False},
             'CH_K2': {'code': 'CH_K2', 'file': 'rte', 'inp': True, 'out': False},
             'CH_COV1': {'code': 'CH_COV1', 'file': 'rte', 'inp': True, 'out': False},
             'CH_COV2': {'code': 'CH_COV2', 'file': 'rte', 'inp': True, 'out': False},
             'CH_WDR': {'code': 'CH_WDR', 'file': 'rte', 'inp': True, 'out': False},
             'ALPHA_BNK': {'code': 'ALPHA_BNK', 'file': 'rte', 'inp': True, 'out': False},
             'ICANAL': {'code': 'ICANAL', 'file': 'rte', 'inp': True, 'out': False},
             'CH_ONCO': {'code': 'CH_ONCO', 'file': 'rte', 'inp': True, 'out': False},
             'CH_OPCO': {'code': 'CH_OPCO', 'file': 'rte', 'inp': True, 'out': False},
             'CH_SIDE': {'code': 'CH_SIDE', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BNK_BD': {'code': 'CH_BNK_BD', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BED_BD': {'code': 'CH_BED_BD', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BNK_KD': {'code': 'CH_BNK_KD', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BED_KD': {'code': 'CH_BED_KD', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BNK_D50': {'code': 'CH_BNK_D50', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BED_D50': {'code': 'CH_BED_D50', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BNK_TC': {'code': 'CH_BNK_TC', 'file': 'rte', 'inp': True, 'out': False},
             'CH_BED_TC': {'code': 'CH_BED_TC', 'file': 'rte', 'inp': True, 'out': False},
             'CH_EQN': {'code': 'CH_EQN', 'file': 'rte', 'inp': True, 'out': False},
             'SHALLST': {'code': 'SHALLST', 'file': 'gw', 'inp': True, 'out': False},
             'DEEPST': {'code': 'DEEPST', 'file': 'gw', 'inp': True, 'out': False},
             'GW_DELAY': {'code': 'GW_DELAY', 'file': 'gw', 'inp': True, 'out': False},
             'ALPHA_BF': {'code': 'ALPHA_BF', 'file': 'gw', 'inp': True, 'out': False},
             'GWQMN': {'code': 'GWQMN', 'file': 'gw', 'inp': True, 'out': False},
             'GW_REVAP': {'code': 'GW_REVAP', 'file': 'gw', 'inp': True, 'out': False},
             'REVAPMN': {'code': 'REVAPMN', 'file': 'gw', 'inp': True, 'out': False},
             'RCHRG_DP': {'code': 'RCHRG_DP', 'file': 'gw', 'inp': True, 'out': False},
             'GWHT': {'code': 'GWHT', 'file': 'gw', 'inp': True, 'out': False},
             'GW_SPYLD': {'code': 'GW_SPYLD', 'file': 'gw', 'inp': True, 'out': False},
             'SHALLST_N': {'code': 'SHALLST_N', 'file': 'gw', 'inp': True, 'out': False},
             'GWSOLP': {'code': 'GWSOLP', 'file': 'gw', 'inp': True, 'out': False},
             'HLIFE_NGW': {'code': 'HLIFE_NGW', 'file': 'gw', 'inp': True, 'out': False},
             'LAT_ORGN': {'code': 'LAT_ORGN', 'file': 'gw', 'inp': True, 'out': False},
             'LAT_ORGP': {'code': 'LAT_ORGP', 'file': 'gw', 'inp': True, 'out': False},
             'ALPHA_BF_D': {'code': 'ALPHA_BF_D', 'file': 'gw', 'inp': True, 'out': False},
             'RE': {'code': 'RE', 'file': 'sdr', 'inp': True, 'out': False},
             'SDRAIN': {'code': 'SDRAIN', 'file': 'sdr', 'inp': True, 'out': False},
             'DRAIN_CO': {'code': 'DRAIN_CO', 'file': 'sdr', 'inp': True, 'out': False},
             'PC': {'code': 'PC', 'file': 'sdr', 'inp': True, 'out': False},
             'LATKSATF': {'code': 'LATKSATF', 'file': 'sdr', 'inp': True, 'out': False},
             'ISEP_TYP': {'code': 'ISEP_TYP', 'file': 'sep', 'inp': True, 'out': False},
             'ISEP_IYR': {'code': 'ISEP_IYR', 'file': 'sep', 'inp': True, 'out': False},
             'ISEP_OPT': {'code': 'ISEP_OPT', 'file': 'sep', 'inp': True, 'out': False},
             'SEP_CAP': {'code': 'SEP_CAP', 'file': 'sep', 'inp': True, 'out': False},
             'BZ_AREA': {'code': 'BZ_AREA', 'file': 'sep', 'inp': True, 'out': False},
             'ISEP_TFAIL': {'code': 'ISEP_TFAIL', 'file': 'sep', 'inp': True, 'out': False},
             'BZ_Z': {'code': 'BZ_Z', 'file': 'sep', 'inp': True, 'out': False},
             'BZ_THK': {'code': 'BZ_THK', 'file': 'sep', 'inp': True, 'out': False},
             'SEP_STRM_DIST': {'code': 'SEP_STRM_DIST', 'file': 'sep', 'inp': True, 'out': False},
             'SEP_DEN': {'code': 'SEP_DEN', 'file': 'sep', 'inp': True, 'out': False},
             'BIO_BD': {'code': 'BIO_BD', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_BOD_DC': {'code': 'COEFF_BOD_DC', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_BOD_CONV': {'code': 'COEFF_BOD_CONV', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_FC1': {'code': 'COEFF_FC1', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_FC2': {'code': 'COEFF_FC2', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_FECAL': {'code': 'COEFF_FECAL', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_PLQ': {'code': 'COEFF_PLQ', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_MRT': {'code': 'COEFF_MRT', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_RSP': {'code': 'COEFF_RSP', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_SLG1': {'code': 'COEFF_SLG1', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_SLG2': {'code': 'COEFF_SLG2', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_NITR': {'code': 'COEFF_NITR', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_DENITR': {'code': 'COEFF_DENITR', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_COEFF_PDISTRB': {'code': 'COEFF_COEFF_PDISTRB', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_PSORPMAX': {'code': 'COEFF_PSORPMAX', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_SOLPSLP': {'code': 'COEFF_SOLPSLP', 'file': 'sep', 'inp': True, 'out': False},
             'COEFF_SOLPINTC': {'code': 'COEFF_SOLPINTC', 'file': 'sep', 'inp': True, 'out': False},
             'Soil Name': {'code': 'Soil Name', 'file': 'sol', 'inp': True, 'out': False},
             'Soil Hydrologic Group': {'code': 'Soil Hydrologic Group', 'file': 'sol', 'inp': True, 'out': False},
             'Maximum rooting depth(mm)': {'code': 'Maximum rooting depth(mm)', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Porosity fraction from which anions are excluded': {
                 'code': 'Porosity fraction from which anions are excluded', 'file': 'sol', 'inp': True, 'out': False},
             'Crack volume potential of soil': {'code': 'Crack volume potential of soil', 'file': 'sol', 'inp': True,
                                                'out': False},
             'Texture 1': {'code': 'Texture 1', 'file': 'sol', 'inp': True, 'out': False},
             'Depth                [mm]': {'code': 'Depth                [mm]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Bulk Density Moist [g/cc]': {'code': 'Bulk Density Moist [g/cc]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Ave. AW Incl. Rock Frag': {'code': 'Ave. AW Incl. Rock Frag', 'file': 'sol', 'inp': True, 'out': False},
             'Ksat. (est.)      [mm/hr]': {'code': 'Ksat. (est.)      [mm/hr]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Organic Carbon [weight %]': {'code': 'Organic Carbon [weight %]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Clay           [weight %]': {'code': 'Clay           [weight %]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Silt           [weight %]': {'code': 'Silt           [weight %]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Sand           [weight %]': {'code': 'Sand           [weight %]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Rock Fragments   [vol. %]': {'code': 'Rock Fragments   [vol. %]', 'file': 'sol', 'inp': True,
                                           'out': False},
             'Soil Albedo (Moist)': {'code': 'Soil Albedo (Moist)', 'file': 'sol', 'inp': True, 'out': False},
             'Erosion K': {'code': 'Erosion K', 'file': 'sol', 'inp': True, 'out': False},
             'Salinity (EC, Form 5)': {'code': 'Salinity (EC, Form 5)', 'file': 'sol', 'inp': True, 'out': False},
             'Soil pH': {'code': 'Soil pH', 'file': 'sol', 'inp': True, 'out': False},
             'Soil CACO3': {'code': 'Soil CACO3', 'file': 'sol', 'inp': True, 'out': False},
             }

# A dictionary to get the variable name from its SWAT code.
codes_to_vars = dict([(v['code'], k) for (k, v) in vars_SWAT.items()])

# A list containing only SWAT input variable codes
SWAT_input_vars = [v['code'] for v in vars_SWAT.values() if v['inp']]

# A list containing only SWAT output variable codes
SWAT_output_vars = [v['code'] for v in vars_SWAT.values() if v['out']]

# A list containing file.cio variables
file_cio_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'file.cio']
SWAT_mgt_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'mgt']
SWAT_bsn_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'bsn']
SWAT_hru_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'hru']
SWAT_pnd_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'pnd']
SWAT_rte_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'rte']
SWAT_gw_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'gw']
SWAT_sdr_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'sdr']
SWAT_sep_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'sep']
SWAT_sol_file_vars = [v['code'] for v in vars_SWAT.values() if v['file'] == 'sol']


def read_reach_output(textinout_path, nsub):
    """
    This function reads output of last day from output.rch file

    :param output_rch_path: Path of the output.rch file in the TextInOut folder
    :type output_rch_path: str

    :param nsub: Number of subbasins
    :type nsub: int

    :return: A dictionary of output values, where each key is a variable name (SWAT variable code format) and each
      value is a numpy array with axis as subbasins
    :rtype: dict[np.array]
    """
    output_rch_path = os.path.join(textinout_path, "output.rch")

    dict_data = dict([(k, np.empty((nsub,))) for k in SWAT_output_vars])

    with open(output_rch_path, 'r') as output_rch:
        output_rch_content = output_rch.readlines()

    # For every subbasin in the project
    for sb_no in range(nsub):
        row_index = sb_no - nsub  # Skipping first 9 header rows
        sb_output = output_rch_content[row_index]
        split_output = sb_output.split()

        dict_data['RCH'][sb_no] = split_output[1]
        dict_data['GIS'][sb_no] = split_output[2]
        dict_data['MON'][sb_no] = split_output[3]
        dict_data['AREA'][sb_no] = split_output[4]
        dict_data['FLOW_IN'][sb_no] = split_output[5]
        dict_data['FLOW_OUT'][sb_no] = split_output[6]
        dict_data['EVAP'][sb_no] = split_output[7]
        dict_data['TLOSS'][sb_no] = split_output[8]
        dict_data['SED_IN'][sb_no] = split_output[9]
        dict_data['SED_OUT'][sb_no] = split_output[10]
        dict_data['SEDCONC'][sb_no] = split_output[11]
        dict_data['ORGN_IN'][sb_no] = split_output[12]
        dict_data['ORGN_OUT'][sb_no] = split_output[13]
        dict_data['ORGP_IN'][sb_no] = split_output[14]
        dict_data['ORGP_OUT'][sb_no] = split_output[15]
        dict_data['NO3_IN'][sb_no] = split_output[16]
        dict_data['NO3_OUT'][sb_no] = split_output[17]
        dict_data['NH4_IN'][sb_no] = split_output[18]
        dict_data['NH4_OUT'][sb_no] = split_output[19]
        dict_data['NO2_IN'][sb_no] = split_output[20]
        dict_data['NO2_OUT'][sb_no] = split_output[21]
        dict_data['MINP_IN'][sb_no] = split_output[22]
        dict_data['MINP_OUT'][sb_no] = split_output[23]
        dict_data['ALGAE_IN'][sb_no] = split_output[24]
        dict_data['ALGAE_OUT'][sb_no] = split_output[25]
        dict_data['CBOD_IN'][sb_no] = split_output[26]
        dict_data['CBOD_OUT'][sb_no] = split_output[27]
        dict_data['DISOX_IN'][sb_no] = split_output[28]
        dict_data['DISOX_OUT'][sb_no] = split_output[29]
        dict_data['SOLPST_IN'][sb_no] = split_output[30]
        dict_data['SOLPST_OUT'][sb_no] = split_output[31]
        dict_data['SORPST_IN'][sb_no] = split_output[32]
        dict_data['SORPST_OUT'][sb_no] = split_output[33]
        dict_data['REACTPST'][sb_no] = split_output[34]
        dict_data['VOLPST'][sb_no] = split_output[35]
        dict_data['SETTLPST'][sb_no] = split_output[36]
        dict_data['RESUSP_PST'][sb_no] = split_output[37]
        dict_data['DIFFUSEPST'][sb_no] = split_output[38]
        dict_data['REACBEDPST'][sb_no] = split_output[39]
        dict_data['BURYPST'][sb_no] = split_output[40]
        dict_data['BED_PST'][sb_no] = split_output[41]
        dict_data['BACTP_OUT'][sb_no] = split_output[42]
        dict_data['BACTLP_OUT'][sb_no] = split_output[43]
        dict_data['CMETAL#1'][sb_no] = split_output[44]
        dict_data['CMETAL#2'][sb_no] = split_output[45]
        dict_data['CMETAL#3'][sb_no] = split_output[46]
        dict_data['TOT_N'][sb_no] = split_output[47]
        dict_data['TOT_P'][sb_no] = split_output[48]
        dict_data['NO3CONC'][sb_no] = split_output[49]

    return dict_data


def read_bsn_file(textinout_path):
    bsn_file_path = os.path.join(textinout_path, "basins.bsn")

    bsn_params = dict([(k, np.empty((1,))) for k in SWAT_bsn_vars])

    with open(bsn_file_path, 'r') as basins_bsn:

        for line in basins_bsn:

            if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                value_text = line.split("|")[0].strip()

                if float(value_text) == int(float(value_text)):

                    if len(str(int(float(value_text)))) == len(value_text):
                        value_num = int(value_text)
                    else:
                        value_num = float(value_text)

                else:
                    value_num = float(value_text)

                code = line.split("|")[1].split(":")[0].strip()

                bsn_params[code] = value_num

    return bsn_params


def write_bsn_file(textinout_path, variables):
    """
    This function writes the updated variable values in the basin.bsn file

    :param textinout_path: Path to textinout folder where basin.bsn file is there
    :type str
    :param variables: A dictionary of updated variables
    :type dict
    :return: None
    """

    bsn_file_path = os.path.join(textinout_path, "basins.bsn")

    new_file_content = list()

    with open(bsn_file_path, 'r') as basin_bsn:
        basin_bsn_content = basin_bsn.readlines()

        for line_no in range(len(basin_bsn_content)):

            line = basin_bsn_content[line_no]

            if line.split("|")[0].strip().replace('.', '', 1).isdigit():
                code = line.split("|")[1].split(":")[0].strip()
                new_line = " " * 12 + str(variables[code]["val"]) + "    | " + line.split("|")[1]
            else:
                new_line = line

            new_file_content.append(new_line)

    with open(bsn_file_path, 'w') as file_cio:
        for line in new_file_content:
            file_cio.write(line)


def read_file_cio(textinout_path):
    """
    This function reads the "file.cio" and stores the values of
    the parameters in dictionary

    :param textinout_path:
    :type str
    :return: file_cio_data
    :type dictionary
    """

    file_cio_path = os.path.join(textinout_path, "file.cio")
    file_cio_data = dict([(k, np.empty((1,))) for k in file_cio_vars])

    with open(file_cio_path, 'r') as file_cio:

        for line in file_cio:
            if line.split("|")[0].strip().replace('.', '', 1).isdigit():
                value_text = line.split("|")[0].strip()

                if float(value_text) == int(float(value_text)):
                    value_num = int(value_text)
                else:
                    value_num = float(value_text)

                code = line.split("|")[1].split(":")[0].strip()
                file_cio_data[code] = value_num

    return file_cio_data


def write_file_cio(textinout_path, variables):
    # Path to the file.cio file (in textinout folder)
    file_cio_path = os.path.join(textinout_path, "file.cio")

    # A list to store the changed content of "file.cio"
    new_file_content = list()

    with open(file_cio_path, 'r') as file_cio:
        file_cio_content = file_cio.readlines()

        for line_no in range(len(file_cio_content)):

            line = file_cio_content[line_no]

            if line.split("|")[0].strip().replace('.', '', 1).isdigit():
                code = line.split("|")[1].split(":")[0].strip()
                new_line = " " * 15 + str(variables[code]["val"]) + "   | " + line.split("|")[1]
            else:
                new_line = line

            new_file_content.append(new_line)

    with open(file_cio_path, 'w') as file_cio:
        for line in new_file_content:
            file_cio.write(line)


def read_hru_details(textinout_path):
    """
    :param textinout_path:
    :return:
    """
    dict_hru_params = dict()

    hru_file_path = os.path.join(textinout_path, "HRULandUseSoilsReport.txt")

    with open(hru_file_path, 'r') as hru_file:
        # Skip first four rows
        for skip in range(4):
            hru_file.readline()

        # Read number of sub-basins in the next line
        line = hru_file.readline()
        if line.split()[2] == "HRUs:":
            no_hru = int(line.split(":")[1].strip())
            dict_hru_params['no_hru'] = no_hru

        # Read number of sub-basins in the next line
        line = hru_file.readline()
        if line.split()[2] == "Subbasins:":
            no_sub = int(line.split(":")[1].strip())
            dict_hru_params['no_sub'] = no_sub

        # Skipping next 4 rows
        for skip in range(4):
            hru_file.readline()

        # Read the area of basin in the next line
        line = hru_file.readline()
        basin_area = float(line.split()[1].strip())
        dict_hru_params['basin_area'] = basin_area

        # Skipping next 3 rows
        for skip in range(3):
            hru_file.readline()

        # Reading the different LULC classes in the watershed
        line = hru_file.readline()

        if line.split(":")[0].strip() == "LANDUSE":

            lulc_classes = list()

            line = hru_file.readline()
            while line != "\n":
                lulc_classes.append(line.split("-->")[1].split()[0])
                line = hru_file.readline()

        dict_hru_params['lulc_classes'] = lulc_classes

        # Reading the different SOIL classes in the watershed
        line = hru_file.readline()

        if line.split(":")[0].strip() == "SOILS":

            soil_types = list()

            line = hru_file.readline()
            while line != "\n":
                soil_types.append(line.split()[0].split()[0])
                line = hru_file.readline()

        dict_hru_params['soil_types'] = soil_types

        # Reading the different SLOPE classes in the watershed
        line = hru_file.readline()

        if line.split(":")[0].strip() == "SLOPE":

            slope_ranges = list()

            line = hru_file.readline()
            while line[0] != "_":
                slope_ranges.append(line.split()[0].split()[0])
                line = hru_file.readline()

        dict_hru_params['slope_ranges'] = slope_ranges

        # Variables to store number of HRUs in each sub-basin
        no_hru_in_sub = np.empty((no_sub,))

        lulc_hru = list()
        soil_hru = list()
        slope_hru = list()

        # Using "for" loop for each subbasins

        for sub in range(no_sub):

            count_HRUs = 0

            # Skipping rows to directly go to HRUs
            while line[0:4] != "HRUs":
                line = hru_file.readline()

            line = hru_file.readline()

            while line[0] != "_":
                count_HRUs += 1
                lulc_hru.append(line.split("-->")[1].split()[0].split("/")[0])
                soil_hru.append(line.split("-->")[1].split()[0].split("/")[1])
                slope_hru.append(line.split("-->")[1].split()[0].split("/")[2])
                line = hru_file.readline()

                if line == "":
                    break

            no_hru_in_sub[sub] = count_HRUs

        dict_hru_params['no_hru_in_sub'] = no_hru_in_sub
        dict_hru_params['lulc_hru'] = lulc_hru
        dict_hru_params['soil_hru'] = soil_hru
        dict_hru_params['slope_hru'] = slope_hru

    return dict_hru_params


def read_mgt_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .mgt files for every
    HRUs.
    The parameters are stored in a dictionary, which contaings numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    mgt_params = dict([(k, np.empty((nhru,))) for k in SWAT_mgt_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".mgt"

            # Full path of mgt file
            mgt_file_path = os.path.join(textinout_path, filename)

            # Reading the mgt file
            with open(mgt_file_path, 'r') as mgt_file:

                for line in mgt_file:

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        value_text = line.split("|")[0].strip()

                        if float(value_text) == int(float(value_text)):

                            if len(str(int(float(value_text)))) == len(value_text):
                                value_num = int(value_text)
                            else:
                                value_num = float(value_text)

                        else:
                            value_num = float(value_text)

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            mgt_params[code][hru_sr_no] = value_num

    return mgt_params


def write_mgt_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .mgt file parameters
    in the .mgt files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".mgt"

            # Full path of mgt file
            mgt_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(mgt_file_path, 'r') as mgt_file:
                mgt_file_content = mgt_file.readlines()

                for line_no in range(len(mgt_file_content)):

                    line = mgt_file_content[line_no]

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            new_line = " " * 12 + str(variables[code]["val"][hru_sr_no]) + "    | " + line.split("|")[1]

                        else:
                            new_line = line
                    else:
                        new_line = line

                    new_file_content.append(new_line)

            with open(mgt_file_path, 'w') as mgt_file:
                for line in new_file_content:
                    mgt_file.write(line)


def read_hru_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .hru files for every
    HRUs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    hru_file_params = dict([(k, np.empty((nhru,))) for k in SWAT_hru_file_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".hru"

            # Full path of mgt file
            hru_file_path = os.path.join(textinout_path, filename)

            # Reading the mgt file
            with open(hru_file_path, 'r') as hru_file:

                for line in hru_file:

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        value_text = line.split("|")[0].strip()

                        if float(value_text) == int(float(value_text)):

                            if len(str(int(float(value_text)))) == len(value_text):
                                value_num = int(value_text)
                            else:
                                value_num = float(value_text)

                        else:
                            value_num = float(value_text)

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()

                            if code in ["SURLAG", "ESCO", "EPCO"]:
                                code2 = code + "_hru"
                                hru_file_params[code2][hru_sr_no] = value_num
                            else:
                                hru_file_params[code][hru_sr_no] = value_num

    return hru_file_params


def write_hru_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .hru file parameters
    in the .mgt files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".hru"

            # Full path of mgt file
            hru_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(hru_file_path, 'r') as hru_file:
                hru_file_content = hru_file.readlines()

                for line_no in range(len(hru_file_content)):

                    line = hru_file_content[line_no]

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()

                            if code in ["SURLAG", "ESCO", "EPCO"]:
                                code2 = code + "_hru"
                                new_line = " " * 12 + str(variables[code2]["val"][hru_sr_no]) + "    | " + \
                                           line.split("|")[1]
                            else:
                                new_line = " " * 12 + str(variables[code]["val"][hru_sr_no]) + "    | " + \
                                           line.split("|")[1]

                        else:
                            new_line = line
                    else:
                        new_line = line

                    new_file_content.append(new_line)

            with open(hru_file_path, 'w') as hru_file:
                for line in new_file_content:
                    hru_file.write(line)


def read_pond_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .pnd files for every
    SBs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    nsub = hru_params["no_sub"]

    pnd_file_params = dict([(k, np.empty((nsub,))) for k in SWAT_pnd_file_vars])

    for sub in range(nsub):
        sub_no = sub + 1

        # Getting the filename for the mgt file based in subbasin and hru no.
        if sub_no < 10:
            sub_no_code = "0000" + str(sub_no)
        elif sub_no < 100:
            sub_no_code = "000" + str(sub_no)
        elif sub_no < 1000:
            sub_no_code = "00" + str(sub_no)
        elif sub_no < 10000:
            sub_no_code = "0" + str(sub_no)
        elif sub_no < 100000:
            sub_no_code = str(sub_no)
        else:
            print("Reduce number of sub_basins")

        filename = sub_no_code + "0000.pnd"

        # Full path of mgt file
        pnd_file_path = os.path.join(textinout_path, filename)

        # Reading the mgt file
        with open(pnd_file_path, 'r') as pnd_file:

            for line in pnd_file:

                if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                    value_text = line.split("|")[0].strip()

                    if float(value_text) == int(float(value_text)):

                        if len(str(int(float(value_text)))) == len(value_text):
                            value_num = int(value_text)
                        else:
                            value_num = float(value_text)

                    else:
                        value_num = float(value_text)

                    if len(line.split("|")) > 1:
                        code = line.split("|")[1].split(":")[0].strip()
                        pnd_file_params[code][sub] = value_num

    return pnd_file_params


def write_pnd_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .pnd file parameters
    in the .pnd files for every SB.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    nsub = hru_params["no_sub"]

    for sub in range(nsub):

        sub_no = sub + 1

        # Getting the filename for the mgt file based in subbasin and hru no.
        if sub_no < 10:
            sub_no_code = "0000" + str(sub_no)
        elif sub_no < 100:
            sub_no_code = "000" + str(sub_no)
        elif sub_no < 1000:
            sub_no_code = "00" + str(sub_no)
        elif sub_no < 10000:
            sub_no_code = "0" + str(sub_no)
        elif sub_no < 100000:
            sub_no_code = str(sub_no)
        else:
            print("Reduce number of sub_basins")

        filename = sub_no_code + "0000.pnd"

        # Full path of mgt file
        pnd_file_path = os.path.join(textinout_path, filename)
        new_file_content = list()

        with open(pnd_file_path, 'r') as pnd_file:

            pnd_file_content = pnd_file.readlines()

            for line_no in range(len(pnd_file_content)):

                line = pnd_file_content[line_no]

                if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                    if len(line.split("|")) > 1:
                        code = line.split("|")[1].split(":")[0].strip()
                        new_line = " " * 12 + str(variables[code]["val"][sub]) + "    | " + \
                                   line.split("|")[1]
                    else:
                        new_line = line
                else:
                    new_line = line

                new_file_content.append(new_line)

        with open(pnd_file_path, 'w') as pnd_file:
            for line in new_file_content:
                pnd_file.write(line)


def read_rte_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .pnd files for every
    SBs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    nsub = hru_params["no_sub"]

    rte_file_params = dict([(k, np.empty((nsub,))) for k in SWAT_rte_file_vars])

    for sub in range(nsub):
        sub_no = sub + 1

        # Getting the filename for the mgt file based in subbasin and hru no.
        if sub_no < 10:
            sub_no_code = "0000" + str(sub_no)
        elif sub_no < 100:
            sub_no_code = "000" + str(sub_no)
        elif sub_no < 1000:
            sub_no_code = "00" + str(sub_no)
        elif sub_no < 10000:
            sub_no_code = "0" + str(sub_no)
        elif sub_no < 100000:
            sub_no_code = str(sub_no)
        else:
            print("Reduce number of sub_basins")

        filename = sub_no_code + "0000.rte"

        # Full path of rte file
        rte_file_path = os.path.join(textinout_path, filename)

        # Reading the rte file
        with open(rte_file_path, 'r') as rte_file:

            for line in rte_file:

                if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                    value_text = line.split("|")[0].strip()

                    if float(value_text) == int(float(value_text)):

                        if len(str(int(float(value_text)))) == len(value_text):
                            value_num = int(value_text)
                        else:
                            value_num = float(value_text)

                    else:
                        value_num = float(value_text)

                    if len(line.split("|")) > 1:
                        code = line.split("|")[1].split(":")[0].strip()
                        rte_file_params[code][sub] = value_num

    return rte_file_params


def write_rte_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .rte file parameters
    in the .rte files for every SB.

    :param textinout_path: Path of textinout folder which contains .rte files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    nsub = hru_params["no_sub"]

    for sub in range(nsub):

        sub_no = sub + 1

        # Getting the filename for the mgt file based in subbasin and hru no.
        if sub_no < 10:
            sub_no_code = "0000" + str(sub_no)
        elif sub_no < 100:
            sub_no_code = "000" + str(sub_no)
        elif sub_no < 1000:
            sub_no_code = "00" + str(sub_no)
        elif sub_no < 10000:
            sub_no_code = "0" + str(sub_no)
        elif sub_no < 100000:
            sub_no_code = str(sub_no)
        else:
            print("Reduce number of sub_basins")

        filename = sub_no_code + "0000.rte"

        # Full path of mgt file
        rte_file_path = os.path.join(textinout_path, filename)
        new_file_content = list()

        with open(rte_file_path, 'r') as rte_file:

            rte_file_content = rte_file.readlines()

            for line_no in range(len(rte_file_content)):

                line = rte_file_content[line_no]

                if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                    if len(line.split("|")) > 1:
                        code = line.split("|")[1].split(":")[0].strip()
                        new_line = " " * 12 + str(variables[code]["val"][sub]) + "    | " + \
                                   line.split("|")[1]
                    else:
                        new_line = line
                else:
                    new_line = line

                new_file_content.append(new_line)

        with open(rte_file_path, 'w') as rte_file:
            for line in new_file_content:
                rte_file.write(line)


def read_gw_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .gw files for every
    HRUs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    gw_file_params = dict([(k, np.empty((nhru,))) for k in SWAT_gw_file_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".gw"

            # Full path of gw file
            gw_file_path = os.path.join(textinout_path, filename)

            # Reading the mgt file
            with open(gw_file_path, 'r') as gw_file:

                for line in gw_file:

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        value_text = line.split("|")[0].strip()

                        if float(value_text) == int(float(value_text)):

                            if len(str(int(float(value_text)))) == len(value_text):
                                value_num = int(value_text)
                            else:
                                value_num = float(value_text)

                        else:
                            value_num = float(value_text)

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            gw_file_params[code][hru_sr_no] = value_num

    return gw_file_params


def write_gw_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .gw file parameters
    in the .gw files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".gw"

            # Full path of mgt file
            gw_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(gw_file_path, 'r') as gw_file:
                gw_file_content = gw_file.readlines()

                for line_no in range(len(gw_file_content)):

                    line = gw_file_content[line_no]

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            new_line = " " * 12 + str(variables[code]["val"][hru_sr_no]) + "    | " + \
                                       line.split("|")[1]

                        else:
                            new_line = line
                    else:
                        new_line = line

                    new_file_content.append(new_line)

            with open(gw_file_path, 'w') as gw_file:
                for line in new_file_content:
                    gw_file.write(line)


def read_sdr_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .sdr files for every
    HRUs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    sdr_file_params = dict([(k, np.empty((nhru,))) for k in SWAT_sdr_file_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sdr"

            # Full path of gw file
            sdr_file_path = os.path.join(textinout_path, filename)

            # Reading the mgt file
            with open(sdr_file_path, 'r') as sdr_file:

                for line in sdr_file:

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        value_text = line.split("|")[0].strip()

                        if float(value_text) == int(float(value_text)):

                            if len(str(int(float(value_text)))) == len(value_text):
                                value_num = int(value_text)
                            else:
                                value_num = float(value_text)

                        else:
                            value_num = float(value_text)

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            sdr_file_params[code][hru_sr_no] = value_num

    return sdr_file_params


def write_sdr_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .sdr file parameters
    in the .sdr files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sdr"

            # Full path of mgt file
            sdr_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(sdr_file_path, 'r') as sdr_file:
                sdr_file_content = sdr_file.readlines()

                for line_no in range(len(sdr_file_content)):

                    line = sdr_file_content[line_no]

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            new_line = " " * 12 + str(variables[code]["val"][hru_sr_no]) + "    | " + \
                                       line.split("|")[1]

                        else:
                            new_line = line
                    else:
                        new_line = line

                    new_file_content.append(new_line)

            with open(sdr_file_path, 'w') as sdr_file:
                for line in new_file_content:
                    sdr_file.write(line)


def read_sep_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .sep files for every
    HRUs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    sep_file_params = dict([(k, np.empty((nhru,))) for k in SWAT_sep_file_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sep"

            # Full path of gw file
            sep_file_path = os.path.join(textinout_path, filename)

            # Reading the mgt file
            with open(sep_file_path, 'r') as sep_file:

                for line in sep_file:

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        value_text = line.split("|")[0].strip()

                        if float(value_text) == int(float(value_text)):

                            if len(str(int(float(value_text)))) == len(value_text):
                                value_num = int(value_text)
                            else:
                                value_num = float(value_text)

                        else:
                            value_num = float(value_text)

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            sep_file_params[code][hru_sr_no] = value_num

    return sep_file_params


def write_sep_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .sep file parameters
    in the .sep files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sep"

            # Full path of mgt file
            sep_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(sep_file_path, 'r') as sep_file:
                sep_file_content = sep_file.readlines()

                for line_no in range(len(sep_file_content)):

                    line = sep_file_content[line_no]

                    if line.split("|")[0].strip().replace('.', '', 1).isdigit():

                        if len(line.split("|")) > 1:
                            code = line.split("|")[1].split(":")[0].strip()
                            new_line = " " * 12 + str(variables[code]["val"][hru_sr_no]) + "    | " + \
                                       line.split("|")[1]

                        else:
                            new_line = line
                    else:
                        new_line = line

                    new_file_content.append(new_line)

            with open(sep_file_path, 'w') as sep_file:
                for line in new_file_content:
                    sep_file.write(line)


def read_sol_file(textinout_path, hru_params):
    """
    This function reads the parameters values from the .sol files for every
    HRUs.
    The parameters are stored in a dictionary, which contains numpy array of
    dimesion [nhru,1]

    :param textinout_path:
    :param hru_params:
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]
    nhru = hru_params["no_hru"]

    sol_file_params = dict([(k, list()) for k in SWAT_sol_file_vars])

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sol"

            # Full path of sol file
            sol_file_path = os.path.join(textinout_path, filename)

            # Reading the sol file
            with open(sol_file_path, 'r') as sol_file:

                lines = sol_file.readlines()

                line_no = 1

                while not lines[line_no].strip() == "":

                    line = lines[line_no]

                    code = line.split(":")[0].strip()
                    value_text = line.split(":")[1].strip()

                    if not " " in line.split(":")[1].strip():

                        if not line.split(":")[1].strip().isnumeric():
                            value_num = value_text

                        else:
                            if float(value_text) == int(float(value_text)):

                                if len(str(int(float(value_text)))) == len(value_text):
                                    value_num = int(value_text)
                                else:
                                    value_num = float(value_text)

                            else:
                                value_num = float(value_text)
                    else:
                        value_text = value_text.split(" ")[0].strip()

                        if not line.split(":")[1].strip().isnumeric():
                            value_num = value_text

                        else:
                            if float(value_text) == int(float(value_text)):

                                if len(str(int(float(value_text)))) == len(value_text):
                                    value_num = int(value_text)
                                else:
                                    value_num = float(value_text)

                            else:
                                value_num = float(value_text)

                    sol_file_params[code].append(value_num)
                    line_no += 1

    return sol_file_params



def write_sol_file(textinout_path, variables, hru_params):
    """
    This function writes the updated values of the .sol file parameters
    in the .sol files for every HRU.

    :param textinout_path: Path of textinout folder which contains .mgt files
    :type str
    :param variables: A dictionary containing updated parameters
    :type dict
    :param hru_params: A dictionary of HRU parameters
    :type dict
    :return:
    """
    no_hru_in_sub = hru_params["no_hru_in_sub"]
    nsub = hru_params["no_sub"]

    hru_sr_no = -1
    for sub in range(nsub):

        for hru_index in range(int(no_hru_in_sub[sub])):
            sub_no = sub + 1
            hru_no = hru_index + 1
            hru_sr_no += 1

            # Getting the filename for the mgt file based in subbasin and hru no.
            if sub_no < 10:
                sub_no_code = "0000" + str(sub_no)
            elif sub_no < 100:
                sub_no_code = "000" + str(sub_no)
            elif sub_no < 1000:
                sub_no_code = "00" + str(sub_no)
            elif sub_no < 10000:
                sub_no_code = "0" + str(sub_no)
            elif sub_no < 100000:
                sub_no_code = str(sub_no)
            else:
                print("Reduce number of sub_basins")

            if hru_no < 10:
                hru_no_code = "000" + str(hru_no)
            elif hru_no < 100:
                hru_no_code = "00" + str(hru_no)
            elif hru_no < 1000:
                hru_no_code = "0" + str(hru_no)
            elif hru_no < 10000:
                hru_no_code = str(hru_no)
            else:
                print("Reduce number of HRUs")

            filename = sub_no_code + hru_no_code + ".sol"

            # Full path of mgt file
            sol_file_path = os.path.join(textinout_path, filename)
            new_file_content = list()

            with open(sol_file_path, 'r') as sol_file:
                lines = sol_file.readlines()
                new_file_content.append(lines[0])
                line_no = 1

                while not lines[line_no].strip() == "":

                    line = lines[line_no]
                    code = line.split(":")[0].strip()
                    value_text = line.split(":")[1].strip()
                    new_value_text = variables[code]["val"][hru_sr_no]

                    if not " " in value_text:
                        new_line = line.split(":")[0] + ": " + new_value_text + "\n"
                    else:
                        value_text1 = value_text.split(" ")[0].strip()
                        value_text2 = value_text.split(" ")[-1].strip()

                        new_line = line.split(":")[0] + ":      " + new_value_text + "    " + value_text2 + "\n"

                    new_file_content.append(new_line)
                    line_no += 1

            with open(sol_file_path, 'w') as sol_file:
                for line in new_file_content:
                    sol_file.write(line)
