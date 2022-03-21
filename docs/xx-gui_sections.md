Reference Guide for the Graphical User Interface (GUI) for GeCos
===================================================

#### Molecule input

* **Molecule file (str)**: This field must contain a path to a reference molecule file in the local machine. The pdf file should have the "CONECT" section. Allowed formats are: *pdb*
* **Name server (str)**: The name or the IP of the remote server. The **localhost** keyword can be used to perform the calculations in local computer. The SLURM system must have installed and configured in either the local or remote servers.
* **Username**: The username to SSH connections with the server.
* **Key SSH file**: Passwordless RSA private key to connect with the server. (Note 1)
* **Encrypted passwd file**: Encrypted password using the library TODO. (Note 1)
* **SLURM partition**: Name of the partition to send the QM calculation.
* **SLURM partition master**: Name of the partition to send the driver (a bash script) which control the flow of QM calculations. (Note 2)