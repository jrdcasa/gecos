import subprocess
import sys
import os
import site
import glob
import logging
from datetime import datetime
from setuptools import setup


# Formatter for the logger
class CustomFormatter(logging.Formatter):

    """Logging Formatter to add colors and count warning / errors"""
    FORMATS = {
        logging.ERROR: "\n\tERROR: %(asctime)s: %(msg)s",
        logging.WARNING: "\n\tWARNING: %(msg)s",
        logging.DEBUG: "%(asctime)s: %(msg)s",
        "DEFAULT": "%(msg)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        date_fmt = '%d-%m-%Y %d %H:%M:%S'
        formatter = logging.Formatter(log_fmt, date_fmt)
        return formatter.format(record)


# Install packages from pip ==============================================================
def install_with_pip(pack, vers=None, log=None):

    # sys.executable gives the path of the python interpreter
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if vers is None:
        m = "{}: ** GECOS: Installing {}".format(now, pack)
        print(m) if log is None else log.info(m)
        # subprocess.call([sys.executable, "-m", "pip", "install", "{0}".format(pack)])
        p = subprocess.Popen([sys.executable, "-m", "pip", "install", "{0}".format(pack)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
    else:
        m = "{}: ** GECOS: Installing {}=={}".format(now, pack, vers)
        print(m) if log is None else log.info(m)
        # subprocess.call([sys.executable, "-m", "pip", "install", "{0}=={1}".format(pack, vers), " &>install.log"])
        p = subprocess.Popen([sys.executable, "-m", "pip", "install", "{0}=={1}".format(pack, vers)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()


# Install indigox-bond software ======================================================================================
def install_indigox_bond(log=None):

    """
    Installing the indigo-bond library if is not present in the python enviorement.
    """

    giturl = 'https://github.com/allison-group/indigo-bondorder.git'
    install_dir = 'thirdparty/indigo-bondorder'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    m = "\n\t\t COMPILING & INSTALLING INDIGO-BONDORDER PACKAGE\n\n"

    try:
        import indigox as ix
        m += "{}: ** GECOS: indigo-bondorder is already installed in your system. {}".format(now, giturl)
        print(m) if log is None else log.info(m)
    except ModuleNotFoundError:
        m += "{}: ** GECOS: indigo-bondorder is not installed in your system\n".format(now)
        m += "{}: ** GECOS: Installing from git... {}\n".format(now, giturl)
        print(m) if log is None else log.info(m)

        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            m = "================= ERROR INSTALL ================"
            m += "** GECOS: Cannot find CMake executable"
            m += "** GECOS: The installation is aborted"
            m += "================= ERROR INSTALL ================"
            print(m) if log is None else log.info(m)
            exit()

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
                    m = "================= ERROR INSTALL ================"
                    m += "** GECOS: The github repository for indigo-bondorder is not valid or not exists.!!!"
                    m += "** GECOS: giturl     : {}".format(giturl)
                    m += "** GECOS: install_dir: {}".format(install_dir)
                    m += "** GECOS: Indigo-bondorder cannot be installed"
                    m += "** GECOS: The installation is aborted"
                    m += "================= ERROR INSTALL ================"
                    print(m) if log is None else log.info(m)
                    exit()
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

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "{}\n".format(now)
        envdir = None
        for ipath in site.getsitepackages():
            g = glob.glob(os.path.join(ipath))
            if g:
                envdir = g
                break
        m += "envdir={}\n".format(envdir)
        m += "The *.so library has been installed in: {envdir}/indigox/" \
            "pyindigox.cpython-36m-x86_64-linux-gnu.so\n"
        m += "                                        {envdir}/indigox/__init__.py\n"
        print(m) if log is None else log.info(m)


# Install eigen library software ======================================================================================
def install_eigen(log=None):

    """
    Installing the eigen library which is needed in openbabel.
    """

    import git

    giturl = 'https://gitlab.com/libeigen/eigen.git'
    install_dir = 'thirdparty/eigen'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m = "\n\t\t COMPILING & INSTALLING EIGEN PACKAGE\n\n"
    print(m) if log is None else log.info(m)

    if not os.path.isdir("thirdparty/eigen/eigen_library/include"):
        m = "{}: ** GECOS: eigen is not installed in your system\n".format(now)
        m += "\t\thttp://eigen.tuxfamily.org/index.php?title=Main_Page\n"
        m += "\t\t** GECOS: Installing from git... {}\n".format(giturl)
        print(m) if log is None else log.info(m)
    else:
        m = "{}: ** GECOS: eigen is already installed in your system. " \
            "{}".format(now, "thirdparty/eigen/eigen_library/include")
        print(m) if log is None else log.info(m)

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        m = "================= ERROR INSTALL ================\n"
        m += "** GECOS: Cannot find CMake executable\n"
        m += "** GECOS: The installation is aborted\n"
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        exit()

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
                m = "================= ERROR INSTALL ================\n"
                m += "** GECOS: The github repository for openbabel is not valid or not exists.!!!\n"
                m += "** GECOS: giturl     : {}\n".format(giturl)
                m += "** GECOS: install_dir: {}\n".format(install_dir)
                m += "** GECOS: openbabel cannot be installed\n"
                m += "** GECOS: The installation is aborted\n"
                m += "================= ERROR INSTALL ================"
                print(m) if log is None else log.info(m)
                exit()
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

        m = "The eigen library has been installed in: thirdparty/eigen/eigen_library\n"
        print(m) if log is None else log.info(m)


# Install indigox-bond software ======================================================================================
def install_openbabel(log=None):

    """
    Installing the openbabel library if is not present in the python enviorement.
    """

    import git

    giturl = 'https://github.com/openbabel/openbabel.git'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m = "\n\t\t COMPILING & INSTALLING OPENBABEL PACKAGE\n\n"
    print(m) if log is None else log.info(m)

    # Look at thirdparty directory
    if not os.path.isdir("thirdparty"):
        os.makedirs("thirdparty")

    install_dir = 'thirdparty'
    eigen_dir = 'thirdparty/eigen/eigen_library/include/eigen3'
    fullpath_cmake = os.path.abspath(install_dir)
    fullpath_eigen = os.path.abspath(eigen_dir)

    if not os.path.isdir(fullpath_cmake+"/openbabel"):
        m = "{}: Downloading: ... openbabel-3-1-1(Wait for one minute)\n".format(now)
        print(m) if log is None else log.info(m)
        git.Repo.clone_from(giturl, fullpath_cmake+"/openbabel")
    else:
        m = "{}: ** GECOS: openbabel is already installed in your system. " \
            "{}".format(now, fullpath_cmake+"/openbabel")
        print(m) if log is None else log.info(m)

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        m = "================= ERROR INSTALL ================\n"
        m += "** GECOS: Cannot find CMake executable\n"
        m += "** GECOS: The installation is aborted\n"
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        exit()

    # Check if swig is installed in the system. This is needed in order to build the python bindings
    error = subprocess.call(["which", "swig"])
    if error != 0:
        m = "================= ERROR INSTALL ================\n"
        m += "** GECOS: Cannot find Swig executable\n"
        m += "** GECOS: Try to install swig in your system (Ubuntu: apt-get install swig)\n"
        m += "** GECOS: The installation is aborted\n"
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        exit()

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
    m = cmd
    print(m) if log is None else log.info(m)
    os.system(cmd)


# Install Dock RMSD software =========================================================================================
def install_dockrmsd(log=None):

    """
    Downloading, compiling and installing the DockRMSD software

    E.W. Bell, Y. Zhang. DockRMSD: an Open-Source Tool for Atom Mapping and
    RMSD calculation of Symmetric Molecules through Graph Isomorphism. Journal of Cheminformatics, 11:40 (2019)

    https://zhanglab.ccmb.med.umich.edu/DockRMSD/
    """

    import urllib.request

    install_dir = 'thirdparty/dock_rmsd'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m = "\n\t\t COMPILING & INSTALLING DockRMSD PACKAGE\n\n"

    if not os.path.isfile("thirdparty/dock_rmsd/dockrmsd.x"):
        m += "{}: ** GECOS: DockRMSD is not installed in your system\n".format(now)
        m += "\t\thttps://zhanglab.ccmb.med.umich.edu/DockRMSD/\n"
        m += "\t\t** GECOS: Installing from web... {}".format("https://zhanglab.ccmb.med.umich.edu/DockRMSD/\n")
        print(m) if log is None else log.info(m)
    else:
        m += "{}: ** GECOS: DockRMSD is already installed in your system\n".format(now)
        print(m) if log is None else log.info(m)
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

    # Creating the logger to install.log file ===================================
    logger = logging.getLogger(name="INSTALL_LOG")
    logger.setLevel(logging.DEBUG)
    h1 = logging.FileHandler("install.log", 'w')
    h1.setFormatter(CustomFormatter())
    # Output also in the screen
    logger.addHandler(h1)
    f1 = logging.StreamHandler()
    f1.setFormatter(CustomFormatter())
    logger.addHandler(f1)

    nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m1 = "\n\t\t Starting installation!!!! at {}\n\n".format(nowm)
    print(m1) if logger is None else logger.info(m1)

    # Print sys path ===================================
    m1 = "\t\t SYS PATH\n"
    for item in sys.path:
        m1 += item + "\n"
    m1 += "\n\t\t INSTALLING PIP PACKAGES\n"
    print(m1) if logger is None else logger.info(m1)

    # Install requirements ===================================
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    for ipack in required:
        try:
            pkg, version = ipack.split(">=")[0:2]
            if pkg[0] == "#":
                continue
            install_with_pip(pkg, vers=version, log=logger)
        except ValueError:
            pkg = ipack
            if pkg[0] == "#":
                continue
            install_with_pip(pkg, log=logger)

    import git

    # Install third-party software ===========================
    install_indigox_bond(log=logger)
    install_eigen(log=logger)
    install_openbabel(log=logger)
    install_dockrmsd(log=logger)

    # Setup Gecos ===========================================
    nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m1 = "\n\t\t RUNNING SETUP FROM SETUPTOOLS {}\n\n".format(nowm)
    print(m1) if logger is None else logger.info(m1)
    setup()

    nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m1 = "\n\t\t Installation Done!!!! at {}\n\n".format(nowm)
    print(m1) if logger is None else logger.info(m1)

