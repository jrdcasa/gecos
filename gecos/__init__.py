__version__ = "0.1"

import contextlib
from typing import Optional, List, TextIO

from gecos.gecos_rdkit import GecosRdkit
from gecos.gecos_pybabel import GecosPyBabel
from gecos.send_qm_conformers import send_qm_conformers, check_qm_jobs


def main(argv: Optional[List[str]] = None, stream: Optional[TextIO] = None) -> int:

    from gecos.gecos import main_gui_app

    with contextlib.ExitStack() as ctx:
        return main_gui_app()
