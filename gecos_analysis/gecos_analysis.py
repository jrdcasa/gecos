import argparse
import utils
import os
try:
    from gecos_analysis.gecos_outputgaussian import GaussianGecos
    from gecos_analysis.gecos_irspectra import GecosIRSpectra
    from gecos_analysis.gecos_exp_irspectra import GecosExpIRSpectra
except ModuleNotFoundError:
    from gecos_outputgaussian import GaussianGecos
    from gecos_irspectra import GecosIRSpectra
    from gecos_exp_irspectra import GecosExpIRSpectra


# =============================================================================
def parse_arguments():

    desc = """Energy QM analysis.
    This is part of the gecos library"""

    parser = argparse.ArgumentParser(description=desc)

    # Subparsers
    subparser = parser.add_subparsers(dest='command', required=True)
    energy = subparser.add_parser('energy')
    spectrum = subparser.add_parser('spectrum')
    exp_spectrum = subparser.add_parser('exp_spectrum')

    # Arguments for energy command
    energy.add_argument("-d", "--logfolder", dest="logfolder",
                        help="Folder containing the QM outputs.\n ",
                        action="store", required=True, default=None)

    energy.add_argument("-p", "--package", dest="qmpackage", choices=['g16'],
                        help="QM package to analyse (Default: Gaussian16).\n ",
                        action="store", required=False, default="g16")

    energy.add_argument("--log", dest="log",
                        help="Name of the file to write logs from this command",
                        action="store", required=False, default="gecos_energy_analysis.log")

    energy.add_argument("--vdw", dest="vdw", nargs="?",
                        help="Calculate close contacts of type Van der Waals\n"
                             "with delta (default = 0.25A) as:\n"
                             " d(at1-at2) < r_vdw(at1)+r_vdw(at2)+delta",
                        action="store", required=False, const=0.25, type=float)

    energy.add_argument("--hbonds", dest="hbonds", nargs='*',
                        help="Calculate hbonds in the molecule\n"
                             "using a distance and an angle.\n"
                             "Default arguments: 3.0 A and 140º\n",
                        metavar="hbond_dist_angstroms, hbond_angle_degrees",
                        action="store", required=False)

    energy.add_argument("--noignoreh", dest="noignoreh",
                        help="No ignore hydrogens for VdW Contacts",
                        action="store_true", required=False)

    energy.add_argument("--indxfile", dest="indxfile",
                        help="A file using the ndx format from "
                             "GROMACS to extract internal coordinates from the log"
                             "files.",
                        action="store", required=False, default=None)

    # Arguments for spectrum command
    spectrum.add_argument("-d", "--logfolder", dest="logfolder",
                          help="Folder containing the QM outputs.\n ",
                          action="store", required=True, default=None)

    spectrum.add_argument("-p", "--package", dest="qmpackage", choices=['g16'],
                          help="QM package to analyse (Default: Gaussian16).\n ",
                          action="store", required=False, default="g16")

    spectrum.add_argument("--log", dest="log",
                          help="Name of the file to write logs from this command",
                          action="store", required=False, default="gecos_spectrum_analysis.log")

    spectrum.add_argument("--scale", dest="scale",
                          help="Scale factor to apply to frequencies",
                          action="store", required=False, default=None, type=float)

    spectrum.add_argument("--start", dest="start",
                          help="Start frequency to fit the spectrum (cm^-1)",
                          action="store", required=False, default=0.0, type=float)

    spectrum.add_argument("--end", dest="end",
                          help="End frequency to fit the spectrum (cm^-1)",
                          action="store", required=False, default=4000.0, type=float)

    spectrum.add_argument("--npoints", dest="npoints",
                          help="Number of points to calculate the spectrum",
                          action="store", required=False, default=500, type=int)

    spectrum.add_argument("--width", dest="width",
                          help="Width used in the fit of the spectrum (cm^-1).",
                          action="store", required=False, default=10.0, type=float)

    spectrum.add_argument("--function", dest="function",
                          help="Function to plot the IR peaks", choices=["lorentzian", "lorentzian_gaussian"],
                          action="store", required=False, default="lorentzian")

    spectrum.add_argument("--avg", dest="averaged",
                          help="Calculate average spestrum",
                          choices=["boltzmann", "simple", "all"],
                          action="store", required=False, default=None)

    # Arguments for preprocesing experimental spectrum command.
    # Quantitative Comparison of Experimental and Computed IR-Spectra
    # Extracted from Ab Initio Molecular Dynamics
    # Beatriz von der Esch, Laurens D. M. Peters, Lena Sauerland, and Christian Ochsenfeld*
    # Cite This: J. Chem. Theory Comput. 2021, 17, 985−995
    exp_spectrum.add_argument("-f", "--file", dest="expspectrum",
                              help="Name of the file containing the experimental spectrum",
                              action="store", required=True)

    exp_spectrum.add_argument("--log", dest="log",
                              help="Name of the file to write logs from this command",
                              action="store", required=False, default="gecos_experimental_spectrum.log")

    args = parser.parse_args()

    if args.command == "spectrum":
        if not os.path.isdir(args.logfolder):
            print("\nERROR: Directory {} does not exist\n".format(args.logfolder))
            exit()

    # Default values for cutoffs in the hydrogen bond
    if args.command == "energy":
        if args.hbonds is not None:
            if len(args.hbonds) == 1:
                args.hbonds = [float(args.hbonds[0]), 140.0]
            elif len(args.hbonds) != 2:
                args.hbonds = [3.2, 140.0]
            else:
                args.hbonds = [float(args.hbonds[0]), float(args.hbonds[1])]

        if args.indxfile is not None:
            if not os.path.isfile(args.indxfile):
                print("ERROR: If you required extract internal coordinates a ndx file is needed.")
                print("ERROR: The file {} does not exist in the current directory.".format(args.indxfile))
                exit()

    return args


# =============================================================================
def main_app():

    # Parse arguments
    args = parse_arguments()

    # Setup log file
    log = utils.init_logger(
        "GaussianGecos",
        fileoutput=args.log,
        append=False, inscreen=True)

    # Print header
    utils.print_header_analysis(logger=log)

    if args.command in ["energy", "spectrum"]:
        if args.qmpackage == "g16":
            workdir = args.logfolder
            g16 = GaussianGecos(workdir, ext="log", logger=log)
            if args.command == "energy":
                g16.extract_energy()
                g16.extract_rmsd()
                g16.close_contacts(args)
                g16.moment_of_inertia()
                if args.indxfile is not None:
                    g16.extract_internalcoords(args)
                g16.write_to_log(workdir, generate_data_gnuplot=True)
            elif args.command == "spectrum":
                g16.extract_vibrational_ir()
                g16.write_vib_to_log(workdir, generate_data_gnuplot=True)
                vf = g16.getvibfreqs()
                vi = g16.getvibirs()
                temp = g16.gettemperature()
                deltag = g16.getdeltag()
                nspectra = len(vf)
                spectra_ir = GecosIRSpectra(nspectra, vf, vi, temp, deltag,
                                            scale=args.scale,
                                            start=args.start,
                                            end=args.end,
                                            npoints=args.npoints,
                                            width=args.width,
                                            function=args.function)
                spectra_ir.calculate_spectrum(avg=args.averaged)
    elif args.command in ["exp_spectrum"]:
        exp_spectra = GecosExpIRSpectra(args.expspectrum)

    else:
        exit()
    # else:
    #     exit()


# =============================================================================
if __name__ == "__main__":
    main_app()
