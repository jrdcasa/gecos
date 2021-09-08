Gecos_rdkit
-----------
**Overview**
============

This class is used to generate conformers from a molecule using the RdKit library.

The following formats have been checked to work:

    * PDB from Materials Studio works if the atom types and formal charges are correctly assigned in MS.
    * MOL2 from Materials Studio does not work. MOL2 generated with Gaussian view works.
    * PDB and MOL2 files generated with openbabel seems to work. 
    * SDF 

Anyway, the user must assign correctly the atom types and formal charges. Hydrogens must be in the input file.
See ``Tutorial: Input file formats for Gecos_Rdkit`` to know how to see if the file is correct. In the case, that the structure has any problem, a solution is try to change the format with openbabel. 

**Attributes**
==============

    * ``mol_rdkit`` (Mol) : `Molecule class <https://rdkit.org/docs/source/rdkit.Chem.rdchem.html?highlight=mol#rdkit.Chem.rdchem.Mol>`_ from rdkit.
    * ``_logger`` (logger) : Logger to send the output generated in this class.
    * ``_charge`` (int) : Charge of the molecule.
    * ``_bond_list`` (list) : Bond list [[1,2], [2,3], ...]. The pair in each bond is ordered. 
    * ``_elements`` (dict) : A dictionary. {1:'C', 2:'H', ...} 
    * ``_atom_formal_charges`` (list) : Formal charge for each atom [0.0, 0.0, -1.0, 1.0, ...] 
    * ``_edmol`` (EditableMol) : `Editable Molecule <https://rdkit.org/docs/source/rdkit.Chem.rdchem.html?highlight=editablemol#rdkit.Chem.rdchem.EditableMol>`_ from rdkit.

**API**
=======

.. autoclass:: gecos.gecos_rdkit.GecosRdkit
    :members:
    :show-inheritance:
    :private-members:
    :special-members: __init__

