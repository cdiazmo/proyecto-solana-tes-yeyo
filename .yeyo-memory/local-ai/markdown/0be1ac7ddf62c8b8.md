---
doc_id: "0be1ac7ddf62c8b8"
path: "02 GD LOI/mama/4521-MOM-LOI-039-062-0001-GAR  Performance Test Procedure.pdf"
title: "4521-MOM-LOI-039-062-0001-GAR Performance Test Procedure"
doc_code: "4521-MOM-LOI-039-062-0001"
revision: ""
discipline: "Proceso / mecanica / tuberias"
deliverable_part: "Memoria y anejos"
chunk_count: 3
completed_chunks: 3
total_chunks: 3
---

# 4521-MOM-LOI-039-062-0001-GAR Performance Test Procedure

## Resumen

- Document describes performance testing procedure for Oil to Salt heat exchangers.
- Tests aim to determine thermal balance, pressure drop, HAT/CAT values, and OHTC/Duty/Pressure loss.
- Calculation method uses ASME PTC 12.5 and Correction Factors for real conditions comparison.
- Stakeholders must agree on testing responsible, reference conditions, and inspection criteria before starting tests.
- Client is responsible for the test execution while Lointek handles analysis and report issuance.
- Four out of six variables are measured to calculate the remaining two based on ASME PTC 12.5.
- Five reference conditions (Cases 1-5) are defined for different operational scenarios.
- Heat exchangers must operate at steady state conditions for at least 15 minutes before testing.
- Fouling coefficient is initially set but may be reviewed based on direct observation and stakeholder agreement.
- Instruments installed during assembly are used to calculate the performance of the exchanger.
- Accuracy requirements include Flow ± 5%, Temperature ± 3.69 ºF, Pressure ± 0.3 %.
- Uncertainty in results: Transfer Rate ± 3 – 10 %, Heat Exchanged ± 3 – 10 %, Pressure Loss ± 3 – 12 %.

## Markdown estructurado

# Performance Test Procedure

**Client:** Arizona Solar One
**Project:** HEX replacement TES Solana
**Document code:** 4521-MOM-LOI-039-062-0001-GAR
**Supplier Code:** 195001-INS-0001
**Revision:** 03
**Date:** 28/03/2017

## Aim
This document aims to describe the actions and measures to be considered during performance testing of Oil to Salt heat exchangers supplied by LOINTEK for HEX replacement TES Solana, placed in Arizona, USA. These tests shall determine:
- The thermal balance of both fluids, in steady state operation at reference conditions as indicated in Section 6 of the current procedure.
- Pressure drop on tube side and shell side at reference conditions.
- HAT (Hot Approach Temperature) and CAT (Cold Approach Temperature) values estimated at reference conditions.
- OHTC, Duty and Pressure loss calculation at reference conditions

## References
- ASME PTC 12.5-2000 Single Phase Heat Exchangers: Performance Test Codes.
- 4521-MEM-EPC-075-000-0001 MS-HTF HEX Warranty Annex COMMENTED

## Calculation method
The calculation method used is based on st ated in ASME PTC 12.5 and predicts the performance values to be compared with the values measured during the test.

During the test, data of variables set for monitoring the performance test, shall be extracted from the centralized information on the DCS.

From these data, those which are considered representative of system operation shall be extracted.

In order to cross check the mentioned real measured values and the equipment production under the given input data, the “Correction Factors” are used. These factors (previously calculated with HTRI) simulate the sensitivity of a specific output of the unit (i.e. Tout_htf, Tout_ms, etc.) when the variables entered to the equipment differ from those in the Performance Case.

For this type of unit, the outputs to be cross checked are: Tout_htf, Tout_ms, Pout_htf and Pout_ms. The Correction Factors for each one of this values will be dependent of the following variables:
- Tout_htf = F (Qhtf, Qms, Tin_htf, Tin_ms)
- Tout_ms = F (Qhtf, Qms, Tin_htf, Tin_ms)
- Pout_htf = F (Qhtf)
- Pout_ms = F (Qms)

First of all, if the data match (within the limits set out in paragraph 7), LOINTEK will compare H&MB of both sides and will confirm that their similitude is acceptable in concordance to AME PTC 12.5. Then, once such acceptance is reach, LOINTEK would be allowed to figuring performance at reference conditions.

In case of non- coincidence, it is necessary to study the possible causes of the deviation (deficient instrument measures, fouling coefficient different from the estimate, other causes...).

The data will be sent to AEPC for approval.

# Performance Test Procedure

## Testing Responsible
Client is responsible for carrying out this test, but Lointek is responsible for the analysis of results and issuance of the report.

## Reference Condition Definition
The measurement of four of the six variables for the thermal calculation of the system shall be established in order to calculate the two other variables and thus determine the accuracy of the calculations according to ASME PTC 12.5. It will be agreed between Client and Lointek which measurements are the most reliable.

## Reference Conditions of the Equipment
### Case 1: Maximum Charge
- **Hot fluid, HTF**: Mass flow Qh = 4,105,612 Lb/hr, Inlet temperature Th = 737.60 ºF, Inlet pressure Ph = 237.6 psia
- **Cold fluid, MOLTEN SALT**: Mass flow Qc = 6,622,459 Lb/hr, Inlet temperature Tc = 554.4 ºF, Inlet pressure Pc = 137.7 psia
- **Calculated variables**: Outlet temperature Th = 564.0 ºF, Outlet pressure Ph = 186.8 psia

### Case 2: Discharging
- **Hot fluid, MOLTEN SALT**: Mass flow Qh = 6,604,023 Lb/hr, Inlet temperature Th = 729 ºF, Inlet pressure Ph = 112.8 psia
- **Cold fluid, HTF**: Mass flow Qc = 4,083,090 Lb/hr, Inlet temperature Tc = 545 ºF, Inlet pressure Pc = 234.2 psia
- **Calculated variables**: Outlet temperature Th = 556.2 ºF, Outlet pressure Ph = 62.69 psia

### Case 3: Summer Charge
- **Hot fluid, HTF**: Mass flow Qh = 3,102,130 Lb/hr, Inlet temperature Th = 737.6 ºF, Inlet pressure Ph = 214.6 psia
- **Cold fluid, MOLTEN SALT**: Mass flow Qc = 5,079,985 Lb/hr, Inlet temperature Tc = 553.9 ºF, Inlet pressure Pc = 114.7 psia
- **Calculated variables**: Outlet temperature Th = 561.2 ºF, Outlet pressure Ph = 184.6 psia

### Case 4: Winter Discharge
- **Hot fluid, MOLTEN SALT**: Mass flow Qh = 6,620,487 Lb/hr, Inlet temperature Th = 728.3 ºF, Inlet pressure Ph = 113.4 psia
- **Cold fluid, HTF**: Mass flow Qc = 4,081,984 Lb/hr, Inlet temperature Tc = 543.8 ºF, Inlet pressure Pc = 237.0 psia
- **Calculated variables**: Outlet temperature Th = 564.3 ºF, Outlet pressure Ph = 63.83 psia

### Case 5: 25% Load Charging
- **Hot fluid, HTF**: Mass flow Qh = 1,659,043 Lb/hr, Inlet temperature Th = 737.60 ºF, Inlet pressure Ph = 187.2 psia
- **Cold fluid, MOLTEN SALT**: Mass flow Qc = 1,001,893 Lb/hr, Inlet temperature Tc = 594.3 ºF, Inlet pressure Pc = 68.49 psia
- **Calculated variables**: Outlet temperature Th = 598.1 ºF, Outlet pressure Ph = 183.2 psia

## Measurement of System Variables
The Oil to Salt heat exchanger must operate at steady state conditions before starting with taking measures for at least 15 minutes.

## Agreements on Fouling Conditions to be Considered
The fouling coefficient used in design calculations is established as the initial criterion. Only in the case that a direct observation of the exchange surfaces is made and it is checked that some extraordinary element involves reasonably a review of this coefficient, a different coefficient to the design one shall be used. In any case, this new value will be agreed between stakeholders.

## Effect of Fouling Resistance in Each Shell
| Case | Load | Fouling Duty | TSalt Out | THTF Out |
|------|------|--------------|-----------|----------|
| Charge Maximum | 0x | 423 MBtu/hr | 732.1 ºF | 562.6 ºF |
| 1x | 419.8 MBtu/hr | 730.8 ºF | 564.0 ºF |
| 2x | 414.5 MBtu/hr | 728 ºF | 566.4 ºF |

## Inlet Conditions (Max Charge)
- **Salt Flow Rate**: 6,622,459 lb/hr
- **Salt Inlet Temperature**: 554.4 ºF
- **HTF Flow Rate**: 4,105,612 lb/hr
- **HTF Inlet Temperature**: 737.6 ºF

# Performance Test Procedure

## Scope and criteria for selection of instruments used in the system variable measurements
- Instruments installed during assembly are used to calculate the performance of the exchanger.
- Placement should be as close as possible to the exchanger.
- Accuracy requirements: Flow ± 5%, Temperature ± 3.69 ºF, Pressure ± 0.3 %
- Result Uncertainty: Transfer Rate ± 3 – 10 %, Heat Exchanged ± 3 – 10 %, Pressure Loss ± 3 – 12 %

## Known damages and deficiencies identification
- Include a plane of the tubesheet for plugged tubes in Annex A.
- Calculate total thermal duty and outlet temperatures using H TRI calculation program if tubes are plugged to prevent leaking.

## Inspections planning
- Review overall dimensions, lagging placement, number of plugged tubes, cleaning of surfaces, and instrument placement before final performance test.

## Number, installation and location of measuring instruments
- Install thermometers, manometers, and mass flow meters at inlet and outlet of hot and cold fluids on each equipment.

## Frequency of measures
- Perform measures during steady state conditions for at least 15 minutes.
- Record 15 measurements every 2 minutes for 30 minutes.
- Reject inconsistent data and repeat process if operating conditions change.
