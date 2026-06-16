---
doc_id: "d66d2b9f2b3faaf6"
path: "12 As Built TES 6/04_Piping/03_Stress Calculation report/4521-INF-AEE-21-63-0004 (A03)_Rev00_Input Echo.pdf"
title: "4521-INF-AEE-21-63-0004 (A03) Rev00 Input Echo"
doc_code: "4521-INF-AEE-21-63-0004"
revision: ""
discipline: "Proceso / mecanica / tuberias"
deliverable_part: "Planos"
chunk_count: 16
completed_chunks: 16
total_chunks: 16
---

# 4521-INF-AEE-21-63-0004 (A03) Rev00 Input Echo

## Resumen

- CAESAR II version 8.00.00.5600 used for analysis
- Job name: HTF2
- License to SPLM
- Static load cases listed from 1 to 46
- Pipe data includes dimensions, materials, and loads
- Uniform load vectors provided in G-s units
- Allowable stresses calculated for different segments
- Job: HTF2
- Software version: CAESAR II 2016 Ver.8.00.00.5600
- Date and time: JAN 31, 2017 Time: 9:55
- Input listing from nodes 23320 to 23445
- Bends at 'TO' end with radius of 30.000 in.

## Observaciones

- Potential OCR issues with some node numbers and values.
- Potential OCR issues with some numbers and symbols
- Potential OCR errors in some values, especially negative numbers.

## Markdown estructurado

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## Table of Contents
- LISTING OF STATIC LOAD CASES FOR THIS ANALYSIS
- INPUT LISTING

## Listing of Static Load Cases
1 (HGR) CASE NOT ACTIVE
2 (HGR) CASE NOT ACTIVE
3 (HYD) WW+HP+H
4 (OPE) W+D1+T1+P1+H
5 (OPE) W+D2+T2+P2+H
6 (OPE) W+D2+T2+P2+H+F1
7 (OPE) W+D1+T1+P1+H+U1
8 (OPE) W+D1+T1+P1+H-U1
9 (OPE) W+D1+T1+P1+H+U2
10 (OPE) W+D1+T1+P1+H-U2
11 (OPE) W+D1+D4+T1+P1+H
12 (OPE) W+D1-D4+T1+P1+H
13 (OPE) W+D1+D5+T1+P1+H
14 (OPE) W+D1-D5+T1+P1+H
15 (OPE) W+D1+D4+T1+P1+H+U1
16 (OPE) W+D1-D4+T1+P1+H+U1
17 (OPE) W+D1+D4+T1+P1+H-U1
18 (OPE) W+D1-D4+T1+P1+H-U1
19 (OPE) W+D1+D5+T1+P1+H+U2
20 (OPE) W+D1-D5+T1+P1+H+U2
21 (OPE) W+D1+D5+T1+P1+H-U2
22 (OPE) W+D1-D5+T1+P1+H-U2
23 (OPE) W+D1+T1+P1+H+WIN1
24 (OPE) W+D1+T1+P1+H-WIN1
25 (SUS) W+P1+H
26 (SUS) W+P2+H
27 (OCC) L27=L6-L5
28 (OCC) L28=L7-L4
29 (OCC) L29=L8-L4
30 (OCC) L30=L9-L4
31 (OCC) L31=L10-L4
32 (OCC) L32=L23-L4
33 (OCC) L33=L24-L4
34 (EXP) L34=L4-L25
35 (EXP) L35=L5-L26
36 (EXP) L36=L11-L25
37 (EXP) L37=L12-L25
38 (EXP) L38=L13-L25
39 (EXP) L39=L14-L25
40 (OCC) L40=L25+L27
41 (OCC) L41=L25+L28
42 (OCC) L42=L25+L29
43 (OCC) L43=L25+L30
44 (OCC) L44=L25+L31
45 (OCC) L45=L25+L32
46 (OCC) L46=L25+L33

## Input Listing
Job Description:
- PROJECT:
- CLIENT :
- ANALYST:
- NOTES : 
CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) JAN 31,2017 9:55:42
PIPE DATA
From 7951 To 9200 DX= 4.750 ft.
B31.3 (2014) Cycle Max Switch = ON Sc= 20,000 lb./sq.in.
Sh1= 18,296 lb./sq.in. Sh2= 13,900 lb./sq.in. Sh3= 20,000 lb./sq.in.
Sh4= 20,000 lb./sq.in. Sh5= 20,000 lb./sq.in. Sh6= 20,000 lb./sq.in.
Sh7= 20,000 lb./sq.in. Sh8= 20,000 lb./sq.in. Sh9= 20,000 lb./sq.in.
Dia= 24.000 in. Wall= .688 in. Cor= .0300 in.
GENERAL
T1= 564 F T2= 750 F P1= 260.0000 lb./sq.in. P2= 350.0000 lb./sq.in.
PHyd= 525.0000 lb./sq.in. Mat= (305)API-5L B E= 29,687,500 lb./sq.in.
EH1= 26,916,000 lb./sq.in. EH2= 24,900,000 lb./sq.in.
EH3= 29,687,500 lb./sq.in. EH4= 29,687,500 lb./sq.in.
EH5= 29,687,500 lb./sq.in. EH6= 29,687,500 lb./sq.in.
EH7= 29,687,500 lb./sq.in. EH8= 29,687,500 lb./sq.in. EH9= 29,687,500 lb./sq.in.
v = .292 Pipe Den= .2830000 lb./cu.in. Fluid Den= .0675000 lb./cu.in. Insul Thk= 7.000 in.
Insul Den= .0066550 lb./cu.in.
RIGID Weight= .00 lb.
UNIFORM LOAD
Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's
Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's
Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's
ALLOWABLE STRESSES
From 7951 To 23221 DX= -4.083 ft.
RIGID Weight= .00 lb.
From 9200 To 9210 DY= -2.283 ft.
B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in.
Sh1= 20,000 lb./sq.in. Sh2= 19,810 lb./sq.in. Sh3= 20,000 lb./sq.in.
Sh4= 20,000 lb./sq.in. Sh5= 20,000 lb./sq.in. Sh6= 20,000 lb./sq.in.
Sh7= 20,000 lb./sq.in. Sh8= 20,000 lb./sq.in. Sh9= 20,000 lb./sq.in.
GENERAL
T1= 247 F T2= 410 F
RIGID Weight= .00 lb.
RESTRAINTS
Node 9210 ANC
ALLOWABLE STRESSES
From 9101 To 9102 DY= -3.500 ft.
B31.3 (2014) Cycle Max Switch = ON Sc= 20,000 lb./sq.in.
Sh1= 14,628 lb./sq.in. Sh2= 13,900 lb./sq.in. Sh3= 20,000 lb./sq.in.

[page 10]

CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

INPUT LISTING
10 
 ----------------------------------------------------------------------------- 
 From 23320 To 23330 DZ= 3.766 ft.
 B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in. Sh1= 14,594 lb./sq.in. Sh2= 13,900 lb./sq.in. Sh3= 20,000 lb./sq.in. Sh4= 20,000 lb./sq.in. Sh5= 20,000 lb./sq.in. Sh6= 20,000 lb./sq.in. Sh7= 20,000 lb./sq.in. Sh8= 20,000 lb./sq.in. Sh9= 20,000 lb./sq.in.
 Dia= 20.000 in. Wall= .375 in.
 GENERAL
 T1= 738 F P1= 260.0000 lb./sq.in. Fluid Den= .0225100 lb./cu.in. Insul Thk= 7.000 in.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23329
 Angle/Node @2= .00 23328
 ALLOWABLE STRESSES
 ----------------------------------------------------------------------------- 
 From 23330 To 23340 DY= -32.573 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23339
 Angle/Node @2= .00 23338
 ----------------------------------------------------------------------------- 
 From 23340 To 23345 DX= 10.240 ft.
 RESTRAINTS
 Node 23345 LIM
 HANGERS
 Hanger Node =23345 Hanger Table = 5 Available Space = .0000 in.
 Allowed Load Variation = 25.0000 No. Hangers = 0.0 Short Range Flag = -1
 User Operating Load = .00 lb. Free Node = 0 Free Node = 0
 Free Code = 0.0 Spring Rate = .00 lb./in.
 Theoretical Cold Load = .00 lb.
 ----------------------------------------------------------------------------- 
 From 23345 To 23347 DX= 30.206 ft.
 RESTRAINTS
 Node 23347 +Y Mu = .30
 ----------------------------------------------------------------------------- 
 From 23347 To 23350 DX= 5.206 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23349
 Angle/Node @2= .00 23348
 ----------------------------------------------------------------------------- 
 From 23350 To 23352 DZ= -10.000 ft.
 RESTRAINTS
 Node 23352 +Y Mu = .30
 Node 23352 LIM K= 0.0 lb./in. Gap= .070 in.
 ----------------------------------------------------------------------------- 
 From 23352 To 23353 DZ= -23.833 ft.
 ----------------------------------------------------------------------------- 
 From 23353 To 23354 DZ= -23.833 ft.
 RESTRAINTS
 Node 23354 +Y Mu = .30
 Node 23354 Guide
 Node 23354 LIM Gap= .070 in.
 ----------------------------------------------------------------------------- 
 From 23354 To 23361 DZ= -30.833 ft.
 RESTRAINTS
 Node 23361 +Y Mu = .30
 Node 23361 Guide Gap= .070 in.

[page 11]

CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

INPUT LISTING
11 
 ----------------------------------------------------------------------------- 
 From 23361 To 23360 DZ= -4.401 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23359
 Angle/Node @2= .00 23358
 ----------------------------------------------------------------------------- 
 From 23360 To 23370 DX= 20.500 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23369
 Angle/Node @2= .00 23368
 ----------------------------------------------------------------------------- 
 From 23370 To 23380 DZ= -17.448 ft.
 RESTRAINTS
 Node 23380 +Y Mu = .30
 ----------------------------------------------------------------------------- 
 From 23380 To 23390 DZ= -42.152 ft.
 RESTRAINTS
 Node 23390 +Y Mu = .30
 Node 23390 Guide Gap= .070 in.
 ----------------------------------------------------------------------------- 
 From 23390 To 23400 DZ= -15.385 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23399
 Angle/Node @2= .00 23398
 ----------------------------------------------------------------------------- 
 From 23400 To 23410 DX= -8.172 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23409
 Angle/Node @2= .00 23408
 ----------------------------------------------------------------------------- 
 From 23410 To 23420 DZ= -2.500 ft.
 ----------------------------------------------------------------------------- 
 From 23420 To 23430 DZ= -4.828 ft.
 RESTRAINTS
 Node 23430 +Y Mu = .30
 ----------------------------------------------------------------------------- 
 From 23430 To 23440 DZ= -3.411 ft.
 BEND at "TO" end
 Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 23439
 Angle/Node @2= .00 23438
 ----------------------------------------------------------------------------- 
 From 23440 To 23441 DY= 6.498 ft.
 ----------------------------------------------------------------------------- 
 From 23441 To 23442 DY= 6.498 ft.
 RESTRAINTS
 Node 23442 X Gap= .200 in.
 ----------------------------------------------------------------------------- 
 From 23442 To 23446 DY= 3.249 ft.
 ----------------------------------------------------------------------------- 
 From 23446 To 23443 DY= 3.249 ft.
 ----------------------------------------------------------------------------- 
 From 23443 To 23447 DY= 3.249 ft.
 ----------------------------------------------------------------------------- 
 From 23447 To 23444 DY= 3.249 ft.
 ----------------------------------------------------------------------------- 
 From 23444 To 23445 DY= 6.498 ft.

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Page 12
- From 23445 To 23450 DY= 6.498 ft.
- From 23450 To 23460 DY= 5.000 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000
- From 23460 To 23470 DZ= -4.000 ft.
- B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in., Sh1= 14,594 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in.
- From 23470 To 23480 DZ= -9.333 ft.
- B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in., Sh1= 14,594 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in.
- From 23320 To 23490 DZ= -3.000 ft.
- SIF's & TEE's
- From 23490 To 23500 DZ= -3.568 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000
- From 23500 To 23510 DX= 1.250 ft., DY= -2.167 ft.
- From 23510 To 23520 DX= .833 ft., DY= -1.443 ft.
- RESTRAINTS
  - Node 23520 ANC Cnode 23521
- From 23030 To 23530 DZ= -.906 ft.
- Dia= 2.375 in., Wall= .154 in., Insul Thk= 7.000 in.
- From 23040 To 23540 DY= .885 ft.
- Dia= 1.315 in., Wall= .133 in., Insul Thk= 7.000 in.
- From 23490 To 23550 DY= .901 ft.
- From 25365 To 25370 DZ= 2.557 ft.

### Page 13
- B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in., Sh1= 18,087 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in.
- Sy= 35,000 lb./sq.in.
- Dia= 20.000 in., Wall= .375 in., Cor= .0300 in.
- GENERAL
  - T1= 583 F, T2= 750 F, P1= 260.0000 lb./sq.in., P2= 350.0000 lb./sq.in.
  - PHyd= 525.0000 lb./sq.in., Mat= (305)API-5L B E= 29,687,500 lb./sq.in.
  - EH1= 26,802,000 lb./sq.in., EH2= 24,900,000 lb./sq.in.
  - EH3= 29,687,500 lb./sq.in., EH4= 29,687,500 lb./sq.in.
  - EH5= 29,687,500 lb./sq.in., EH6= 29,687,500 lb./sq.in.
  - EH7= 29,687,500 lb./sq.in., EH8= 29,687,500 lb./sq.in.
  - EH9= 29,687,500 lb./sq.in.
  - v = .292 Pipe Den= .2830000 lb./cu.in., Fluid Den= .0292993 lb./cu.in.
  - Insul Thk= 7.000 in., Insul Den= .0050800 lb./cu.in.
- RESTRAINTS
  - Node 25370 +Y Mu = .30, Node 25370 LIM Gap= .500 in.
- UNIFORM LOAD
  - Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's
  - Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's
  - Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's
- From 25370 To 25400 DZ= 1.348 ft.
- From 25400 To 25450 DZ= 3.281 ft.
- From 25450 To 25455 DZ= 5.230 ft.
- RESTRAINTS
  - Node 25455 Guide Gap= .070 in., Node 25455 +Y Mu = .30
- From 25455 To 25500 DZ= 13.353 ft.
- BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000
- UNIFORM LOAD
  - Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's
  - Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's
  - Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's
- From 25500 To 23020 DX= -2.500 ft.
- From 24000 To 24005 DZ= 2.556 ft.
- B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in., Sh1= 14,594 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in.
- Dia= 20.000 in., Wall= .375 in.
- GENERAL
  - T1= 738 F, P1= 260.0000 lb./sq.in., P2= 350.0000 lb./sq.in.
  - PHyd= 525.0000 lb./sq.in., Mat= (305)API-5L B E= 29,687,500 lb./sq.in.
  - EH1= 25,048,800 lb./sq.in., EH2= 24,900,000 lb./sq.in.

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Page 16
- **Node 27033**: +Y Mu = .30, Guide
- **From 27033 to 27036**: DZ= 32.130 ft., Bend Angle= 90.000°
- **Node 27036**: +Y Mu = .30, Guide
- **From 27040 to 27043**: DX= -7.000 ft., Bend Angle= 90.000°
- **Node 27048**: +Y Mu = .30
- **From 27055 to 27060**: DZ= 29.689 ft., Bend Angle= 90.000°
- **Node 27065**: +Y Mu = .30
- **From 27073 to 27076**: DZ= 42.083 ft.
### Page 17
- **Node 27095**: +Y Mu = .30, Guide
- **From 27095 to 27100**: DY= .002 ft., DZ= 31.796 ft., Bend Angle= 90.000°
- **Node 27102**: +Y Mu = .30, Guide
- **From 27105 to 27110**: DX= 14.161 ft., Bend Angle= 90.000°
- **Node 27120**: Weldolet, Hanger Node = 27120, Available Space = -500.0000 in.
- **From 27140 to 27150**: DX= .003 ft., DY= .003 ft., DZ= 4.285 ft.

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Page 18
- **BEND at "TO" end**: Radius= 30.000 in. (LONG), Bend Angle= 89.984, Angle/Node @1= 44.99 27149, Angle/Node @2= .00 27148
- **From 27150 To 27160**: DX= -4.567 ft., DY= 7.910 ft.
- **From 27160 To 27170**: DX= -.833 ft., DY= 1.444 ft.
- **RESTRAINTS**: Node 27170 ANC Cnode 27171
- **From 27120 To 27180**: DY= 1.063 ft., Dia= 8.625 in., Wall= .322 in., Insul Thk= 7.000 in.
- **From 27190 To 27195**: DZ= 10.582 ft., B31.3 (2014) Cycle Max Switch = --- Sc= 20,000 lb./sq.in., Sh1= 14,594 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in., Sh4= 20,000 lb./sq.in., Sh5= 20,000 lb./sq.in., Sh6= 20,000 lb./sq.in., Sh7= 20,000 lb./sq.in., Sh8= 20,000 lb./sq.in., Sh9= 20,000 lb./sq.in., Dia= 20.000 in., Wall= .375 in.
- **GENERAL**: T1= 738 F P1= 260.0000 lb./sq.in., Fluid Den= .0256504 lb./cu.in., Insul Thk= 7.000 in.
- **RESTRAINTS**: Node 27195 +Y Mu = .30, Node 27195 LIM Gap= .070 in., Node 27195 Guide Gap= .070 in.
- **UNIFORM LOAD**: Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's, Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's, Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's
- **ALLOWABLE STRESSES**: From 27195 To 27200: DZ= 5.702 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27199, Angle/Node @2= .00 27198
- **From 27200 To 27205**: DY= -5.000 ft.
- **From 27205 To 27207**: DY= -26.214 ft.
- **From 27207 To 27210**: DY= -12.985 ft., BEND at "TO" end, Radius= 20.000 in. (user), Bend Angle= 90.000, Angle/Node @1= 45.00 27209, Angle/Node @2= .00 27208
- **RESTRAINTS**: Node 27207 X Gap= .200 in.
- **From 27210 To 27215**: DZ= 3.328 ft., RESTRAINTS: Node 27215 +Y Mu = .30
- **From 27215 To 27220**: DZ= 7.328 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27219
### Page 19
- **Angle/Node @2= .00 27218**
- **From 27220 To 27225**: DX= -3.275 ft.
- **From 27225 To 27230**: DX= -4.275 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27229, Angle/Node @2= .00 27228
- **From 27230 To 27233**: DZ= 15.281 ft., RESTRAINTS: Node 27233 +Y Mu = .30, Node 27233 Guide Gap= .070 in.
- **From 27233 To 27240**: DZ= 18.035 ft.
- **From 27240 To 27239**: DZ= 24.035 ft., RESTRAINTS: Node 27239 +Y Mu = .30
- **From 27239 To 27234**: DZ= 17.629 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27235, Angle/Node @2= .00 27232
- **From 27234 To 27236**: DX= 20.500 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27237, Angle/Node @2= .00 27238
- **From 27236 To 27251**: DZ= 4.400 ft., RESTRAINTS: Node 27251 +Y Mu = .30, Node 27251 Guide Gap= .070 in.
- **From 27251 To 27252**: DZ= 30.833 ft., RESTRAINTS: Node 27252 +Y Mu = .30, Node 27252 Guide, Node 27252 LIM Gap= .070 in.
- **From 27252 To 27256**: DZ= 23.833 ft.
- **From 27256 To 27261**: DZ= 23.833 ft., RESTRAINTS: Node 27261 +Y Mu = .30, Node 27261 LIM K= 0.0 lb./in. Gap= .070 in.
- **From 27261 To 27260**: DZ= 10.000 ft., BEND at "TO" end, Radius= 30.000 in. (LONG), Bend Angle= 90.000, Angle/Node @1= 45.00 27259, Angle/Node @2= .00 27258
- **From 27260 To 27262**: DX= 5.376 ft., RESTRAINTS: Node 27262 +Y Mu = .30

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Page 20
- From 27262 To 27265 DX= 30.376 ft.
- RESTRAINTS: Node 27265 LIM, Hanger Node =27265, Hanger Table = 5 Available Space = .0000 in., Allowed Load Variation = 25.0000 No. Hangers = 0.0 Short Range Flag = -1
- From 27265 To 27270 DX= 9.898 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 89.994 Angle/Node @1= 45.00 27269, Angle/Node @2= .00 27268
- From 27270 To 27280 DX= .003 ft., DY= 32.562 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 27279, Angle/Node @2= .00 27278
- From 27280 To 27290 DZ= -3.763 ft., SIF's & TEE's: Node 27290 Weldolet
- From 27290 To 27300 DZ= -1.942 ft., SIF's & TEE's: Node 27300 Weldolet
- From 27300 To 27310 DZ= -4.646 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 27309, Angle/Node @2= .00 27308
- From 27310 To 27320 DX= -1.250 ft., DY= -2.165 ft.
- From 27320 To 27330 DX= -.833 ft., DY= -1.444 ft., RESTRAINTS: Node 27330 ANC Cnode 27331
- From 27290 To 27420 DY= 1.063 ft., Dia= 8.625 in., Wall= .322 in., Insul Thk= 7.000 in.
- From 27300 To 27430 DY= 1.004 ft., Dia= 4.500 in., Wall= .237 in., Insul Thk= 7.000 in.
- From 27190 To 28680 FILTER DZ= -3.224 ft., B31.3 (2014) Cycle Max Switch = ON Sc= 20,000 lb./sq.in., Sh1= 15,574 lb./sq.in., Sh2= 15,500 lb./sq.in., Sh3= 20,000 lb./sq.in., Sh4= 20,000 lb./sq.in., Sh5= 20,000 lb./sq.in., Sh6= 20,000 lb./sq.in., Sh7= 20,000 lb./sq.in., Sh8= 20,000 lb./sq.in., Sh9= 20,000 lb./sq.in., Sy= 30,000 lb./sq.in., Dia= 20.000 in., Wall= .375 in., Cor= .0300 in.

### Page 21
- T1= 738 F T2= 750 F P1= 260.0000 lb./sq.in. P2= 350.0000 lb./sq.in., PHyd= 525.0000 lb./sq.in., Mat= (155)A312 TP304 E= 28,487,500 lb./sq.in., EH1= 24,574,400 lb./sq.in., EH2= 24,500,000 lb./sq.in., EH3= 28,487,500 lb./sq.in., EH4= 28,487,500 lb./sq.in., EH5= 28,487,500 lb./sq.in., EH6= 28,487,500 lb./sq.in., EH7= 28,487,500 lb./sq.in., EH8= 28,487,500 lb./sq.in., EH9= 28,487,500 lb./sq.in., v = .292 Pipe Den= .2900000 lb./cu.in., Fluid Den= .0254800 lb./cu.in., Insul Thk= 7.000 in., Insul Den= .0050800 lb./cu.in.
- UNIFORM LOAD: Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's, Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's, Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's
- ALLOWABLE STRESSES: From 28680 To 28690 DZ= -7.792 ft., B31.3 (2014) Cycle Max Switch = ON Sc= 20,000 lb./sq.in., Sh1= 14,594 lb./sq.in., Sh2= 13,900 lb./sq.in., Sh3= 20,000 lb./sq.in., Sh4= 20,000 lb./sq.in., Sh5= 20,000 lb./sq.in., Sh6= 20,000 lb./sq.in., Sh7= 20,000 lb./sq.in., Sh8= 20,000 lb./sq.in., Sh9= 20,000 lb./sq.in., Sy= 35,000 lb./sq.in.
- T1= 738 F P1= 260.0000 lb./sq.in. P2= 350.0000 lb./sq.in., PHyd= 525.0000 lb./sq.in., Mat= (305)API-5L B E= 29,687,500 lb./sq.in., EH1= 25,048,800 lb./sq.in., EH2= 24,900,000 lb./sq.in., EH3= 29,687,500 lb./sq.in., EH4= 29,687,500 lb./sq.in., EH5= 29,687,500 lb./sq.in., EH6= 29,687,500 lb./sq.in., EH7= 29,687,500 lb./sq.in., EH8= 29,687,500 lb./sq.in., EH9= 29,687,500 lb./sq.in., v = .292 Pipe Den= .2830000 lb./cu.in.
- RESTRAINTS: Node 28690 +Y Mu = .30, Node 28690 Guide Gap= .070 in.
- ALLOWABLE STRESSES: From 28690 To 28700 DZ= -7.521 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 28699, Angle/Node @2= .00 28698
- From 28700 To 28725 DX= 12.880 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 28724, Angle/Node @2= .00 28723
- From 28725 To 28730 DZ= -14.107 ft., RESTRAINTS: Node 28730 +Y Mu = .30
- From 28730 To 28740 DZ= -8.252 ft.
- From 28740 To 28750 DZ= -3.642 ft., BEND at "TO" end, Radius= 30.000 in. (LONG) Bend Angle= 90.000 Angle/Node @1= 45.00 28749, Angle/Node @2= .00 28748
- From 28750 To 28775 DX= -13.758 ft.

# Stress Calculation Report

## Input Listing

### Bend at 'TO' end
- Radius: 30.000 in. (LONG)
- Bend Angle: 90.000
- Angle/Node @1: 45.00
- Angle/Node @2: .00

### DZ Values
- From 28775 To 28790: -4.750 ft.
- From 28790 To 28800: -25.430 ft.
- From 28800 To 28810: -2.061 ft.
- From 28810 To 28825: -7.939 ft.
- From 28825 To 28850: -23.479 ft.
- From 28850 To 28860: -3.380 ft.
- From 28860 To 28880: -19.083 ft.
- From 28880 To 28881: -2.372 ft.

### Uniform Load
- Vector1 in G-s X1 Dir = .11 g's Y1 Dir = .00 g's Z1 Dir = .00 g's
- Vector2 in G-s X2 Dir = .00 g's Y2 Dir = .00 g's Z2 Dir = .11 g's
- Vector3 in G-s X3 Dir = .00 g's Y3 Dir = .00 g's Z3 Dir = .00 g's

### Material Changes
- Mat= (305)API-5L B E= 29,687,500 lb./sq.in. v = .292 Density= .2830 lb./cu.in.
- Mat= (155)A312 TP304 E= 28,487,500 lb./sq.in. v = .292

### Allowable Stress Changes
- B31.3 (2014) Cycle Max Switch = ON Sc= 20,000 lb./sq.in.
- Sh1= 18,109 lb./sq.in. Sh2= 13,900 lb./sq.in. Sh3= 20,000 lb./sq.in. Sh4= 20,000 lb./sq.in. Sh5= 20,000 lb./sq.in. Sh6= 20,000 lb./sq.in. Sh7= 20,000 lb./sq.in. Sh8= 20,000 lb./sq.in. Sh9= 20,000 lb./sq.in.

## General Information
- T1= 581 F P1= 260.0000 lb./sq.in. P2= 350.0000 lb./sq.in.
- PHyd= 525.0000 lb./sq.in. Mat= (305)API-5L B E= 29,687,500 lb./sq.in.
- EH1= 26,814,000 lb./sq.in. EH2= 24,900,000 lb./sq.in. EH3= 29,687,500 lb./sq.in. EH4= 29,687,500 lb./sq.in. EH5= 29,687,500 lb./sq.in. EH6= 29,687,500 lb./sq.in. EH7= 29,687,500 lb./sq.in. EH8= 29,687,500 lb./sq.in. EH9= 29,687,500 lb./sq.in.
- v = .292 Pipe Den= .2830000 lb./cu.in. Fluid Den= .0292700 lb./cu.in. Insul Thk= 7.000 in.

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
Sc= 20,000 lb./sq.in.
Sh1= 14,628 lb./sq.in.
Sh2= 13,900 lb./sq.in.
Sh3= 20,000 lb./sq.in.
Sh4= 20,000 lb./sq.in.
Sh5= 20,000 lb./sq.in.
Sh6= 20,000 lb./sq.in.
Sh7= 20,000 lb./sq.in.
Sh8= 20,000 lb./sq.in.
Sh9= 20,000 lb./sq.in.

## BEND ELEMENTS
23045 23050 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23049 Angle/Node @2= .00 23048
23062 23060 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23059 Angle/Node @2= .00 23058
23060 23063 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23067 Angle/Node @2= .00 23071
23063 23066 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23065 Angle/Node @2= .00 23064
23072 23070 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23069 Angle/Node @2= .00 23068
23081 23080 Radius= 30.000 in. (LONG)
Bend Angle= 90.000 Angle/Node @1= 45.00
23079 Angle/Node @2= .00 23078
23085 23090 Radius= 30.000 in. (LONG)

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
Bend Angle= 90.000 Angle/Node @1= 45.00 Radius= 30.000 in. (LONG)
Bend Angle= 89.984 Angle/Node @1= 44.99 Radius= 20.000 in.

## RIGIDS
7951 9200 RIGID Weight= .00 lb.

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Page 32
- **Nodes and Weights**:
  - Nodes 9110, 9115, 9120, ..., 27331 with RIGID Weight = .00 lb.
  - Node 23180, 27130 with RIGID Weight = 4,012.00 lb.
- **Weldolets**:
  - Nodes 23020, 23030, ..., 27290 with Weldolet
- **Reducers**:
  - Nodes 23210, 23510, 27160, 27320 with Diam2= 24.000 in. Wall2= .375 in.
- **Restraints**:
  - Nodes 9210, 9125, ..., 23085 with various types and properties
### Page 33
- **Additional Restraints**:
  - Nodes 23102, 23103, ..., 24290 with +Y, Guide, LIM, ANC, X, etc.
- **Hanger Control Data**:
  - No. of Hanger Design Load Cases = 1
  - Actual Cold Load Flag = 0.0
  - Short Range Spring Flag = 1
  - Allowed Load Variation (%) = 25.0000
### Page 34
- **Hanger Data**:
  - Nodes 27105, 27170, ..., 29940 with Hanger Node and Table
- **Equipment Limits**:
  - Limiting Loads for Nozzle Nodes 23210, 23510, 27160, 27320
### Page 35
- **Additional Equipment Limits**

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
### Limiting Loads:
- A=pipe; B=ref; C=AxB
- FA= 5,129.00 lb.
- FB= 6,276.00 lb.
- FC= 6,276.00 lb.
- MA= 606,672.00 in.lb.
- MB= 428,652.00 in.lb.
- MC= 428,652.00 in.lb.

### Equipment Major Direction Vector:
- .0000 .0000 1.0000

### Interact. Mtd= Absolute

## UNIFORM LOAD Changes
### Vectors in G-s and F/L
- Multiple vectors with X, Y, Z directions set to .11 g's or lb./in.

## WIND/WAVE
- Wind Shape= .650 for multiple entries

## INPUT UNITS USED
- ENGLISH NOM/SCH INPUT= ON
- LENGTH inches x 1.000 = in.
- FORCE pounds x 1.000 = lb.
- MOMENTS(OUTPUT) inch-pounds x 0.083 = ft.lb.

## SETUP FILE PARAMETERS
- CONNECT GEOMETRY THRU CNODES = YES
- MIN ALLOWED BEND ANGLE = 5.00000
- MAX ALLOWED BEND ANGLE = 95.0000
- LOOP CLOSURE TOLERANCE = 1.00000 in.
- AUTO NODE NUMBER INCREMENT= 10.0000

# CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

## INPUT LISTING
40
BS 7159 Pressure Stiffening= Design Strain
FRP Property Data File= CAESAR.FRP
FRP Emod (axial) = 0.320000E+07 lb./sq.in.
FRP Ratio Gmod/Emod (axial) = 0.250000
FRP Ea/Eh*Vh/a = 0.152730
FRP Laminate Type = THREE
FRP Alpha = 12.0000 F
FRP Density = 0.600000E-01 lb./cu.in.
EXCLUDE f2 FROM UKOOA BENDING = NO

## EXECUTION CONTROL PARAMETERS
Rigid/ExpJt Print Flag ..... 1.000
Bourdon Option ............. .000
Loop Closure Flag .......... 2.000
Thermal Bowing Delta Temp .. .000 F
Liberal Allowable Flag ..... 1.000
Uniform Load Option ........ 1.000

Ambient Temperature ........ 25.000 F
Plastic (FRP) Alpha ........ 12.000
Plastic (FRP) GMOD/EMODa ... .250
Plastic (FRP) Laminate Type. 3.000
Eqn Optimizer .............. .000
Node Selection ............. .000
Eqn Ordering ............... .000
Collins .................... .000
Degree Determination ....... .000
User Eqn Control ........... .000

## COORDINATE REPORT
NODE X Y Z
7951 -1644.001 189.756 -394.080
9200 -1587.001 189.756 -394.080
...
24190 -1154.552 593.313 -2605.000

[page 43]

CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

INPUT LISTING
43
24235 -1154.552 593.313 -2428.125
24285 -1010.552 593.313 -2428.125
...
27046 -486.496 78.433 -2409.513
27048 -444.496 78.433 -2409.513
...
27261 -485.535 65.559 4.213

[page 44]

CAESAR II 2016 Ver.8.00.00.5600, (Build 150930) Date: JAN 31, 2017 Time: 9:55
Job:: HTF2
Licensed To:: SPLM: Edit company name in <system>\company.txt

INPUT LISTING
44
27260 -485.535 65.559 124.213
27262 -421.023 65.559 124.213
...
28881 -651.474 314.203 -3528.266
27010 -601.866 327.763 -3250.380
...
29943 -601.866 327.763 -3528.191
