"""blk.charger (feature blocks #7) and blk.gauge (#8): the input mux, the 2S charger, the battery
path from the BQ25798 BAT node to the six battery contacts, and the fuel gauge.

Sources: board ADRs 0014, 0017, 0020; BOM v1 lines 39-48, 104, 115, 120, 142; power tree v0 §2,
§4.7, §4.7.1; pinout v1 (I2C1, CHG_INT_N, expander P02 and P03); feature blocks §3 records 7 and 8;
TI SLUSDV2C (BQ25798), SLVSEA3F (TPS2121), SLUSE07B Figure 9-1 (BQ28Z610-R1); the parts-lib
sheets."""

from __future__ import annotations

from blocks_audio import grp, ic_group, parts_group, tvs_group, two_pin_box
from draw import Flow, Group, corner_notes, ic, part, prow, tp
from sch import snap


KIDS = ["charger-input", "charger-core", "charger-battery"]


def sheets(proj):
    charger = proj.sheet("charger.kicad_sch", "blk.charger", "Charger and battery path",
                         "TPS2121 input mux, BQ25798 2S charger, ship FET, fuse and the six battery contacts", "A4")
    kids = {
        "charger-input": proj.sheet("charger-input.kicad_sch", "blk.charger-input", "Charger: input mux",
                                    "TPS2121 picks USB-C or the HAT port into VBUS_CHG; the OV interlocks", "A3"),
        "charger-core": proj.sheet("charger-core.kicad_sch", "blk.charger-core", "Charger: BQ25798",
                                   "2S buck-boost charger, its inductor and capacitors; VSYS out", "A3"),
        "charger-battery": proj.sheet("charger-battery.kicad_sch", "blk.charger-battery", "Charger: battery path",
                                      "Ship FET, 5 A fuse, BATP and the six battery contacts with their ESD", "A3"),
    }
    gauge = proj.sheet("gauge.kicad_sch", "blk.gauge", "Fuel gauge",
                       "BQ28Z610-R1 on the pack side, its 3 mΩ sense resistor and board NTC (ADR 0017)", "A3")
    return charger, kids, gauge


def rail_probe(s, net, x, y, flag=False):
    """A test pad on a rail (PCB-T-02): the pad, a short wire and the rail's power symbol; with
    flag, the rail's PWR_FLAG hangs from that wire (a rail no output pin on the sheet drives).
    Returns the bbox."""
    tp(s, x, y, net, text="left", key="TP")
    s.wire((x, y), (x + 10.16, y))
    s.attach(net, x + 10.16, y, "up")
    if flag:
        s.flag_at(x + 5.08, y, "down", 2.54)
    from sch import RAILS
    top = y - 7.62 if net in RAILS else y - 2.54 - len(net) * 1.16 - 2.54   # a label reads upward
    return (x - 1.27 - len(net) * 1.16 - 2.54, top, x + 10.16 + len(net) * 0.58 + 2.54, y + 10.16)


def or_diode(s, x, y, anode, cathode):
    """A BAT54J from anode (left) to cathode (right), its text above the body and its labels on
    5.08 mm stubs clear of it. Returns the bbox."""
    part(s, "Diode", "BAT54J", x, y, {"2": anode, "1": cathode}, key="D_BAT54J", angle=180, prefix="D",
         ref_at=(x, y - 6.35), val_at=(x, y - 3.81), stub=5.08)
    return (x - 7.62 - len(anode) * 1.27 - 2.54, y - 8.89, x + 7.62 + len(cathode) * 1.27 + 2.54, y + 2.54)


# ---------------------------------------------------------------------- blk.charger

def draw_parent(s):
    corner_notes(s, [
        "1. Function: TPS2121 picks USB-C (IN1, priority) or the HAT port (IN2) into VBUS_CHG; the",
        "   BQ25798 charges the 2S pack and makes VSYS (6.0-8.8 V); the ship FET (SDRV) and the 5 A fuse",
        "   join the BQ25798 BAT node to the six battery contacts (feature blocks #7; ADR 0014, 0020).",
        "2. Absent state: never omitted. Pack out: with no adapter the BQ25798 is unpowered and the ship",
        "   FET off, so an inserted pack meets a soft start; with an adapter it reports no battery.",
        "3. Drawn on three sub-sheets (blk.charger-*), sheets of blk.charger as the SoC's sub-sheets.",
        "4. SYS leaves as VSYS_SRC; the VSYS INA236 shunt (10 mΩ, blk.current-monitors) makes VSYS.",
    ])


def draw_input(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "Input mux: TPS2121, USB-C on IN1 with priority (BOM v1 line 45)", "Texas_Instruments", "TPS2121RUXR",
        {"IN1": "USBC_VBUS", "IN2": "HAT_5V", "OUT": "VBUS_CHG", "OV1": "MUX_OV1", "OV2": "MUX_OV2",
         "PR1": "MUX_PR1", "CP2": "GND", "ST": "MUX_ST", "ILM": "MUX_ILM", "SS": "MUX_SS", "GND": "GND"},
        rows=[[("R_1M02", "USBC_VBUS", "MUX_OV1"), ("R_100k", "MUX_OV1", "GND"),
               ("R_464k", "HAT_5V", "MUX_OV2"), ("R_100k", "MUX_OV2", "GND")],
              [("R_31k6", "USBC_VBUS", "MUX_PR1"), ("R_10k", "MUX_PR1", "GND"),
               ("R_45k3_TF", "MUX_ILM", "GND"), ("C_100n_0402", "MUX_SS", "GND")],
              [("C_1u_0402_25V", "USBC_VBUS", "GND"), ("C_1u_0402_25V", "HAT_5V", "GND")]],
        extra={"Constraints": "PCB-P-01"}))

    def interlock():
        g = Group(s, "OV interlocks (BOM v1 line 45)")
        for i, (src, node) in enumerate((("USB_SRC_ON", "MUX_OV1"), ("HAT5V_EN", "MUX_OV2"))):
            y = 101.6 + i * 12.7
            g.add(or_diode(s, 116.84, y, src, node))
        return g.close()
    grp(f, interlock)

    def probes():
        g = Group(s, "Test pads (PCB-T-02)")
        for i, (net, flag) in enumerate((("USBC_VBUS", False), ("HAT_5V", False), ("VBUS_CHG", False))):
            g.add(rail_probe(s, net, 116.84 + i * 33.02, 101.6, flag))
        x = 116.84 + 3 * 33.02
        tp(s, x, 101.6, "MUX_ST", text="left")
        s.point("MUX_ST", x, 101.6, "down", "pas")
        g.add((x - 2.54 - 6 * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + 6 * 1.16))
        return g.close()
    grp(f, probes, newline=True)
    s.iface_rows = [
        ["USBC_VBUS", "Supply in", "From blk.usb-c: 5-12 V PD sink; TVS2200 there"],
        ["HAT_5V", "Supply in / out", "HAT port VBUS (blk.hat-5v): IN2 sinks 5 V only (BOM v1.14)"],
        ["USB_SRC_ON, HAT5V_EN", "Input", "Expander P03, P02: high while the T1 sources the port; forces OVx high"],
        ["VBUS_CHG", "Supply out", "To the BQ25798 VBUS, VAC1, VAC2 (blk.charger-core)"],
    ]
    s.rail_rows = [["USBC_VBUS, HAT_5V", "1 µF 25 V each at IN1, IN2", "SLVSEA3F §11 (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: TPS2121 picks USB-C (IN1, priority above 4.4 V) or the HAT port (IN2) into VBUS_CHG.",
        "2. Absent state: both inputs absent: VBUS_CHG off, the charger unpowered.",
        "3. OV1 1.02 MΩ / 100 kΩ (11.1-12.6 V), OV2 464 kΩ / 100 kΩ (5.60-6.31 V), RILM 45.3 kΩ 0.1 %",
        "   (1.94-2.95 A); USB_SRC_ON and HAT5V_EN force OV1 and OV2 through a BAT54J each, so the T1's",
        "   own 5 V never re-enters the charger. PR1 31.6 kΩ / 10 kΩ (4.3-4.6 V), SS 100 nF, CP2 to",
        "   GND: capture choices (SLVSEA3F Eq. 5, Table 9-1, pin table).",
        "4. ST to a test pad instead of GND (SLVSEA3F §10.2.3): high when IN1 feeds the output, read",
        "   at bring-up with a pull-up on the probe.",
    ])


def draw_core(s, variants):
    f = Flow(s)
    pins = {"VBUS": "VBUS_CHG", "VAC1": "VBUS_CHG", "VAC2": "VBUS_CHG", "ACDRV1": "GND", "ACDRV2": "GND",
            "D+": None, "D-": None, "SCL": "I2C1_SCL", "SDA": "I2C1_SDA", "CE": "CHG_CE", "QON": "CHG_QON",
            "TS": "BAT_NTC", "ILIM_HIZ": "CHG_REGN", "PROG": "CHG_PROG",
            "PMID": "CHG_PMID", "BTST1": "CHG_BTST1", "SW1": "CHG1_SW", "SW2": "CHG2_SW", "BTST2": "CHG_BTST2",
            "SYS": "VSYS_SRC", "BAT": "VBAT", "BATP": "CHG_BATP", "SDRV": "CHG_SDRV", "REGN": "CHG_REGN",
            "STAT": "CHG_STAT", "INT": "CHG_INT_N", "GND": "GND"}
    grp(f, lambda: ic_group(
        s, "Charger: BQ25798, 1.5 MHz, 2S (BOM v1 lines 39, 115)", "Texas_Instruments", "BQ25798RQMR", pins,
        rows=[[("R_6k04", "CHG_PROG", "GND"), ("R_10k", "CHG_CE", "GND"), ("C_4u7_0603_10V", "CHG_REGN", "GND"),
               ("R_5k23", "CHG_REGN", "BAT_NTC"), ("R_30k1", "BAT_NTC", "GND"), ("R_10k", "CHG_REGN", "CHG_STAT")],
              [("C_47n_0402", "CHG_BTST1", "CHG1_SW"), ("C_47n_0402", "CHG_BTST2", "CHG2_SW"),
               ("C_47n_0402", "CHG_BATP", "GND")]],
        extra={"Constraints": "PCB-P-01 PCB-P-07"}))

    def power_stage():
        g = Group(s, "Inductor, input and output capacitors (SLUSDV2C §8.2.2)")
        g.add(two_pin_box(s, "L_XGL4015_102", 109.22, 101.6, "CHG1_SW", "CHG2_SW", prefix="L"))
        y = 127.0
        for row in ([("C_10u_0805_25V", "VBUS_CHG", "GND")] * 2 + [("C_100n_0402_50V", "VBUS_CHG", "GND")],
                    [("C_10u_0805_25V", "CHG_PMID", "GND")] * 3 + [("C_100n_0402_50V", "CHG_PMID", "GND")]):
            b = g.add(prow(s, 101.6, y, row))
            y = b[3] + 20.32                    # room for the next row's vertical label
        x = g.boxes[-1][2] + 7.62
        y = 127.0
        for row in ([("C_10u_0805_25V", "VSYS_SRC", "GND")] * 5 + [("C_100n_0402_50V", "VSYS_SRC", "GND")],
                    [("C_10u_0805_25V", "VBAT", "GND")] * 2):
            b = g.add(prow(s, x, y, row))
            y = b[3] + 12.7
        return g.close()
    grp(f, power_stage)

    def probes():
        g = Group(s, "Test pads (PCB-T-02)")
        g.add(rail_probe(s, "VSYS", 116.84, 101.6))
        for i, net in enumerate(("CHG_STAT", "CHG_QON")):
            x = 149.86 + i * 33.02
            tp(s, x, 101.6, net, text="left")
            s.point(net, x, 101.6, "down", "pas")
            g.add((x - 2.54 - len(net) * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + len(net) * 1.16))
        return g.close()
    grp(f, probes, newline=True)
    s.iface_rows = [
        ["VBUS_CHG", "Supply in", "From the TPS2121 (blk.charger-input)"],
        ["VSYS_SRC", "Supply out", "SYS output to the VSYS INA236 shunt (blk.current-monitors); never omitted"],
        ["VBAT", "Passive", "BAT node to the ship FET (blk.charger-battery)"],
        ["CHG_SDRV, CHG_BATP, BAT_NTC", "Passive", "Ship FET gate, pack-side sense, pack NTC (blk.charger-battery)"],
        ["I2C1_SCL, I2C1_SDA", "Bidirectional", "BQ25798 at 0x6B; pull-ups on blk.soc-pmuio"],
        ["CHG_INT_N", "Output", "Open drain, 256 µs pulses; pull-up on blk.soc-pmuio"],
    ]
    s.rail_rows = [
        ["VBUS_CHG", "2 x 10 µF 25 V + 100 nF", "SLUSDV2C Table 5-1, §8.2.2.3"],
        ["CHG_PMID", "3 x 10 µF 25 V + 100 nF", "SLUSDV2C Table 5-1 (no backup mode)"],
        ["VSYS_SRC", "5 x 10 µF + 100 nF (25 V parts)", "SLUSDV2C §8.2.2.4: 16 V or higher at 2S"],
        ["VBAT", "2 x 10 µF", "SLUSDV2C Table 5-1"],
        ["CHG_REGN", "4.7 µF 10 V", "SLUSDV2C Table 5-1"],
    ]
    corner_notes(s, [
        "1. Function: BQ25798 buck-boost charger for the 2S pack; VSYS 6.0-8.8 V.",
        "2. Absent state: never omitted. Unpowered without an adapter; the pack feeds VSYS through BATFET.",
        "3. PROG 6.04 kΩ (1.5 MHz, 2S, Table 7-1); ILIM_HIZ to REGN (input limit by IINDPM, BOM v1.11);",
        "   TS: 5.23 kΩ / 30.1 kΩ for a 103AT at 0-60 °C (§7.3.9.5.1), pack NTC type UNVERIFIED.",
        "4. VAC1, VAC2 on VBUS, ACDRV to GND (the TPS2121 selects the input); D+/D- open (BC1.2 not",
        "   used, line 39); CE pulled low (charging by EN_CHG); QON and STAT on test pads; STAT 10 kΩ",
        "   to REGN.",
    ])


def draw_battery(s, variants):
    f = Flow(s)

    def battery_path():
        g = Group(s, "Battery path: ship FET, 5 A fuse, BATP (ADR 0014 item 6, ADR 0017, ADR 0020 item 6)")
        q = ic(s, "Texas_Instruments", "CSD17575Q3", 116.84, 101.6, {"G": "CHG_SDRV", "S": "VBAT", "D": "BAT_F"},
               prefix="Q", extra={"Constraints": "PCB-L-09"})
        g.add(q.bbox)
        x = q.bbox[2] + 22.86
        g.add(two_pin_box(s, "F_5A", x, 101.6, "BAT_F", "BAT_P", prefix="F"))
        g.add(two_pin_box(s, "R_100", x, 116.84, "BAT_F", "CHG_BATP"))
        part(s, "Device", "D_TVS", x + 25.4, 101.6 + 10.16, {"2": "BAT_P", "1": "GND"}, key="D_TVS_DNP", angle=90,
             prefix="D", dnp=True, extra={"Alternate": "p-plus-tvs"}, in_bom=False, ref_at=(x + 25.4 + 5.4, 110.49), val_at=(x + 25.4 + 4.9, 113.03))
        g.add((x + 25.4 - 5.08, 101.6 + 10.16 - 10.16, x + 25.4 + 12.7, 101.6 + 10.16 + 10.16))
        return g.close()
    grp(f, battery_path)

    def contacts():
        g = Group(s, "Battery contacts, face compression, 3.5 mm pitch (ADR 0020 item 2; BOM v1 line 47)")
        order = [("BAT_P", "P+"), ("BAT_P", "P+"), ("BAT_MID", "mid-cell tap"), ("BAT_NTC", "NTC"),
                 ("BAT_N", "P-"), ("BAT_N", "P-")]
        for i, (net, role) in enumerate(order):
            x = 109.22 + (i % 3) * 45.72
            y = 101.6 + (i // 3) * 20.32
            u = ic(s, "KYOCERA_AVX", "70-9258-001-120-006", x, y, {"1": net}, prefix="J",
                   extra={"Contact": role, "Constraints": "PCB-L-04 PCB-L-05 PCB-L-06"})
            g.add(u.bbox)
        return g.close()
    grp(f, contacts, newline=True)
    grp(f, lambda: tvs_group(s, "Contact ESD, within 3 mm (BOM v1 line 142)", ("BAT_MID", "BAT_NTC")))

    def probes():
        g = Group(s, "Test pads (PCB-T-02; CB-07, PCB-L-09)")
        g.add(rail_probe(s, "VBAT", 116.84, 101.6, True))
        tp(s, 149.86, 101.6, "BAT_P", text="left")
        s.point("BAT_P", 149.86, 101.6, "down", "pas")
        g.add((149.86 - 2.54 - 5 * 1.16, 93.98, 149.86 + 2.54, 101.6 + 2.54 + 5 * 1.16))
        return g.close()
    grp(f, probes, newline=True)
    s.iface_rows = [
        ["VBAT", "Passive", "BQ25798 BAT node (blk.charger-core)"],
        ["CHG_SDRV, CHG_BATP", "Passive", "Ship FET gate drive and BATP sense (blk.charger-core)"],
        ["BAT_NTC", "Passive", "Pack NTC contact to the BQ25798 TS divider"],
        ["BAT_F, BAT_MID, BAT_N", "Passive", "To blk.gauge: VC2/PBI after the fuse, VC1, cell negative"],
    ]
    corner_notes(s, [
        "1. Function: the ship FET (BQ25798 SDRV) and the 5 A fuse join the BAT node to the six battery",
        "   contacts (ADR 0014 item 6, ADR 0020).",
        "2. Absent state: never omitted. Ship mode: SDRV low, the FET off, the pack disconnected.",
        "3. Pack side of the ship FET: only the gauge (VC2, PBI, VC1, sense), BATP (100 Ω, 47 nF) and",
        "   the FET (ADR 0017). P+ TVS position DNP until CB-07 and CB-10 ask for it (line 142).",
        "4. Open: the Mill-Max 0965 pogo fallback land (line 47); bring-up terminal board (ADR 0020 item 9).",
    ])


# ---------------------------------------------------------------------- blk.gauge

def draw_gauge(s, variants):
    f = Flow(s)
    pins = {"VC1": "GAUGE_VC1", "SRP": "GAUGE_SRP", "SRN": "GAUGE_SRN", "TS1": "GAUGE_TS1", "SCL": "GAUGE_SCL",
            "SDA": "GAUGE_SDA", "VC2": "GAUGE_VC2", "PBI": "GAUGE_PBI", "PACK": "GAUGE_PACK", "CHG": None,
            "DSG": None, "VSS": "BAT_N", "PWPD": "BAT_N"}
    grp(f, lambda: ic_group(
        s, "Gauge: BQ28Z610-R1, gauge only (ADR 0014, ADR 0017)", "Texas_Instruments", "BQ28Z610DRZR-R1", pins,
        rows=[[("C_100n_0402", "GAUGE_VC1", "BAT_N"), ("C_1u_0402_25V", "GAUGE_VC2", "GAUGE_VC1"),
               ("C_2u2_0402", "GAUGE_PBI", "BAT_N")],
              [("C_100n_0402", "GAUGE_SRP", "BAT_N"), ("C_100n_0402", "GAUGE_SRN", "BAT_N"),
               ("C_100n_0402", "GAUGE_SRP", "GAUGE_SRN"), ("TH_10k", "GAUGE_TS1", "BAT_N")]],
        extra={"Constraints": "PCB-P-01"}))

    def series():
        g = Group(s, "Inputs (SLUSE07B Figure 9-1)")
        s.flag_net("GAUGE_VC2", since=s.mark()[1], side="right")     # fed through R_5R1
        for i, (key, a, b) in enumerate((("R_100", "BAT_MID", "GAUGE_VC1"), ("R_5R1", "BAT_F", "GAUGE_VC2"),
                                         ("R_10R", "VBAT", "GAUGE_PACK"), ("R_100", "BAT_N", "GAUGE_SRP"),
                                         ("R_100", "GND", "GAUGE_SRN"), ("R_100", "I2C1_SCL", "GAUGE_SCL"),
                                         ("R_100", "I2C1_SDA", "GAUGE_SDA"))):
            # the row below GAUGE_VC2 one step lower, clear of its PWR_FLAG's text
            g.add(two_pin_box(s, key, 101.6, 101.6 + i * 10.16 + (5.08 if i > 1 else 0.0), a, b))
        return g.close()
    grp(f, series)

    def sense():
        g = Group(s, "Sense resistor, low side, Kelvin (ADR 0017 item 4)")
        g.add(two_pin_box(s, "R_SENSE_3m", 116.84, 101.6, "BAT_N", "GND", stub=7.62,
                          extra={"Constraints": "PCB-P-01"}))
        s.flag_at(116.84 - 3.81 - 5.08, 101.6, "down", 2.54)       # BAT_N: no output pin drives it
        g.add((101.6, 96.52, 132.08, 114.3))
        return g.close()
    grp(f, sense)

    s.iface_rows = [
        ["BAT_F", "Passive", "Pack side of the ship FET, after the 5 A fuse (blk.charger)"],
        ["BAT_MID", "Passive", "Mid-cell tap contact (blk.charger)"],
        ["BAT_N", "Passive", "P- contacts: cell negative, the gauge's VSS"],
        ["VBAT", "Passive", "BQ25798 BAT node: PACK senses the switched side (ADR 0017 item 2)"],
        ["I2C1_SCL, I2C1_SDA", "Bidirectional", "0x55; pull-ups on blk.soc-pmuio"],
    ]
    s.rail_rows = [
        ["GAUGE_VC2", "1 µF to VC1 (5 Ω in)", "SLUSE07B Figure 9-1"],
        ["GAUGE_PBI", "2.2 µF", "SLUSE07B §7.3, Figure 9-1"],
    ]
    corner_notes(s, [
        "1. Function: BQ28Z610-R1 reads both cells (VC2 after the fuse, VC1 on the tap) and counts charge",
        "   on a 3 mΩ low-side sense resistor; the pack PCM protects and balances (ADR 0014, ADR 0017).",
        "2. Absent state: never omitted. Storage: Blackbird OS sends MAC 0x0010 twice, then the BQ25798",
        "   enters shutdown mode; the ship FET opens, PACK falls and the gauge shuts down (ADR 0017 item 3).",
        "3. VSS, PWPD and every gauge capacitor return to BAT_N, the cell side of the sense resistor;",
        "   SRP to the cell side, SRN to GND, each through 100 Ω, 100 nF at the pins (SLUSE07B Figure 9-1).",
        "4. CHG and DSG open (no FETs: SLUSE07B §8.3.14; TI E2E 903283, forum guidance).",
        "5. TS1: board NTC NCP15XH103F03RC against the pocket floor (BOM v1 line 48).",
        "6. Golden image, CC Gain calibration per board: ADR 0017 items 4-5.",
    ])
