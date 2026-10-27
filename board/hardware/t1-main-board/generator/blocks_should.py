"""The should parts of BRD-057 to BRD-059 on I2C2: blk.haptics (#44), blk.tpm (#45) and
blk.nfc-tag (#41). Prototypes fit every option (BRD-053).

Sources: BOM v1 lines 122-126 and the v1.7 and v1.8 changes (G5, G6, G20); pinout v1 §3 (Radio,
NFC, sensors, key holder) and the expander table (P04); feature blocks records 41, 44, 45; TI
SLOS854D (DRV2605L), Infineon OPTIGA TPM SLB 9673 data sheet Rev. 1.3, NXP NT3H2111_2211 Rev. 3.6;
the parts-lib sheets."""

from __future__ import annotations

from blocks_audio import grp, ic_group, link_group
from draw import Flow, Group, corner_notes, tp
from sch import snap


def sheets(proj):
    hap = proj.sheet("haptics.kicad_sch", "blk.haptics", "Haptic driver",
                     "DRV2605L LRA driver on I2C2 at 0x5A and the actuator contacts", "A4")
    tpm = proj.sheet("tpm.kicad_sch", "blk.tpm", "Hardware key holder",
                     "SLB9673 TPM 2.0 on I2C2 at 0x2E, always on", "A4")
    tag = proj.sheet("nfc-tag.kicad_sch", "blk.nfc-tag", "NFC tag",
                     "NTAG I2C plus on I2C2 at 0x55, field detect and the loop antenna contacts", "A4")
    rdr = proj.sheet("nfc-reader.kicad_sch", "blk.nfc-reader", "NFC controller",
                     "PN7160 on I2C2 at 0x28: NFC_VBAT switch, EMC filter, matching, RX path and 27.12 MHz crystal", "A3")
    rp = proj.sheet("rp2354.kicad_sch", "blk.rp2354", "Coprocessor",
                    "RP2354A orchestration coprocessor, drawn on two sub-sheets", "A4")
    rp.kids = {
        "rp2354-core": proj.sheet("rp2354-core.kicad_sch", "blk.rp2354-core", "Coprocessor: RP2354A",
                                  "System and GPIO units, 12 MHz oscillator, BOOTSEL, USB series, I2S taps, test pads", "A3"),
        "rp2354-power": proj.sheet("rp2354-power.kicad_sch", "blk.rp2354-power", "Coprocessor: supplies",
                                   "RP2354A supply unit, core regulator, RP_3V3 and RP_IOVDD_1V8 switches and links", "A3"),
    }
    return hap, tpm, tag, rdr, rp


def column(s, f, w=100.0):
    """A column of groups right of what the flow placed so far (a link above its block's pads)."""
    col = Flow(s, x0=snap(f.x_right + f.gap))
    col.x_max = col.x0 + w
    return col


def pads(s, title, nets, key="TP"):
    """Pads in a row: contact pads of parts in the case (KEY "TP", 1.0 mm) or, with KEY None, test
    pads sized by their net (PCB-D-06)."""
    def draw():
        g = Group(s, title)
        for i, net in enumerate(nets):
            x = 116.84 + i * 17.78
            tp(s, x, 101.6, net, text="left", key=key)
            s.point(net, x, 101.6, "down", "pas")
            g.add((x - 2.54 - len(net) * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + len(net) * 1.16))
        return g.close()
    return draw


# ---------------------------------------------------------------------- blk.haptics

def draw_haptics(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "DRV2605L at I2C2 0x5A (BOM v1 line 123)", "texas-instruments", "DRV2605LDGSR",
        {"SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "EN": "HAPTIC_EN", "IN/TRIG": "GND", "OUT+": "LRA_P",
         "OUT-": "LRA_N", "REG": "HAPTIC_REG", "VDD": "HAPTIC_VDD", "VDD/NC": "HAPTIC_VDD", "GND": "GND"},
        rows=[[("C_1u_0402", "HAPTIC_VDD", "GND"), ("C_1u_0402", "HAPTIC_REG", "GND")]]))
    col = column(s, f)
    grp(col, lambda: link_group(s, "LINK_M", "vcc3v3_sys", "HAPTIC_VDD", variants, "Link #19"))
    grp(col, pads(s, "LRA contacts (BOM v1 line 124)", ("LRA_P", "LRA_N")))
    s.iface_rows = [["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x5A; pull-ups on blk.soc-pmuio"],
                    ["HAPTIC_EN", "Input", "Expander P04, pulled down on blk.gpio-expander: standby"]]
    s.rail_rows = [["HAPTIC_VDD", "1 µF", "SLOS854D Table 32"], ["HAPTIC_REG", "1 µF", "SLOS854D Table 32"]]
    corner_notes(s, [
        "1. Function: DRV2605L closed-loop LRA driver with auto-resonance (BRD-058, should) for the",
        "   Vybronics VG1040003D coin LRA on the case; mainline drv260x (DKMS on Debian).",
        "2. Absent state: EN low: standby; unfitted: 0x5A free, LRA contacts open.",
        "3. IN/TRIG to GND (effects over I2C, SLOS854D p. 5); VDD/NC tied to VDD.",
        "4. VDD from vcc3v3_sys through link #19, 0.1 Ω (power tree §4.12: 0.1 A est., 10 mV).",
    ])


# ---------------------------------------------------------------------- blk.tpm

def draw_tpm(s, variants):
    f = Flow(s)
    pins = {"SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "RST#": "TPM_RST_N", "TEST#": "TPM_VDD",
            "GPIO_00": None, "GPIO_01": None, "GPIO_02": None, "NCI": None, "NC": None, "I2C_PIRQ#": "TPM_PIRQ_N",
            "VDD": "TPM_VDD", "NCI/VDD": "TPM_VDD", "GND": "GND", "NCI/GND": "GND", "EP": "GND"}
    grp(f, lambda: ic_group(
        s, "SLB9673 TPM 2.0 at I2C2 0x2E (BOM v1 line 122)", "infineon", "SLB9673XU20FW2613XTMA1", pins,
        rows=[[("C_1u_0402", "TPM_VDD", "GND"), ("C_100n_0402", "TPM_VDD", "GND"),
               ("C_100n_0402", "TPM_VDD", "GND"), ("C_100n_0402", "TPM_VDD", "GND")],
              [("R_2k2", "TPM_VDD", "TPM_RST_N")]], pad_left=15.24, rows_dx=5.08))
    grp(f, lambda: link_group(s, "LINK_M", "vcca1v8_pmu", "TPM_VDD", variants, "Link #20"))
    s.iface_rows = [["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x2E; pull-ups on blk.soc-pmuio"],
                    ["TPM_RST_N", "Input", "GPIO0_D3; 2.2 kΩ pull-up here wins over the SoC pull-down"],
                    ["TPM_PIRQ_N", "Output", "Open drain; pull-up on vcc_1v8 on blk.soc-vccio-a"]]
    s.rail_rows = [["TPM_VDD", "1 µF + 3 x 100 nF", "SLB9673 DS Figure 2"]]
    corner_notes(s, [
        "1. Function: SLB9673 TPM 2.0, the keystore's hardware key holder (BRD-059, should; OS-032);",
        "   mainline tpm_tis_i2c (DKMS on Debian).",
        "2. Absent state: unfitted: 0x2E free; reset pulled to its inactive level; PIRQ pulled up.",
        "3. Always on (vcca1v8_pmu, G5). TEST# held high; GPIO_00-02, NC and NCI open (DS Table 4).",
        "4. VDD from vcca1v8_pmu through link #20, 0.1 Ω (power tree §4.12: 30 mA est., 3 mV).",
    ])


# ---------------------------------------------------------------------- blk.nfc-tag

def draw_tag(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "NT3H2111 NTAG I2C plus at I2C2 0x55 (BOM v1 line 125)", "nxp", "NT3H2111W0FHKH",
        {"SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "FD": "NFC_FD_N", "LA": "NFC_TAG_LA", "LB": "NFC_TAG_LB",
         "VOUT": None, "VCC": "NFC_TAG_VCC", "VSS": "GND"},
        rows=[[("C_100n_0402", "NFC_TAG_VCC", "GND")]]))
    col = column(s, f)
    grp(col, lambda: link_group(s, "LINK_L10", "vcca1v8_pmu", "NFC_TAG_VCC", variants, "Link #33"))
    grp(col, pads(s, "Loop antenna contacts (BOM v1 line 126)", ("NFC_TAG_LA", "NFC_TAG_LB")))
    s.iface_rows = [["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x55; pull-ups on blk.soc-pmuio"],
                    ["NFC_FD_N", "Output", "Open drain, field detect; 4.7 kΩ pull-up on blk.soc-pmuio; wake on tap"]]
    s.rail_rows = [["NFC_TAG_VCC", "100 nF", "Capture choice: the DS gives no value (UNVERIFIED)"]]
    corner_notes(s, [
        "1. Function: NTAG I2C plus dynamic tag for tap-to-pair (BRD-057, should): phones read it with",
        "   the T1 off; the T1 writes it over I2C2.",
        "2. Absent state: unfitted: 0x55 free; FD pulled up. Always on (vcca1v8_pmu, G6).",
        "3. VOUT (energy harvesting) not used: open. The loop antenna (about 20 x 30 mm, line 126) and",
        "   its tuning against the 50 pF input are open items; the tag with VCC at 0 V and a live I2C2",
        "   is UNVERIFIED (G6).",
        "4. VCC from vcca1v8_pmu through link #33, 10 Ω (power tree §4.12: 1 mA est., UNVERIFIED).",
    ])


# ---------------------------------------------------------------------- blk.nfc-reader

def draw_reader(s, variants):
    """blk.nfc-reader (#42): PN7160 (BOM v1 line 127) with the front end of line 128: EMC filter,
    matching and RX path per NXP AN13219 Rev. 1.6, supplies per AN12988 Rev. 1.6 Table 9, the
    27.12 MHz crystal per the PN7160 DS Rev. 4.2 Table 17 and AN14518 Rev. 6.0 Table 9."""
    from draw import ic, prow
    from parts import PARTS, fields
    import library
    f = Flow(s)
    pins = {"I2C_SCL/SPI_SCK": "I2C2_SCL", "I2C_SDA/SPI_MISO": "I2C2_SDA", "I2C_ADR0/SPI_NSS": "",
            "I2C_ADR1/SPI_MOSI": "", "VEN": "NFC_VEN", "DWL_REQ": "NFC_DWL_REQ", "WKUP_REQ": "",
            "NFC_CLK_XTAL1": "NFC_XTAL1", "XTAL2": "NFC_XTAL2", "i.c.": None, "n.c.": None, "IRQ": "NFC_IRQ",
            "CLK_REQ": None, "DCDC_EN": None, "TX1": "NFC_TX1", "TX2": "NFC_TX2", "RXP": "NFC_RXP", "RXN": "NFC_RXN",
            "VDD(VMID)": "NFC_VMID", "ANT1": None, "ANT2": None, "VDD(HF)": None,
            "VBAT": "NFC_VBAT", "VBAT2": "NFC_VBAT", "VDD(UP)": "NFC_VBAT", "VDD(PAD)": "",
            "VDD(TX)": "NFC_TVDD", "TVDD_IN": "NFC_TVDD", "TVDD_IN2": "NFC_TVDD",
            "VDD": "NFC_VDD", "VDD(A)": "NFC_VDD", "VDD(D)": "NFC_VDD",
            "VSS(PAD)": "GND", "VSS(A)": "GND", "VSS(TX)": "GND", "VSS": "GND"}
    def controller():
        from draw import row_need
        g = Group(s, "PN7160 at I2C2 0x28 (BOM v1 line 127; AN12988 Table 9)")
        u = ic(s, "nxp", "PN7160A1HN-C100E", 101.6, 101.6, pins)
        # VDD(PAD) sits next to VDD(TX): its rail symbol stands above the NFC_TVDD label's text
        px, py = u.pos(u.pin("6"))
        s.wire((px, py), (px, py - 15.24))
        s.power("vcca1v8_pmu", px, py - 15.24)
        # ADR0, ADR1 (0x28) and WKUP_REQ to ground on one collector left of the VEN and DWL_REQ labels
        ends = [u.pos(u.pin(k)) for k in ("1", "3", "39")]
        xc = snap(ends[0][0] - 22.86)
        for (ex, ey) in ends:
            s.wire((ex, ey), (xc, ey))
        s.wire((xc, ends[0][1]), (xc, ends[-1][1] + 2.54))
        for (_, ey) in ends[1:]:
            s.junction(xc, ey)
        s.power("GND", xc, ends[-1][1] + 2.54)
        g.add((xc - 2.54, ends[0][1], xc, ends[-1][1] + 5.08))
        g.add(u.bbox)
        g.add((u.bbox[0], py - 15.24 - 12.7, u.bbox[2], u.bbox[1]))
        rx, ry = u.bbox[2] + 12.7, u.bbox[1]          # clear of the long value above the IC
        for r in [[("C_4u7_0402_10V", "NFC_VBAT", "GND"), ("C_100n_0402", "NFC_VBAT", "GND"),
                   ("C_4u7_0402_10V", "NFC_VBAT", "GND"), ("C_2u2_0402", "NFC_TVDD", "GND"),
                   ("C_2u2_0402", "NFC_TVDD", "GND")],
                  [("C_2u2_0402", "NFC_VDD", "GND"), ("C_2u2_0402", "NFC_VDD", "GND"),
                   ("C_1u_0402", "vcca1v8_pmu", "GND"), ("C_100n_0402", "NFC_VMID", "GND")]]:
            b_ = g.add(prow(s, rx, snap(ry + row_need(r) + 3.81), r))
            ry = b_[3] + 2.54
        return g.close()
    grp(f, controller)

    def xtal():
        g = Group(s, "27.12 MHz crystal (DS Table 17; AN14518 Table 9)")
        ysym = library.load("opendap-generic", "Crystal_GND24")
        p = PARTS["Y_27M12"]
        pl = s.place(ysym, s.next_ref("Y"), 127.0, 101.6, fields=fields("Y_27M12", s.block), value=p["value"],
                     ref_at=(130.81, 96.52), val_at=(130.81, 107.95))
        s.connect(pl, "1", "NFC_XTAL1")
        s.connect(pl, "3", "NFC_XTAL2")
        s.connect(pl, "2", "GND")
        s.connect(pl, "4", "GND")
        g.add((127.0 - 7.62 - 13.97, 93.98, 127.0 + 7.62 + 13.97, 111.76))   # with the XTAL labels
        g.add(prow(s, 154.94, 109.22, [("C_15p_0402", "NFC_XTAL1", "GND"), ("C_15p_0402", "NFC_XTAL2", "GND")]))
        return g.close()
    col = column(s, f, w=120.0)
    grp(col, xtal)

    grp(col, lambda: ic_group(
        s, "NFC_VBAT switch (BOM v1 line 50)", "texas-instruments", "TPS22919DCKR",
        {"IN": "VSYS_LV", "ON": "NFC_PWR_EN", "NC": None, "VOUT": "NFC_VBAT_SRC", "QOD": "NFC_VBAT_SRC",
         "GND": "GND"}, rows=[[("C_1u_0402", "VSYS_LV", "GND")]]))
    f.x_right = col.x_right
    col2 = column(s, f, w=90.0)
    grp(col2, lambda: link_group(s, "LINK_M", "NFC_VBAT_SRC", "NFC_VBAT", variants, "Link #18"))

    def side(title, tx, emc, match, ant):
        def draw():
            g = Group(s, title)
            g.add(prow(s, 101.6, 109.22, [("L_LQW18CN_R16", tx, emc), ("C_330p_0402_2", emc, "GND"),
                                           ("C_68p_0402_2", emc, match), ("C_100p_0402_2", match, "GND"),
                                           ("R_2R7", match, ant)]))
            return g.close()
        return draw
    row2 = Flow(s, y0=snap(max(f.bottom(), col.bottom()) + 5.08))
    grp(row2, side("TX1: L0, C0, C1, C2, Rs (AN13219 §4.1.3.7)",
                   "NFC_TX1", "NFC_EMC_P", "NFC_MATCH_P", "NFC_ANT_P"))
    grp(row2, side("TX2: as TX1", "NFC_TX2", "NFC_EMC_N", "NFC_MATCH_N", "NFC_ANT_N"))

    def rx():
        g = Group(s, "RX: Rrx, Crx (AN13219 §6.1)")
        g.add(prow(s, 101.6, 109.22, [("R_2k2", "NFC_EMC_P", "NFC_RXP_R"), ("C_1n_0402", "NFC_RXP_R", "NFC_RXP"),
                                       ("R_2k2", "NFC_EMC_N", "NFC_RXN_R"), ("C_1n_0402", "NFC_RXN_R", "NFC_RXN")]))
        return g.close()
    grp(col2, rx)
    # the contacts close the TX row, whose paths end at them (the column keeps to the frame)
    grp(row2, pads(s, "Antenna contacts (BOM v1 lines 126, 127)", ("NFC_ANT_P", "NFC_ANT_N")))

    s.iface_rows = [
        ["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x28 (ADR0, ADR1 low); pull-ups on blk.soc-pmuio. Unfitted: 0x28 free"],
        ["NFC_VEN, NFC_DWL_REQ", "Input", "GPIO2_C0, GPIO2_C6 at 1.8 V; SoC pull-downs: hard power-down, normal boot"],
        ["NFC_IRQ", "Output", "GPIO0_D5; SoC pull-down: no interrupt unfitted"],
        ["NFC_PWR_EN", "Input", "Expander P05, 100 kΩ pull-down on blk.gpio-expander: NFC_VBAT off"],
    ]
    s.rail_rows = [
        ["NFC_VBAT", "4.7 µF + 100 nF (VBAT), 4.7 µF (VDD(UP))", "AN12988 Table 9: Cvbat, Cvbat1, Cvdd(up)"],
        ["NFC_TVDD", "2 x 2.2 µF", "AN12988 Table 9: Ctvdd1, Ctvdd2 (2 against derating)"],
        ["NFC_VDD", "2 x 2.2 µF", "AN12988 Table 9: Cvdd1, Cvdd2, one at VDD(D), one at VDD(A)"],
        ["vcca1v8_pmu, NFC_VMID", "1 µF (VDD(PAD)), 100 nF (VDD(VMID))", "AN12988 Table 9: Cvdd(pad), Cvdd(mid)"],
        ["VSYS_LV", "1 µF at the switch input", "Capture choice (SLVSEN5B)"],
    ]
    corner_notes(s, [
        "1. Function: PN7160 NFC controller, reader and T1-to-T1 hand-off (BRD-057, should); nxp-nci",
        "   over I2C2. Fitted on prototypes, DNP option in production (BOM v1 line 127).",
        "2. Absent state: unfitted or NFC_PWR_EN low: VEN and DWL_REQ held low by the SoC, IRQ pulled",
        "   down, 0x28 free. VEN must not go high before NFC_VBAT (DS §11.5.2; driver rule).",
        "3. NFC_VBAT = VSYS_LV 3.8 V through a TPS22919 and link #18 (power tree §4.12): VBAT, VBAT2",
        "   and VDD(UP) (DS Table 30: 2.8-5.5 V reader). VDD(PAD) on the always-on vcca1v8_pmu.",
        "4. Front end: L0 160 nH and C0 330 pF (EMC cut-off about 22 MHz, asymmetrical), C1 68 pF,",
        "   C2 100 pF, Rs 2.7 Ω: the first-iteration values of AN13219 §4.1.3.7 for its example",
        "   antenna. They are retuned with a VNA on the T1's antenna (BOM line 126, open: shared",
        "   loop or own) before any measurement. Tolerances (AN13219 Table 5): L0 5 %; C0, C1, C2",
        "   C0G 2 %, 50 V; Rs 1 %.",
        "5. Crystal NX2016SA (CL 10 pF); 15 pF each side from CL = 10 pF with Ci 2 pF (DS Table 46)",
        "   and the EVK's PCB parasitics (AN14518 Table 2): UNVERIFIED until the offset is measured",
        "   (-5 to 0 ppm, AN14518 §7.2); the NDK pad assignment on the 2016 land is UNVERIFIED.",
        "6. Open: WKUP_REQ tied low (host wakes the PN7160 over I2C); CLK_REQ, DCDC_EN, i.c., n.c.,",
        "   VDD(HF), ANT1 and ANT2 open (AN12988 §6.2.2; the optional field detector is not used).",
    ])


# ---------------------------------------------------------------------- blk.rp2354

RP_GPIO = {"GPIO0": "RP_UART_TX", "GPIO1": "RP_UART_RX", "GPIO2": "RP_IRQ", "GPIO3": "RP_SPARE",
           "GPIO4": "RP_TAP_BCLK", "GPIO5": "RP_TAP_LRCK", "GPIO6": "RP_TAP_SDO0", "GPIO7": "RP_TAP_DSD_L",
           "GPIO8": "RP_TAP_DSD_R"}        # pinout v1 §3, Coprocessor: RP2354A GPIO allocation (2026-10-26)
TAPS = [("I2S_BCLK", "RP_TAP_BCLK"), ("I2S_LRCK", "RP_TAP_LRCK"), ("I2S_SDO0", "RP_TAP_SDO0"),
        ("DSD_L", "RP_TAP_DSD_L"), ("DSD_R", "RP_TAP_DSD_R")]


def rp_unit(s, ref, unit, mapping, title, rows=(), rows_dx=5.08):
    """One unit of the RP2354A (kicad-lib raspberry-pi:RP2354A, three units) with passive rows."""
    from draw import ic as _ic, prow, row_need, unit_box, unit_extent
    import library
    sym = library.load("raspberry-pi", "RP2354A")
    g = Group(s, title)
    pl = s.place(sym, ref, 101.6, 101.6, unit=unit, fields={"Block": s.block})
    s.connect_all(pl, mapping)
    bx0, by0, bx1, by1 = unit_box(sym, unit)
    l_, r_, t_, b_ = unit_extent(sym, unit, mapping)
    box = (snap(101.6 + bx0 - l_), snap(101.6 + by0 - t_), snap(101.6 + bx1 + r_), snap(101.6 + by1 + b_))
    g.add(box)
    rx, ry = box[2] + rows_dx, box[1]
    for r in rows:
        b = g.add(prow(s, rx, snap(ry + row_need(r) + 3.81), r))
        ry = b[3] + 2.54
    return g.close()


def draw_rp2354(parent, variants):
    """blk.rp2354 (#46): RP2354A (BOM v1 line 12) with IOVDD at 1.8 V, its core regulator (line 13),
    12 MHz oscillator (line 14), BOOTSEL FET (line 35), SWD pads (line 89), tap positions (line 134),
    rails through two TPS22919 (line 50) and links #21 and #30 (power tree §4.12). One reference,
    its three units on two sub-sheets (as blk.soc)."""
    from draw import part, prow
    ref = parent.next_ref("U")
    corner_notes(parent, [
        "1. Function: RP2354A orchestration coprocessor (BRD-014, should); flashed by Blackbird OS over",
        "   SWD or USB BOOTSEL (BRD-015); never in a data path (BRD-005); the SoC boots without it (BRD-019).",
        "2. Absent state: unfitted or RP_PWR_EN low: rails off; RP_IRQ low (no wake); UART, SWD and RUN",
        "   parked low by the SoC; the I2S taps reach FT pads only (3.63 V at IOVDD 0 V, G4).",
        "3. Drawn on two sub-sheets (blk.rp2354-core, blk.rp2354-power) holding the units of one part.",
    ])
    s = parent.kids["rp2354-core"]
    f = Flow(s)
    sysmap = {"26": "RP_RUN", "24": "RP_SWCLK", "25": "RP_SWDIO", "21": "RP_XIN", "22": None,
              "60": "RP_QSPI_SS", "56": None, "57": None, "59": None, "58": None, "55": None,
              "52": "RP_USB_DP_R", "51": "RP_USB_DM_R"}
    grp(f, lambda: rp_unit(s, ref, 1, sysmap, "RP2354A system: RUN, SWD, clock, BOOTSEL, USB (BOM v1 line 12)",
                           rows=[[("R_4k7", "RP_IOVDD_1V8", "RP_RUN")],
                                 [("R_27", "RP_USB_DP", "RP_USB_DP_R"), ("R_27", "RP_USB_DM", "RP_USB_DM_R")]]))
    gmap = {str(p): None for p in [13, 14, 15, 16, 17, 18, 19, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43]}
    for name, net in RP_GPIO.items():
        gmap[name] = net
    grp(f, lambda: rp_unit(s, ref, 2, gmap, "RP2354A GPIO (pinout v1 §3 allocation)"))
    col = column(s, f, w=130.0)

    def taps():
        g = Group(s, "Tap 0 Ω positions (BOM v1 line 134; PCB-A-12), RP_IRQ pull-down")
        g.add(prow(s, 101.6, 109.22, [("R_0_0402", a, b) for a, b in TAPS] + [("R_100k", "RP_IRQ", "GND")]))
        return g.close()

    def bootsel():
        g = Group(s, "BOOTSEL: N-FET on QSPI_SS (BOM v1 line 35; pinout v1 C6)")
        g.add(prow(s, 101.6, 109.22, [("R_1k", "RP_QSPI_SS", "RP_BOOTSEL_D"), ("R_100k", "RP_BOOTSEL_DRV", "GND")]))
        part(s, "Transistor_FET", "DMG1012T", 139.7, 116.84, {"1": "RP_BOOTSEL_DRV", "3": "RP_BOOTSEL_D", "2": "GND"},
             key="Q_DMG1012T", prefix="Q")
        g.add((127.0, 101.6, 152.4, 129.54))
        return g.close()

    def osc():
        from draw import ic as _ic
        g = Group(s, "12 MHz oscillator on RP_IOVDD_1V8 (BOM v1 line 14)")
        u = _ic(s, "ecs", "ECS-2016MV-120-BN-TR", 101.6, 101.6,
                {"TRI-STATE": None, "OUTPUT": "RP_XIN", "VDD": "RP_IOVDD_1V8", "GND": "GND"}, prefix="Y", value="12 MHz")
        g.add(u.bbox)
        g.add(prow(s, u.bbox[2] + 15.24, 109.22, [("C_100n_0402", "RP_IOVDD_1V8", "GND")]))
        return g.close()
    grp(col, osc)
    grp(col, pads(s, "Test pads (BOM v1 line 89; PCB-T-09)",
                  ("RP_SWCLK", "RP_SWDIO", "RP_RUN", "RP_QSPI_SS", "RP_SPARE"), key=None))
    row2 = Flow(s, y0=snap(max(f.bottom(), col.bottom()) + 5.08))
    grp(row2, taps)
    grp(row2, bootsel)
    core_tables(s)
    s = parent.kids["rp2354-power"]
    f = Flow(s)

    pmap = {"1": "RP_IOVDD_1V8", "11": "RP_IOVDD_1V8", "20": "RP_IOVDD_1V8", "30": "RP_IOVDD_1V8",
            "38": "RP_IOVDD_1V8", "45": "RP_IOVDD_1V8", "54": "RP_3V3", "53": "RP_3V3", "44": "RP_3V3",
            "49": "RP_3V3", "46": "RP_VREG_AVDD", "6": "RP_DVDD", "23": "RP_DVDD", "39": "RP_DVDD",
            "48": "RP_VREG_SW", "50": "RP_DVDD", "47": "GND", "EP": "GND"}

    def power():
        g = Group(s, "RP2354A supplies, core regulator (DS §6.1, §6.3.8; HDG §2.2.1)")
        # fed through the inductor and through the 33 Ω filter: flags on their output stubs
        s.flag_net("RP_DVDD", since=s.mark()[1], side="down")
        s.flag_net("RP_VREG_AVDD", since=s.mark()[1], side="down")
        g.add(rp_unit(s, ref, 3, pmap, "", rows=[
            [("C_100n_0402", "RP_IOVDD_1V8", "GND")] * 6,
            [("C_4u7_0402", "RP_3V3", "GND"), ("C_100n_0402", "RP_3V3", "GND"), ("C_100n_0402", "RP_3V3", "GND"),
             ("C_100n_0402", "RP_3V3", "GND")],
            [("C_4u7_0402", "RP_DVDD", "GND"), ("C_100n_0402", "RP_DVDD", "GND"), ("C_100n_0402", "RP_DVDD", "GND"),
             ("R_33", "RP_3V3", "RP_VREG_AVDD"), ("C_4u7_0402", "RP_VREG_AVDD", "GND")],
            [("L_AOTA_3R3", "RP_VREG_SW", "RP_DVDD")]]))
        return g.close()
    grp(f, power)

    col = column(s, f, w=110.0)
    grp(col, lambda: ic_group(
        s, "RP_3V3 switch (BOM v1 line 50)", "texas-instruments", "TPS22919DCKR",
        {"IN": "vcc3v3_sys", "ON": "RP_PWR_EN", "NC": None, "VOUT": "RP_3V3_SRC", "QOD": "RP_3V3_SRC",
         "GND": "GND"}, rows=[[("C_1u_0402", "vcc3v3_sys", "GND")]]))
    grp(col, lambda: ic_group(
        s, "RP_IOVDD_1V8 switch (BOM v1 line 50)", "texas-instruments", "TPS22919DCKR",
        {"IN": "vcc_1v8", "ON": "RP_PWR_EN", "NC": None, "VOUT": "RP_IOVDD_1V8_SRC", "QOD": "RP_IOVDD_1V8_SRC",
         "GND": "GND"}, rows=[[("C_1u_0402", "vcc_1v8", "GND")]]))
    f.x_right = col.x_right
    col2 = column(s, f, w=100.0)
    grp(col2, lambda: link_group(s, "LINK_M", "RP_3V3_SRC", "RP_3V3", variants, "Link #21"))
    grp(col2, lambda: link_group(s, "LINK_L1", "RP_IOVDD_1V8_SRC", "RP_IOVDD_1V8", variants, "Link #30"))

    s.iface_rows = [
        ["RP_PWR_EN", "Input", "Both switches; SoC pull-down and the TPS22919 ON pull-down: off (BRD-019)"],
        ["RP_IOVDD_1V8, RP_3V3", "Supply out", "To blk.rp2354-core (pull-ups, oscillator); off with RP_PWR_EN low"],
    ]
    s.rail_rows = RP_RAILS
    corner_notes(s, [
        "1. Function: the RP2354A supply unit with its core regulator (3.3 µH, DS §6.3.8) and the two",
        "   switched rails RP_3V3 (VREG, QSPI, USB, ADC) and RP_IOVDD_1V8 (IOVDD at 1.8 V, BOM v1 line 12).",
        "2. Absent state: RP_PWR_EN low: both switches off (QOD discharges), the part unpowered.",
        "3. VREG_VIN and VREG_AVDD ramp together from RP_3V3 (DS §6.1.8); VREG_AVDD through 33 Ω + 4.7 µF.",
        "4. Links #21 (RP_3V3, 0.1 Ω) and #30 (RP_IOVDD_1V8, 1 Ω), power tree §4.12. The inductor's",
        "   polarity dot faces VREG_LX as in DS Figure 28: UNVERIFIED until checked on the Pico 2 layout.",
    ])


def core_tables(s):
    s.iface_rows = [
        ["RP_UART_TX, RP_UART_RX", "Bidirectional", "UART0 to the SoC's UART0 (PMUIO2); SoC pull-downs park both"],
        ["RP_IRQ", "Output", "GPIO2 to 1V20 (wake): 100 kΩ pull-down here, no wake when off or unfitted"],
        ["RP_RUN, RP_SWCLK, RP_SWDIO", "Input", "SoC open drain / SWD (VCCIO6); parked low while the rails are off (G4)"],
        ["RP_BOOTSEL_DRV", "Input", "N-FET gate, 100 kΩ pull-down: normal boot"],
        ["RP_USB_DP, RP_USB_DM", "Bidirectional", "USB_HOST2 (EHCI/OHCI) of the SoC"],
        ["I2S_BCLK, I2S_LRCK, I2S_SDO0, DSD_L, DSD_R", "Input", "Taps on FT GPIO4-8 through 0 Ω (G4); no load on the DAC path"],
    ]
    s.rail_rows = [["RP_IOVDD_1V8", "100 nF at the oscillator", "ECS-2016MV (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: RP2354A system and GPIO units (BRD-014, should; BRD-015, BRD-041): UART0 and",
        "   RP_IRQ to the SoC, SWD and RUN from it, BOOTSEL, USB to USB_HOST2, passive I2S/DSD taps.",
        "2. Absent state: unfitted or unpowered: RP_IRQ held low here; UART, SWD, RUN parked low by the",
        "   SoC; taps on FT pads (G4), 0 Ω positions keep a series value possible at bring-up.",
        "3. IOVDD at 1.8 V: firmware sets VOLTAGE_SELECT = 1 for bank 0 at boot (DS §6.1.1).",
        "4. QSPI pads go to the in-package flash only: open here (HDG §3.1); BOOTSEL pulls QSPI_SS low",
        "   through 1 kΩ and the N-FET. USB: 27 Ω series at the RP2354A (DS Table 1678).",
        "5. GPIO allocation (pinout v1 §3, 2026-10-26): UART0 GPIO0/1, RP_IRQ GPIO2, spare GPIO3 (pad),",
        "   taps GPIO4-8 for one PIO IN (DS §11.5.6); GPIO9-29 open. The I2C2 option is not wired (G16).",
    ])


RP_RAILS = [
        ["RP_IOVDD_1V8", "6 x 100 nF", "DS §6.1: 100 nF per power pin"],
        ["RP_3V3", "4.7 µF (VREG_VIN) + 3 x 100 nF", "DS §6.1, §6.3.8 (CIN 4.7 µF); QSPI_IOVDD, USB_OTP_VDD, ADC_AVDD"],
        ["RP_DVDD", "4.7 µF at pin 23 + 2 x 100 nF", "HDG §2.2.1: 4.7 µF on the furthest DVDD pin"],
        ["RP_VREG_AVDD", "33 Ω + 4.7 µF", "HDG p. 7 (RC filter)"],
        ["vcc3v3_sys, vcc_1v8", "1 µF at each switch input", "Capture choice (SLVSEN5B)"],
]
