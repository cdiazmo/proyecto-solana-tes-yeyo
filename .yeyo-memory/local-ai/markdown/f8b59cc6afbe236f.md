---
doc_id: "f8b59cc6afbe236f"
path: "02 GD LOI/Calculos/4521-CAL-LOI-039-062-0001-GAR_REV 1_MECHANICAL CALCULATIONS OIL TO SALT HEX.pdf"
title: "4521-CAL-LOI-039-062-0001-GAR REV 1 MECHANICAL CALCULATIONS OIL TO SALT HEX"
doc_code: "4521-CAL-LOI-039-062-0001"
revision: ""
discipline: "Proceso / mecanica / tuberias"
deliverable_part: "Memoria y anejos"
chunk_count: 25
completed_chunks: 25
total_chunks: 25
---

# 4521-CAL-LOI-039-062-0001-GAR REV 1 MECHANICAL CALCULATIONS OIL TO SALT HEX

## Resumen

- Document title: Mechanical Calculation OIL TO SALT HEX
- Client: Arizona Solar One
- Project: HEX replacement TES Solana
- Supplier Code: 195001-CAL-001
- Revised by Alberto Abad A a and approved by Aitor Lopez de Subijana
- ASME VIII Div.2 is referenced for technical data
- Internal pressure calculations include shell side and channel side pressures
- External pressure, tubesheet calculation, nozzles, manhole cover, wind load, seismic load, and horizontal vessel analysis are not detailed in the provided text
- PV Elite 2016 Licensee: INGENIERIA Y TECNICAS DE MONTAJE LOINTEK S.L.
- File Name: 195001-CAL-001.00
- ASME TS Calc: tsh
- Shell and Channel data provided with specific dimensions, materials, and pressures

## Observaciones

- Shell Membrane + Bending Stress exceeds limit.

## Markdown estructurado

# Mechanical Calculation OIL TO SALT HEX
Client: Arizona Solar One
Project: HEX replacement TES Solana
4521-CAL-LOI-039-062-0001-GAR
Supplier Code: 195001-CAL-001
Revisor: Alberto Abad A a | Prepared by: Ivan Sainz de la Maza Sat, Reviewed by: Alberto Abad A a | Approved by: Aitor Lopez de Subijana
This Procedure is owned by Abengpoa. Its total or partial reproduction by any means as well as its distribution to third parties without the express written consent of Abengoa is forbidden
## Contents
- TECHNICAL DATA
- INTERNAL PRESSURE CALCULATIONS
- EXTERNAL PRESSURE CALCULATIONS
- TUBESHEET CALCULATION
- NOZZLES
- MANHOLE COVER
- WIND LOAD CALCULATION: LOWER SUPPORTS AND BOLTS
- SEISMIC LOAD CALCULATION: LOWER SUPPORTS AND BOLTS
- WIND LOAD CALCULATION: MIDSPANS, UPPER SUPPORTS AND BOLTS
- SEISMIC LOAD CALCULATION: MIDSPANS, UPPER SUPPORTS AND BOLTS
- HORIZONTAL VESSEL ANALYSIS: LOWER SUPPORTS AND BOLTS
- HORIZONTAL VESSEL ANALYSIS: MIDSPANS, UPPER SUPPORTS AND BOLTS
## TECHNICAL DATA
ASME VIII Div.2
84.8424 x 464.17 [Shell Side Tube Side]
Corrosion (except tubes) 0.125
Joint Efficiency eS
WIND CODE 1 ASCE 7-05 @
SEISMIC CODE 1 ASCE 7-05 @
## INTERNAL PRESSURE CALCULATIONS
| Element | Int. Press | Nominal | Total Corr | Thickness | Allowable Stress |
|---------|------------|---------|------------|-----------|------------------|
| Shell Side | 320 | 85.8661 | 37195.2 | 0.12500 | 84.8425 |
| Channel Side | 320 | 84.8425 | 37195.2 | 0.12500 | 84.8425 |
## EXTERNAL PRESSURE CALCULATIONS
Not detailed in the provided text.
## TUBESHEET CALCULATION
Not detailed in the provided text.
## NOZZLES
Not detailed in the provided text.
## MANHOLE COVER
Not detailed in the provided text.
## WIND LOAD CALCULATION: LOWER SUPPORTS AND BOLTS
Not detailed in the provided text.
## SEISMIC LOAD CALCULATION: LOWER SUPPORTS AND BOLTS
Not detailed in the provided text.
## WIND LOAD CALCULATION: MIDSPANS, UPPER SUPPORTS AND BOLTS
Not detailed in the provided text.
## SEISMIC LOAD CALCULATION: MIDSPANS, UPPER SUPPORTS AND BOLTS
Not detailed in the provided text.
## HORIZONTAL VESSEL ANALYSIS: LOWER SUPPORTS AND BOLTS
Not detailed in the provided text.
## HORIZONTAL VESSEL ANALYSIS: MIDSPANS, UPPER SUPPORTS AND BOLTS
Not detailed in the provided text.

[page 47]
PV Elite 2016 Licensee: INGENIERIA Y TECNICAS DE MONTAJE LOINTEK S.L.
FileName : 195001-CAL-001.00
ASME TS Calc : tsh
Shell Membrane + Bending Stress [Sigmas]:
= abs(Sigma_sm) + abs(Sigma_sb) (Should be <= 1.5*Ss)
= 100235.617 psi (Should be <= 55792.84)
Axial Channel Membrane Stress [Sigmacm]:
= De? / (4 * te * (De + te) ) * Pt
= 86.1161? / (4 * 0.6624 * (86.1161 + 0.6624 ) ) * -14.997
= -483.712 psi
Axial Channel! Bending Stress [Sigmacb]:
= 6*kc/tc? * [ Betac * (deltac*Pt) - 6*(1 - nu*) / (E*) *
Do/h? * (1 + h * Betac/2) * (Mp + Do?/32 * (Ps-Pt)) ]
= 6*313939.59 /0.6627 * [ 0.240 * 0.00 - 6*(1 - 0.350 )/6981298 *
83.031 /6.443? * (1 + 6.443 * 0.240 /2) *(-26253.09 + 83.0317/32 *
(320.00 - -15.00 )) ]
= -61175.688 psi
Channel Membrane + Bending Stress [Sigmac]:
= abs(Sigmacm) + abs(Sigmacb) (Should be <= 1.5*Sc)
= 61659.398 psi (Should be <= 55792.84)
Step 11, The Cylinder-to-Tubesheet Juncture is Overstressed.
Performing a simplified Elastic-Plastic calculation
(option 3 ) to reduce the overstress condition.
Modify Es and/or Ec and Recompute from Step 4 onwards.
Es = Es * (1.5 * Ss / Sigmas )%
= 24597214 * (1.5 * 37195.23 / 100235 )¥?
Es = 18351186.0 psi
Ec = Ec * (1.5 * Sc / Sigmac )%
= 24597214 * (1.5 * 37195.23 / 61659.40 )%
Ec = 23397826.0 psi
Tubesheet Bending Stress at Original Thk., after Elas-Plas iteration:
=6*M/ ( (mu*) * (h - h'g)?
= 6 * 96990.930 / ( (0.3051 ) * ( 6.4429 - 0.0000 )?
= 45941.9648 psi (Should be <= 52993.60)
Note: Tubesheet is Not overstressed after Elas-Plastic iteration
the design is acceptable. Recomputing tubesheet required thkickness.
Required Tubesheet Thk., for Bending Stress after Elas-Plas iteration [HreqB]:
= H + CATS + CATC = 5.9468 + 0.1250 + 0.1250 = 6.1968 in.
Required Tubesheet Thk. after Elas-Plas iteration (includes CA) [Hreq]:
= Max( HreqB, HreqS ) = Max( 6.1968 , 1.3982 ) = 6.1968 in.
Tube Weld Size Results per UW-20:
Tube Strength [Ft]:
= 3.1415 * t * (do-t) * Sa
= 3.1415 * 0.065 * ( 0.625 - 0.065 ) * 13890.00 = 1588.377 lb.
Fillet Weld Strength, Ff = 0.0
Groove Weld Strength [Fg]:
= .85 * 3.1415 * ag * (do + 0.67*ag) * Sw (but not > Ft)
= .85 * 3.1415 * 0.065 * (0.625 + 0.67*0.065 ) * 13890.00
= 1588.3766 1b.
Max. Allow. Tube-Tubesheet Joint load, Lmax
40
[page 48]
PV Elite 2016 Licensee: INGENIERIA Y TECNICAS DE MONTAJE LOINTEK S.L.
FileName : 195001-CAL-001.00
ASME TS Calc : tsh
= Ft = 1588.3766 1b.
Design Strength Ratio [fd]:
= 1.0000
Weld Strength Factor [fw]:
= Sot / ( Min(Sot, S) ) = 1.0000
Min Weld Length [ar]:
= ( (0.75 * do)? + 1.76*t*(do - t)* fw * fd) )% - .75 * do
= 0.0640 in.
Minimum Required Groove Weld Leg agr 0.0650 in.
Tube-Tubesheet Jt allowable, 1588.38 is >= tube strength 1588.38 lb.
Note: This tube-tubesheet joint is a Full Strength joint
Stress/Force summary for loadcase D2 corr. (Psd,max + Ptd,min):
Stress Description Actual Allowable Pass/Fail
Tubesheet bend. stress 45942.0 <= 52993.6 psi Ok
Tubesheet shear stress 3777.5 <= 21197.4 psi ok
Stress in Shell at Tubesheet 100235.6 <= 111585.7 psi ok
Stress in Channel at Tubesheet 61659.4 <= 111585.7 psi ok
Thickness results for loadcase D2 corr. (Psd,max + Ptd,min):
Thickness (in.) Required Actual P/F |
Tubesheet Thickness : 6.1968 6.6929 ok |

= 97.101 psig
Average Primary Membrane Stress [SigmaAvg]:
= ( f£N + fS + fY ) / AT
= ( 604.201 + 2011.841 + 3629.958 )/4.782
= 1306.184 psi
General Primary Membrane Stress [SigmaCirc]:
=P +*Rxs / (2 * teff )
= 14.997 * 43.388/( 2 * 0.662 )
= 491.2 psi
Maximum Local Primary Membrane Stress [PL]:
= max( 2 * SigmaAvg - SigmaCire, SigmaCire )
= max( 2 * 1306,.184 - 491.171 , 491.171 )
= 2121.2 psi
Summary of Nozzle Pressure/Stress Results:
Allowed Local Primary Membrane Stress Sallow 13733.84 psi
Local Primary Membrane Stress PL 2121.20 psi
Maximum Allowable External Pressure Pmax 97.10 psig
Input Echo, WRC107/537 Item 1, Description: T2 H
Diameter Basis for Vessel Vbasis ID
Cylindrical or Spherical vessel cylsph Spherical
Internal Corrosion Allowance Cas 0.1250 in
Vessel Diameter Dv 85.866 in.
Vessel Thickness Tv 0.787 in.
Design Temperature 750.20 °F
Vessel Material SA-533 B
Vessel Cold S.I. Allowable sme 37500.00 psi
Vessel Hot S.I. Allowable Smh 37195.20 psi
Attachment Type Type Round
WRC107 Attachment Classification Holsol Hollow
Corrosion Allowance for Nozzle can 0.1250 in.
Nozzle Diameter Dn 22.064 in.
Nozzle Thickness Tn 0.968 in.
Nozzle Material SA-106 C
Nozzle Cold S.I. Allowable sNme 26700.00 psi
Nozzle Hot §.I. Allowable SNmh 14788.80 psi
Design Internal Pressure Dp 322.349 psig
Include Pressure Thrust No
External Forces and Moments in WRC 107/537 Convention:
Radial Load (sus) P -5129.0 Ib.
Longitudinal Shear (sus) (vl) vi 6276.3 1b.
Circumferential Shear (SUS) (ve) v2 6276.3 1b.
Circumferential Moment (SUS) (Mc) M1 35721.0 £t.1b.
Longitudinal Moment (sus) (M1) M2 35721.0 £t.1b.
Torsional Moment (sus) Mt 50555.5 ft.1b.
Use Interactive Control No
WRC1O7 Version Version March 1979
Include Pressure Stress Indices per Div. 2 No
Compute Pressure Stress per WRC-368 No
WRC 107 Stress Calculation for SUStained loads:
Radial Load P -5129.0 lb.
