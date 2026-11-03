========================================================================
PUBLIC TRANSPORT ROUTE HELPER FOR INDIA - DATASET SEPARATION POLICY
========================================================================

1. VERIFIED PRODUCTION DATASET:
   Location: data/processed/chennai_bengaluru/
   Coverage: Chennai Urban (CMRL Metro, MTC), Intercity Rail Corridor
             (Southern Railway / South Western Railway), Intercity Bus
             (KSRTC, SETC), and Bengaluru Urban (Namma Metro BMRCL, BMTC).
   Verification: Cross-referenced with official timetables (IRCTC, CMRL, BMRCL, KSRTC)
                 for 2026 operational schedules.
   is_verified: TRUE

2. DEMO / EXPERIMENTAL DATASET:
   Location: data/demo/
   Purpose: Pipeline testing, edge cases, synthetic stress tests.
   is_verified: FALSE (Clearly tagged in API responses as 'DEMO DATA').
   Never presented as verified real-time transport information.

3. DATA REFRESH & GTFS INGESTION:
   New GTFS ZIP files or CSVs can be uploaded via POST /api/data/import
   with automatic schema validation, India bounding-box coordinate checks,
   and audit logs in table 'dataset_imports'.
========================================================================

