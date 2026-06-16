---
doc_id: "9dd0c7deb0a33ad5"
path: "12 As Built TES 6/04_Piping/03_Stress Calculation report/4521-INF-AEE-21-63-0004 (A06)_Rev00_Restraint and Stress Report.pdf"
title: "4521-INF-AEE-21-63-0004 (A06) Rev00 Restraint and Stress Report"
doc_code: "4521-INF-AEE-21-63-0004"
revision: ""
discipline: "Proceso / mecanica / tuberias"
deliverable_part: "Planos"
chunk_count: 13
completed_chunks: 13
total_chunks: 13
---

# 4521-INF-AEE-21-63-0004 (A06) Rev00 Restraint and Stress Report

## Resumen

- Axial, bending, torsion, and hoop stress calculations for various nodes.
- Code stress checks passed for multiple load cases.
- Load case definitions include hydraulic (HYD) and operational (OPE).
- Software used: CAESAR II 2016 Ver.8.00.00.5600, Build 150930.
- Job name: HTF2.

## Markdown estructurado

# Stress Calculation Report

## Axial, Bending, Torsion, and Hoop Stress Analysis

- **Node 27170**: Axial Stress: 4466.2 lb./sq.in., Bending Stress: 6415.2 lb./sq.in., Torsion Stress: 1140.0 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.
- **Node 27239**: Axial Stress: 4463.4 lb./sq.in., Bending Stress: 6835.4 lb./sq.in., Torsion Stress: 1102.5 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.
- **Node 23220**: Axial Stress: 4448.4 lb./sq.in., Bending Stress: 7779.9 lb./sq.in., Torsion Stress: 621.5 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.
- **Node 27060**: Axial Stress: 4458.0 lb./sq.in., Bending Stress: 7653.5 lb./sq.in., Torsion Stress: 1354.0 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.
- **Node 27236**: Axial Stress: 4455.6 lb./sq.in., Bending Stress: 8210.8 lb./sq.in., Torsion Stress: 749.5 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.
- **Node 23380**: Axial Stress: 4455.6 lb./sq.in., Bending Stress: 8210.8 lb./sq.in., Torsion Stress: 749.5 lb./sq.in., Hoop Stress: 8783.5 lb./sq.in.

## Code Stress Checks

- **LOADCASE 42 (OCC) L42=L25+L29**: Code Stress Check Passed, Ratio (%): 56.3
- **LOADCASE 43 (OCC) L43=L25+L30**: Code Stress Check Passed, Ratio (%): 61.8
- **LOADCASE 44 (OCC) L44=L25+L31**: Code Stress Check Passed, Ratio (%): 59.2
- **LOADCASE 45 (OCC) L45=L25+L32**: Code Stress Check Passed, Ratio (%): 55.0
- **LOADCASE 46 (OCC) L46=L25+L33**: Code Stress Check Passed, Ratio (%): 57.0

## Load Cases and Node Data

- **Node 27170**: Load Case 42 (OCC), FX: -565 lb., FY: -3588 lb., FZ: 93 lb.
- **Node 27239**: Load Case 43 (OCC), FX: -542 lb., FY: -3352 lb., FZ: 727 lb.
- **Node 23220**: Load Case 44 (OCC), FX: -542 lb., FY: -3352 lb., FZ: 727 lb.

## Software and Job Information

- **Software**: CAESAR II 2016 Ver.8.00.00.5600, Build 150930
- **Job Name**: HTF2
- **Licensed To**: SPLM: Edit company name in <system>

## Summary of Restraint Loads

- **Node Load Case FX lb. FY lb. FZ lb. MX ft.lb. MY ft.lb. MZ ft.lb. DX in. DY in. DZ in.
  - **LOADCASE 3 (HYD)**: WW+HP+H
  - **LOADCASE 4 (OPE)**: W+D1+T1+P1+H
  - **LOADCASE 5 (OPE)**: W+D2+T2+P2+H
  - **LOADCASE 6 (OPE)**: W+D2+T2+P2+H+F1
  - **LOADCASE 7 (OPE)**: W+D1+T1+P1+H+U1
  - **LOADCASE 8 (OPE)**: W+D1+T1+P1+H-U1
  - **LOADCASE 9 (OPE)**: W+D1+T1+P1+H+U2
  - **LOADCASE 10 (OPE)**: W+D1+T1+P1+H-U2
  - **LOADCASE 11 (OPE)**: W+D1+D4+T1+P1+H
  - **LOADCASE 12 (OPE)**: W+D1-D4+T1+P1+H
  - **LOADCASE 13 (OPE)**: W+D1+D5+T1+P1+H
  - **LOADCASE 14 (OPE)**: W+D1-D5+T1+P1+H
  - **LOADCASE 15 (OPE)**: W+D1+D4+T1+P1+H+U1
  - **LOADCASE 16 (OPE)**: W+D1-D4+T1+P1+H+U1
  - **LOADCASE 17 (OPE)**: W+D1+D4+T1+P1+H-U1
  - **LOADCASE 18 (OPE)**: W+D1-D4+T1+P1+H-U1
  - **LOADCASE 19 (OPE)**: W+D1+D5+T1+P1+H+U2
  - **LOADCASE 20 (OPE)**: W+D1-D5+T1+P1+H+U2
  - **LOADCASE 21 (OPE)**: W+D1+D5+T1+P1+H-U2
  - **LOADCASE 22 (OPE)**: W+D1-D5+T1+P1+H-U2
  - **LOADCASE 23 (OPE)**: W+D1+T1+P1+H+WIN1
  - **LOADCASE 24 (OPE)**: W+D1+T1+P1+H-WIN1
  - **LOADCASE 25 (SUS)**: W+P1+H
  - **LOADCASE 26 (SUS)**: W+P2+H
