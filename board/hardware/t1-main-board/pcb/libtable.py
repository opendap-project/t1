"""Resolve footprint library nicknames through the project's fp-lib-table (pure Python)."""

from __future__ import annotations

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
KICAD_SHARED = os.environ.get("KICAD_SHARED", "/Applications/KiCad/KiCad.app/Contents/SharedSupport")

_LIB = re.compile(r'\(lib \(name "([^"]+)"\)\(type "[^"]+"\)\(uri "([^"]+)"\)')


def _project_vars(project: str) -> dict:
    """The project's text variables (.kicad_pro), which KiCad also applies to library and model paths."""
    for pro in glob.glob(os.path.join(project, "*.kicad_pro")):
        with open(pro, encoding="utf-8") as fh:
            return dict(json.load(fh).get("text_variables", {}))
    return {}


def expand(uri: str, project: str = PROJECT) -> str:
    env = {
        "KIPRJMOD": project,
        "KICAD10_FOOTPRINT_DIR": os.environ.get("KICAD10_FOOTPRINT_DIR", os.path.join(KICAD_SHARED, "footprints")),
        "KICAD10_3DMODEL_DIR": os.environ.get("KICAD10_3DMODEL_DIR", os.path.join(KICAD_SHARED, "3dmodels")),
    }
    env.update(_project_vars(project))
    sub = lambda text: re.sub(r"\$\{([^}]+)\}", lambda m: env.get(m.group(1), m.group(0)), text)
    return os.path.normpath(sub(sub(uri)))  # twice: a project variable may itself use ${KIPRJMOD}


def read(path: str = os.path.join(PROJECT, "fp-lib-table"), project: str = PROJECT) -> dict:
    """Nickname -> absolute .pretty directory."""
    with open(path, encoding="utf-8") as fh:
        return {name: expand(uri, project) for name, uri in _LIB.findall(fh.read())}
