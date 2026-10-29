"""Build test/t1-main-board-rules-test.kicad_pcb: one failing and one passing object per rule.

The product rules use net classes, named rule areas, footprint references,
footprint fields and pad fabrication properties, so this board extends
libs' kicad/ TestBoard (design-rules/tools/testboard.py, through the
submodule) with nets in those classes, rule areas, footprints with
courtyards, holes, zones, and rows of any height. Every value is read from
the rules file, so the board follows it.

Run with KiCad's Python, from any directory:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
      hardware/rules/test/make_test_board.py
Then check it with:
  python3 hardware/lib/opendap/kicad/design-rules/tools/check_drc.py \
      hardware/rules/test/t1-main-board-rules-test.kicad_pcb
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, "..", "t1-main-board.kicad_dru"))
sys.path.insert(0, os.path.normpath(
    os.path.join(HERE, "..", "..", "lib", "opendap", "kicad", "design-rules", "tools")))

import pcbnew  # noqa: E402
import testboard as tbm  # noqa: E402
from testboard import TEST_BOARD_IGNORED_CHECKS, TestBoard, mm, pt  # noqa: E402

NAME = "t1-main-board-rules-test"
P = "T1 "

# libs' kicad/ reader takes lengths only; the product rules also use angles
# (track_angle, in degrees without a unit: KiCad 10.0.7 rejects "90deg"),
# counts (via_count) and negative values. Read those as plain numbers.
_to_mm = tbm.to_mm


def _to_value(token):
    if token.startswith("-"):
        return -_to_value(token[1:])
    if re.fullmatch(r"[0-9.]+deg", token):
        return float(token[:-3])
    return _to_mm(token)


tbm.to_mm = _to_value

# Net classes used by the rules, with the netclasses.toml names.
CLASSES = ("PWR_BAT", "PWR_VSYS", "PWR_VBUS", "PWR_5V1",
           "PWR_AMP", "SW_NODE", "AUDIO_ANALOG", "AUDIO_REF", "MCLK_50SE",
           "USB2_90D", "USB3_90D", "MIPI_100D", "BAT_SENSE",
           "PWR_HAT5V", "DDR_50SE",
           "DDR_100D", "EMMC_SD_50SE", "I2S_50SE", "RF_50SE", "PWR_AUDIO",
           "ZONE_CORE", "ZONE_AUDIO", "ZONE_POWER", "ZONE_IO", "ZONE_RADIO", "ZONE_FACEPLATE",
           "ZONE_SHARED")

# Stackup v3: six copper layers. L1 = F.Cu, L2 = In1.Cu (L1's reference,
# cut under an L1 RF line), L3 = In2.Cu (RF ground of an L1 line), L4 =
# In3.Cu (the stripline), L5 = In4.Cu (full ground, cut under an L6 RF
# line), L6 = B.Cu.
L2, L3, L4, L5 = pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu
L6 = pcbnew.B_Cu

CRT = 0.6      # courtyard square of a generic small part
EDGE_W = 0.05  # Edge.Cuts line width (testboard): physical rules measure
               # from the line's outer edge, edge_clearance from its centre
# A footprint's courtyard is measured from the courtyard line's centre.
SPACE = 3.0    # extra row height, so no rule reaches into the next row
FAR = 4.0      # half-height of rows with test points and fiducials, which
               # keep up to 3.85 mm from any edge (the cutouts of other rows)


def assertion_bound(text, rule, prop, op):
    """The number a rule's assertion compares PROP with (OP '>=' or '<=')."""
    m = re.search(r'\(rule "' + re.escape(rule) + r'".*?\(constraint assertion "([^"]+)"',
                  text, re.S)
    if not m:
        raise KeyError(f"no assertion in rule '{rule}'")
    v = re.search(re.escape(prop) + r"\s*" + re.escape(op) + r"\s*([0-9.]+)mm", m.group(1))
    if not v:
        raise KeyError(f"rule '{rule}' has no {prop} {op} bound")
    return float(v.group(1))


class ProductTestBoard(TestBoard):
    """Rows of any height, nets in named classes, named rule areas, footprints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = tbm.TOP
        self.board_w = tbm.BOARD_W
        self._class_nets = {}
        self._prefix = {}
        self._gnd_taps = []
        with open(args[1], encoding="utf-8") as fh:
            self.text = fh.read()

    def class_net(self, netclass, shared=False):
        """A net in NETCLASS; with SHARED also in ZONE_SHARED (name suffix _ZS), so the zone
        rules leave it alone."""
        n = self._class_nets.get(netclass, 0) + 1
        self._class_nets[netclass] = n
        net = pcbnew.NETINFO_ITEM(self.board, f"{netclass}_{n}" + ("_ZS" if shared else ""))
        self.board.Add(net)
        return net

    def gnd_bus_x(self, x):
        """The GND bus beside the column of X (layer L5, In4.Cu, the full-layer
        ground, which takes GND): every GND object is joined to it, so the
        board has no unconnected GND items."""
        return (tbm.FAIL_X if x < tbm.PASS_EDGE else tbm.PASS_X) - 2.5

    def gnd_track(self, x2, y, width, layer):
        """A GND track on LAYER from the column's GND bus to X2, with the
        via that joins it to the bus."""
        bx = self.gnd_bus_x(x2)
        self._via(bx, y, 0.2, 0.45, net=self.gnd())
        self._gnd_taps.append((bx, y))
        return self._track(bx, y, x2, y, width, layer, self.gnd())

    def gnd(self):
        net = self.board.FindNet("GND")
        if net is None:
            net = pcbnew.NETINFO_ITEM(self.board, "GND")
            self.board.Add(net)
        return net

    def area(self, name, x1, y1, x2, y2, layers=None, no_fill=False):
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName(name)
        zone.SetDoNotAllowTracks(False)
        zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowZoneFills(no_fill)
        zone.SetDoNotAllowFootprints(False)
        if layers:
            ls = pcbnew.LSET()
            for layer in layers:
                ls.AddLayer(layer)
            zone.SetLayerSet(ls)
        else:
            zone.SetLayerSet(pcbnew.LSET.AllCuMask())
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            outline.Append(mm(x), mm(y))
        self.board.Add(zone)

    def add_row(self, name, height, builder, fires=1):
        self._label(tbm.LABEL_X, self.y, name)
        builder(tbm.FAIL_X, self.y, True)
        builder(tbm.PASS_X, self.y, False)
        self.expected_rules[name] = self.expected_rules.get(name, 0) + fires
        self.y += height
        self.row += 1

    def widen(self, x):
        self.board_w = max(self.board_w, x + 2.0)

    @staticmethod
    def _vd(limit, fail, delta):
        """Like _v, with a wider margin for checks KiCad measures coarser."""
        return limit - delta if fail else limit + delta

    # objects --------------------------------------------------------------

    def _via(self, x, y, drill, diameter, vtype=None, layers=None, net=None):
        # PCB-W-02: every via of the board has teardrops enabled.
        v = super()._via(x, y, drill, diameter, vtype, layers, net)
        v.SetTeardropsEnabled(True)
        return v

    def part(self, prefix, x, y, size=None, back=False, field=None):
        """A footprint with reference PREFIX<n>, centred at (x, y), with a
        square courtyard of SIZE (none if SIZE is None)."""
        n = self._prefix.get(prefix, 0) + 1
        self._prefix[prefix] = n
        fp = pcbnew.FOOTPRINT(self.board)
        fp.SetReference(f"{prefix}{n}")
        fp.SetValue("test")
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        fp.SetAttributes(pcbnew.FP_SMD | pcbnew.FP_BOARD_ONLY)
        fp.SetPosition(pt(x, y))
        if field:
            fp.SetField(*field)
        self.board.Add(fp)
        if size:
            sx, sy = size if isinstance(size, tuple) else (size, size)
            s = pcbnew.PCB_SHAPE(fp)
            s.SetShape(pcbnew.SHAPE_T_RECT)
            s.SetStart(pt(x - sx / 2, y - sy / 2))
            s.SetEnd(pt(x + sx / 2, y + sy / 2))
            s.SetLayer(pcbnew.B_CrtYd if back else pcbnew.F_CrtYd)
            s.SetWidth(mm(0.05))
            fp.Add(s)
        return fp

    def hole(self, x, y, drill, plated=False, pad=None, net=None):
        """A mounting hole H<n>: NPTH, or plated with a round pad."""
        fp = self.part("H", x, y)
        if plated:
            self._pad(fp, x, y, pad or drill + 0.6, kind="pth", drill=drill, net=net)
        else:
            self._pad(fp, x, y, drill, kind="npth", drill=drill)
        return fp

    def smd(self, prefix, x, y, size, net=None, prop=None):
        fp = self.part(prefix, x, y)
        pad = self._pad(fp, x, y, size, net=net if net is not None else self._net())
        if prop is not None:
            pad.SetProperty(prop)
        return pad

    def silk_line(self, x1, y1, x2, y2, width=0.15):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(x1, y1))
        s.SetEnd(pt(x2, y2))
        s.SetLayer(pcbnew.F_SilkS)
        s.SetWidth(mm(width))
        self.board.Add(s)

    def zone(self, net, points, min_width=0.05, layer=pcbnew.F_Cu):
        z = pcbnew.ZONE(self.board)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetMinThickness(mm(min_width))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        outline = z.Outline()
        outline.NewOutline()
        for x, y in points:
            outline.Append(mm(x), mm(y))
        self.board.Add(z)
        return z

    # fixtures ------------------------------------------------------------

    def width_row(self, name, layer, netclass=None, area=None):
        w = self.rule(name).value("track_width")
        height = max(tbm.ROW_H, w + 3.0)

        def build(x, y, fail):
            if area:
                self.area(area, x - 0.5, y - 0.5, x + 3.5, y + 0.5)
            net = self.class_net(netclass) if netclass else None
            cy = y + w / 2
            # A wide track's round ends reach w / 2 past its end points: the
            # failing one starts at the FAIL column, the passing one clears it.
            xs = x + w / 2 if fail else max(x, tbm.FAIL_X + 2 * w + 2.0)
            self._track(xs, cy, xs + 1, cy, self._v(w, fail), layer, net)
            self.widen(xs + 1 + w / 2)
        self.add_row(name, height, build)

    def clearance_row(self, name, width, net_a=None, net_b=None, area=None,
                      layer=pcbnew.F_Cu, width_b=None, gnd_b=False):
        """Two tracks; WIDTH for the first, WIDTH_B (default WIDTH) for the
        second; centre lines apart by the gap plus the two half widths."""
        gap = self.rule(name).value("clearance")
        wb = width if width_b is None else width_b
        height = max(tbm.ROW_H, gap + width + wb + 2.5)

        def build(x, y, fail):
            if area:
                self.area(area, x - 0.5, y - 0.5, x + 3.5, y + width + wb + gap + 0.5)
            g = self._v(gap, fail)
            a = self.class_net(net_a) if net_a else None
            self._track(x, y, x + 3, y, width, layer, a)
            yb = y + width / 2 + g + wb / 2
            if gnd_b:
                self.gnd_track(x + 3, yb, wb, layer)
            else:
                b = self.class_net(net_b) if net_b else None
                self._track(x, yb, x + 3, yb, wb, layer, b)
        self.add_row(name, height, build)

    def via_diameter_row(self, name, drill, vtype=None, layers=None):
        dia = self.rule(name).value("via_diameter")

        def build(x, y, fail):
            self._via(x, y, drill, self._v(dia, fail), vtype, layers)
        self.add_row(name, tbm.ROW_H, build)

    def edge_row(self, name, width, area=None):
        gap = self.rule(name).value("edge_clearance")

        def build(x, y, fail):
            if area:
                self.area(area, x - 1.5, y - 0.5, x + 2.5, y + 0.5 + gap + width + 0.5)
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            ty = y + 0.5 + self._v(gap, fail) + width / 2
            self._track(x - 1, ty, x + 2, ty, width, pcbnew.F_Cu)
        self.add_row(name, max(tbm.ROW_H, gap + 3.0), build)

    def foreign_track_row(self, name, area, allowed, width=0.2):
        """A track of another net in the area (FAIL), an allowed one (PASS)."""
        def build(x, y, fail):
            cy = y + width / 2
            self.area(area, x - 0.5, y - 0.5, x + 3.5, y + width + 0.5)
            net = self._net() if fail else allowed()
            self._track(x + width / 2, cy, x + 3 - width / 2, cy,
                        0.2 if fail else width, pcbnew.F_Cu, net)
        self.add_row(name, max(tbm.ROW_H, width + 2.5), build)

    # mounting holes (PCB-H)

    def hole_to_part_row(self, name, drill, prefix):
        """A mounting hole and a part's courtyard to its right."""
        gap = self.rule(name).value("physical_hole_clearance")

        def build(x, y, fail):
            hx = x + drill / 2
            self.hole(hx, y, drill)
            cx = hx + drill / 2 + self._v(gap, fail) + CRT / 2
            self.part(prefix, cx, y, CRT)
            self.widen(cx + CRT)
        self.add_row(name, drill + SPACE, build)

    def hole_to_bga_row(self, name, drill, pad):
        gap = self.rule(name).value("physical_hole_clearance")

        def build(x, y, fail):
            hx = x + drill / 2
            self.hole(hx, y, drill)
            fp = self.part("U", hx, y)  # no courtyard: only the pad is tested
            px = hx + drill / 2 + self._v(gap, fail) + pad / 2
            self._pad(fp, px, y, pad, bga=True, net=self._net())
            self.widen(px + pad)
        self.add_row(name, max(tbm.ROW_H, drill + 2.0), build)

    def hole_to_copper_row(self, name, drill, width, layer=pcbnew.F_Cu):
        gap = self.rule(name).value("hole_clearance")

        def build(x, y, fail):
            self.hole(x + drill / 2, y, drill)
            ty = y + drill / 2 + self._v(gap, fail) + width / 2
            self._track(x - 1, ty, x + drill + 1, ty, width, layer)
        self.add_row(name, max(tbm.ROW_H, drill + gap + 2.0), build)

    def plated_hole_net_row(self, name, drill):
        def build(x, y, fail):
            net = self._net() if fail else self.gnd()
            hx = x + drill / 2 + 0.3
            self.hole(hx, y, drill, plated=True, net=net)
            if not fail:  # join the GND bus on L5
                bx = self.gnd_bus_x(hx)
                self._gnd_taps.append((bx, y))
                self._track(bx, y, hx, y, 0.2, L5, net)
        self.add_row(name, max(tbm.ROW_H, drill + 2.0), build)

    def hole_to_edge_row(self, name, drill):
        gap = self.rule(name).value("physical_hole_clearance")

        def build(x, y, fail):
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            hy = y + 0.5 + EDGE_W / 2 + self._v(gap, fail) + drill / 2
            self.hole(x + 0.5, hy, drill)
        self.add_row(name, gap + drill + SPACE, build)

    # edges (PCB-E)

    def part_to_edge_row(self, name, prefix, area=None):
        gap = self.rule(name).value("physical_clearance")

        def build(x, y, fail):
            if area:
                self.area(area, x - 1.5, y - 0.5, x + 2.5, y + 0.5 + gap + CRT + 0.5)
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            cy = y + 0.5 + EDGE_W / 2 + self._v(gap, fail) + CRT / 2
            self.part(prefix, x + 0.5, cy, CRT)
        self.add_row(name, 2 * gap + CRT + SPACE, build)

    # assembly (PCB-D)

    def courtyard_row(self, name, field):
        gap = self.rule(name).value("courtyard_clearance")
        big = 2.0

        def build(x, y, fail):
            self.part("U", x + big / 2, y, big, field=field)
            # KiCad reports courtyard gaps rounded up by about 0.01 mm.
            cx = x + big + self._vd(gap, fail, 0.05) + CRT / 2
            self.part("C", cx, y, CRT)
            self.widen(cx + CRT)
        self.add_row(name, big + gap + SPACE, build)

    def pad_size_row(self, name, prop):
        low = assertion_bound(self.text, name, "A.Size_X", ">=")

        def build(x, y, fail):
            self.smd("FID" if "FIDUCIAL" in str(prop) else "TP", x, y,
                     self._v(low, fail), prop=prop)
        self.add_row(name, 2 * FAR, build)

    def pad_to_track_row(self, name, pad, prop=None, netclass=None, constraint="clearance",
                         prefix="R"):
        """An SMD pad and a track of another net below it."""
        gap = self.rule(name).value(constraint)

        def build(x, y, fail):
            net = self.class_net(netclass) if netclass else self._net()
            self.smd(prefix, x + pad / 2, y, pad, net=net, prop=prop)
            ty = y + pad / 2 + self._v(gap, fail) + 0.1
            self._track(x - 0.5, ty, x + pad + 0.5, ty, 0.2, pcbnew.F_Cu)
        self.add_row(name, max(tbm.ROW_H, pad + gap + 2.0, 2 * FAR + pad), build)

    def pad_to_pad_row(self, name, pad, prop_a, prop_b, prefix_b):
        """Two SMD pads of one net (so only the physical rule applies)."""
        gap = self.rule(name).value("physical_clearance")

        def build(x, y, fail):
            net = self._net()
            self.smd("TP", x + pad / 2, y, pad, net=net, prop=prop_a)
            bx = x + pad + self._v(gap, fail) + pad / 2
            self.smd(prefix_b, bx, y, pad, net=net, prop=prop_b)
            self._track(x + pad / 2, y, bx, y, 0.2, pcbnew.F_Cu, net)
            self.widen(bx + pad + FAR)
        self.add_row(name, 2 * FAR + pad, build)

    def own_pads_row(self, name, pad, netclass):
        """Two SMD pads of other nets, the first in NETCLASS, closer than the rule's clearance:
        in two footprints (fail) and in one footprint (pass), for a rule that leaves a
        footprint's own pins out."""
        gap = 0.2
        assert gap < self.rule(name).value("clearance")

        def build(x, y, fail):
            a, b = self.class_net(netclass), self._net()
            fp = self.part("U", x, y)
            self._pad(fp, x + pad / 2, y, pad, net=a)
            bx = x + pad + gap + pad / 2
            fp_b = self.part("U", bx, y) if fail else fp
            p2 = self._pad(fp_b, bx, y, pad, net=b)
            p2.SetNumber("2")
            self.widen(bx + pad + FAR)
        self.add_row(name, 2 * FAR + pad, build)

    def pad_to_edge_row(self, name, pad, prop):
        gap = self.rule(name).value("edge_clearance")

        def build(x, y, fail):
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            py = y + 0.5 + self._v(gap, fail) + pad / 2
            self.smd("FID" if "FIDUCIAL" in str(prop) else "TP", x + 0.5, py, pad,
                     prop=prop)
        self.add_row(name, gap + pad + FAR + SPACE, build)

    def silk_to_pad_row(self, name, pad, width=0.15):
        gap = self.rule(name).value("silk_clearance")

        def build(x, y, fail):
            self.smd("R", x + pad / 2, y, pad)
            sx = x + pad + self._v(gap, fail) + width / 2
            self.silk_line(sx, y - pad / 2, sx, y + pad / 2, width)
        self.add_row(name, max(tbm.ROW_H, pad + 2.0), build)

    def silk_to_edge_row(self, name, width=0.15):
        """KiCad 10.0.7 reports a silkscreen line near the board edge only
        when the edge clips it, and measures text to an internal cutout in a
        way that does not follow the text's position, so the FAIL line
        crosses the cutout and the PASS line keeps the clearance."""
        gap = self.rule(name).value("silk_clearance")

        def build(x, y, fail):
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            sy = y + 0.5 + EDGE_W / 2 + gap + 0.01 + width / 2
            self.silk_line(x - 0.5, y if fail else sy, x + 1.5, sy, width)
        self.add_row(name, gap + SPACE + FAR, build)

    def via_near_pad_row(self, name, pad, drill, dia):
        """An open via next to an SMD pad of its own net; on the PASS side
        also a filled and capped via inside a pad, which the rule allows."""
        gap = self.rule(name).value("physical_hole_clearance")

        def build(x, y, fail):
            net = self._net()
            self.smd("R", x + pad / 2, y, pad, net=net)
            vx = x + pad + self._v(gap, fail) + drill / 2
            self._via(vx, y, drill, dia, net=net)
            self._track(x + pad / 2, y, vx, y, 0.2, pcbnew.F_Cu, net)
            if not fail:
                net2 = self._net()
                px = vx + 2.0
                self.smd("R", px, y, pad, net=net2)
                v = self._via(px, y, drill, dia, net=net2)
                v.SetFillingMode(pcbnew.FILLING_MODE_FILLED)
                v.SetCappingMode(pcbnew.CAPPING_MODE_CAPPED)
                self.widen(px + pad)
        self.add_row(name, max(tbm.ROW_H, pad + 2.0), build)

    # routing (PCB-W)

    def angle_row(self, name, length=1.5):
        limit = self.rule(name).value("track_angle")

        def build(x, y, fail):
            import math
            a = math.radians(limit - 1.0 if fail else limit + 1.0)
            net = self._net()
            x1, y1 = x + length, y + length
            self._track(x, y1, x1, y1, 0.15, pcbnew.F_Cu, net)
            # second segment leaving the corner at the interior angle a
            x2, y2 = x1 - length * math.cos(a), y1 - length * math.sin(a)
            self._track(x1, y1, x2, y2, 0.15, pcbnew.F_Cu, net)
        # KiCad reports each acute pair once per order of the two segments.
        self.add_row(name, max(tbm.ROW_H, length + 2.0), build, fires=2)

    def neck_row(self, name, area=None, netclass=None):
        neck = self.rule(name).value("connection_width")

        def build(x, y, fail):
            if area:
                self.area(area, x - 0.5, y - 0.5, x + 7.5, y + 3.5)
            net = self.class_net(netclass) if netclass else self._net()
            # KiCad only reports a neck more than about 0.01 mm under the limit.
            w = self._vd(neck, fail, 0.02)
            yc = y + 1.5
            self.zone(net, ((x, y), (x + 3, y), (x + 3, yc - w / 2), (x + 4, yc - w / 2),
                            (x + 4, y), (x + 7, y), (x + 7, y + 3), (x + 4, y + 3),
                            (x + 4, yc + w / 2), (x + 3, yc + w / 2), (x + 3, y + 3),
                            (x, y + 3)), min_width=min(0.05, w / 2))
            self.smd("R", x + 1.5, yc, 0.6, net=net)
            self.smd("R", x + 5.5, yc, 0.6, net=net)
            self.widen(x + 7)
        self.add_row(name, 4.5, build)

    def teardrop_row(self, name):
        def build(x, y, fail):
            v = self._via(x, y, 0.1, 0.25, pcbnew.VIATYPE_MICROVIA, (pcbnew.F_Cu, pcbnew.In1_Cu))
            v.SetTeardropsEnabled(not fail)
        self.add_row(name, tbm.ROW_H, build)

    def via_count_row(self, name, netclass, width):
        """Vias on one net of the class, joined by a track on L4 at the
        class's inner width (PCB-S-14 keeps impedance classes on L4 inside)."""
        limit = int(round(self.rule(name).value("via_count", "max")))

        def build(x, y, fail):
            net = self.class_net(netclass)
            n = limit + 1 if fail else limit
            pitch = 0.8
            for i in range(n):
                self._via(x + i * pitch, y, 0.2, 0.45, net=net)
            self._track(x, y, x + (n - 1) * pitch, y, width, L4, net)
            self.widen(x + n * pitch)
        self.add_row(name, tbm.ROW_H, build)

    # impedance classes (PCB-S-14, PCB-I, PCB-R-03)

    def pair_nets(self, netclass):
        """Two nets KiCad reads as a differential pair (suffix _P / _N)."""
        n = self._class_nets.get(netclass, 0) + 1
        self._class_nets[netclass] = n
        nets = []
        for sfx in ("P", "N"):
            net = pcbnew.NETINFO_ITEM(self.board, f"{netclass}_{n}_{sfx}")
            self.board.Add(net)
            nets.append(net)
        return nets

    def layer_row(self, name, netclass, width, fail_layer, pass_layer, fail_width=None):
        """A class track on a layer the class may not use (FAIL), and on one
        it may use (PASS). FAIL_WIDTH keeps the failing track clear of the
        width rules of its layer."""
        def build(x, y, fail):
            w = (fail_width or width) if fail else width
            cy = y + w / 2
            self._track(x + w / 2, cy, x + 3 - w / 2, cy, w,
                        fail_layer if fail else pass_layer, self.class_net(netclass))
        self.add_row(name, max(tbm.ROW_H, width + 2.5), build)

    def band_width_row(self, name, layer, netclass):
        """FAIL: one track under the minimum and one over the maximum; PASS:
        one track at the optimum (the computed width)."""
        r = self.rule(name)
        lo, opt, hi = (r.value("track_width", k) for k in ("min", "opt", "max"))

        def build(x, y, fail):
            widths = (self._v(lo, True), self._v(hi, True, "max")) if fail else (opt,)
            for i, w in enumerate(widths):
                ty = y + i * 1.0
                self._track(x, ty, x + 3, ty, w, layer, self.class_net(netclass))
        self.add_row(name, tbm.ROW_H + 1.0, build, fires=2)

    def pair_gap_row(self, name, layer, netclass):
        """A pair at the class width: FAIL just under the minimum gap, PASS at
        the computed gap (the minimum plus 5 %)."""
        lo = self.rule(name).value("clearance")
        w = self._pair_width(layer, netclass)

        def build(x, y, fail):
            g = self._v(lo, True) if fail else lo / 0.95
            p, n = self.pair_nets(netclass)
            self._track(x, y, x + 3, y, w, layer, p)
            self._track(x, y + w + g, x + 3, y + w + g, w, layer, n)
        self.add_row(name, tbm.ROW_H, build)

    def _pair_width(self, layer, netclass):
        """The class's computed width on LAYER, read from its width rule."""
        side = "outer" if layer in (pcbnew.F_Cu, pcbnew.B_Cu) else "inner"
        for rule in self.rules.values():
            if (rule.layer == side and "track_width" in rule.constraints
                    and f"'{netclass}'" in (rule.condition or "")):
                return rule.value("track_width", "opt")
        raise KeyError(f"no {side} width rule for {netclass}")

    def rf_cutout_row(self, name, fail_layer, pass_layer, pass_gnd, plane=False):
        """Rule area RF_CUTOUT on L2 and L3 only (the side of an L1 line).
        FAIL: a track of another net on FAIL_LAYER inside it. PASS: a track
        on PASS_LAYER inside it, on GND if PASS_GND (joined to the bus).
        With PLANE, both sides also get a GND plane on L2 over the area: on
        the FAIL side its fill enters the area (a second report), on the
        PASS side the area keeps the fill out, as the board draws it."""
        def build(x, y, fail):
            self.area("RF_CUTOUT", x - 0.5, y - 0.8, x + 3.5, y + 0.8,
                      layers=(L2, L3), no_fill=plane and not fail)
            if plane:
                bx = self.gnd_bus_x(x)
                self._via(bx, y - 1.0, 0.2, 0.45, net=self.gnd())
                self._gnd_taps.append((bx, y - 1.0))
                self.zone(self.gnd(), ((bx - 0.5, y - 1.5), (x + 4, y - 1.5), (x + 4, y + 1.5),
                                       (bx - 0.5, y + 1.5)), layer=L2)
            if fail:
                self._track(x, y, x + 3, y, 0.2, fail_layer, self._net())
            elif pass_gnd:
                self.gnd_track(x + 3, y, 0.2, pass_layer)
            else:
                self._track(x, y, x + 3, y, 0.2, pass_layer, self._net())
        self.add_row(name, tbm.ROW_H + 1.5, build, fires=2 if plane else 1)

    # zones (PCB-S-14 per zone, PCB-S-17, PCB-S-18, PCB-A-20)

    def zone_layer_row(self, name, area, netclass, fail_layer, pass_layer, width=None,
                       pass_class=None, pour=False, pass_pour=None):
        """FAIL: a NETCLASS track (or, with POUR, a copper zone) on FAIL_LAYER inside AREA.
        PASS: the same class on PASS_LAYER (or PASS_CLASS on the same layer) inside it, a pour
        if PASS_POUR (default POUR). A track takes WIDTH, or the class's width on its layer when
        WIDTH is None. Nets are also ZONE_SHARED, so the zone rules of PCB-S-17 leave them
        alone."""
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 0.5, x + 3.5, y + 0.5)
            layer = fail_layer if fail else pass_layer
            cls = netclass if fail or not pass_class else pass_class
            net = self.class_net(cls, shared=True)
            if pour if fail else (pour if pass_pour is None else pass_pour):
                self.zone(net, ((x, y - 0.3), (x + 3, y - 0.3), (x + 3, y + 0.3), (x, y + 0.3)),
                          layer=layer)
            else:
                w = width if width is not None else self._pair_width(layer, cls)
                self._track(x + w / 2, y, x + 3 - w / 2, y, w, layer, net)
        self.add_row(name, tbm.ROW_H + 0.5, build)

    def zone_row(self, name, zone, foreign):
        """FAIL: a track of FOREIGN's zone inside ZONE_<zone>. PASS: a track of the zone's own
        class, and a foreign track wholly inside a ZONE_CORRIDOR crossing the zone."""
        def build(x, y, fail):
            self.area("ZONE_" + zone, x - 0.5, y - 0.5, x + 3.5, y + 2.0)
            if fail:
                self._track(x, y, x + 3, y, 0.2, pcbnew.F_Cu, self.class_net("ZONE_" + foreign))
            else:
                self._track(x, y, x + 3, y, 0.2, pcbnew.F_Cu, self.class_net("ZONE_" + zone))
                self.area("ZONE_CORRIDOR", x - 0.7, y + 0.8, x + 3.7, y + 1.6)
                self._track(x, y + 1.2, x + 3, y + 1.2, 0.2, pcbnew.F_Cu,
                            self.class_net("ZONE_" + foreign))
        self.add_row(name, tbm.ROW_H + 2.0, build)

    # thermal and safety placement (PCB-T)

    def part_in_area_row(self, name, area):
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 1.0, x + 3.5, y + 1.0)
            field = ("Thermal", "hot") if fail else None
            self.part("U", x + 1.5, y, 1.0, field=field)
        self.add_row(name, tbm.ROW_H, build)

    def area_copper_row(self, name, area):
        """A track inside the no-copper area (FAIL), one beside it (PASS)."""
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 0.5, x + 2.5, y + 0.5)
            ty = y if fail else y + 1.5
            self._track(x, ty, x + 2, ty, 0.2, pcbnew.F_Cu, self._net())
        self.add_row(name, tbm.ROW_H + 1.5, build)

    def pad_in_area_row(self, name, area, allowed):
        """An SMD pad of another net in the area (FAIL), an allowed one (PASS)."""
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 1.0, x + 3.5, y + 1.0)
            net = self._net() if fail else allowed()
            self.smd("R", x + 1.5, y, 0.6, net=net)
        self.add_row(name, tbm.ROW_H, build)

    def part_outside_area_row(self, name, area, field):
        """A footprint with FIELD outside the area (FAIL), inside it (PASS)."""
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 1.0, x + 1.5, y + 1.0)
            self.part("D", x + (3.5 if fail else 0.5), y, 1.0, field=field)
            self.widen(x + 4.5)
        self.add_row(name, tbm.ROW_H, build)

    # output --------------------------------------------------------------

    def _gnd_bus(self):
        """Join every GND tap: one track on L5 per column and one between
        the two columns, below the last tap."""
        if len(self._gnd_taps) < 2:
            return
        y_join = max(y for _, y in self._gnd_taps) + 1.2
        buses = sorted({bx for bx, _ in self._gnd_taps})
        for bx in buses:
            y0 = min(y for b, y in self._gnd_taps if b == bx)
            self._track(bx, y0, bx, y_join, 0.2, L5, self.gnd())
        if len(buses) > 1:
            self._track(buses[0], y_join, buses[-1], y_join, 0.2, L5, self.gnd())

    def save(self, out_dir, ignore_checks=()):
        self._gnd_bus()
        # Fill the zones once testboard has drawn the outline, just before
        # it writes the board.
        save_board = pcbnew.SaveBoard

        def fill_and_save(path, board):
            pcbnew.ZONE_FILLER(board).Fill(board.Zones())
            save_board(path, board)
        pcbnew.SaveBoard = fill_and_save
        # testboard.save() sizes the outline from TOP, ROW_H and BOARD_W.
        tbm.TOP, saved_rows = self.y - self.row * tbm.ROW_H, self.row
        tbm.BOARD_W = self.board_w
        try:
            pcb = super().save(out_dir, ignore_checks)
        finally:
            pcbnew.SaveBoard = save_board
        self.row = saved_rows
        return pcb

    def _write_project(self, out_dir, ignore_checks):
        super()._write_project(out_dir, ignore_checks)
        path = os.path.join(out_dir, f"{self.name}.kicad_pro")
        with open(path, encoding="utf-8") as fh:
            project = json.load(fh)
        default = project["net_settings"]["classes"][0]
        for i, name in enumerate(CLASSES):
            cls = dict(default)
            cls["name"] = name
            cls["priority"] = i
            project["net_settings"]["classes"].append(cls)
        project["net_settings"]["netclass_patterns"] = [
            {"netclass": name, "pattern": f"{name}_*"} for name in CLASSES] + [
            {"netclass": "ZONE_SHARED", "pattern": "*_ZS"}]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(project, fh, indent=2, sort_keys=True)
            fh.write("\n")


def main():
    tb = ProductTestBoard(NAME, RULES, copper_layers=6)
    micro = (pcbnew.VIATYPE_MICROVIA, (pcbnew.F_Cu, pcbnew.In1_Cu))
    fid = pcbnew.PAD_PROP_FIDUCIAL_GLBL
    tp = pcbnew.PAD_PROP_TESTPOINT

    # Geometry (PCB-G)
    tb.clearance_row(P + "PCB-G-01 [Q1]: Copper clearance", width=0.2)
    tb.width_row(P + "PCB-G-01 [Q1]: Track width", pcbnew.F_Cu)
    tb.clearance_row(P + "PCB-G-02 [Q1]: Copper clearance in the BGA escape", width=0.1,
                     area="BGA_ESCAPE")
    tb.width_row(P + "PCB-G-02 [Q1]: Track width in the BGA escape", pcbnew.F_Cu,
                 area="BGA_ESCAPE")
    tb.via_diameter_row(P + "PCB-G-03 [Q1]: Microvia diameter", 0.1, *micro)
    tb.via_diameter_row(P + "PCB-G-04 [Q1]: Mechanical via diameter", 0.2)
    tb.edge_row(P + "PCB-G-05 [Q1]: Copper to board edge", width=0.2)
    # L4 (In3.Cu), the inner signal layer: no zone rule acts on it outside the corridors
    tb.hole_to_copper_row(P + "PCB-G-11 [Q1]: Hole to copper, inner layers (six-layer row)", 0.5, 0.1,
                          layer=pcbnew.In3_Cu)

    # Voltage spacing (PCB-V)
    tb.pad_to_track_row(P + "PCB-V-01 [Q1]: Exposed termination spacing", pad=0.6)
    tb.pad_to_track_row(P + "PCB-V-02 [Q1]: VBUS termination spacing", pad=0.6,
                        netclass="PWR_VBUS")

    # Power (PCB-P)
    for rule, netclass in (
            ("PCB-P-01 [Q0]: Battery path track width", "PWR_BAT"),
            ("PCB-P-02 [Q0]: VSYS track width", "PWR_VSYS"),
            ("PCB-P-03 [Q0]: VBUS input track width", "PWR_VBUS"),
            ("PCB-P-04 [Q0]: 5.1 V source track width", "PWR_5V1"),
            ("PCB-P-20 [Q0]: HAT 5 V track width", "PWR_HAT5V")):
        tb.width_row(P + rule + " (outer)", pcbnew.F_Cu, netclass)
        tb.width_row(P + rule + " (inner)", pcbnew.In1_Cu, netclass)
    tb.width_row(P + "PCB-P-06 [Q1]: Amplifier rail track width", pcbnew.In2_Cu, "PWR_AMP")

    # Audio and clocks (PCB-A, PCB-I-09)
    tb.clearance_row(P + "PCB-A-06 [Q1]: Switch node to analog audio", width=0.2,
                     net_a="SW_NODE", net_b="AUDIO_ANALOG")
    tb.foreign_track_row(P + "PCB-A-07 [Q1]: Foreign track in the analog audio area",
                         "AUDIO_ANALOG", lambda: tb.class_net("AUDIO_ANALOG"))
    mclk_w = tb.rule(P + "PCB-I-05/06/08/09 [Q1]: 50 ohm single-ended width (inner)") \
        .value("track_width", "opt")
    tb.clearance_row(P + "PCB-I-09 [Q1]: Master clock to other nets", width=mclk_w,
                     net_a="MCLK_50SE", layer=L4, width_b=0.1)
    tb.own_pads_row(P + "PCB-I-09 [Q1]: Master clock to other nets", 0.3, "MCLK_50SE")

    # Mounting holes (PCB-H)
    tb.hole_to_part_row(P + "PCB-H-01 [Q1]: Part under the screw head", 2.2, "R")
    tb.hole_to_copper_row(P + "PCB-H-02 [Q1]: Copper under the screw head", 2.2, 0.2)
    tb.plated_hole_net_row(P + "PCB-H-03 [Q2]: Plated mounting hole on GND", 2.2)
    tb.hole_to_edge_row(P + "PCB-H-04 [Q1]: Mounting hole to board edge", 2.2)
    tb.hole_to_part_row(P + "PCB-H-05 [Q1]: MLCC to mounting hole", 2.2, "C")
    tb.hole_to_bga_row(P + "PCB-H-06 [Q2]: BGA to mounting hole", 2.2, 0.25)

    # Board edges and panelisation (PCB-B)
    tb.part_to_edge_row(P + "PCB-B-01 [Q1]: Part to board edge", "R")
    tb.edge_row(P + "PCB-B-02 [Q1]: Copper to edge at a break tab", width=0.2,
                area="BREAK_TAB")
    tb.part_to_edge_row(P + "PCB-B-03 [Q1]: MLCC at a break tab", "C",
                        area="BREAK_TAB")

    # Assembly (PCB-D)
    tb.courtyard_row(P + "PCB-D-01 [Q1]: BGA rework clearance", ("Rework", "BGA"))
    tb.pad_size_row(P + "PCB-D-02 [Q1]: Fiducial size", fid)
    tb.pad_to_track_row(P + "PCB-D-03 [Q1]: Fiducial clear area", pad=1.0, prop=fid,
                        constraint="physical_clearance", prefix="FID")
    tb.pad_to_edge_row(P + "PCB-D-04 [Q2]: Fiducial to board edge", 1.0, fid)
    tb.silk_to_edge_row(P + "PCB-D-05 [Q2]: Silkscreen to board edge")
    tb.pad_size_row(P + "PCB-D-06 [Q2]: Test point size", tp)
    tb.pad_to_pad_row(P + "PCB-D-07 [Q2]: Test point spacing", 1.0, tp, tp, "TP")
    tb.pad_to_pad_row(P + "PCB-D-08 [Q2]: Test point to other pads", 1.0, tp, None, "R")
    tb.pad_to_edge_row(P + "PCB-D-09 [Q2]: Test point to board edge", 1.0, tp)
    tb.via_near_pad_row(P + "PCB-D-10 [Q1]: Open via near an SMD pad", 0.6, 0.2, 0.45)

    # Routing hygiene (PCB-W)
    tb.neck_row(P + "PCB-W-01 [Q1]: Copper neck")
    tb.neck_row(P + "PCB-W-01 [Q1]: Copper neck on impedance classes", netclass="DDR_50SE")
    tb.neck_row(P + "PCB-W-01 [Q1]: Copper neck in the BGA escape", area="BGA_ESCAPE")
    tb.teardrop_row(P + "PCB-W-02 [Q2]: Teardrops on vias")
    for line, netclass in (("USB 2", "USB2_90D"), ("USB 3", "USB3_90D"),
                           ("MIPI", "MIPI_100D")):
        tb.via_count_row(P + f"PCB-W-03 [Q2]: Vias per {line} line", netclass,
                         tb._pair_width(L4, netclass))

    # Stackup layers and impedance classes (PCB-S-14, PCB-I, PCB-R-03)
    tb.layer_row(P + "PCB-S-14 [Q1]: Impedance class on a plane layer", "USB2_90D",
                 tb._pair_width(L4, "USB2_90D"), L2, L4)
    tb.layer_row(P + "PCB-S-14 [Q1]: Master clock on an outer layer", "MCLK_50SE",
                 mclk_w, pcbnew.F_Cu, L4, fail_width=0.1)
    rf_w = tb.rule(P + "PCB-I-07 [Q1]: RF line width").value("track_width", "opt")
    tb.layer_row(P + "PCB-S-14 [Q1]: RF line on an inner layer", "RF_50SE", rf_w,
                 L4, pcbnew.B_Cu)
    for rule, layer, netclass in (
            ("PCB-I-05/06/08 [Q1]: 50 ohm single-ended width (outer)", pcbnew.F_Cu,
             "DDR_50SE"),
            ("PCB-I-05/06/08/09 [Q1]: 50 ohm single-ended width (inner)", L4, "MCLK_50SE"),
            ("PCB-I-01/02 [Q1]: 90 ohm pair width (outer)", pcbnew.B_Cu, "USB3_90D"),
            ("PCB-I-01/02 [Q1]: 90 ohm pair width (inner)", L4, "USB2_90D"),
            ("PCB-I-04/05 [Q1]: 100 ohm pair width (outer)", pcbnew.F_Cu, "MIPI_100D"),
            ("PCB-I-04/05 [Q1]: 100 ohm pair width (inner)", L4, "DDR_100D"),
            ("PCB-I-07 [Q1]: RF line width", pcbnew.F_Cu, "RF_50SE")):
        tb.band_width_row(P + rule, layer, netclass)
    tb.pair_gap_row(P + "PCB-I-01/02 [Q1]: 90 ohm pair gap (outer)", pcbnew.F_Cu,
                    "USB2_90D")
    tb.pair_gap_row(P + "PCB-I-01/02 [Q1]: 90 ohm pair gap (inner)", L4,
                    "USB3_90D")
    tb.pair_gap_row(P + "PCB-I-04/05 [Q1]: 100 ohm pair gap (outer)", pcbnew.B_Cu,
                    "DDR_100D")
    tb.pair_gap_row(P + "PCB-I-04/05 [Q1]: 100 ohm pair gap (inner)", L4,
                    "MIPI_100D")
    tb.clearance_row(P + "PCB-I-07 [Q1]: RF line to same-layer ground", width=rf_w,
                     net_a="RF_50SE", width_b=0.2, gnd_b=True)
    tb.clearance_row(P + "PCB-S-24 [Q1]: LPDDR4X spacing on the inner layer",
                     width=tb._pair_width(L4, "DDR_50SE"), net_a="DDR_50SE", layer=L4,
                     width_b=0.1)
    # The PASS track of the cut-out row is on L4, outside the area's layers:
    # the area applies only on the side it is drawn for.
    tb.rf_cutout_row(P + "PCB-R-03 [Q1]: Copper in the RF ground cut-out", L2, L4, False,
                     plane=True)
    tb.rf_cutout_row(P + "PCB-R-03 [Q1]: Foreign copper on the RF ground pour", L3, L3, True)

    # Zone-aware layers (PCB-S-14, PCB-S-18, PCB-S-25, PCB-P-22, PCB-A-20)
    tb.zone_layer_row(P + "PCB-S-14 [Q1]: Impedance class on L1 in the core zone", "ZONE_CORE",
                      "USB2_90D", pcbnew.F_Cu, L4)
    tb.zone_layer_row(P + "PCB-S-14 [Q1]: Impedance class on L4 in the power or radio zone",
                      "ZONE_POWER", "USB2_90D", L4, pcbnew.B_Cu)
    tb.zone_layer_row(P + "PCB-S-18 [Q1]: Foreign copper on a corridor reference layer",
                      "ZONE_CORRIDOR", "AUDIO_REF", L3, L4, width=0.2)
    tb.zone_layer_row(P + "PCB-S-25 [Q1]: Foreign copper on the full-layer ground", "ZONE_CORE",
                      "AUDIO_REF", L5, L4, width=0.2)
    tb.zone_layer_row(P + "PCB-S-25 [Q1]: Foreign copper on L2 outside the core zone", "ZONE_IO",
                      "AUDIO_REF", L2, L4, width=0.2)
    tb.zone_layer_row(P + "PCB-S-25 [Q1]: Foreign copper on L3 outside the power zone",
                      "ZONE_AUDIO", "AUDIO_REF", L3, L4, width=0.2)
    tb.zone_layer_row(P + "PCB-P-22 [Q0]: VBUS on an inner layer in the I/O zone", "ZONE_IO",
                      "PWR_HAT5V", L4, pcbnew.F_Cu, pour=True)
    tb.zone_layer_row(P + "PCB-A-20 [Q1]: Inner pour in the analog audio area", "AUDIO_ANALOG",
                      "PWR_AUDIO", L4, L4, width=0.2, pour=True, pass_pour=False)

    # Zones (PCB-S-17)
    for zone, label, foreign in (("CORE", "core", "AUDIO"), ("AUDIO", "audio", "CORE"),
                                 ("POWER", "power", "AUDIO"), ("IO", "I/O", "POWER"),
                                 ("RADIO", "radio", "POWER"), ("FACEPLATE", "faceplate", "POWER")):
        tb.zone_row(P + f"PCB-S-17 [Q1]: Foreign track in the {label} zone", zone, foreign)

    # Battery interface and heat placement (PCB-L)
    tb.part_in_area_row(P + "PCB-L-01 [Q0]: Hot part at the battery pocket",
                        "BATTERY_POCKET")
    tb.foreign_track_row(P + "PCB-L-02 [Q0]: Foreign track at the battery contacts",
                         "BATTERY_CONNECTOR", lambda: tb.class_net("PWR_BAT"),
                         width=tb.rule(P + "PCB-P-01 [Q0]: Battery path track width (outer)")
                         .value("track_width") + 0.01)
    tb.pad_in_area_row(P + "PCB-L-05 [Q0]: Foreign pad at the battery contacts",
                       "BATTERY_CONNECTOR", lambda: tb.class_net("BAT_SENSE"))
    tb.area_copper_row(P + "PCB-L-04 [Q0]: Copper at the empty battery contact position",
                       "BATTERY_CONTACT_EMPTY")
    tb.part_outside_area_row(P + "PCB-L-08 [Q1]: Battery contact ESD away from the contacts",
                             "BATTERY_ESD", ("ESD", "battery"))

    # The PCB-A-20 and PCB-P-22 rows' pours have no pad to join: their isolated-fill report is a fixture
    # artefact, not a rule.
    print(tb.save(HERE, ignore_checks=tuple(TEST_BOARD_IGNORED_CHECKS) + ("isolated_copper",)))


if __name__ == "__main__":
    main()
