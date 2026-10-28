"""Read a KiCad 10 netlist (`kicad-cli sch export netlist --format kicadsexpr`).

Pure Python (3.9 or later, so KiCad's bundled Python runs it): no pcbnew import, so the reader
is tested with the system Python.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generator"))

import sexpr  # noqa: E402  (the generator's reader; Python 3.9 compatible)


@dataclass
class Component:
    ref: str
    value: str
    footprint: str                     # "Lib:Name"
    fields: dict = field(default_factory=dict)
    path: str = ""                     # KIID path: sheet tstamps + symbol tstamp
    sheet_names: str = ""
    sheet_file: str = ""
    dnp: bool = False
    pins: dict = field(default_factory=dict)   # pad number -> net name
    pin_info: dict = field(default_factory=dict)   # pad number -> (pin function, pin type), from the symbol

    @property
    def block(self) -> str:
        return self.fields.get("Block", "")

    @property
    def lib(self) -> str:
        return self.footprint.split(":", 1)[0]

    @property
    def fp_name(self) -> str:
        return self.footprint.split(":", 1)[1]

    @property
    def nets(self) -> set:
        return set(self.pins.values())


@dataclass
class Netlist:
    components: dict                   # ref -> Component
    nets: dict                         # net name -> list of (ref, pin)


def parse(text: str) -> Netlist:
    root = sexpr.parse(text)
    comps = {}
    for c in sexpr.kids(sexpr.kid(root, "components"), "comp"):
        ref = sexpr.val(c, "ref")
        fields = {}
        fl = sexpr.kid(c, "fields")
        if fl is not None:
            for f in sexpr.kids(fl, "field"):
                name = sexpr.val(f, "name")
                fields[name] = f[2] if len(f) > 2 else ""
        props = {}
        for p in sexpr.kids(c, "property"):
            props[sexpr.val(p, "name")] = sexpr.val(p, "value", "")
        for k in ("Sheetname", "Sheetfile"):
            if k in props:
                fields.setdefault(k, props[k])
        sp = sexpr.kid(c, "sheetpath")
        tstamps = sexpr.val(c, "tstamps", "")
        sheet_ts = sexpr.val(sp, "tstamps", "/") if sp is not None else "/"
        comps[ref] = Component(
            ref=ref,
            value=sexpr.val(c, "value", ""),
            footprint=sexpr.val(c, "footprint", ""),
            fields=fields,
            path=sheet_ts + tstamps,
            sheet_names=sexpr.val(sp, "names", "") if sp is not None else "",
            sheet_file=props.get("Sheetfile", ""),
            dnp="dnp" in props,
        )
    nets = {}
    for n in sexpr.kids(sexpr.kid(root, "nets"), "net"):
        name = sexpr.val(n, "name")
        nodes = []
        for nd in sexpr.kids(n, "node"):
            ref, pin = sexpr.val(nd, "ref"), sexpr.val(nd, "pin")
            nodes.append((ref, pin))
            if ref in comps:
                comps[ref].pins[pin] = name
                comps[ref].pin_info[pin] = (sexpr.val(nd, "pinfunction", ""), sexpr.val(nd, "pintype", ""))
        nets[name] = nodes
    return Netlist(comps, nets)


def load(path: str) -> Netlist:
    with open(path, encoding="utf-8") as fh:
        return parse(fh.read())


def short(net: str) -> str:
    """The net's own name without its sheet path (`/Sheet/VCC` -> `VCC`)."""
    return net.rsplit("/", 1)[-1]
