# Transit Data Sources & Provenance Policy
## Public Transport Route Helper for India

### 1. Data Provenance & Verification Policy

To guarantee data integrity and protect users from fabricated transit information:
1. **Verified Corridor Data**:
   - Location: `data/processed/chennai_bengaluru/`
   - Verification Flag: `is_verified: TRUE`
   - Data Source Label: `Official Published Timetable 2026`
   - Cross-referenced against official schedules for Indian Railways, Chennai Metro (CMRL), Bengaluru Metro (Namma Metro BMRCL), and State Express Transport Corporations (KSRTC, SETC, BMTC, MTC).
2. **Demo Quarantine**:
   - Location: `data/demo/`
   - Verification Flag: `is_verified: FALSE`
   - Clearly labeled in API responses as `DEMO DATA`.
   - Never mixed into verified production records without explicit ingestion audits.
3. **No Fabrication Rule**:
   - If an external provider is unreachable or a schedule is unavailable, the application returns a clear diagnostic notice rather than inventing fictitious timings or fares.

---

### 2. Verified Stations Included (28 Stations)

| Station ID | Station Name | City | Transport Modes | Hub |
|---|---|---|---|---|
| `MAS` | Puratchi Thalaivar Dr. M.G.R Central Railway Station | Chennai | Train, Metro, Bus | Yes |
| `MS` | Chennai Egmore Railway Station | Chennai | Train, Metro, Bus | Yes |
| `TBM` | Tambaram Railway Station | Chennai | Train, Bus | Yes |
| `CMRL_CENTRAL` | Puratchi Thalaivar Dr. M.G.R Central Metro | Chennai | Metro | Yes |
| `CMRL_EGMORE` | Egmore Metro Station | Chennai | Metro | No |
| `CMRL_GUINDY` | Guindy Metro & Suburban Interchange | Chennai | Metro, Train, Bus | Yes |
| `CMRL_AIRPORT` | Chennai International Airport Metro | Chennai | Metro | Yes |
| `CMBT_BUS` | Chennai Mofussil Bus Terminus (Koyambedu) | Chennai | Bus, Metro | Yes |
| `KCBT_BUS` | Kalaignar Centenary Bus Terminus (Kilambakkam) | Chennai | Bus | Yes |
| `TNAGAR_BUS` | T. Nagar Bus Terminus | Chennai | Bus | No |
| `AJJ` | Arakkonam Junction | Arakkonam | Train | Yes |
| `KPD` | Katpadi Junction | Vellore | Train, Bus | Yes |
| `JTJ` | Jolarpettai Junction | Tirupattur | Train | Yes |
| `BWT` | Bangarapet Junction | Bangarapet | Train | Yes |
| `KJM` | Krishnarajapuram Railway Station | Bengaluru | Train, Metro, Bus | Yes |
| `BNC` | Bengaluru Cantt Railway Station | Bengaluru | Train, Bus | Yes |
| `SBC` | KSR Bengaluru City Junction | Bengaluru | Train, Metro, Bus | Yes |
| `YPR` | Yesvantpur Junction | Bengaluru | Train, Metro, Bus | Yes |
| `SMVB` | Sir M. Visvesvaraya Terminal (SMVT Bengaluru) | Bengaluru | Train, Bus | Yes |
| `BMRCL_MAJESTIC` | Nadaprabhu Kempegowda Station Majestic Metro | Bengaluru | Metro | Yes |
| `BMRCL_MGROAD` | Mahatma Gandhi Road Metro | Bengaluru | Metro | No |
| `BMRCL_INDIRANAGAR`| Indiranagar Metro Station | Bengaluru | Metro | No |
| `BMRCL_BYPL` | Baiyappanahalli Metro Station | Bengaluru | Metro | Yes |
| `BMRCL_WHITEFIELD` | Whitefield (Kadugodi) Metro Station | Bengaluru | Metro | Yes |
| `KBS_BUS` | Kempegowda Majestic Bus Station | Bengaluru | Bus | Yes |
| `SHANTINAGAR_BUS` | Shantinagar Bus Station | Bengaluru | Bus | Yes |
| `SILKBOARD_BUS` | Central Silk Board Bus Interchange | Bengaluru | Bus | No |
| `ECITY_BUS` | Electronic City Bus Terminal | Bengaluru | Bus | Yes |

---

### 3. Real Verified Services & Timetables

1. **Vande Bharat Express (20607 / 20608)**
   - MAS Dep: 05:50 | KPD: 07:13 | KJM: 09:48 | SBC Arr: 10:10 (Fastest: ~4h 20m)
   - Fares: Chair Car ₹995 | Executive ₹1885
2. **Shatabdi Express (12007 / 12008)**
   - MAS Dep: 06:00 | KPD: 07:38 | BNC: 10:18 | SBC Arr: 10:45 (~4h 45m)
   - Fares: Chair Car ₹965 | Executive ₹1750
3. **Brindavan Superfast Express (12639 / 12640)**
   - MAS Dep: 07:10 | AJJ: 08:08 | KPD: 08:58 | JTJ: 10:18 | BWT: 11:43 | KJM: 12:48 | BNC: 13:08 | SBC Arr: 13:40
   - Fares: Second Sitting (2S) ₹145 | AC Chair Car ₹520
4. **Lalbagh Superfast Express (12607 / 12608)**
   - MAS Dep: 15:30 | SBC Arr: 21:55
   - Fares: Second Sitting (2S) ₹145 | AC Chair Car ₹520
5. **Chennai - Bengaluru Superfast Mail (12657 / 12658)**
   - Overnight: MAS Dep: 22:50 | SBC Arr: 04:30
   - Fares: Sleeper ₹265 | AC 3-Tier ₹715 | AC 2-Tier ₹1010
6. **Kaveri Express (16021 / 16022)**
   - MAS Dep: 21:15 | SBC Arr: 03:55
7. **KSRTC Airavat Multi-Axle AC Buses**
   - CMBT Koyambedu &harr; Kempegowda Majestic (Dep: 06:30, 14:00, 23:00) | Fare: ₹780
8. **SETC Ultra Deluxe Semi-Sleeper Buses**
   - KCBT Kilambakkam &harr; Shantinagar (Dep: 08:00, 22:00) | Fare: ₹380
9. **Chennai Metro Rail (CMRL)**
   - Blue Line (Airport &harr; Central) & Green Line (Central &harr; CMBT) every 8-10 mins.
10. **Bengaluru Namma Metro (BMRCL)**
   - Purple Line (Whitefield &harr; Majestic) & Green Line (Yesvantpur &harr; Majestic) every 6-7 mins.

---

### 4. Extending to New Corridors

To import additional cities or corridors:
1. Export GTFS feed or CSV files adhering to the standard headers (`stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `transfers.txt`, `fares.txt`).
2. Upload via `POST /api/data/import` or place files in `data/processed/<corridor_name>/`.
3. The system executes automated validation (India geographic bounds check, stop sequence monotonicity, non-negative fares) and automatically indexes new nodes into the NetworkX graph.

