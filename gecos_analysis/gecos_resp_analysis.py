# import glob
import os.path
# from collections import defaultdict
# import numpy as np
# import pandas as pd
from openbabel import openbabel as ob
from utils.resp_files_pyresp_server import system_config, project_config


class GecosRespAnalysis:

    """
    This class is use to analyze RESP calculations from PYRED server
    (https://upjv.q4md-forcefieldtools.org/REDServer-Development/).
    """

    # =========================================================================
    def __init__(self, gaussian_gecos_obj, is_prepareinputs, deltaenergythreshold):

        """
        Initialize the instance
        """

        self._isprepareinputs = is_prepareinputs
        self._deltaenergythreshold = deltaenergythreshold
        self._gaussian_gecos_obj = gaussian_gecos_obj

        if self._isprepareinputs:
            self._writepdb_forpyred_server()

    # =========================================================================
    def _writepdb_forpyred_server(self):

        print(self._gaussian_gecos_obj._df['DeltaEnergy(kcal/mol)'][0])
        print(self._gaussian_gecos_obj._df['DeltaEnergy(kcal/mol)'][1])

        with open(os.path.join("./", "Mol_red1.pdb"), 'w') as fpdb:
            for idx, item in enumerate(self._gaussian_gecos_obj._xyzlist):
                if self._gaussian_gecos_obj._df['DeltaEnergy(kcal/mol)'][idx] > self._deltaenergythreshold:
                    continue

                igeomxyz = item
                molref = ob.OBMol()
                obref = ob.OBConversion()
                obref.SetInAndOutFormats('xyz', 'pdb')
                obref.ReadString(molref, igeomxyz)
                namefileref = os.path.join("./", "tmp_resp.pdb")
                obref.WriteFile(molref, namefileref)

                line = "MODEL {}\n".format(idx+1)

                with open(namefileref, 'r') as fref:
                    linestmp = fref.readlines()
                    for iline in linestmp:
                        if iline.count("HETATM") != 0 or iline.count("ATOM") != 0:
                            line += iline
                line += "ENDMDL\n".format(idx+1)

                fpdb.writelines(line)

        with open("System.config", 'w') as fsys:
            fsys.writelines(system_config)

        with open("Project.config", 'w') as fsys:
            fsys.writelines(project_config)