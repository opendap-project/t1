import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import netlist

NET = '''(export (version "E")
 (components
  (comp (ref "C1") (value "100 nF") (footprint "Capacitor_SMD:C_0402_1005Metric")
   (fields (field (name "Block") "blk.soc-power") (field (name "MPN") "GRM155"))
   (property (name "Sheetfile") (value "soc-power.kicad_sch"))
   (property (name "dnp"))
   (sheetpath (names "/SoC/Power/") (tstamps "/aaa/bbb/"))
   (tstamps "ccc"))
  (comp (ref "U1") (value "RK3566") (footprint "rockchip:FCCSP")
   (fields (field (name "Block") "blk.soc-ddr"))
   (sheetpath (names "/SoC/") (tstamps "/aaa/"))
   (tstamps "ddd")))
 (nets
  (net (code "1") (name "GND") (class "Default") (node (ref "C1") (pin "2")) (node (ref "U1") (pin "A1")))
  (net (code "2") (name "/SoC/vdd_cpu") (class "Default") (node (ref "C1") (pin "1")) (node (ref "U1") (pin "B2")))))
'''


def test_parse_components_fields_and_pins():
    nl = netlist.parse(NET)
    c = nl.components["C1"]
    assert c.block == "blk.soc-power"
    assert c.fields["MPN"] == "GRM155"
    assert c.path == "/aaa/bbb/ccc"
    assert c.sheet_file == "soc-power.kicad_sch"
    assert c.dnp is True
    assert c.pins == {"2": "GND", "1": "/SoC/vdd_cpu"}
    assert nl.components["U1"].dnp is False
    assert nl.nets["/SoC/vdd_cpu"] == [("C1", "1"), ("U1", "B2")]


def test_short_name():
    assert netlist.short("/SoC/vdd_cpu") == "vdd_cpu"
    assert netlist.short("GND") == "GND"


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
