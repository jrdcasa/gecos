import subprocess
import sys
import os
import site
from setuptools import setup, find_packages


# Install packages from pip ==============================================================
def install_with_pip(pack, vers=None):

    # sys.executable gives the path to the python interpreter
    if vers is None:
        print("** GECOS: Installing {}".format(pack))
        subprocess.call([sys.executable, "-m", "pip", "install", "{0}".format(pack)])
    else:
        print("** GECOS: Installing {}=={}".format(pack, vers))
        subprocess.call([sys.executable, "-m", "pip", "install", "{0}=={1}".format(pack, vers)])


# Install indigox-bond software ======================================================================================
def install_indigox_bond():

    """
    Installing the indigo-bond library if is not present in the python enviorement.
    """

    giturl = 'https://github.com/allison-group/indigo-bondorder.git'
    install_dir = 'thirdparty/indigo-bondorder'

    try:
        import indigox as ix
        print("** GECOS: indigo-bondorder is already installed in your system. {}".format(giturl))
    except ModuleNotFoundError:
        print("** GECOS: indigo-bondorder is not installed in your system")
        print("** GECOS: Installing from git... {}".format(giturl))

        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            print("================= ERROR INSTALL ================")
            print("** GECOS: Cannot find CMake executable")
            print("** GECOS: The installation is aborted")
            print("================= ERROR INSTALL ================")
            sys.exit()

        # Look at thirdparty directory
        if os.path.isdir("thirdparty"):
            pass
        else:
            os.makedirs("thirdparty")

        fullpath_cmake = os.path.abspath(install_dir)

        # Check if exists a distribution of indigox in the thirdparty directory
        # git clone https://github.com/allison-group/indigo-bondorder.git
        if os.path.isdir("thirdparty/indigo-bondorder"):
            pass
        else:
            try:
                git.Repo.clone_from(giturl, install_dir)
            except git.GitCommandError:
                if not os.path.isdir(install_dir):
                    print("================= ERROR INSTALL ================")
                    print("** GECOS: The github repository for indigo-bondorder is not valid or not exists.!!!")
                    print("** GECOS: giturl     : {}".format(giturl))
                    print("** GECOS: install_dir: {}".format(install_dir))
                    print("** GECOS: Indigo-bondorder cannot be installed")
                    print("** GECOS: The installation is aborted")
                    print("================= ERROR INSTALL ================")
                    sys.exit()
                else:
                    pass

            subprocess.call(["rm", "-rf", "thirdparty/indigo-bondorder/build"])
            subprocess.call(["mkdir", "thirdparty/indigo-bondorder/build"])
            os.chdir("thirdparty/indigo-bondorder/build")
            cmake_arguments = ["-DCMAKE_INSTALL_PREFIX={}".format(fullpath_cmake)]
            subprocess.check_call(["cmake", "{}".format(fullpath_cmake)]+cmake_arguments)
            subprocess.call("make")
            subprocess.call(["make", "install"])
            os.chdir("../../")
            subprocess.call(["tar", "cvfz", "indigo-bondorder.tar.gz", "indigo-bondorder"])
            subprocess.call(["rm", "-rf", "indigo-bondorder ./git"])
            os.chdir("..")

        print("The *.so library has been installed in: {envdir}/lib/python3.8/site-packages/indigox/"
              "pyindigox.cpython-36m-x86_64-linux-gnu.so")
        print("                                        {envdir}/lib/python3.8/site-packages/indigox/__init__.py")


# Install eigen library software ======================================================================================
def install_eigen():

    """
    Installing the eigen library which is needed in openbabel.
    """

    import git

    giturl = 'https://gitlab.com/libeigen/eigen.git'
    install_dir = 'thirdparty/eigen'

    if not os.path.isdir("thirdparty/eigen/eigen_library/include"):
        print("** GECOS: eigen is not installed in your system")
        print("http://eigen.tuxfamily.org/index.php?title=Main_Page")
        print("** GECOS: Installing from git... {}".format(giturl))

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        print("================= ERROR INSTALL ================")
        print("** GECOS: Cannot find CMake executable")
        print("** GECOS: The installation is aborted")
        print("================= ERROR INSTALL ================")
        sys.exit()

    # Look at thirdparty directory
    if os.path.isdir("thirdparty"):
        pass
    else:
        os.makedirs("thirdparty")

    fullpath_cmake = os.path.abspath(install_dir)

    # Check if exists a distribution of indigox in the thirdparty directory
    # git clone https://gitlab.com/libeigen/eigen.git
    if os.path.isdir("thirdparty/eigen/eigen_library/include"):
        pass
    else:
        try:
            git.Repo.clone_from(giturl, install_dir)
        except git.GitCommandError:
            if not os.path.isdir(install_dir):
                print("================= ERROR INSTALL ================")
                print("** GECOS: The github repository for openbabel is not valid or not exists.!!!")
                print("** GECOS: giturl     : {}".format(giturl))
                print("** GECOS: install_dir: {}".format(install_dir))
                print("** GECOS: openbabel cannot be installed")
                print("** GECOS: The installation is aborted")
                print("================= ERROR INSTALL ================")
                sys.exit()
            else:
                pass

        subprocess.call(["rm", "-rf", "thirdparty/eigen/build"])
        subprocess.call(["mkdir", "thirdparty/eigen/build"])
        subprocess.call(["mkdir", "thirdparty/eigen/eigen_library"])
        os.chdir("thirdparty/eigen/build")
        cmake_arguments1 = ["-DCMAKE_INSTALL_PREFIX={}".format(fullpath_cmake+"/eigen_library")]
        subprocess.check_call(["cmake", "{}", "{}".format(fullpath_cmake)]+cmake_arguments1)
        subprocess.call("make")
        subprocess.call(["make", "install"])
        os.chdir("../../")
        subprocess.call(["tar", "cvfz", "eigen.tar.gz", "eigen"])
        os.chdir("..")

        print("The eigen library has been installed in: thirdparty/eigen/eigen_library")


# Install indigox-bond software ======================================================================================
def install_openbabel():

    """
    Installing the openbabel library if is not present in the python enviorement.
    """

    import git

    giturl = 'https://github.com/openbabel/openbabel.git'
    # Look at thirdparty directory
    if not os.path.isdir("thirdparty"):
        os.makedirs("thirdparty")

    install_dir = 'thirdparty'
    eigen_dir = 'thirdparty/eigen/eigen_library/include/eigen3'
    fullpath_cmake = os.path.abspath(install_dir)
    fullpath_eigen = os.path.abspath(eigen_dir)

    if not os.path.isdir(fullpath_cmake+"/openbabel"):
        print("Downloading: ... openbabel-3-1-1(Wait for one minute)")
        git.Repo.clone_from(giturl, fullpath_cmake+"/openbabel")

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        print("================= ERROR INSTALL ================")
        print("** GECOS: Cannot find CMake executable")
        print("** GECOS: The installation is aborted")
        print("================= ERROR INSTALL ================")
        sys.exit()

    # Check if swig is installed in the system. This is needed in order to build the python bindings
    error = subprocess.call(["which", "swig"])
    if error != 0:
        print("================= ERROR INSTALL ================")
        print("** GECOS: Cannot find Swig executable")
        print("** GECOS: Try to install swig in your system (Ubuntu: apt-get install swig)")
        print("** GECOS: The installation is aborted")
        print("================= ERROR INSTALL ================")
        sys.exit()

    if not os.path.isdir(fullpath_cmake+"/openbabel/build"):

        subprocess.call(["rm", "-rf", "thirdparty/openbabel/build"])
        subprocess.call(["mkdir", "thirdparty/openbabel/build"])
        os.chdir("thirdparty/openbabel/build")
        cmake_arguments1 = ["-DCMAKE_INSTALL_PREFIX={}".format(fullpath_cmake+"/openbabel")]
        cmake_arguments2 = ["-DPYTHON_BINDINGS=ON"]
        cmake_arguments3 = ["-DRUN_SWIG=ON"]
        cmake_arguments4 = ["-DEIGEN3_INCLUDE_DIR={}".format(fullpath_eigen)]
        subprocess.check_call(["cmake", "{}", "{}".format(fullpath_cmake+"/openbabel")] +
                              cmake_arguments1+cmake_arguments2+cmake_arguments3+cmake_arguments4)
        subprocess.call(["make", "-j4"])
        subprocess.call(["make", "install"])
        os.chdir("../../")
        os.chdir("..")

    # Copy the library to the root site-engines of the python distribution
    dir_env_python = site.getsitepackages()[0]
    dir_openbabel_installed = fullpath_cmake+"/openbabel/lib/python3.8/site-packages/openbabel"
    cmd = 'cp -rf {} {}'.format(dir_openbabel_installed, dir_env_python)
    print(cmd)
    os.system(cmd)


# Install Dock RMSD software =========================================================================================
def install_dockrmsd():

    """
    Downloading, compiling and installing the DockRMSD software

    E.W. Bell, Y. Zhang. DockRMSD: an Open-Source Tool for Atom Mapping and
    RMSD calculation of Symmetric Molecules through Graph Isomorphism. Journal of Cheminformatics, 11:40 (2019)

    https://zhanglab.ccmb.med.umich.edu/DockRMSD/
    """

    import urllib.request

    install_dir = 'thirdparty/dock_rmsd'

    if not os.path.isfile("thirdparty/dock_rmsd/dockrmsd.x"):
        print("** GECOS: DockRMSD is not installed in your system")
        print("https://zhanglab.ccmb.med.umich.edu/DockRMSD/")
        print("** GECOS: Installing from web... {}".format("https://zhanglab.ccmb.med.umich.edu/DockRMSD/"))
    else:
        print("** GECOS: DockRMSD is already installed in your system")
        return True

    # Look at thirdparty directory
    if os.path.isdir("thirdparty"):
        pass
    else:
        os.makedirs("thirdparty")

    fullpath_cmake = os.path.abspath(install_dir)+"/"

    url1 = "https://zhanglab.ccmb.med.umich.edu/DockRMSD/DockRMSD.h"
    url2 = "https://zhanglab.ccmb.med.umich.edu/DockRMSD/DockRMSD.c"

    if not os.path.isdir(fullpath_cmake):
        os.mkdir(fullpath_cmake)
    urllib.request.urlretrieve(url1, fullpath_cmake+"DockRMSD.h")
    urllib.request.urlretrieve(url2, fullpath_cmake+"DockRMSD.c")

    subprocess.call(["gcc", fullpath_cmake+"DockRMSD.c", "-o", fullpath_cmake+"dockrmsd.x", "-lm", "-O3"])


# Main setup
if __name__ == '__main__':

    print(sys.path)

    # Install requirements ===================================
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    for ipack in required:
        try:
            pkg, version = ipack.split(">=")[0:2]
            if pkg[0] == "#":
                continue
            install_with_pip(pkg, version)
        except ValueError:
            pkg = ipack
            if pkg[0] == "#":
                continue
            install_with_pip(pkg)

    import git

    # Install third-party software ===========================
    install_indigox_bond()
    install_eigen()
    install_openbabel()
    install_dockrmsd()

    # Setup Gecos ===========================================
    setup()
