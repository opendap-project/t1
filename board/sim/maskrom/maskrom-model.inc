* MaskROM combo: behavioural model of the power-on path and the combo logic.
* Included by the maskrom-*.cir scenario files, which define the buttons
* (sources Vmain and Vvol: 0 = released, 1 = pressed) and the .param values.
* Parameters used here: TKEY SLOT18 SLOTPMU NSLOT TRST TSUSP TRESUME SUP TD
* RPWR RD0 RPU (SUP = 0: TPS3839G18 on vcc_1v8, BOM v1.5; SUP = 1: TPS3808G01
* on vcca1v8_pmu, proposal; TD = supervisor delay corner). Sources and status
* of every value: README.md.
*
* PWRON: RK809 internal 17 kohm to VCC_RTC (3.0 V assumed), 100 nF to GND
Vrtc vrtc 0 3.0
Rrk vrtc pwron 17k
Cpw pwron 0 100n
Smain pwron 0 mainb 0 SWB
* Vol- on SARADC_VIN1: 10 kohm pull-up to vcca1v8_pmu (assumed), 100 nF
Rvol pmu voldn 10k
Cvol voldn 0 100n
Svol voldn 0 volb 0 SWB
.model SWB SW(VT=0.5 VH=0.1 RON=0.1 ROFF=100MEG)
*
* --- RK809 power-on: PWRON held low for TKEY ---
Bkey 0 kt I = V(pwron) < 0.4 ? 1 : -V(kt)*1e3
Ckey kt 0 1
Rkey kt 0 1G
Bon onq 0 V = (V(kt) > {TKEY} || V(on) > 0.5) ? 1 : 0
Ron onq on 1k
Con on 0 1n
* time since power-on
Bs 0 s I = V(on) > 0.5 ? 1 : 0
Cs s 0 1
Rs s 0 1G
* rails: slot k rises at (k-1)*2 ms after power-on, 0.5 ms ramp (est.)
Bsusp susp 0 V = (time > {TSUSP} && time < {TRESUME}) ? 1 : 0
B18 v18 0 V = 1.8*min(max((V(s)-({SLOT18}-1)*2m)/0.5m,0),1)*(1-V(susp))
Bpmu pmu 0 V = 1.8*min(max((V(s)-({SLOTPMU}-1)*2m)/0.5m,0),1)
Brst resetb 0 V = V(s) > ({NSLOT}-1)*2m+0.5m+{TRST} ? 1.8 : 0
*
* --- window supervisor ---
* sensed rail: vcc_1v8 (TPS3839) or vcca1v8_pmu (TPS3808)
Bsen sen 0 V = {SUP} < 0.5 ? V(v18) : V(pmu)
* delay timer: runs while the rail is above VIT+ (1.687 V / 1.67 V), resets below VIT-
* rising thresholds: TPS3839G18 1.67 V + 17 mV (SBVS193D); TPS3808G01 with a
* 280k / 100k divider, 0.405 V x 3.8 = 1.54 V + 3 % hysteresis max (SBVS050N)
Btd 0 td I = V(sen) > ({SUP} < 0.5 ? 1.687 : 1.59) ? 1/{TD} : -V(td)*1e4
Ctd td 0 1
Rtd td 0 1G
* RESET (WINDOW_N): low until the timer expires; undefined below 0.6 V
* is modelled low (the worst case: window open)
Bwin win 0 V = V(td) > 1 ? ({SUP} < 0.5 ? V(v18) : V(pmu)) : 0
*
* --- logic on vcca1v8_pmu (SN74LVC1G57 / 1G58, Schmitt inputs) ---
* Thresholds at VCC 1.65 V (SCES414P): VT+ 0.79-1.16 V, VT- 0.35-0.62 V.
* Worst case for each use: VT+ = 1.16 V, VT- = 0.35 V.
* In2 = PWRON through the BAT54 with RPWR pull-up
.model BAT54MAX D(IS=100n N=1.35 RS=1.5 EG=0.69 XTI=2 CJO=10p)
Rin2 pmu in2 {RPWR}
Dpw in2 pwron BAT54MAX
Cin2 in2 0 5p
* Schmitt state for each input (1 = high)
Bh2 h2q 0 V = V(in2) > 1.16 ? 1 : (V(in2) < 0.35 ? 0 : V(h2))
Rh2 h2q h2 1k
Ch2 h2 0 1n
Bh0 h0q 0 V = V(voldn) > 1.16 ? 1 : (V(voldn) < 0.35 ? 0 : V(h0))
Rh0 h0q h0 1k
Ch0 h0 0 1n
Bhw hwq 0 V = V(win) > 1.16 ? 1 : (V(win) < 0.35 ? 0 : V(hw))
Rhw hwq hw 1k
Chw hw 0 1n
* gate 1: BOTH = both pressed; gate 2: GATE = BOTH and window open
* outputs valid only when vcca1v8_pmu >= 1.65 V (below: modelled low)
Bgate gate 0 V = (V(pmu) > 1.65 && V(h2) < 0.5 && V(h0) < 0.5 && V(hw) < 0.5) ? V(pmu) : 0
*
* --- DMG1012T and eMMC_D0 ---
* switch: on above VGS(th) max 1.0 V, off below 0.5 V; 0.7 ohm at VGS 1.8 V
Sfet drn 0 gate 0 SWF
.model SWF SW(VT=0.75 VH=0.25 RON=0.7 ROFF=1G)
Rd0 d0 drn {RD0}
Rpu v18 d0 {RPU}
Cd0 d0 0 10p
*
