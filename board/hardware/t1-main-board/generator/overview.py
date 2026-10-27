"""The overview sheets (root block diagram, power, interconnect) and the placement of sheet symbols."""

from __future__ import annotations

import os

from sch import RAILS as RAILS_ORDER, snap
from draw import corner_notes
from sexpr import n, q
from sch import uid

# Power tree v0.6 (§2 tree, §3 rail table, §4.12 links) for the rails drawn so far.
RAIL_ROWS = [
    ["USBC_VBUS", "5-12 V", "USB-C sink; eFuse #C source (blk.usb-vbus-out)", "PD contract; USB_SRC_ON", "TPS2121 IN1, FUSB302B", "PWR_VBUS", "eFuse #C IMON"],
    ["HAT_5V", "5 V", "HAT port: eFuse #A source, or a source HAT", "HAT5V_EN (TCPM)", "TPS2121 IN2, FUSB302B01", "PWR_HAT5V", "eFuse #A IMON"],
    ["VBUS_CHG", "5-12 V", "TPS2121 (blk.charger-input)", "input priority", "BQ25798 VBUS", "PWR_VBUS", "-"],
    ["VBAT", "6.0-8.4 V", "BQ25798 BAT, 2S pack (blk.charger-core)", "ship FET to the pack", "BQ25798 BATFET, gauge PACK", "PWR_BAT", "gauge (blk.gauge)"],
    ["VSYS", "6.0-8.8 V", "BQ25798 SYS (VSYS_SRC) through the 10 mΩ shunt", "ship FET", "TPS62136, TPS62903, LMR33630C", "PWR_VSYS", "INA236 0x40"],
    ["VSYS_SRC", "6.0-8.8 V", "BQ25798 SYS (blk.charger-core)", "-", "VSYS shunt 10 mΩ (blk.current-monitors)", "PWR_VSYS", "INA236 0x40 (IN+)"],
    ["VSYS_AUDIO", "6.0-8.8 V", "VSYS through 20 mΩ (blk.current-monitors)", "-", "LMR33630C and its EN shifter (blk.hpa-rails-pre)", "PWR_VSYS", "INA236 0x48"],
    ["VSYS_P5V1", "6.0-8.8 V", "VSYS through 20 mΩ (blk.current-monitors)", "-", "TPS62903 VIN (blk.pwr-5v1)", "PWR_VSYS", "INA236 0x43"],
    ["VSYS_LV", "3.8 V", "TPS62136 (blk.pwr-vsys-lv)", "always on (EN = VSYS)", "RK809 VCC1-4, TPS62869, TPS62827, audio, display", "-", "H5 link"],
    ["VSYS_LV_AUDIO", "3.8 V", "VSYS_LV through 20 mΩ (blk.current-monitors)", "-", "DAC_VP switch, TPS62840, link #27, TPS65131", "-", "INA236 0x41"],
    ["VSYS_LV_BL", "3.8 V", "VSYS_LV through 100 mΩ (blk.current-monitors)", "-", "TPS61160 VIN (blk.fp-backlight)", "-", "INA236 0x42"],
    ["vcc3v3_sys", "3.3 V", "TPS62827 (blk.pwr-3v3-sys)", "always on (EN = VSYS_LV)", "RK809 VCC5-9, eMMC VCC, SoC VCCIO1/5/7, USB", "-", "H5 link"],
    ["vdd_cpu", "0.85-1.15 V", "TPS62869 (blk.vdd-cpu)", "EN from vcc3v3_pmu; I2C DVS", "SoC CPU", "-", "H5 link"],
    ["vdd_logic", "0.90 V", "RK809 BUCK1 (blk.pmic)", "off in suspend", "SoC logic", "-", "H5 link (blk.soc)"],
    ["vdd_gpu", "0.90 V", "RK809 BUCK2", "DT regulator", "SoC GPU", "-", "-"],
    ["vcc_ddr", "1.113 V", "RK809 BUCK3 (47k / 120k)", "on in suspend", "DRAM VDD2, SoC DDR_VDDQ, TPS7A1006", "-", "H5 link (blk.lpddr4x)"],
    ["vdd_npu", "0.90 V", "RK809 BUCK4", "off by default", "SoC NPU", "-", "-"],
    ["vcc_1v8", "1.80 V", "RK809 BUCK5", "off in suspend", "SoC VCCIO2/4, eMMC VCCQ, vccio6_1v8", "-", "-"],
    ["vccio6_1v8", "1.80 V", "vcc_1v8 through a 0 Ω link", "follows vcc_1v8", "SoC VCCIO6", "-", "-"],
    ["vcc0v6_ddr", "0.60 V", "TPS7A1006 (blk.lpddr4x)", "EN = vcc_ddr", "DRAM VDDQ, SoC DDR_VDDQL", "-", "H20 link"],
    ["vcc1v8_ddr", "1.80 V", "vcca1v8_pmu through a link", "always on", "DRAM VDD1, TPS7A1006 BIAS", "-", "M link"],
    ["vdda0v9_image", "0.9 V", "RK809 LDO1", "unused (RFC 0014)", "none: CSI RX has no consumer", "-", "-"],
    ["vdda_0v9", "0.9 V", "RK809 LDO2", "on", "SoC USB/PCIe/DSI PHY", "-", "-"],
    ["vdda0v9_pmu", "0.9 V", "RK809 LDO3", "always on", "SoC PMU", "-", "-"],
    ["FP_VCI_SRC", "2.8 V", "RK809 LDO4", "RK809 I2C", "FP_VCI switch (blk.fp-display)", "-", "M link"],
    ["FP_VCI", "2.8 V", "TPS22945 from FP_VCI_SRC", "FP_IO_EN", "panel VCI (contact 44)", "-", "-"],
    ["vccio_sd", "1.8/3.3 V", "RK809 LDO5", "SD driver", "SoC VCCIO3", "-", "-"],
    ["vcc3v3_pmu", "3.3 V", "RK809 LDO6", "always on", "SoC PMUIO1, FUSB302B, TPS62869 EN", "-", "-"],
    ["vcca_1v8", "1.8 V", "RK809 LDO7", "on", "SoC PLL and PHY analog", "-", "-"],
    ["vcca1v8_pmu", "1.8 V", "RK809 LDO8", "always on", "SoC PMUIO0/2, vcc1v8_ddr, pull-ups", "-", "-"],
    ["vcca1v8_image", "1.8 V", "RK809 LDO9", "unused (RFC 0014)", "none: CSI RX has no consumer", "-", "-"],
    ["vcc3v3_sd", "3.3 V", "RK809 SWOUT2", "RK809 I2C", "microSD VDD", "-", "M link"],
    ["vcc3v3_wl", "3.3 V", "TPS22919 from vcc3v3_sys (blk.radio-power)", "WL_PWR_EN", "Type 2EL AVDD33, AVDD18 buck EN", "-", "H20 link #11"],
    ["vcc1v8_wl", "1.80 V", "TPS62826 from VSYS_LV (blk.radio-power)", "EN from vcc3v3_wl", "Type 2EL AVDD18", "-", "H20 link #12"],
    ["FP_3V3", "3.3 V", "TPS22950 from vcc3v3_sys (blk.fp-connector)", "FP_IO_EN", "faceplate logic, pull-ups", "-", "-"],
    ["FP_1V8", "1.80 V", "TPS22945 from vcc_1v8 (blk.fp-connector)", "FP_IO_EN", "faceplate IOVCC", "-", "-"],
    ["MIC_1V8", "1.80 V", "TPS22945 from vcc_1v8 (blk.mic-main)", "MIC_EN", "both microphone branches", "-", "-"],
    ["MIC_1V8_FP", "1.80 V", "MIC_1V8 through link #34 (blk.mic-main)", "MIC_EN", "faceplate microphone (contact 40)", "-", "L10 link #34"],
]


def draw_power(s):
    # rail table on the left, power tree as an indented column of boxes on the right
    s.table(25.4, 35.56, [27.94, 20.32, 45.72, 40.64, 60.96, 20.32, 30.48],
            [["Rail", "Voltage", "Source", "Switch or enable", "Consumers", "Net class", "Measure"]] + RAIL_ROWS,
            "railtab", title="Rail table (power tree v0.6 §3, §4.12)")
    s.text("Power tree (drawn blocks)", 279.4, 35.56 - 1.27, size=2.54)
    # (label, sub-label, indent level, parent index)
    boxes = [
        ("VSYS 6.0-8.8 V", "BQ25798 (blk.charger)", 0, None),
        ("TPS62136", "VSYS_LV 3.8 V", 1, 0),
        ("TPS62827", "vcc3v3_sys 3.3 V", 2, 1),
        ("RK809-5 BUCK5, LDO1-9, SWOUT2", "VCC5-9 from vcc3v3_sys", 3, 2),
        ("RK809-5 BUCK1-4", "VCC1-4 from VSYS_LV", 2, 1),
        ("TPS7A1006", "vcc0v6_ddr 0.60 V from vcc_ddr", 3, 4),
        ("TPS62869", "vdd_cpu 0.85-1.15 V", 2, 1),
        ("TPS62903", "P5V1_SRC 5.1 V from VSYS", 1, 0),
    ]
    pos = []
    for i, (a, b, lvl, parent) in enumerate(boxes):
        x, y = 279.4 + lvl * 12.7, 38.1 + i * 20.32
        pos.append((x, y))
        s.add(f"(rectangle (start {n(x)} {n(y)}) (end {n(x + 55.88)} {n(y + 12.7)}) (stroke (width 0) (type solid)) "
              f"(fill (type none)) (uuid {q(uid(s.name, 'pbox', a))}))")
        s.text(a, x + 2.54, y + 5.08)
        s.text(b, x + 2.54, y + 10.16)
        if parent is not None:
            px, py = pos[parent]
            s.add(f"(polyline (pts (xy {n(px + 6.35)} {n(py + 12.7)}) (xy {n(px + 6.35)} {n(y + 6.35)}) "
                  f"(xy {n(x)} {n(y + 6.35)})) (stroke (width 0) (type solid)) "
                  f"(fill (type none)) (uuid {q(uid(s.name, 'parrow', i))}))")
    corner_notes(s, [
        "1. Rail names are the power tree's; every power symbol on every sheet names one (CRAFT-84, -85).",
        "2. Only the rails of the blocks drawn so far are listed; the rest join with their blocks.",
        "3. Measure: the block measurement links of BOM v1 line 137 (shunt in full, 0 Ω in production,",
        "   H5 kept); the five INA236 channels and their shunts are on blk.current-monitors.",
        "4. PWR_FLAG: KiCad 10.0.7's ERC reports a flag on a net island of power symbols as",
        "   pin_not_connected, so each flag sits on the sheet that feeds its rail, on a branch of the",
        "   rail's wire outside the block's groups (link load side, inductor output). Local nets fed",
        "   through a passive part (TPM_VDD, RP_DVDD) take their flag the same way on their own sheet.",
        "5. Net class '-': the class rules of the product apply through the switch nodes and DDR",
        "   classes; rail copper widths come with the layout (PCB design constraints).",
    ])


def draw_interconnect(s):
    s.text("External connectors", 25.4, 30.48, size=2.54)
    s.table(25.4, 35.56, [38.1, 66.04, 101.6], [
        ["Connector", "Block", "Pin map"],
        ["USB-C (USB4105-GF-A)", "blk.usb-c", "added when the block is drawn"],
        ["HAT connector", "blk.hat-signals", "follows the connector decision (RFC 0014; hat-standard interface v2)"],
        ["Faceplate (FH35C-51S)", "blk.fp-connector", "added when the block is drawn (faceplate interface v1)"],
        ["Battery contacts (6 x 70-9258)", "blk.charger", "added when the block is drawn (ADR 0020)"],
        ["Headphone jacks 3.5 / 4.4 mm", "blk.jack-se, blk.jack-bal", "added when the blocks are drawn"],
        ["microSD (DM3AT)", "blk.microsd", "added when the block is drawn"],
    ], "conn")
    corner_notes(s, [
        "1. One pin-map table per external connector (pin, net, direction, block, notes), named as on the",
        "   block sheets (CRAFT-110). No external connector is drawn yet: the blocks drawn so far",
        "   (power converters, PMIC, vdd_cpu, SoC, LPDDR4X, eMMC) are internal to the board.",
    ], w=129.54)


BAND = 25.4   # the page-order check reads the root in bands of this height, then left to right (CRAFT-111)
CLEAR = 5.08  # clearance of every symbol, label and file name from the frame and the title block


def reading_order(rows):
    """The root's blocks in the order the diagram reads (CRAFT-111): row by row; inside a row,
    stack level by stack level, left to right. Page numbers are given in this order before
    anything is drawn, and layout_rows() then places the symbols so the plot reads the same way."""
    out = []
    for _title, items in rows:
        cols = [it if isinstance(it, list) else [it] for it in items]
        for k in range(max(len(c) for c in cols)):
            out += [c[k] for c in cols if len(c) > k and c[k] is not None]
    return out


def _band(y):
    return round(y / BAND)


def layout_rows(sheet, rows, x0=25.4, y0=25.4, gap=5.08, hgap=5.08, head=3.81, width_step=7.62):
    """Place sheet symbols in titled rows, left to right in reading order (CRAFT-111). A row item
    is a sheet or a list of sheets stacked in one column. Each symbol is spaced by the text its
    outside labels and its top pins take (cs.ext), so no label meets a neighbour or a heading.

    Equivalent boxes look alike: every box in a stacked column takes the column's width, and
    widths come in steps of width_step. Every stack level of every row sits in a band of its own
    (BAND), so the plot reads in the page order whatever the boxes' heights. The layout fails
    (SystemExit) instead of letting a symbol, label or file name reach the frame or the title
    block. Returns the bottom y of the last row; the headings are kept in sheet.headings.

    A column may leave a stack level empty (None): its next box sits in the next band, below a
    shorter neighbour's level or the notes box (draw_root checks the notes against every box)."""
    from draw import frame, tb_box, MARGIN
    W, H = frame(sheet)
    tx0, ty0, _, _ = tb_box(sheet)
    x_max, y_max = W - MARGIN - CLEAR, H - MARGIN - CLEAR
    by = {cs.sheet: cs for cs in sheet.children}
    sheet.headings = []
    y = y0
    last_band = None
    for title, items in rows:
        cols = [[by[s] if s is not None else None for s in (it if isinstance(it, list) else [it])] for it in items]
        for col in cols:
            w = max(cs.w for cs in col if cs is not None)
            w = snap(width_step * -(-round(w / width_step, 6) // 1)) if w > 30.48 else w
            for cs in col:
                if cs is not None:
                    cs.w = w
        sheet.headings.append((title, x0, y))
        top = snap(y + head + max(c[0].ext["top"] for c in cols if c[0] is not None))
        # stacked symbols share one line per stack level across the row; each level in a band of
        # its own, below the previous level's band
        lines = []
        for k in range(max(len(c) for c in cols)):
            ln = top if k == 0 else snap(max(lines[k - 1] + 2.54 + (c[k - 1].h if c[k - 1] else 0.0) + 5.08
                                              + (c[k].ext["top"] if c[k] else 0.0) for c in cols if len(c) > k))
            while last_band is not None and _band(ln + 2.54) <= last_band:
                ln = snap(ln + 1.27)
            lines.append(ln)
            last_band = _band(ln + 2.54)
            if os.environ.get("T1_LAYOUT_DEBUG"):
                print(f"layout: root row {title[:20]!r} level {k}: line {ln:.1f}")
        x = x0
        placed = []
        for col in cols:
            le = max(cs.ext["left"] for cs in col if cs is not None)
            re_ = max(cs.ext["right"] for cs in col if cs is not None)
            w = next(cs.w for cs in col if cs is not None)
            cx = snap(x + le)
            if cx + w + re_ > x_max:
                raise SystemExit(f"generator: row {title!r} does not fit the root sheet")
            for k, cs in enumerate(col):
                if cs is None:
                    continue
                cs.x, cs.y = cx, snap(lines[k] + 2.54)   # sheet name above
                cy = cs.y + cs.h + 5.08                    # file name below the box
                # the frame, and the title block in the lower right corner
                bottom = ty0 - CLEAR if cs.x + w + re_ > tx0 - CLEAR else y_max
                if cy > bottom:
                    raise SystemExit(f"generator: {cs.sheet.name} reaches y {cy:.1f} mm on the root, "
                                     f"below {bottom:.1f} mm (frame or title block)")
            placed.append((col, cy))
            if os.environ.get("T1_LAYOUT_DEBUG"):
                print(f"layout: root column at x {cx:.1f}: le {le:.1f} w {w:.1f} re {re_:.1f}: "
                      + ", ".join(cs.sheet.name.split(".")[0] for cs in col if cs is not None))
            x = cx + w + re_ + hgap
        y = snap(max(cy for _, cy in placed) + gap)
    return y


def check_reading(sheet):
    """The page numbers equal the order the plot reads in (the page-order check's own key)."""
    on = sorted(sheet.children, key=lambda cs: (_band(cs.y), cs.x))
    pages = [int(cs.sheet.page) for cs in on]
    if pages != sorted(pages):
        raise SystemExit("generator: the root reads in a different order than its page numbers: "
                         + ", ".join(f"{cs.sheet.name}:{cs.sheet.page}" for cs in on))


def layout_column(parent, start=30.48, x=25.4, y_max=180.0):
    """Sub-sheets in columns from the left, each below the previous one's file name and above the
    next one's top pins; a new column starts when the next symbol would pass y_max."""
    y, cols, col = start, [], []
    for cs in parent.children:
        need = cs.ext["top"] + 2.54 + cs.h
        if col and y + need > y_max:
            cols.append(col)
            col, y = [], start
        y = snap(y + cs.ext["top"] + 2.54)
        col.append((cs, y))
        y += cs.h + 7.62
    cols.append(col)
    for col in cols:
        le = max(cs.ext["left"] for cs, _ in col)
        for cs, cy in col:
            cs.x, cs.y = snap(x + le), cy
        x = snap(x + le + max(cs.w for cs, _ in col) + max(cs.ext["right"] for cs, _ in col) + 7.62)


def draw_root(root):
    for title, x, y in root.headings:
        root.text(title, x, y, size=2.54)
    # the notes sit at the right end of the second row, clear of its symbols, so the bottom row
    # keeps the space above the title block for blocks
    from draw import frame, MARGIN
    notes_y = root.headings[1][2] + 5.08
    lines = [
        "1. Reading order: overviews first, then blocks left to right as power and signals flow;",
        "   page numbers follow it (CRAFT-111). The SoC's sub-sheets follow the SoC.",
        "2. Rails cross the hierarchy as power symbols named as the power tree; signals as sheet pins",
        "   named as each block's interface (CRAFT-112). Buses cross as one bus pin through the",
        "   project's bus aliases (DDR_CHA, DDR_CHB, EMMC); their members keep their names.",
        "3. Every block in use has a sheet; a net with a single pin by design ends in a local label.",
    ]
    corner_notes(root, w=99.06, y=notes_y, right=frame(root)[0] - MARGIN - CLEAR, lines=lines)
    # a box in an empty stack level (layout_rows) may sit below the notes, never on them
    from draw import G
    h = G * -(-((len(lines) + 1) * 2.03 + 3.81) // G)      # as corner_notes sizes the box
    nx1 = frame(root)[0] - MARGIN - CLEAR
    nx0, ny0, ny1 = nx1 - 99.06, notes_y, notes_y + h
    for cs in root.children:
        bx0, by0 = cs.x - cs.ext["left"], cs.y - 3.81 - cs.ext["top"]
        bx1, by1 = cs.x + cs.w + cs.ext["right"], cs.y + cs.h + 5.08
        if bx0 < nx1 and bx1 > nx0 and by0 < ny1 and by1 > ny0:
            raise SystemExit(f"generator: {cs.sheet.name} meets the root notes")
