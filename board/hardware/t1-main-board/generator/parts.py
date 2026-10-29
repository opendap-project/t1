"""Part data for the parts the schematic places from KiCad's generic symbols (passives, crystal,
inductors, test pads, net ties).

Parts named by the BOM, an ADR or a datasheet carry that source in `src`. Generic passives
(capacitors and resistors whose value, rating and size come from a data sheet or the BOM but whose
orderable part the BOM does not name) are capture choices from the Murata GRM and Yageo RC
families: their stock and the effective capacitance under DC bias are not checked here (UNVERIFIED),
which the BOM pass confirms or replaces. Data-sheet links of the generic families are the makers'
product pages."""

from __future__ import annotations

MURATA = "https://www.murata.com/en-us/products/productdetail?partno="
YAGEO = "https://yageogroup.com/en/ProductSearch/PartNumberSearch?part="   # the maker's part page
VISHAY_WSL = "https://www.vishay.com/docs/30100/wsl.pdf"
TDK_MLCC = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no="


def _c(value, mpn, size, volts, diel, maker="Murata", ds=None, spec=None, src="capture choice"):
    fp = {"0201": "Capacitor_SMD:C_0201_0603Metric", "0402": "Capacitor_SMD:C_0402_1005Metric",
          "0603": "Capacitor_SMD:C_0603_1608Metric", "0805": "Capacitor_SMD:C_0805_2012Metric", "1206": "Capacitor_SMD:C_1206_3216Metric",
          "1210": "Capacitor_SMD:C_1210_3225Metric"}[size]
    return dict(kind="C", value=value, Footprint=fp,
                Datasheet=ds or (MURATA + mpn if maker == "Murata" else TDK_MLCC + mpn),
                Description=f"Capacitor, {value}, {volts} V, {diel}, {size}", Manufacturer=maker, MPN=mpn,
                spec=spec if spec is not None else f"{volts} V {diel}", src=src)


def _r(value, code, size="0402", tol="1 %", spec=None, src="capture choice", power=None):
    fp = {"0201": "Resistor_SMD:R_0201_0603Metric", "0402": "Resistor_SMD:R_0402_1005Metric", "0603": "Resistor_SMD:R_0603_1608Metric",
          "0805": "Resistor_SMD:R_0805_2012Metric", "1206": "Resistor_SMD:R_1206_3216Metric"}[size]
    series = "RC" + size
    jumper = value.startswith("0 ")
    mpn = f"{series}{'JR' if jumper else 'FR'}-07{code}L"
    desc = "Jumper, 0 Ohm, " + size if jumper else f"Resistor, {value}, {tol}, {power or {'0201': '1/20 W', '0402': '1/16 W', '0603': '1/10 W', '0805': '1/8 W'}.get(size, '1/4 W')}, {size}"
    return dict(kind="R", value=value, Footprint=fp, Datasheet=YAGEO + mpn, Description=desc, Manufacturer="YAGEO",
                MPN=mpn, spec=spec if spec is not None else "", src=src)


PARTS = {
    # capacitors -------------------------------------------------------------------------------
    "C_100n_0201": _c("100 nF", "GRM033R61A104KE15D", "0201", 10, "X5R"),
    "C_100n_0201_DEC": _c("100 nF", "GRM033R61A104KE15D", "0201", 10, "X5R", spec="",
                          src="compaction (2026-10-27): 0402 decoupling in 0201 on rails <= 3.3 V; the sheet's "
                              "unless-noted rating (at least twice the rail) covers it"),
    "C_100n_0402": _c("100 nF", "GRM155R71C104KA88D", "0402", 16, "X7R", spec=""),
    "C_1u_0402": _c("1 µF", "GRM155C71A105KE11D", "0402", 10, "X7S", spec="",
                     src="successor of GRM155R61A105KE15D (to be discontinued): BOM v1.18 item 2"),
    "C_2u2_0402_LDO": _c("2.2 µF", "GRM155R61C225KE11D", "0402", 16, "X5R", spec="",
                         src="TPS7A20 CIN and COUT: 0.47 µF effective minimum (SBVS338H §5.3), 1.03 µF effective "
                             "at 3.8 V, -20 to 85 °C (BOM v1.18 item 2)"),
    "C_2u2_0402": _c("2.2 µF", "GRM155R61A225KE95D", "0402", 10, "X5R", spec=""),
    "C_4u7_0402": _c("4.7 µF", "GRM155R60J475ME47D", "0402", 6.3, "X5R"),
    "C_10u_0603": _c("10 µF", "GRM188R61A106KE69D", "0603", 10, "X5R"),
    "C_10u_0603_X7R": _c("10 µF", "C1608X7R1A106K080AC", "0603", 10, "X7R", maker="TDK",
                         src="value, rating, dielectric and size: board ADR 0021 item 3"),
    "C_10u_0805_25V": _c("10 µF", "GRM21BR61E106KA73L", "0805", 25, "X5R"),
    "C_10u_0603_25V": _c("10 µF", "GRM188R61E106MA73D", "0603", 25, "X5R"),
    "C_22u_0805_16V_LP": _c("22 µF", "GRM219R61C226ME15L", "0805", 16, "X5R",
                            src="LT3045/LT3094 OUT and LT3094 IN, 10 µF minimum (Rev. D p. 16, Rev. B pp. 15, 20): "
                                "three each, 13.4 µF effective at 6.04 V, 11.3 µF at 7.06 V, -20 to 85 °C, tolerance "
                                "included; 1.0 mm max, either side (BOM v1.18 item 5)"),
    "C_22u_0805_25V": _c("22 µF", "GRM21BR61E226ME44L", "0805", 25, "X5R",
                         src="Murata DC-bias data, -20 to 85 °C, tolerance included (BOM v1.18 items 1, 3, 5): "
                             "TPS62136 and TPS62903 inputs, 3 µF effective minimum (SLVSDV2 §7.3, SLVSES3A §6.3): "
                             "3.9 µF; TPS62903 output, two: 13.5 µF at 5.1 V (>= 12 µF, BOM line 121)"),
    "C_1u_0201": _c("1 µF", "GRM033R60J105MEA2D", "0201", 6.3, "X5R"),
    "C_22u_0603": _c("22 µF", "GRM188R60J226MEA0D", "0603", 6.3, "X5R"),
    "C_22u_0603_10V": _c("22 µF", "GRM188R61A226ME15D", "0603", 10, "X5R"),
    "C_22u_0805_16V": _c("22 µF", "GRM21BR61C226ME44L", "0805", 16, "X5R"),
    "C_4u7_0603_X7R": _c("4.7 µF", "GRM188R70J475KE19D", "0603", 6.3, "X7R",
                         src="value, rating, dielectric and size: TPS62827 typical application (SLVSEF9I Fig. 8-2)"),
    "C_10p_0402": _c("10 pF", "GRM1555C1H100JA01D", "0402", 50, "C0G",
                     src="24 MHz crystal load: 2 x (CL 8 pF - 3 pF stray) (NDK 2008E_NX3225GA; BOM v1 line 15)"),
    "C_120p_0402": _c("120 pF", "GRM1555C1H121JA01D", "0402", 50, "C0G"),
    "C_3n3_0402": _c("3.3 nF", "GRM155R71H332KA01D", "0402", 50, "X7R"),
    "C_1n_0402": _c("1 nF", "GRM155R71H102KA01D", "0402", 50, "X7R"),
    "C_1u_0402_10V": _c("1 µF", "GRM155C71A105KE11D", "0402", 10, "X7S",
                        src="LP5521 VOUT 10 V (SNVS441I p. 37); successor of GRM155R61A105KE15D: BOM v1.18 item 2"),
    "C_390n_0603": _c("390 nF", "GRM188R71C394KA01D", "0603", 16, "X7R",
                      src="TPS3808 CT 390 nF X7R ±10 % (BOM v1 line 97); part capture choice"),
    "C_470n_0402": _c("470 nF", "GRM155R61A474KE15D", "0402", 10, "X5R",
                      src="LP5521 CFLY1, CFLY2 470 nF X5R, 6.3 V or more (SNVS441I p. 37, Table 36); part capture choice"),
    # audio (blk.audio and children; BOM v1 lines 22-29, 108-118, 140) --------------------------
    "C_4u7_0402_10V": _c("4.7 µF", "GRM155R61A475MEAAD", "0402", 10, "X5R",
                         src="TPS62840 CI: SLVSEC6D p. 17, Table 2 (the datasheet's part)"),
    "C_10u_0402_4V": _c("10 µF", "GRM155R60G106ME44D", "0402", 4, "X5R",
                        src="TPS62840 CO: SLVSEC6D p. 17, Table 2 (the datasheet's part)"),
    "C_4u7_0603_10V": _c("4.7 µF", "GRM188R61A475KE15D", "0603", 10, "X5R"),
    "C_15u_0603": _c("15 µF", "C1608X5R0J156M080AC", "0603", 6.3, "X5R", maker="TDK",
                     src="CS43198 FILT+/FILT- 15 µF (DS1156F2 Fig. 2-1); part capture choice"),
    "C_10n_0402": _c("10 nF", "GRM155R71H103KA88D", "0402", 50, "X7R"),
    "C_10n_0402_C0G": _c("10 nF", "GRM1555C1H103JA01D", "0402", 50, "C0G",
                         src="TPS65131 CP 10 nF C0G (BOM v1 line 111)"),
    "C_15p_0402": _c("15 pF", "GRM1555C1H150JA01D", "0402", 50, "C0G"),
    "C_22p_0402": _c("22 pF", "GRM1555C1H220JA01D", "0402", 50, "C0G"),
    # vdd_cpu TPS62870Z4 (board ADR 0026): input per VIN pin, compensation (SLVSGC5E pp. 9, 45-48)
    "C_47u_0603": _c("47 µF", "GRM188R60J476ME15D", "0603", 6.3, "X5R",
                     src="board ADR 0026 item 3: 8.65 µF effective at 3.8 V (SimSurfing, -20..85 C, -20 %) "
                         "against 5 µF per VIN pin (SLVSGC5E p. 9)"),
    "C_5n6_C0G": _c("5.6 nF", "GRM1555C1H562JE01D", "0402", 50, "C0G",
                    src="board ADR 0026 item 4: CC from SLVSGC5E Eq. 24 (5.16 nF)"),
    "R_82R5": _r("82.5 Ω", "82R5", src="board ADR 0026 item 4: RZ from SLVSGC5E Eq. 15 at 45.7 µF effective"),
    "C_100p_0603": _c("100 pF", "GRM1885C1H101JA01D", "0603", 50, "C0G",
                      src="HP-amp network C1 = C2 100 pF C0G 0603 50 V (BOM v1 line 108)"),
    "C_220n_0402": _c("220 nF", "GRM155R61A224KE19D", "0402", 10, "X5R",
                      src="TPS65131 VREF 220 nF (BOM v1 line 111)"),
    "C_470n_0603": _c("470 nF", "GRM188R71C474KA88D", "0603", 16, "X7R",
                      src="LT3045/LT3094 CSET 0.47 µF (BOM v1 line 110: C0G or film preferred; X7R capture choice, UNVERIFIED)"),
    "C_4u7_0805_25V": _c("4.7 µF", "GRM21BR71E475KA73L", "0805", 25, "X7R",
                         src="TPS65131 output 4 x 4.7 µF 25 V X7R (BOM v1 line 111)"),
    "C_4u7_0805_X7R": _c("4.7 µF", "GRM21BR71C475KA73L", "0805", 16, "X7R",
                         src="LT3045 CIN 4.7 µF X7R (BOM v1 line 110)"),
    "C_22u_1206_16V": _c("22 µF", "GRM31CR71C226ME15L", "1206", 16, "X7R",
                         src="LMR33630C COUT 3 x 22 µF 16 V X7R (BOM v1 line 118)"),
    "C_1u_0603_25V": _c("1 µF", "GRM188R71E105KA12D", "0603", 25, "X7R"),
    # resistors --------------------------------------------------------------------------------
    "R_0_0402": _r("0 Ω", "0R"),
    "R_0_0603": _r("0 Ω", "0R", size="0603", src="vccio6_1v8 link, 0603 (BOM v1 line 141, pinout v1 B1)"),
    "R_2R2": _r("2.2 Ω", "2R2"),
    "R_22": _r("22 Ω", "22R"),
    "R_100": _r("100 Ω", "100R"),
    "R_120": _r("120 Ω", "120R", src="DDR_RZQ 120 Ohm 1 % (RK3566 HDG 1.1 p. 25)"),
    "R_240": _r("240 Ω", "240R", src="ZQ 240 Ohm 1 % to VDDQ (board ADR 0022, BOM changes)"),
    "R_1k": _r("1 kΩ", "1K"),
    "R_2k2": _r("2.2 kΩ", "2K2"),
    "R_4k7": _r("4.7 kΩ", "4K7"),
    "R_10k": _r("10 kΩ", "10K"),
    "R_51k": _r("51 kΩ", "51K"),
    "R_86k6": _r("86.6 kΩ", "86K6"),
    "R_100k": _r("100 kΩ", "100K"),
    "R_280k": _r("280 kΩ", "280K", src="TPS3808 SENSE divider 280 kΩ / 100 kΩ 1 % (BOM v1 line 97)"),
    "R_442k": _r("442 kΩ", "442K"),
    "R_453k": _r("453 kΩ", "453K"),
    "R_470k": _r("470 kΩ", "470K"),
    "R_1M": _r("1 MΩ", "1M"),
    "R_22k": _r("22 kΩ", "22K"),
    "R_47k": _r("47 kΩ", "47K"),
    "R_120k": _r("120 kΩ", "120K"),
    "R_4k32": _r("4.32 kΩ", "4K32", src="TPS62840 VSET 4.32 kΩ 1 % E96 for 2.2 V (SLVSEC6D p. 13, Table 1)"),
    "R_4k99": _r("4.99 kΩ", "4K99", src="CS43198 ADR 4.99 kΩ 5 % to GND: address bits 01 (DS1156F2 Table 4-12)"),
    "R_33": _r("33 Ω", "33R", src="Oscillator series 33 Ω (ADR 0019 decision 1; BOM v1 line 140)"),
    "R_27": _r("27 Ω", "27R", src="Divider-to-XTI series 27 Ω (ADR 0019 decision 2; BOM v1 line 140)"),
    "R_475k": _r("475 kΩ", "475K", size="0603", src="TPS65131 R1 475 kΩ 1 % 0603 (BOM v1 line 111)"),
    "R_100k_0603": _r("100 kΩ", "100K", size="0603", src="TPS65131 R2 / LMR33630C feedback 100 kΩ 1 % (BOM v1 lines 111, 118)"),
    "R_16k5": _r("16.5 kΩ", "16K5", size="0603", src="LMR33630C feedback 16.5 kΩ 1 % (BOM v1 line 118)"),
    "R_523": _r("523 Ω", "523R", size="0603", src="LT3045 RILIM 523 Ω 1 % (BOM v1 line 109)"),
    "R_13k": _r("13 kΩ", "13K", size="0603", src="LT3094 RILIM 13.0 kΩ 1 % (BOM v1 line 109)"),
    "R_1R0": _r("1 Ω", "1R", size="0603", src="HP-amp ballast 1.0 Ω 1 % 0603 (BOM v1 line 107)"),
    # INA236 shunts (BOM v1 lines 54, 136; power tree §4.12): fitted in every variant (ADR 0013)
    "R_SHUNT_10m_2512": dict(kind="R", value="10 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL2512_7m-500m", Datasheet=VISHAY_WSL,
                             Description="Current-sense resistor, 10 mOhm, 1 %, 1 W, 2512 metal strip: INA236 VSYS shunt",
                             Manufacturer="Vishay Dale", MPN="WSL2512R0100FEA", spec="2512 1 W",
                             src="BOM v1 line 54: VSYS shunt 10 mΩ, 1 W or more, 2512 (doc 30100: WSL2512 1.0 W)"),
    "R_SHUNT_20m_2010": dict(kind="R", value="20 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL2010_7m-500m", Datasheet=VISHAY_WSL,
                             Description="Current-sense resistor, 20 mOhm, 1 %, 0.5 W, 2010 metal strip: INA236 HAT shunt",
                             Manufacturer="Vishay Dale", MPN="WSL2010R0200FEA", spec="2010 0.5 W",
                             src="BOM v1 line 54: HAT shunt 20 mΩ, 0.5 W or more (doc 30100: WSL2010 0.5 W); part: "
                                 "capture choice in the line 43 family"),
    "R_SHUNT_20m_1206": dict(kind="R", value="20 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL1206_6m-200m", Datasheet=VISHAY_WSL,
                             Description="Current-sense resistor, 20 mOhm, 1 %, 0.25 W, 1206 metal strip: INA236 audio shunt",
                             Manufacturer="Vishay Dale", MPN="WSL1206R0200FEA", spec="1206",
                             src="BOM v1 lines 54 (audio, v1.8) and 136 (LMR33630C input): WSL1206R0200FEA"),
    "R_SHUNT_100m_1206": dict(kind="R", value="100 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL1206_6m-200m", Datasheet=VISHAY_WSL,
                              Description="Current-sense resistor, 100 mOhm, 1 %, 0.25 W, 1206 metal strip: INA236 display shunt",
                              Manufacturer="Vishay Dale", MPN="WSL1206R1000FEA", spec="1206",
                              src="BOM v1 line 54: display shunt 100 mΩ (doc 30100: WSL1206 to 0.2 Ω); part: "
                                  "capture choice in the line 43 family"),
    # measurement links (BOM v1 line 137): shunt in `full`, 0 Ohm jumper in `production`
    "LINK_H5": dict(kind="R", value="5 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL1206_2m-5m9", Datasheet=VISHAY_WSL,
                    Description="Current-sense resistor, 5 mOhm, 1 %, 0.5 W, 1206 metal strip: measurement link H5",
                    Manufacturer="Vishay Dale", MPN="WSL12065L000FEA", spec="1206",
                    src="BOM v1 line 137 (H5; kept in production)"),
    "LINK_H20": dict(kind="R", value="20 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL1206_6m-200m", Datasheet=VISHAY_WSL,
                     Description="Current-sense resistor, 20 mOhm, 1 %, 1206 metal strip: measurement link H20",
                     Manufacturer="Vishay Dale", MPN="WSL1206R0200FEA", spec="1206",
                     src="BOM v1 line 137 (H20)", production=dict(Value="0 Ω", MPN="RC1206JR-070RL", Manufacturer="YAGEO")),
    "LINK_M": dict(kind="R", value="100 mΩ", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RL0603FR-070R1L",
                   Description="Resistor, 0.1 Ohm, 1 %, 0603 thick film low-ohmic: measurement link M",
                   Manufacturer="YAGEO", MPN="RL0603FR-070R1L", spec="0603", src="BOM v1 line 137 (M)",
                   production=dict(Value="0 Ω", MPN="RC0603JR-070RL", Manufacturer="YAGEO")),
    "LINK_L1": dict(kind="R", value="1 Ω", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RC0603FR-071RL",
                    Description="Resistor, 1 Ohm, 1 %, 0603: measurement link L1", Manufacturer="YAGEO",
                    MPN="RC0603FR-071RL", spec="0603", src="BOM v1 line 137 (L1)",
                    production=dict(Value="0 Ω", MPN="RC0603JR-070RL", Manufacturer="YAGEO")),
    "LINK_L10": dict(kind="R", value="10 Ω", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RC0603FR-0710RL",
                     Description="Resistor, 10 Ohm, 1 %, 0603: measurement link L10", Manufacturer="YAGEO",
                     MPN="RC0603FR-0710RL", spec="0603", src="BOM v1 line 137 (L10)",
                     production=dict(Value="0 Ω", MPN="RC0603JR-070RL", Manufacturer="YAGEO")),
    # inductors --------------------------------------------------------------------------------
    "L_XGL4012_221": dict(kind="L", value="220 nH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/getmedia/80d2e45e-9ea9-4518-8af9-e8c2c28ee954/xgl4012.pdf",
                          Description="Power inductor, 0.22 uH 20 %, Isat 9.9 A (20 % drop), Irms 10.9 A, 4.0 x 4.0 x 1.2 mm",
                          Manufacturer="Coilcraft", MPN="XGL4012-221MEC", spec="Isat 9.9 A",
                          src="board ADR 0021 item 2; land of the 4020 family assumed (UNVERIFIED against Document 1718)"),
    "L_XEL4012_920": dict(kind="L", value="92 nH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xel/xel4012/",
                          Description="Power inductor, 92 nH, Isat 24 A (25 C), 5.2 mOhm typ, 4 x 4 x 1.2 mm",
                          Manufacturer="Coilcraft", MPN="XEL4012-920NEC", spec="Isat 24 A",
                          src="board ADR 0026 item 2 (SLVSGC5E Table 9-2: XEL4012-920NE); 4020-family land, "
                              "UNVERIFIED against the XEL4012 drawing"),
    "L_XGL4020_152": dict(kind="L", value="1.5 µH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf",
                          Description="Power inductor, 1.5 uH 20 %, Isat 5.3 A (20 % drop), Irms 8.0 A, 4.0 x 4.0 x 2.1 mm",
                          Manufacturer="Coilcraft", MPN="XGL4020-152MEC", spec="Isat 5.3 A",
                          Second_Source="Coilcraft XEL4020-152MEC (same land, BOM v1 line 114)",
                          Manufacturer_2="Coilcraft", MPN_2="XEL4020-152MEC", src="BOM v1 line 114"),
    "L_DFE252012F_R47": dict(kind="L", value="470 nH", Footprint="T1_Main_Board:L_Murata_DFE252012F",
                             Datasheet="https://www.murata.com/en-us/products/productdetail?partno=DFE252012F-R47M%3DP2",
                             Description="Power inductor, 0.47 uH 20 %, 2.5 x 2.0 x 1.2 mm",
                             Manufacturer="Murata", MPN="DFE252012F-R47M", spec="",
                             Second_Source="TDK TFM252012ALMAR47MTAA; Changjiang FPA252012D-R47MT0 (BOM v1 line 5)",
                             src="BOM v1 line 5"),
    "R_60k4_TF": dict(kind="R", value="60.4 kΩ", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RT0603BRD0760K4L",
                      Description="Resistor, 60.4 kOhm, 0.1 %, 25 ppm/K, 0603 thin film", Manufacturer="YAGEO",
                      MPN="RT0603BRD0760K4L", spec="0.1 %", src="LT3045/LT3094 RSET (BOM v1 line 109)"),
    "R_1k_TF": dict(kind="R", value="1 kΩ", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RT0603BRD071KL",
                    Description="Resistor, 1.00 kOhm, 0.1 %, 25 ppm/K, 0603 thin film", Manufacturer="YAGEO",
                    MPN="RT0603BRD071KL", spec="0.1 %", Second_Source="Panasonic ERA-3AEB102V (BOM v1 line 37)",
                    Manufacturer_2="Panasonic", MPN_2="ERA-3AEB102V", src="HP-amp R1 = R3 (BOM v1 line 37)"),
    "R_1k62_TF": dict(kind="R", value="1.62 kΩ", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet=YAGEO + "RT0603BRD071K62L",
                      Description="Resistor, 1.62 kOhm, 0.1 %, 25 ppm/K, 0603 thin film", Manufacturer="YAGEO",
                      MPN="RT0603BRD071K62L", spec="0.1 %", Second_Source="Panasonic ERA-3AEB1621V (BOM v1 line 37)",
                      Manufacturer_2="Panasonic", MPN_2="ERA-3AEB1621V", src="HP-amp R2 = R4 (BOM v1 line 37)"),
    "L_DFE201610E_2R2": dict(kind="L", value="2.2 µH", Footprint="T1_Main_Board:L_Murata_DFE201610E",
                             Datasheet="https://www.murata.com/en-us/products/productdetail?partno=DFE201610E-2R2M%23",
                             Description="Power inductor, 2.2 uH 20 %, 2.0 x 1.6 x 1.0 mm",
                             Manufacturer="Murata", MPN="DFE201610E-2R2M", spec="",
                             src="TPS62840 inductor (BOM v1 line 28)"),
    "L_DFE252012F_4R7": dict(kind="L", value="4.7 µH", Footprint="T1_Main_Board:L_Murata_DFE252012F",
                             Datasheet="https://www.murata.com/en-us/products/productdetail?partno=DFE252012F-4R7M%3DP2",
                             Description="Power inductor, 4.7 uH 20 %, 2.5 x 2.0 x 1.2 mm",
                             Manufacturer="Murata", MPN="DFE252012F-4R7M", spec="",
                             src="TPS65131 boost inductor (BOM v1 line 23)"),
    "L_XGL4020_222": dict(kind="L", value="2.2 µH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf",
                          Description="Power inductor, 2.2 uH 20 %, Isat 4.4 A (20 % drop), 4.0 x 4.0 x 2.1 mm",
                          Manufacturer="Coilcraft", MPN="XGL4020-222MEC", spec="Isat 4.4 A",
                          Second_Source="Coilcraft XAL4020-222MEC (same land, BOM v1 line 117)",
                          Manufacturer_2="Coilcraft", MPN_2="XAL4020-222MEC", src="LMR33630C inductor (BOM v1 line 117)"),
    # low-profile power inductors (compaction study, hardware/studies/compaction; 2026-10-27): the
    # XGL4015 is 4.0 x 4.0 x 1.5 mm max on the XxL4020 land (Coilcraft Document 1660 and its drawing:
    # pads 0.98 x 3.4 mm, 2.37 mm apart), so it stands under the battery pocket (PCB-Z-01, 1.5 mm)
    "L_XGL4015_102": dict(kind="L", value="1 µH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://coilcraft.com/getmedia/c5d04454-742d-473e-8b80-06c97338c587/xgl4015.pdf",
                          Description="Power inductor, 1.0 uH 20 %, Isat 7.3 A (30 % drop), Irms 6.5 A, 4.0 x 4.0 x 1.5 mm",
                          Manufacturer="Coilcraft", MPN="XGL4015-102MEC", spec="Isat 7.3 A",
                          Second_Source="Coilcraft XGL4012-102MEC (same land, 1.2 mm, Isat 6.6 A at 30 % drop)",
                          Manufacturer_2="Coilcraft", MPN_2="XGL4012-102MEC",
                          src="compaction study (2026-10-27): BQ25798 and TPS62903 inductor at 1.5 mm; Document 1660-1"),
    "L_XGL4015_471": dict(kind="L", value="470 nH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://coilcraft.com/getmedia/c5d04454-742d-473e-8b80-06c97338c587/xgl4015.pdf",
                          Description="Power inductor, 0.47 uH 20 %, Isat 10.5 A (30 % drop), Irms 9.6 A, 4.0 x 4.0 x 1.5 mm",
                          Manufacturer="Coilcraft", MPN="XGL4015-471MEC", spec="Isat 10.5 A",
                          Second_Source="Wurth 744373240047 (other land, 1.8 mm: bands only; BOM v1 line 106)",
                          src="compaction study (2026-10-27): TPS62827 and TPS62826 inductor at 1.5 mm; Document 1660-1"),
    "D_PMEG2010AEH": dict(kind="D", value="PMEG2010AEH", Footprint="Diode_SMD:D_SOD-123F",
                          Datasheet="https://assets.nexperia.com/documents/data-sheet/PMEG2010AEH_PMEG2010AET.pdf",
                          Description="Schottky rectifier, 20 V, 1 A, SOD-123F", Manufacturer="Nexperia",
                          MPN="PMEG2010AEH", spec="", Second_Source="onsemi MBRM120LT1G (BOM v1 line 24)",
                          Manufacturer_2="onsemi", MPN_2="MBRM120LT1G", src="TPS65131 boost rectifier (BOM v1 line 24)"),
    "D_TPD1E10B06": dict(kind="D", value="TPD1E10B06", Footprint="Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm",
                         Datasheet="https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf",
                         Description="ESD protection diode, bidirectional, 5.5 V working, 12 pF, X1SON-2 (DPY)",
                         Manufacturer="Texas Instruments", MPN="TPD1E10B06DPYR", spec="",
                         Second_Source="onsemi ESD9B5.0ST5G (BOM v1 line 36; other land)", src="BOM v1 line 36"),
    "Q_DMG1012T": dict(kind="Q", value="DMG1012T", Footprint="Package_TO_SOT_SMD:SOT-523",
                       Datasheet="https://www.diodes.com/assets/Datasheets/ds31783.pdf",
                       Description="N-channel MOSFET, 20 V, 0.63 A, VGS(th) <= 1.0 V, SOT-523", Manufacturer="Diodes Incorporated",
                       MPN="DMG1012T-7", spec="", src="BOM v1 line 35"),
    "Q_DMP3099L": dict(kind="Q", value="DMP3099L", Footprint="Package_TO_SOT_SMD:SOT-23",
                       Datasheet="https://www.diodes.com/assets/Datasheets/DMP3099L.pdf",
                       Description="P-channel MOSFET, -30 V, +-20 V VGS, SOT-23", Manufacturer="Diodes Incorporated",
                       MPN="DMP3099L-7", spec="", src="LMR33630C EN level shifter (BOM v1 line 119)"),
    "NT_BALLAST": dict(kind="NT", value="20 mΩ trace", Footprint="NetTie:NetTie-2_SMD_Pad0.5mm", Datasheet="~",
                       Description="Net tie: 20 mOhm PCB trace ballast between paralleled LDO outputs (LT3045 Rev. D p. 21)",
                       src="BOM v1 lines 25, 26"),
    "NT_SENSE": dict(kind="NT", value="NetTie", Footprint="NetTie:NetTie-2_SMD_Pad0.5mm", Datasheet="~",
                     Description="Net tie: a reference trace joins ground at the headphone jack's ground pin (PCB-A-03, -16)",
                     src="PCB design constraints PCB-A-03, PCB-A-16"),
    # input, charger, battery path and gauge (blk.charger, blk.gauge; BOM v1 lines 39-48, 104, 115, 120, 142)
    "C_100n_0402_50V": _c("100 nF", "GRM155R71H104KE14D", "0402", 50, "X7R",
                          src="BQ25798 VBUS, PMID, SYS 0.1 µF, 25 V or higher (SLUSDV2C §8.2.2.3; BOM v1 line 115)"),
    "C_47n_0402": _c("47 nF", "GRM155R71C473KA01D", "0402", 16, "X7R",
                     src="BQ25798 BTST1, BTST2 47 nF 10 V; BATP 47 nF (SLUSDV2C Table 5-1, Figure 8-2 note 2; BOM v1 line 115)"),
    "C_1u_0402_25V": _c("1 µF", "GRM155R61E105KA12D", "0402", 25, "X5R"),
    "C_100n_0402_25V": _c("100 nF", "GRM155R71E104KE14D", "0402", 25, "X7R"),
    "R_1M02": _r("1.02 MΩ", "1M02", src="TPS2121 OV1 R1 1.02 MΩ 1 % (BOM v1 line 45)"),
    "R_464k": _r("464 kΩ", "464K", src="TPS2121 OV2 R1 464 kΩ 1 % (BOM v1 line 45, v1.14)"),
    "R_31k6": _r("31.6 kΩ", "31K6"),
    "R_45k3_TF": dict(kind="R", value="45.3 kΩ", Footprint="Resistor_SMD:R_0402_1005Metric",
                      Datasheet=YAGEO + "RT0402BRD0745K3L",
                      Description="Resistor, 45.3 kOhm, 0.1 %, 25 ppm/K, 0402 thin film", Manufacturer="YAGEO",
                      MPN="RT0402BRD0745K3L", spec="0.1 %", src="TPS2121 RILM 45.3 kΩ 0.1 % (BOM v1 line 45, v1.11)"),
    "R_6k04": _r("6.04 kΩ", "6K04", src="BQ25798 PROG 6.04 kΩ: 1.5 MHz, 2S (SLUSDV2C Table 7-1)"),
    "R_5k23": _r("5.23 kΩ", "5K23", src="BQ25798 TS RT1 (SLUSDV2C §7.3.9.5.1: 5.24 kΩ for a 103AT, 0-60 °C)"),
    "R_30k1": _r("30.1 kΩ", "30K1", src="BQ25798 TS RT2 (SLUSDV2C §7.3.9.5.1: 30.31 kΩ for a 103AT, 0-60 °C)"),
    "R_5R1": _r("5.1 Ω", "5R1", src="BQ28Z610-R1 VC2 series 5 Ω (SLUSE07B Figure 9-1)"),
    "R_10R": _r("10 Ω", "10R", src="BQ28Z610-R1 PACK series 10 Ω (SLUSE07B Figure 9-1)"),
    "R_SENSE_3m": dict(kind="R", value="3 mΩ", Footprint="T1_Main_Board:R_Vishay_WSL1206_2m-5m9", Datasheet=VISHAY_WSL,
                       Description="Current-sense resistor, 3 mOhm, 1 %, 0.25 W, 1206 metal strip", Manufacturer="Vishay Dale",
                       MPN="WSL12063L000FEA", spec="1206", Second_Source="Vishay WSL12063L000FEA18 (BOM v1 line 43)",
                       Manufacturer_2="Vishay Dale", MPN_2="WSL12063L000FEA18",
                       src="Gauge sense resistor (board ADR 0017 item 4; BOM v1 line 43)"),
    "F_5A": dict(kind="F", value="5 A", Footprint="Fuse:Fuse_Littelfuse-NANO2-451_453",
                 Datasheet="https://www.littelfuse.com/products/overcurrent-protection/fuses/surface-mount-fuses/nano2-fuses/451-453/0451005-mrl",
                 Description="Fuse, 5 A, 125 V, very fast-acting, NANO2 451", Manufacturer="Littelfuse",
                 MPN="0451005.MRL", spec="", src="Battery fuse (board ADR 0014; BOM v1 line 104)"),
    "TH_10k": dict(kind="RT", value="10 kΩ", Footprint="Resistor_SMD:R_0402_1005Metric",
                   Datasheet=MURATA + "NCP15XH103F03RC",
                   Description="NTC thermistor, 10 kOhm 1 %, B 3380 K, 0402", Manufacturer="Murata",
                   MPN="NCP15XH103F03RC", spec="", src="Board-side battery NTC to the gauge TS1 (BOM v1 line 48)"),
    "L_XAL4020_102": dict(kind="L", value="1 µH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/getmedia/6adcb47d-8b55-416c-976e-1e22e0d2848c/xal4000.pdf",
                          Description="Power inductor, 1.0 uH 20 %, Isat 8.7 A (30 % drop), 4.0 x 4.0 x 2.1 mm",
                          Manufacturer="Coilcraft", MPN="XAL4020-102MEC", spec="Isat 8.7 A",
                          Second_Source="Coilcraft XGL4020-102MEC (same land, BOM v1 line 40)",
                          Manufacturer_2="Coilcraft", MPN_2="XGL4020-102MEC", src="BQ25798 inductor (BOM v1 line 40)"),
    "D_BAT54J": dict(kind="D", value="BAT54J", Footprint="Diode_SMD:D_SOD-323F",
                     Datasheet="https://assets.nexperia.com/documents/data-sheet/BAT54J.pdf",
                     Description="Schottky diode, 30 V, 200 mA, SOD-323F", Manufacturer="Nexperia", MPN="BAT54J,115",
                     spec="", src="TPS2121 OVx forcing diode: capture choice in the BAT54 family of BOM v1 line 78"),
    "D_TVS_DNP": dict(kind="D", value="TVS", Footprint="Diode_SMD:D_SOD-123F", Datasheet="~",
                      Description="TVS position on P+, part to choose (standoff >= 9 V, clamp < 20 V), not fitted",
                      spec="", src="BOM v1 line 142 (ADR 0020 item 6)"),
    # USB ports and their power (blk.usb-c, blk.pwr-5v1, blk.usb-vbus-out, blk.hat-5v, blk.hat-signals)
    "C_100n_0603_50V": _c("100 nF", "GRM188R71H104KA93D", "0603", 50, "X7R",
                          src="TPD8S300A VBIAS 0.1 µF, >= 35 V, the datasheet's example part (SLVSEL9 §9.2.2.1, Table 3)"),
    "R_15k": _r("15 kΩ", "15K", src="OTG0 VBUSDET divider 10 kΩ / 15 kΩ (RK3566 HDG 1.1 Figure 2-43)"),
    "R_95k3": _r("95.3 kΩ", "95K3", src="TPS62903 VSET 95.3 kΩ: 5.1 V (SLVSES3A Table 7-2; BOM v1 line 91)"),
    "R_26k1": _r("26.1 kΩ", "26K1", src="TPS62903 MODE/S-CONF 26.1 kΩ (SLVSES3A Table 7-1; BOM v1 line 91)"),
    "R_1k47": _r("1.47 kΩ", "1K47", src="eFuse #D RILM 1.47 kΩ 1 % (BOM v1 line 44, v1.14)"),
    "R_1k87": _r("1.87 kΩ", "1K87", src="eFuse #A and #C RILM 1.87 kΩ 1 % (BOM v1 line 44, v1.13)"),
    "R_100_0805": _r("100 Ω", "100R", size="0805", src="HAT VBUS discharge resistor: capture choice, UNVERIFIED (BOM §7 item 47)"),
    "L_XGL4020_102": dict(kind="L", value="1 µH", Footprint="Inductor_SMD:L_Coilcraft_XxL4020",
                          Datasheet="https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf",
                          Description="Power inductor, 1.0 uH 20 %, Isat 8.8 A (30 % drop), 4.0 x 4.0 x 2.1 mm",
                          Manufacturer="Coilcraft", MPN="XGL4020-102MEC", spec="Isat 8.8 A",
                          src="TPS62903 5.1 V inductor (BOM v1 line 92)"),
    # radio and antennas (blk.radio, blk.antennas; BOM v1 lines 55-58, 129-131)
    "R_200k_0603": _r("200 kΩ", "200K", size="0603", src="TPS62826 R1 200 kΩ 1 % 0603 (BOM v1 line 131)"),
    "R_1k_0603": _r("1 kΩ", "1K", size="0603", src="Discharge position 1 kΩ 0603, DNP (BOM v1 line 131, G13)"),
    "C_10p_0603": _c("10 pF", "GRM0335C1H100JA01D", "0201", 50, "C0G",
                     src="Type 2EL shared-antenna link 10 pF (E2B-54-1953 §4.3.3); Murata's GRM03 class (0603 metric)"),
    "R_0_0201": _r("0 Ω", "0R", size="0201", src="RF series position, 0 Ω (BOM v1 line 58; Murata's 0603-metric copy)"),
    "C_NF_0603": dict(kind="C", value="DNP", Footprint="Capacitor_SMD:C_0201_0603Metric", Datasheet="~",
                      Description="Matching shunt position, not fitted (Murata's copy, E2B-09-1413 Figures 9-10)",
                      spec="", src="BOM v1 line 58: shunts DNP", in_bom=False),
    # faceplate interface (blk.fp-*, blk.mic-main; BOM v1 lines 51-53, 145, 146)
    "R_3k57": _r("3.57 kΩ", "3K57", src="TPS22950 RILIM 3.57 kΩ 1 % (BOM v1 line 145)"),
    "R_3R32": _r("3.32 Ω", "3R32", size="0603", src="TPS61160 RSET 3.32 Ω for 60.2 mA (BOM v1 line 51, v1.11)"),
    "C_1u_0603_50V": _c("1 µF", "GRM188R71H105KA12D", "0603", 50, "X7R",
                        src="TPS61160 output 1 µF 50 V (BOM v1 §8 backlight row; SLVS791E 0.47-10 µF)"),
    "D_PMEG6010CEH": dict(kind="D", value="PMEG6010CEH", Footprint="Diode_SMD:D_SOD-123F",
                          Datasheet="https://assets.nexperia.com/documents/data-sheet/PMEG6010CEH_PMEG6010CEJ.pdf",
                          Description="Schottky rectifier, 60 V, 1 A, SOD-123F", Manufacturer="Nexperia",
                          MPN="PMEG6010CEH,115", spec="", Second_Source="Nexperia PMEG6010CEJ,115 (BOM v1 line 53)",
                          Manufacturer_2="Nexperia", MPN_2="PMEG6010CEJ,115", src="Backlight rectifier (BOM v1 line 53)"),
    "L_XFL3012_223": dict(kind="L", value="22 µH", Footprint="T1_Main_Board:L_Coilcraft_XFL3012",
                          Datasheet="https://www.coilcraft.com/getmedia/f76a3c9b-4fff-4397-8028-ef8e043eb200/xfl3012.pdf",
                          Description="Power inductor, 22 uH +-20 %, 0.63 Ohm max, Isat 0.45 A (20 % drop), 3.0 x 3.0 x 1.3 mm",
                          Manufacturer="Coilcraft", MPN="XFL3012-223MEC", spec="",
                          Second_Source="none on the same land recorded (BOM v1 line 52)",
                          src="Backlight inductor (BOM v1 line 52, v1.22: Coilcraft Document 747-1)"),
    "L_AOTA_3R3": dict(kind="L", value="3.3 µH", Footprint="T1_Main_Board:L_Abracon_AOTA-B201610",
                       Datasheet="https://abracon.com/datasheets/AOTA-B201610S3R3-101-T.pdf",
                       Description="Inductor, shielded molded, 3.3 uH, 20 %, Isat 2.4 A, 2.0 x 1.6 mm, polarity dot",
                       Manufacturer="Abracon", MPN="AOTA-B201610S3R3-101-T", spec="", src="BOM v1 line 13"),
    # buttons (BOM v1 lines 76, 77) ------------------------------------------------------------
    "SW_PTS815": dict(kind="SW", value="PTS815", Footprint="T1_Main_Board:SW_CK_PTS815",
                      Datasheet="https://www.ckswitches.com/media/2768/pts815.pdf",
                      Description="Tactile switch, SPST-NO, top actuated, 4.2 x 3.2 x 2.5 mm, 180 gf",
                      Manufacturer="C&K", MPN="PTS815SJM250SMTRLFS", spec="", src="BOM v1 line 77"),
    "SW_ACTION": dict(kind="SW", value="PTS815 400 gf", Footprint="T1_Main_Board:SW_CK_PTS815",
                      Datasheet="https://www.ckswitches.com/media/2768/pts815.pdf",
                      Description="Action button: tactile switch, SPST-NO, 4.2 x 3.2 x 2.5 mm, 400 gf (UNVERIFIED)",
                      Manufacturer="C&K", MPN="PTS815SJG250SMTRLFS", spec="",
                      src="BOM v1 line 76 (v1.22): the side-button family and land of line 77, the heavier force"),
    # crystal, net tie, test pad ---------------------------------------------------------------
    "Y_24M": dict(kind="Y", value="24 MHz", Footprint="ndk:Crystal_SMD_NDK_NX3225GA-4Pin_3.2x2.5mm",
                  Datasheet="https://static.chipdip.ru/lib/694/DOC028694308.pdf",
                  Description="Crystal, 24 MHz, CL 8 pF, ESR 50 Ohm max, 3225 4-pin (#1-#3 crystal, #2 #4 ground)",
                  Manufacturer="NDK", MPN="NX3225GA-24MHZ-STD-CRG-2", spec="",
                  Second_Source="none recorded (BOM v1 line 15)",
                  src="BOM v1 line 15 (v1.22: NDK 2008E_NX3225GA, CL 8 pF, ESR 50 Ohm at 20-50 MHz)"),
    "TP_SIG": dict(kind="TP", value="TP", Footprint="T1_Main_Board:TestPoint_Pad_D0.8mm", Datasheet="~",
                   Description="Test pad, 0.8 mm, signal net", src="PCB-D-06 (signal nets 0.8 mm minimum)"),
    "TP": dict(kind="TP", value="TP", Footprint="TestPoint:TestPoint_Pad_D1.0mm", Datasheet="~",
               Description="Test pad, 1.0 mm", src="PCB-T-02 test access; PCB-D-06 (power and ground nets 1.0 mm)"),
    "PAD_COVER": dict(kind="TP", value="TP", Footprint="TestPoint:TestPoint_Pad_2.0x2.0mm", Datasheet="~",
                      Description="Board-edge contact pad, ENIG, for the back cover's actuator (size set with the case, UNVERIFIED)",
                      src="BOM v1 line 143; PCB-L-10"),
    "NT": dict(kind="NT", value="NetTie", Footprint="NetTie:NetTie-2_SMD_Pad0.5mm", Datasheet="~",
               Description="Net tie: a separate trace leaves the net here (remote sense)", src="board ADR 0026 item 5"),
}


def fields(key, block, **extra):
    """Hidden fields of a placed part (CRAFT-140), from the catalog."""
    p = PARTS[key]
    f = {k: p[k] for k in ("Footprint", "Datasheet", "Description", "Manufacturer", "MPN",
                           "Second_Source", "Manufacturer_2", "MPN_2") if k in p}
    f["Block"] = block
    f.update(extra)
    return f


# ---- compaction (hardware/studies/compaction, 2026-10-27) ------------------------------------------
# 100 nF decoupling in 0201 (GRM033R61A104KE15D, 10 V X5R, the part already under the BGA, ADR 0016)
# instead of 0402, where the rail is at most 3.3 V (at most half the 10 V rating) and the block is in
# the core, I/O or radio zone. The audio zone keeps its captured parts (audiophile first, T1-040),
# the power zone its higher rails. Rail voltages: power tree v0 §3.
RAILS_0201 = {
    "vcc3v3_sys": 3.3, "vcc3v3_pmu": 3.3, "vcca1v8_pmu": 1.8, "vcc_1v8": 1.8, "vcc_ddr": 1.14,
    "vcc1v8_ddr": 1.8, "vccio_sd": 3.3, "vccio6_1v8": 1.8, "vdda_0v9": 0.9, "vcca_1v8": 1.8,
    "vcc1v8_wl": 1.8, "RP_3V3": 3.3, "RP_IOVDD_1V8": 1.8, "RP_DVDD": 1.1, "TPM_VDD": 1.8,
    "IMU_VDD": 1.8, "NFC_TAG_VCC": 1.8, "SD_VDD": 3.3,
}
BLOCKS_0201 = ("blk.soc", "blk.lpddr4x", "blk.emmc", "blk.microsd", "blk.pmic", "blk.rp2354", "blk.tpm",
               "blk.gpio-expander", "blk.board-id", "blk.imu", "blk.haptics", "blk.nfc-tag", "blk.status-led",
               "blk.maskrom", "blk.buttons", "blk.debug", "blk.usb-c", "blk.hat-signals", "blk.fp-",
               "blk.mic-main", "blk.radio", "blk.antennas")


def compact(key, block, top, bottom):
    """The part to place for KEY between nets TOP and BOTTOM in BLOCK: the 0201 100 nF where the
    compaction rule above allows it, else KEY."""
    if key == "C_100n_0402" and bottom == "GND" and top in RAILS_0201 and 2 * RAILS_0201[top] <= 10 \
            and block and block.startswith(BLOCKS_0201):
        return "C_100n_0201_DEC"
    return key


# ---- area recovery (board ADR 0025, 2026-10-27): part swaps applied at placement ------------------
# Applied to every placed part (sch.Sheet.place), after its catalog fields:
# - 0402 resistors to 0201 of the same series (Yageo RC0201, 1/20 W, 25 V), outside the audio chain
#   and the VBUS and charger-input paths; 0 Ω links and values under 10 Ω (current paths) keep 0402.
#   Every 0402 resistor outside those blocks is a pull-up, divider, bias or series part on rails of at
#   most VSYS (8.8 V), within half the 0201's 25 V; sourcing (T1-029), 2026-10-27: pass.
# - 100 nF capacitors on low-voltage signal nodes (PMIC power-on and VDC, vdd_cpu EN, SoC
#   reset) to the 0201 already used for decoupling (GRM033R61A104KE15D, 10 V X5R; at most 1.8 V on
#   each node, power tree v0 §3). The 0201 1 nF positions wait for a sourced part.
# - DC-bias gate (DRV-107, BOM v1.17): the maker's DC-bias data at each node's highest voltage,
#   -20 to 85 °C, tolerance included, against what each circuit needs. Passed: the BQ25798 VBUS
#   and SYS capacitors (2 µF and 6 µF effective minimum, SLUSDV2C §6.3) in 10 µF 25 V X5R 0603, and
#   the two TPS22945 output capacitors (0.1 µF, SLVS832D §9.1.5) in 1 µF 6.3 V X5R 0201. The other
#   positions keep their part (a minimum missed, no minimum below the present value, or audio).
AREA_C_DCBIAS = {("blk.charger-core", r): "C_10u_0603_25V" for r in ("C605", "C606", "C612", "C613", "C614",
                                                                     "C615", "C616")}
AREA_C_DCBIAS.update({("blk.fp-connector", "C5304"): "C_1u_0201", ("blk.mic-main", "C6502"): "C_1u_0201"})
AREA_R_EXCLUDE = ("blk.dac", "blk.mclk", "blk.hpa", "blk.audio", "blk.jack", "blk.charger-input", "blk.usb-c",
                  "blk.hat-5v", "blk.usb-vbus-out")
AREA_C_SIGNAL = {("blk.pmic", "C1114"), ("blk.pmic", "C1115"), ("blk.soc-pmuio", "C1303")}
_OHM = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6, "mΩ": 1e-3}


def ohms(value):
    num, _, unit = value.partition(" ")
    try:
        return float(num) * _OHM[unit]
    except (KeyError, ValueError):
        return None


def area_swap(block, ref, f, value):
    """The fields of a placed part after the area-recovery swaps (ADR 0025); f is not modified."""
    fp = f.get("Footprint", "")
    if fp == "Resistor_SMD:R_0402_1005Metric" and f.get("Manufacturer") == "YAGEO" and block \
            and not block.startswith(AREA_R_EXCLUDE) and (ohms(value) or 0) >= 10 \
            and f.get("MPN", "").startswith("RC0402FR-07"):
        g = dict(f)
        g["Footprint"] = "Resistor_SMD:R_0201_0603Metric"
        g["MPN"] = "RC0201" + f["MPN"][6:]
        g["Datasheet"] = YAGEO + g["MPN"]
        g["Description"] = f["Description"].replace("1/16 W, 0402", "1/20 W, 0201")
        return g
    if (block, ref) in AREA_C_DCBIAS and f.get("MPN") in ("GRM21BR61E106KA73L", "GRM155C71A105KE11D"):
        g = dict(f)
        g.update({k: PARTS[AREA_C_DCBIAS[(block, ref)]][k] for k in ("Footprint", "Datasheet", "Description", "MPN")})
        return g
    if (block, ref) in AREA_C_SIGNAL and f.get("MPN") == "GRM155R71C104KA88D":
        g = dict(f)
        g.update({k: PARTS["C_100n_0201"][k] for k in ("Footprint", "Datasheet", "Description", "MPN")})
        return g
    return f
