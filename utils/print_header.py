def print_header(logger=None):

    msg = """
        ***********************************************************************
                           Generation of Conformers (GeCoS)
                         -----------------------------------
                         
                                    Version 0.1
                         
                                  Dr. Javier Ramos
                          Macromolecular Physics Department
                    Instituto de Estructura de la Materia (IEM-CSIC)
                                   Madrid (Spain)
                                   
                GeCoS is an open-source python library to quickly generate
                conformers of small molecules or polymer segments 
                using RdKit and OpenBabel libraries. Once, the
                conformers are generated, QM optimizations and subsequent 
                clustering can be done.
                
                This software is distributed under the terms of the
                GNU General Public License v3.0 (GNU GPLv3). A copy of 
                the license (LICENSE.txt) is included with this distribution. 
                
        ***********************************************************************
                     
        """

    print(msg) if logger is None else logger.info(msg)
