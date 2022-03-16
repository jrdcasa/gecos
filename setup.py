import subprocess
import sys
import os
import site
import glob
import logging
import urllib.request
import tarfile
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
def install_with_pip(pack, vers=None, log=None, namepkg=None):

    # Update pip
    p = subprocess.Popen([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    # sys.executable gives the path of the python interpreter
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if vers is None:
        m = "{}: ** {}: Installing {}".format(now, namepkg, pack)
        print(m) if log is None else log.info(m)
        # subprocess.call([sys.executable, "-m", "pip", "install", "{0}".format(pack)])
        p = subprocess.Popen([sys.executable, "-m", "pip", "install", "{0}".format(pack)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
    else:
        m = "{}: ** {}: Installing {}=={}".format(now, namepkg, pack, vers)
        print(m) if log is None else log.info(m)
        # subprocess.call([sys.executable, "-m", "pip", "install", "{0}=={1}".format(pack, vers), " &>install.log"])
        p = subprocess.Popen([sys.executable, "-m", "pip", "install", "{0}=={1}".format(pack, vers)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()


# Install indigox-bond software ======================================================================================
def install_indigox_bond(log=None, namepkg=None):
    """
    Installing the indigo-bond library if is not present in the python enviorement.
    """

    import git

    giturl = 'https://github.com/allison-group/indigo-bondorder.git'
    install_dir = 'thirdparty/indigo-bondorder'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    m = "\n\t\t ============== COMPILING & INSTALLING INDIGO-BONDORDER PACKAGE ==============\n\n"

    try:
        import indigox as ix
        m += "{}: ** {}: indigo-bondorder is already installed in your system. {}".format(now, namepkg, giturl)
        print(m) if log is None else log.info(m)
    except ModuleNotFoundError:
        m += "{}: ** {}: indigo-bondorder is not installed in your system\n".format(now, namepkg)
        m += "{}: ** {}: Installing from git... {}\n".format(now, namepkg, giturl)
        print(m) if log is None else log.info(m)

        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            m = "================= ERROR INSTALL ================\n"
            m += "** {}: Cannot find CMake executable needed \n".format(namepkg)
            m += "** {}: for indigo-bondorder compilation.\n".format(namepkg)
            m += "** {}: Instal CMake in your Linux\n".format(namepkg)
            m += "** {}: The installation is aborted\n".format(namepkg)
            m += "================= ERROR INSTALL ================"
            print(m) if log is None else log.info(m)
            exit()

        # Look at thirdparty directory
        if os.path.isdir("thirdparty"):
            pass
        else:
            os.makedirs("thirdparty")

        # Share data in indigox
        envdir = None
        for ipath in site.getsitepackages():
            g = glob.glob(os.path.join(ipath))
            if g:
                envdir = g[0]
                break

        fullpathlib_cmake = os.path.abspath(install_dir)
        fullpathdata_cmake = os.path.abspath(envdir+"/indigox/share")
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
                    m += "** {}: The github repository for indigo-bondorder is not valid or not exists.!!!\n".format(namepkg)
                    m += "** {}: giturl     : {}\n".format(namepkg, giturl)
                    m += "** {}: install_dir: {}\n".format(namepkg, install_dir)
                    m += "** {}: Indigo-bondorder cannot be installed\n".format(namepkg)
                    m += "** {}: The installation is aborted\n".format(namepkg)
                    m += "================= ERROR INSTALL ================"
                    print(m) if log is None else log.info(m)
                    exit()
                else:
                    pass

            subprocess.call(["rm", "-rf", "thirdparty/indigo-bondorder/build"])
            subprocess.call(["mkdir", "thirdparty/indigo-bondorder/build"])
            os.chdir("thirdparty/indigo-bondorder/build")
            cmake_arguments = ["-DCMAKE_INSTALL_PREFIX={}".format(fullpathlib_cmake),
                               "-DCMAKE_INSTALL_DATAROOTDIR={}".format(fullpathdata_cmake)]
            subprocess.check_call(["cmake", "{}".format(fullpathlib_cmake)] + cmake_arguments)
            subprocess.call("make")
            subprocess.call(["make", "install"])
            os.chdir("../../")
            subprocess.call(["tar", "cvfz", "indigo-bondorder.tar.gz", "indigo-bondorder"])
            subprocess.call(["rm", "-rf", "./indigo-bondorder"])
            os.chdir("..")

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "** {}: {}\n".format(namepkg, now)
        m += "** {}: envdir={}\n".format(namepkg, envdir)
        m += "** {}: The *.so library has been installed in: {}/indigox/" \
             "pyindigox.cpython-36m-x86_64-linux-gnu.so\n".format(namepkg, envdir)
        m += "                                        {envdir}/indigox/__init__.py\n"
        m += "** {}: Share library for indigo in {}\n".format(namepkg, envdir+"/indigox/share")
        print(m) if log is None else log.info(m)

    try:
        import indigox as ix
        m = "\n{}: ** {}: indigo-bondorder is correctly imported. {}".format(now, namepkg, giturl)
        print(m) if log is None else log.info(m)
    except (ModuleNotFoundError, ImportError):
        m = "================= ERROR INSTALL ================\n"
        m += "{}: ** {}: indigo-bondorder libray cannot be imported as:\n".format(now, namepkg)
        m += "{}: ** {}: \timport indigox as ix\n".format(now, namepkg)
        m += "{}: ** {}: Something wrong during compilation.\n".format(now, namepkg)
        m += "================= ERROR INSTALL ================"
        print(m) if log is None else log.info(m)
        exit()


# Install eigen library software ======================================================================================
def install_eigen(log=None, namepkg=None):

    """
    Installing the eigen library which is needed in openbabel.
    """

    import git

    # Version eigen 3.4.0 might not work. Error obtained compiler too old.
    # giturl = 'https://gitlab.com/libeigen/eigen.git'
    giturl = 'https://gitlab.com/libeigen/eigen/-/archive/3.3.9/eigen-3.3.9.tar.gz'
    tar_download_file = os.path.basename(giturl)
    install_dir = 'thirdparty/eigen-3.3.9'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    m = "\n\t\t ============== COMPILING & INSTALLING EIGEN PACKAGE ==============\n\n"
    print(m) if log is None else log.info(m)

    if not os.path.isdir(install_dir+"/eigen_library/include"):
        m = "{}: ** {}: eigen is not installed in your system\n".format(now, namepkg)
        m += "http://eigen.tuxfamily.org/index.php?title=Main_Page\n"
        m += "** {}: Installing version 3.3.9 from git... {}".format(namepkg, giturl)
        print(m) if log is None else log.info(m)

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        m = "================= ERROR INSTALL ================\n"
        m += "** {}: Cannot find CMake executable\n".format(namepkg)
        m += "** {}: The installation is aborted\n".format(namepkg)
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        sys.exit()

    # Look at thirdparty directory
    if os.path.isdir("thirdparty"):
        pass
    else:
        os.makedirs("thirdparty")

    fullpath_cmake = os.path.abspath(install_dir)

    # Check if exists a distribution of indigox in the thirdparty directory
    if os.path.isdir(install_dir+"/eigen_library/include"):
        m = "{}: ** {}: eigen_library seems to be already compiled in your system. " \
            "{}".format(now, namepkg, install_dir+"/eigen_library/include")
        print(m) if log is None else log.info(m)
    else:
        # git clone https://gitlab.com/libeigen/eigen.git
        try:
            # git.Repo.clone_from(giturl, install_dir)
            urllib.request.urlretrieve(giturl, "thirdparty/"+tar_download_file)
            tar = tarfile.open("thirdparty/"+tar_download_file)
            tar.extractall(path="./thirdparty/")
            tar.close()
        except (urllib.error.HTTPError, FileNotFoundError) as e:
            if not os.path.isdir(install_dir):
                m = "================= ERROR INSTALL ================\n"
                m += "** {}: The github repository for eigen is not valid or not exists.!!!\n".format(namepkg)
                m += "** {}: giturl     : {}\n".format(namepkg, giturl)
                m += "** {}: install_dir: {}\n".format(namepkg, install_dir)
                m += "** {}: eigen cannot be installed\n".format(namepkg)
                m += "** {}: The installation is aborted\n".format(namepkg)
                m += "================= ERROR INSTALL ================"
                print(m) if log is None else log.info(m)
                exit()
            else:
                pass

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "{}: ** {}: Compiling eigen\n".format(now, namepkg)
        print(m) if log is None else log.info(m)
        subprocess.call(["rm", "-rf", install_dir+"/build"])
        subprocess.call(["mkdir",  install_dir+"/build"])
        subprocess.call(["mkdir", install_dir+"/eigen_library"])
        os.chdir(install_dir+"/build")
        cmake_arguments1 = ["-DCMAKE_INSTALL_PREFIX={}".format(fullpath_cmake+"/eigen_library")]
        subprocess.check_call(["cmake", "{}", "{}".format(fullpath_cmake)]+cmake_arguments1)
        subprocess.call("make")
        subprocess.call(["make", "install"])
        os.chdir("../../")
        os.chdir("..")

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "{}: ** {}: The eigen library has been installed in: thirdparty/eigen/eigen_library\n".format(now, namepkg)
        print(m) if log is None else log.info(m)


# Install indigox-bond software ======================================================================================
def install_openbabel(log=None, namepkg=None):

    """
    Installing the openbabel library if is not present in the python enviorement.
    """

    import git

    giturl = 'https://github.com/openbabel/openbabel.git'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m = "\n\t\t ============== COMPILING & INSTALLING OPENBABEL PACKAGE ==============\n\n"
    print(m) if log is None else log.info(m)

    # Look at thirdparty directory
    if not os.path.isdir("thirdparty"):
        os.makedirs("thirdparty")

    install_dir = 'thirdparty'
    eigen_dir = 'thirdparty/eigen-3.3.9/eigen_library/include/eigen3'
    fullpath_cmake = os.path.abspath(install_dir)
    fullpath_eigen = os.path.abspath(eigen_dir)

    try:
        from openbabel import openbabel as ob
        m = "{}: ** {}: openbabel is already installed in your system. " \
            "{}".format(now, namepkg, fullpath_cmake + "/openbabel")
        print(m) if log is None else log.info(m)
    except (ModuleNotFoundError, ImportError) as e:
        if os.path.isdir(os.path.join(fullpath_cmake, "openbabel")):
            subprocess.call(["rm", "-rf", os.path.join(fullpath_cmake, "openbabel")])
        m = "{}: Downloading: ... openbabel-3-1-1(Wait for one minute)\n".format(now)
        print(m) if log is None else log.info(m)
        git.Repo.clone_from(giturl, fullpath_cmake + "/openbabel")

    try:
        subprocess.check_output(['cmake', '--version'])
    except OSError:
        m = "================= ERROR INSTALL ================\n"
        m += "** {}: Cannot find CMake executable\n".format(namepkg)
        m += "** {}: The installation is aborted\n".format(namepkg)
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        exit()

    # Check if swig is installed in the system. This is needed in order to build the python bindings
    error = subprocess.call(["which", "swig"])
    if error != 0:
        m = "================= ERROR INSTALL ================\n"
        m += "** {}: Cannot find Swig executable\n".format(namepkg)
        m += "** {}: Try to install swig in your system (Ubuntu: apt-get install swig)\n".format(namepkg)
        m += "** {}: The installation is aborted\n".format(namepkg)
        m += "================= ERROR INSTALL ================\n"
        print(m) if log is None else log.info(m)
        exit()

    if not os.path.isdir(fullpath_cmake+"/openbabel/build"):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "{}: ** {}: Compiling openbabel\n".format(now, namepkg)
        print(m) if log is None else log.info(m)
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
        subprocess.call(["rm", "-rf", "{}".format(os.path.join(dir_env_python, "openbabel"))])
        subprocess.call(["mv", "-f", "{}".format(dir_openbabel_installed), "{}".format(dir_env_python)])
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "{}: ** {}: Open babel move from {} to {}\n".format(now, namepkg,
                                                                os.path.join(dir_env_python, "openbabel"), dir_env_python)
        print(m) if log is None else log.info(m)

    try:
        from openbabel import openbabel as ob
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "\n{}: ** {}: openbabel is correctly imported. {}".format(now, namepkg, giturl)
        print(m) if log is None else log.info(m)
    except (ModuleNotFoundError, ImportError) as e:
        m = "================= ERROR INSTALL ================\n"
        m += "{}: ** {}: openbabel libray cannot be imported as:\n".format(now, namepkg)
        m += "{}: ** {}: \tfrom openbabel import openbabel as ob\n".format(now, namepkg)
        m += "{}: ** {}: Something wrong during compilation.\n".format(now, namepkg)
        m += "Error: {}\n".format(e)
        m += "================= ERROR INSTALL ================"
        print(m) if log is None else log.info(m)
        exit()


# Install Dock RMSD software =========================================================================================
def install_dockrmsd(log=None, namepkg=None):

    """
    Downloading, compiling and installing the DockRMSD software

    E.W. Bell, Y. Zhang. DockRMSD: an Open-Source Tool for Atom Mapping and
    RMSD calculation of Symmetric Molecules through Graph Isomorphism. Journal of Cheminformatics, 11:40 (2019)

    https://zhanglab.ccmb.med.umich.edu/DockRMSD/
    """

    import urllib.request

    install_dir = 'thirdparty/dock_rmsd'

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m = "\n\t\t ============== COMPILING & INSTALLING DockRMSD PACKAGE ==============\n\n"

    if not os.path.isfile("thirdparty/dock_rmsd/dockrmsd.x"):
        m += "{}: ** {}: DockRMSD is not installed in your system\n".format(now, namepkg)
        m += "\t\thttps://zhanglab.ccmb.med.umich.edu/DockRMSD/\n"
        m += "\t\t** {}: Installing from web... {}".format(namepkg, "https://zhanglab.ccmb.med.umich.edu/DockRMSD/\n")

        print(m) if log is None else log.info(m)
    else:
        m += "{}: ** {}: DockRMSD is already installed in your system\n".format(now, namepkg)
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

    # Wheel can be needed for install
    try:
        import wheel
    except ModuleNotFoundError:
        nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        m = "Install wheel in your system\n"
        m = "================= ERROR INSTALL ================\n"
        m += "{}: ** {}: wheel libray cannot be imported as:\n".format(nowm, "GECOS")
        m += "{}: ** {}: \timport wheel\n".format(nowm, "GECOS")
        m += "{}: ** {}: Install wheel in your system:\n".format(nowm, "GECOS")
        m += "{}: ** {}: \tpython -m pip install wheel\n".format(nowm, "GECOS")
        m += "================= ERROR INSTALL ================"
        print(m) if logger is None else logger.info(m)
        exit()

    # Print sys path ===================================
    m1 = "\t\t ============== SYS PATH ==============\n"
    for item in sys.path:
        m1 += item + "\n"
    m1 += "\n\t\t ============== INSTALLING PIP PACKAGES ==============\n"
    print(m1) if logger is None else logger.info(m1)

    # Install requirements ===================================
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    for ipack in required:
        try:
            pkg, version = ipack.split(">=")[0:2]
            if pkg[0] == "#":
                continue
            install_with_pip(pkg, vers=version, log=logger, namepkg="GECOS")
        except ValueError:
            pkg = ipack
            if pkg[0] == "#":
                continue
            install_with_pip(pkg, log=logger, namepkg="GECOS")

    # Install third-party software ===========================
    import git
    install_indigox_bond(log=logger, namepkg="GECOS")
    install_eigen(log=logger, namepkg="GECOS")
    install_openbabel(log=logger, namepkg="GECOS")
    install_dockrmsd(log=logger, namepkg="GECOS")

    # Setup Gecos ===========================================
    nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m1 = "\n\t\t ============== RUNNING SETUP FROM SETUPTOOLS {} ==============\n\n".format(nowm)
    print(m1) if logger is None else logger.info(m1)
    setup()

    nowm = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m1 = "\n\t\t Installation Done!!!! at {}\n\n".format(nowm)
    print(m1) if logger is None else logger.info(m1)

