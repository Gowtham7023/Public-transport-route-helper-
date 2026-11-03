import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.models import (
    DataSource, TransportMode, Station, Route, Trip,
    StopTime, Connection, Transfer, Fare, TransportAgency, Place
)
from app.services.gazetteer_service import GazetteerService

logger = logging.getLogger(__name__)

def seed_india_wide_transit(db: Session = None):
    """Seed comprehensive multi-state transit records covering all major Indian corridors."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        logger.info("Initializing India-wide transit datasets and agencies...")

        # 1. Transport Agencies
        agencies = [
            TransportAgency(id="IR", name="Indian Railways", short_name="Indian Railways", agency_type="railway", state="All India", website="https://indianrailways.gov.in"),
            TransportAgency(id="KSRTC", name="Karnataka State Road Transport Corporation", short_name="KSRTC", agency_type="intercity_bus", state="Karnataka", website="https://ksrtc.in"),
            TransportAgency(id="SETC", name="State Express Transport Corporation Tamil Nadu", short_name="SETC", agency_type="intercity_bus", state="Tamil Nadu", website="https://tnstc.in"),
            TransportAgency(id="TNSTC", name="Tamil Nadu State Transport Corporation", short_name="TNSTC", agency_type="intercity_bus", state="Tamil Nadu", website="https://tnstc.in"),
            TransportAgency(id="APSRTC", name="Andhra Pradesh State Road Transport Corporation", short_name="APSRTC", agency_type="intercity_bus", state="Andhra Pradesh", website="https://apsrtc.ap.gov.in"),
            TransportAgency(id="TSRTC", name="Telangana State Road Transport Corporation", short_name="TSRTC", agency_type="intercity_bus", state="Telangana", website="https://tsrtc.telangana.gov.in"),
            TransportAgency(id="KSRTC_KL", name="Kerala State Road Transport Corporation (SWIFT)", short_name="Kerala RTC", agency_type="intercity_bus", state="Kerala", website="https://keralartc.com"),
            TransportAgency(id="MSRTC", name="Maharashtra State Road Transport Corporation", short_name="MSRTC", agency_type="intercity_bus", state="Maharashtra", website="https://msrtc.maharashtra.gov.in"),
            TransportAgency(id="RSRTC", name="Rajasthan State Road Transport Corporation", short_name="RSRTC", agency_type="intercity_bus", state="Rajasthan", website="https://transport.rajasthan.gov.in/rsrtc"),
            TransportAgency(id="GSRTC", name="Gujarat State Road Transport Corporation", short_name="GSRTC", agency_type="intercity_bus", state="Gujarat", website="https://gsrtc.in"),
            TransportAgency(id="UPSRTC", name="Uttar Pradesh State Road Transport Corporation", short_name="UPSRTC", agency_type="intercity_bus", state="Uttar Pradesh", website="https://upsrtc.up.gov.in"),
            TransportAgency(id="OSRTC", name="Odisha State Road Transport Corporation", short_name="OSRTC", agency_type="intercity_bus", state="Odisha", website="https://osrtc.in"),
            TransportAgency(id="CMRL", name="Chennai Metro Rail Limited", short_name="CMRL", agency_type="metro", state="Tamil Nadu", website="https://chennaimetrorail.org"),
            TransportAgency(id="BMRCL", name="Bangalore Metro Rail Corporation (Namma Metro)", short_name="BMRCL", agency_type="metro", state="Karnataka", website="https://bmrc.co.in"),
            TransportAgency(id="HMRL", name="Hyderabad Metro Rail Limited", short_name="Hyderabad Metro", agency_type="metro", state="Telangana", website="https://hmrl.co.in"),
            TransportAgency(id="DMRC", name="Delhi Metro Rail Corporation", short_name="Delhi Metro", agency_type="metro", state="Delhi", website="https://delhimetrorail.com"),
        ]
        for a in agencies:
            db.merge(a)
        db.commit()

        # 2. Data Sources
        sources = [
            DataSource(id=1, name="Indian Railways Published Timetables 2026", provider="Indian Railways", dataset_type="OFFICIAL_TIMETABLE", coverage_area="India National Railway Network", is_verified=True),
            DataSource(id=2, name="State Road Transport Corporations (SRTC) Schedule Feeds", provider="KSRTC, SETC, TNSTC, APSRTC, TSRTC, Kerala RTC, MSRTC, RSRTC, GSRTC, UPSRTC, OSRTC", dataset_type="SRTC_OFFICIAL", coverage_area="Intercity Bus Corridors", is_verified=True),
            DataSource(id=3, name="Urban Metro Transit Open Data (CMRL, BMRCL, HMRL, DMRC)", provider="Metro Rail Corporations", dataset_type="GTFS_METRO", coverage_area="Metropolitan Rapid Transit", is_verified=True),
        ]
        for s in sources:
            db.merge(s)
        db.commit()

        # 3. Stations & Terminals across India
        station_data = [
            # Chennai
            ("MAS", "Puratchi Thalaivar Dr. M.G. Ramachandran Central Railway Station", "MAS", "Chennai", "Tamil Nadu", 13.0827, 80.2755, "train,metro", "railway", "place_chennai_tn", True),
            ("MS", "Chennai Egmore Railway Station", "MS", "Chennai", "Tamil Nadu", 13.0782, 80.2608, "train,metro", "railway", "place_chennai_tn", True),
            ("TBM", "Tambaram Railway Station", "TBM", "Chennai", "Tamil Nadu", 12.9250, 80.1170, "train", "railway", "place_chennai_tn", True),
            ("CMBT_BUS", "Puratchi Thalaivar Dr. MGR Intercity Bus Terminus (Koyambedu)", "CMBT", "Chennai", "Tamil Nadu", 13.0694, 80.1948, "bus,metro", "bus_terminal", "place_chennai_tn", True),
            ("KCBT_BUS", "Kalaignar Centenary Bus Terminus (Kilambakkam)", "KCBT", "Chennai", "Tamil Nadu", 12.8711, 80.0823, "bus", "bus_terminal", "place_chennai_tn", True),
            ("CMRL_CENTRAL", "Chennai Central Metro Station", "CMRL1", "Chennai", "Tamil Nadu", 13.0820, 80.2745, "metro", "metro", "place_chennai_tn", True),
            ("CMRL_AIRPORT", "Chennai International Airport Metro", "CMRL4", "Chennai", "Tamil Nadu", 12.9815, 80.1636, "metro", "metro", "place_chennai_tn", False),

            # Intermediate Tamil Nadu Corridor
            ("AJJ", "Arakkonam Junction", "AJJ", "Arakkonam", "Tamil Nadu", 13.0836, 79.6687, "train", "railway", "place_arakkonam_tn", False),
            ("KPD", "Katpadi Junction", "KPD", "Vellore", "Tamil Nadu", 12.9723, 79.1352, "train", "railway", "place_vellore_tn", True),
            ("JTJ", "Jolarpettai Junction", "JTJ", "Jolarpettai", "Tamil Nadu", 12.5714, 78.5772, "train", "railway", "place_jolarpettai_tn", True),
            ("BWT", "Bangarapet Junction", "BWT", "Bangarapet", "Karnataka", 12.9972, 78.1994, "train", "railway", "place_bangarapet_ka", False),
            ("SA", "Salem Junction", "SA", "Salem", "Tamil Nadu", 11.6643, 78.1460, "train", "railway", "place_salem_tn", True),
            ("SA_BUS", "Salem New Central Bus Stand", "SA_BUS", "Salem", "Tamil Nadu", 11.6605, 78.1510, "bus", "bus_terminal", "place_salem_tn", True),
            ("ED", "Erode Junction", "ED", "Erode", "Tamil Nadu", 11.3410, 77.7172, "train", "railway", "place_erode_tn", True),
            ("TUP", "Tiruppur Railway Station", "TUP", "Tiruppur", "Tamil Nadu", 11.1085, 77.3411, "train", "railway", "place_tiruppur_tn", False),

            # Madurai & Tiruchirappalli
            ("TPJ", "Tiruchirappalli Junction", "TPJ", "Tiruchirappalli", "Tamil Nadu", 10.7942, 78.6854, "train", "railway", "place_tiruchirappalli_tn", True),
            ("TPJ_BUS", "Tiruchirappalli Central Bus Stand", "TPJ_BUS", "Tiruchirappalli", "Tamil Nadu", 10.7990, 78.6830, "bus", "bus_terminal", "place_tiruchirappalli_tn", True),
            ("DG", "Dindigul Junction", "DG", "Dindigul", "Tamil Nadu", 10.3673, 77.9803, "train", "railway", "place_dindigul_tn", False),
            ("MDU", "Madurai Junction Railway Station", "MDU", "Madurai", "Tamil Nadu", 9.9178, 78.1121, "train", "railway", "place_madurai_tn", True),
            ("MDU_BUS", "Madurai Mattuthavani Integrated Bus Terminal", "MDU_BUS", "Madurai", "Tamil Nadu", 9.9430, 78.1582, "bus", "bus_terminal", "place_madurai_tn", True),

            # Pudukkottai
            ("PDKT", "Pudukkottai Railway Station", "PDKT", "Pudukkottai", "Tamil Nadu", 10.3804, 78.8214, "train", "railway", "place_pudukkottai_tn", True),
            ("PDKT_BUS", "Pudukkottai New Bus Stand", "PDKT_BUS", "Pudukkottai", "Tamil Nadu", 10.3750, 78.8250, "bus", "bus_terminal", "place_pudukkottai_tn", True),

            # Coimbatore
            ("CBE", "Coimbatore Junction Railway Station", "CBE", "Coimbatore", "Tamil Nadu", 11.0016, 76.9628, "train", "railway", "place_coimbatore_tn", True),
            ("CBE_BUS", "Coimbatore Gandhipuram Central Bus Stand", "CBE_BUS", "Coimbatore", "Tamil Nadu", 11.0183, 76.9686, "bus", "bus_terminal", "place_coimbatore_tn", True),

            # Bengaluru Hubs
            ("SBC", "KSR Bengaluru City Junction", "SBC", "Bengaluru", "Karnataka", 12.9781, 77.5695, "train,metro", "railway", "place_bengaluru_ka", True),
            ("BNC", "Bengaluru Cantt Railway Station", "BNC", "Bengaluru", "Karnataka", 12.9934, 77.5983, "train", "railway", "place_bengaluru_ka", False),
            ("KJM", "Krishnarajapuram Railway Station", "KJM", "Bengaluru", "Karnataka", 13.0012, 77.6789, "train", "railway", "place_bengaluru_ka", False),
            ("YPR", "Yesvantpur Junction", "YPR", "Bengaluru", "Karnataka", 13.0238, 77.5503, "train,metro", "railway", "place_bengaluru_ka", True),
            ("KBS_BUS", "Kempegowda Bus Station (Majestic KBS)", "KBS", "Bengaluru", "Karnataka", 12.9768, 77.5713, "bus,metro", "bus_terminal", "place_bengaluru_ka", True),
            ("SHANTINAGAR_BUS", "Shantinagar KSRTC Bus Stand", "SNTNGR", "Bengaluru", "Karnataka", 12.9542, 77.5925, "bus", "bus_terminal", "place_bengaluru_ka", True),
            ("BMRCL_MAJESTIC", "Nadaprabhu Kempegowda Majestic Metro Interchange", "BMRCL_MJS", "Bengaluru", "Karnataka", 12.9757, 77.5728, "metro", "metro", "place_bengaluru_ka", True),

            # Mysuru, Mandya
            ("MYS", "Mysuru Junction Railway Station", "MYS", "Mysuru", "Karnataka", 12.3164, 76.6433, "train", "railway", "place_mysuru_ka", True),
            ("MYS_BUS", "Mysuru KSRTC Suburban Central Bus Stand", "MYS_BUS", "Mysuru", "Karnataka", 12.3106, 76.6558, "bus", "bus_terminal", "place_mysuru_ka", True),
            ("MANDYA", "Mandya Railway Station", "MYA", "Mandya", "Karnataka", 12.5244, 76.8958, "train", "railway", "place_mandya_ka", False),

            # Hubballi
            ("UBL", "SSS Hubballi Junction", "UBL", "Hubballi", "Karnataka", 15.3524, 75.1480, "train", "railway", "place_hubballi_ka", True),
            ("UBL_BUS", "Hubballi Hosur Central Bus Stand", "UBL_BUS", "Hubballi", "Karnataka", 15.3610, 75.1320, "bus", "bus_terminal", "place_hubballi_ka", True),

            # Mangaluru
            ("MAQ", "Mangaluru Central Railway Station", "MAQ", "Mangaluru", "Karnataka", 12.8628, 74.8398, "train", "railway", "place_mangaluru_ka", True),
            ("MAQ_BUS", "Mangaluru KSRTC Central Bus Stand", "MAQ_BUS", "Mangaluru", "Karnataka", 12.8715, 74.8430, "bus", "bus_terminal", "place_mangaluru_ka", True),

            # Hyderabad & Telangana
            ("SC", "Secunderabad Junction Railway Station", "SC", "Hyderabad", "Telangana", 17.4334, 78.5045, "train,metro", "railway", "place_hyderabad_ts", True),
            ("HYB", "Hyderabad Deccan (Nampally) Railway Station", "HYB", "Hyderabad", "Telangana", 17.3920, 78.4697, "train,metro", "railway", "place_hyderabad_ts", True),
            ("KCG", "Kacheguda Railway Station", "KCG", "Hyderabad", "Telangana", 17.3888, 78.4989, "train", "railway", "place_hyderabad_ts", True),
            ("MGBS_BUS", "Mahatma Gandhi Bus Station (MGBS Imlibun)", "MGBS", "Hyderabad", "Telangana", 17.3789, 78.4815, "bus,metro", "bus_terminal", "place_hyderabad_ts", True),
            ("JBS_BUS", "Jubilee Bus Station (JBS Secunderabad)", "JBS", "Hyderabad", "Telangana", 17.4520, 78.4980, "bus,metro", "bus_terminal", "place_hyderabad_ts", True),
            ("HYD_METRO_MGBS", "MGBS Hyderabad Metro Station", "HMR_MGBS", "Hyderabad", "Telangana", 17.3792, 78.4820, "metro", "metro", "place_hyderabad_ts", True),
            ("HYD_METRO_AMEERPET", "Ameerpet Metro Interchange", "HMR_AMR", "Hyderabad", "Telangana", 17.4375, 78.4482, "metro", "metro", "place_hyderabad_ts", True),

            # Warangal & Karimnagar
            ("WL", "Warangal Railway Station", "WL", "Warangal", "Telangana", 17.9784, 79.5941, "train", "railway", "place_warangal_ts", True),
            ("KZJ", "Kazipet Junction", "KZJ", "Warangal", "Telangana", 17.9750, 79.5160, "train", "railway", "place_warangal_ts", True),
            ("WL_BUS", "Hanamkonda Central Bus Stand", "WL_BUS", "Warangal", "Telangana", 18.0060, 79.5620, "bus", "bus_terminal", "place_warangal_ts", True),
            ("KRMR", "Karimnagar Railway Station", "KRMR", "Karimnagar", "Telangana", 18.4230, 79.1415, "train", "railway", "place_karimnagar_ts", True),
            ("KRMR_BUS", "Karimnagar Central TSRTC Bus Stand", "KRMR_BUS", "Karimnagar", "Telangana", 18.4320, 79.1310, "bus", "bus_terminal", "place_karimnagar_ts", True),

            # Andhra Pradesh: Vijayawada, Visakhapatnam, Tirupati
            ("BZA", "Vijayawada Junction Railway Station", "BZA", "Vijayawada", "Andhra Pradesh", 16.5186, 80.6200, "train", "railway", "place_vijayawada_ap", True),
            ("PNBS_BUS", "Pandit Nehru Bus Station (Vijayawada PNBS)", "PNBS", "Vijayawada", "Andhra Pradesh", 16.5097, 80.6133, "bus", "bus_terminal", "place_vijayawada_ap", True),
            ("KMT", "Khammam Railway Station", "KMT", "Khammam", "Telangana", 17.2473, 80.1514, "train", "railway", "place_khammam_ts", False),
            ("VSKP", "Visakhapatnam Junction", "VSKP", "Visakhapatnam", "Andhra Pradesh", 17.7215, 83.2872, "train", "railway", "place_visakhapatnam_ap", True),
            ("VSKP_BUS", "Dwaraka RTC Bus Complex (RTC Complex)", "VSKP_BUS", "Visakhapatnam", "Andhra Pradesh", 17.7265, 83.3030, "bus", "bus_terminal", "place_visakhapatnam_ap", True),
            ("TPTY", "Tirupati Main Railway Station", "TPTY", "Tirupati", "Andhra Pradesh", 13.6288, 79.4192, "train", "railway", "place_tirupati_ap", True),
            ("RU", "Renigunta Junction Railway Station", "RU", "Tirupati", "Andhra Pradesh", 13.6492, 79.5160, "train", "railway", "place_tirupati_ap", True),
            ("TPTY_BUS", "Tirupati Central Bus Station", "TPTY_BUS", "Tirupati", "Andhra Pradesh", 13.6260, 79.4230, "bus", "bus_terminal", "place_tirupati_ap", True),

            # Kerala: Kochi, Thiruvananthapuram, Kozhikode
            ("ERS", "Ernakulam Junction (South) Railway Station", "ERS", "Kochi", "Kerala", 9.9678, 76.2890, "train", "railway", "place_kochi_kl", True),
            ("ERS_BUS", "Ernakulam KSRTC Central Bus Stand", "ERS_BUS", "Kochi", "Kerala", 9.9720, 76.2840, "bus", "bus_terminal", "place_kochi_kl", True),
            ("TVC", "Thiruvananthapuram Central Railway Station", "TVC", "Thiruvananthapuram", "Kerala", 8.4875, 76.9525, "train", "railway", "place_thiruvananthapuram_kl", True),
            ("TVC_BUS", "Thampanoor Central Bus Station", "TVC_BUS", "Thiruvananthapuram", "Kerala", 8.4890, 76.9535, "bus", "bus_terminal", "place_thiruvananthapuram_kl", True),
            ("CLT", "Kozhikode Railway Station", "CLT", "Kozhikode", "Kerala", 11.2435, 75.7804, "train", "railway", "place_kozhikode_kl", True),
            ("CLT_BUS", "Kozhikode KSRTC Terminal", "CLT_BUS", "Kozhikode", "Kerala", 11.2505, 75.7850, "bus", "bus_terminal", "place_kozhikode_kl", True),

            # Maharashtra: Mumbai & Pune
            ("CSMT", "Chhatrapati Shivaji Maharaj Terminus", "CSMT", "Mumbai", "Maharashtra", 18.9402, 72.8356, "train", "railway", "place_mumbai_mh", True),
            ("DR", "Dadar Central Railway Station", "DR", "Mumbai", "Maharashtra", 19.0182, 72.8431, "train", "railway", "place_mumbai_mh", True),
            ("TNA", "Thane Railway Station", "TNA", "Thane", "Maharashtra", 19.1860, 72.9759, "train", "railway", "place_thane_mh", False),
            ("LNL", "Lonavala Railway Station", "LNL", "Lonavala", "Maharashtra", 18.7557, 73.4091, "train", "railway", "place_lonavala_mh", False),
            ("DADAR_ASIAD_BUS", "Dadar Asiad MSRTC Stand", "DADAR_BUS", "Mumbai", "Maharashtra", 19.0191, 72.8443, "bus", "bus_terminal", "place_mumbai_mh", True),
            ("PUNE", "Pune Junction Railway Station", "PUNE", "Pune", "Maharashtra", 18.5284, 73.8744, "train", "railway", "place_pune_mh", True),
            ("SHIVAJINAGAR_BUS", "Shivajinagar MSRTC Stand", "SHIVAJI_BUS", "Pune", "Maharashtra", 18.5312, 73.8505, "bus", "bus_terminal", "place_pune_mh", True),

            # Delhi NCR & Rajasthan: Delhi & Jaipur
            ("NDLS", "New Delhi Railway Station", "NDLS", "Delhi", "Delhi", 28.6431, 77.2197, "train,metro", "railway", "place_delhi_dl", True),
            ("DLI", "Old Delhi Junction", "DLI", "Delhi", "Delhi", 28.6619, 77.2309, "train,metro", "railway", "place_delhi_dl", True),
            ("DEC", "Delhi Cantt Railway Station", "DEC", "Delhi", "Delhi", 28.5912, 77.1215, "train", "railway", "place_delhi_dl", False),
            ("KASHMERE_GATE_BUS", "Maharana Pratap ISBT Kashmere Gate", "ISBT_KG", "Delhi", "Delhi", 28.6672, 77.2325, "bus,metro", "bus_terminal", "place_delhi_dl", True),
            ("GGN", "Gurugram Railway Station", "GGN", "Gurugram", "Haryana", 28.4682, 77.0192, "train", "railway", "place_gurgaon_hr", False),
            ("RE", "Rewari Junction", "RE", "Rewari", "Haryana", 28.1990, 76.6180, "train", "railway", "place_rewari_hr", False),
            ("AWR", "Alwar Junction", "AWR", "Alwar", "Rajasthan", 27.5645, 76.6253, "train", "railway", "place_alwar_rj", False),
            ("JP", "Jaipur Junction Railway Station", "JP", "Jaipur", "Rajasthan", 26.9196, 75.7878, "train", "railway", "place_jaipur_rj", True),
            ("SINDHI_CAMP_BUS", "Sindhi Camp Central Bus Stand", "SINDHI_BUS", "Jaipur", "Rajasthan", 26.9242, 75.8016, "bus", "bus_terminal", "place_jaipur_rj", True),

            # West Bengal & Odisha: Kolkata & Bhubaneswar
            ("HWH", "Howrah Junction Railway Station", "HWH", "Kolkata", "West Bengal", 22.5840, 88.3426, "train", "railway", "place_kolkata_wb", True),
            ("BABUGHAT_BUS", "Babughat Intercity Bus Terminal", "BABUGHAT_BUS", "Kolkata", "West Bengal", 22.5665, 88.3440, "bus", "bus_terminal", "place_kolkata_wb", True),
            ("BBS", "Bhubaneswar Railway Station", "BBS", "Bhubaneswar", "Odisha", 20.2648, 85.8400, "train", "railway", "place_bhubaneswar_od", True),
            ("BARAMUNDA_BUS", "Baramunda ISBT Central Bus Stand", "BARAMUNDA_BUS", "Bhubaneswar", "Odisha", 20.2785, 85.7950, "bus", "bus_terminal", "place_bhubaneswar_od", True),

            # Gujarat: Ahmedabad & Surat
            ("ADI", "Ahmedabad Junction Railway Station", "ADI", "Ahmedabad", "Gujarat", 23.0225, 72.6015, "train", "railway", "place_ahmedabad_gj", True),
            ("GEETA_MANDIR_BUS", "Geeta Mandir Central Bus Stand", "GEETA_BUS", "Ahmedabad", "Gujarat", 23.0120, 72.5890, "bus", "bus_terminal", "place_ahmedabad_gj", True),
            ("ST", "Surat Railway Station", "ST", "Surat", "Gujarat", 21.2045, 72.8406, "train", "railway", "place_surat_gj", True),
            ("SURAT_BUS", "Surat Central GSRTC Bus Station", "SURAT_BUS", "Surat", "Gujarat", 21.2060, 72.8430, "bus", "bus_terminal", "place_surat_gj", True),

            # Uttar Pradesh: Lucknow & Varanasi
            ("LKO", "Lucknow Charbagh Railway Station", "LKO", "Lucknow", "Uttar Pradesh", 26.8322, 80.9190, "train", "railway", "place_lucknow_up", True),
            ("KAISARBAGH_BUS", "Kaisarbagh Bus Stand", "KAISAR_BUS", "Lucknow", "Uttar Pradesh", 26.8520, 80.9320, "bus", "bus_terminal", "place_lucknow_up", True),
            ("BSB", "Varanasi Junction (Cantt) Railway Station", "BSB", "Varanasi", "Uttar Pradesh", 25.3280, 82.9860, "train", "railway", "place_varanasi_up", True),
            ("CANTT_BUS_BSB", "Varanasi Cantt UPSRTC Bus Station", "CANTT_BUS", "Varanasi", "Uttar Pradesh", 25.3260, 82.9890, "bus", "bus_terminal", "place_varanasi_up", True),
        ]

        for sid, name, code, city, state, lat, lon, ttypes, st_type, pid, hub in station_data:
            st = Station(
                id=sid,
                name=name,
                code=code,
                city=city,
                state=state,
                latitude=lat,
                longitude=lon,
                transport_types=ttypes,
                station_type=st_type,
                place_id=pid,
                is_hub=hub,
                wheelchair_accessible=True
            )
            db.merge(st)
        db.commit()

        # 4. Routes
        routes_data = [
            # Trains
            ("IR_20605", "20605", "Chennai Egmore - Madurai Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_20606", "20606", "Madurai - Chennai Egmore Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_12637", "12637", "Pandian Superfast Express (Chennai - Madurai)", 1, "Southern Railway", 1),
            ("IR_12638", "12638", "Pandian Superfast Express (Madurai - Chennai)", 1, "Southern Railway", 1),
            ("IR_12635", "12635", "Vaigai Superfast Express (Chennai - Madurai)", 1, "Southern Railway", 1),
            ("IR_12636", "12636", "Vaigai Superfast Express (Madurai - Chennai)", 1, "Southern Railway", 1),
            ("IR_16181", "16181", "Silambu Express (Chennai - Pudukkottai - Sengottai)", 1, "Southern Railway", 1),
            ("IR_16182", "16182", "Silambu Express (Pudukkottai - Chennai)", 1, "Southern Railway", 1),
            ("IR_20643", "20643", "Chennai Central - Coimbatore Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_20644", "20644", "Coimbatore - Chennai Central Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_12673", "12673", "Cheran Superfast Express (Chennai - Coimbatore)", 1, "Southern Railway", 1),
            ("IR_12674", "12674", "Cheran Superfast Express (Coimbatore - Chennai)", 1, "Southern Railway", 1),
            ("IR_20607", "20607", "Chennai - Mysuru Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_20608", "20608", "Mysuru - Chennai Vande Bharat Express", 1, "South Western Railway", 1),
            ("IR_12613", "12613", "Tippu Superfast Express (Bengaluru - Mysuru)", 1, "South Western Railway", 1),
            ("IR_12614", "12614", "Tippu Superfast Express (Mysuru - Bengaluru)", 1, "South Western Railway", 1),
            ("IR_20661", "20661", "Bengaluru - Hubballi Vande Bharat Express", 1, "South Western Railway", 1),
            ("IR_20662", "20662", "Hubballi - Bengaluru Vande Bharat Express", 1, "South Western Railway", 1),
            ("IR_12725", "12725", "Siddhaganga Intercity Express (Bengaluru - Hubballi)", 1, "South Western Railway", 1),
            ("IR_16575", "16575", "Gomteshwara Express (Yesvantpur - Mangaluru)", 1, "South Western Railway", 1),
            ("IR_16576", "16576", "Gomteshwara Express (Mangaluru - Yesvantpur)", 1, "South Western Railway", 1),
            ("IR_12713", "12713", "Satavahana Superfast Express (Secunderabad - Vijayawada)", 1, "South Central Railway", 1),
            ("IR_12714", "12714", "Satavahana Superfast Express (Vijayawada - Secunderabad)", 1, "South Central Railway", 1),
            ("IR_12761", "12761", "Tirupati - Karimnagar Superfast Express", 1, "South Central Railway", 1),
            ("IR_12762", "12762", "Karimnagar - Tirupati Superfast Express", 1, "South Central Railway", 1),
            ("IR_20833", "20833", "Visakhapatnam - Secunderabad Vande Bharat Express", 1, "East Coast Railway", 1),
            ("IR_20834", "20834", "Secunderabad - Visakhapatnam Vande Bharat Express", 1, "East Coast Railway", 1),
            ("IR_12717", "12717", "Ratnachal Superfast Express (Vijayawada - Visakhapatnam)", 1, "South Central Railway", 1),
            ("IR_12718", "12718", "Ratnachal Superfast Express (Visakhapatnam - Vijayawada)", 1, "South Central Railway", 1),
            ("IR_16057", "16057", "Sapthagiri Express (Chennai Central - Tirupati)", 1, "Southern Railway", 1),
            ("IR_16058", "16058", "Sapthagiri Express (Tirupati - Chennai Central)", 1, "Southern Railway", 1),
            ("IR_20633", "20633", "Kasaragod - Thiruvananthapuram Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_20634", "20634", "Thiruvananthapuram - Kasaragod Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_12075", "12075", "Kozhikode - Thiruvananthapuram Jan Shatabdi Express", 1, "Southern Railway", 1),
            ("IR_12076", "12076", "Thiruvananthapuram - Kozhikode Jan Shatabdi Express", 1, "Southern Railway", 1),
            ("IR_12123", "12123", "Deccan Queen Superfast Express (Mumbai - Pune)", 1, "Central Railway", 1),
            ("IR_12124", "12124", "Deccan Queen Superfast Express (Pune - Mumbai)", 1, "Central Railway", 1),
            ("IR_20977", "20977", "Ajmer - Delhi Cantt Vande Bharat Express", 1, "North Western Railway", 1),
            ("IR_20978", "20978", "Delhi Cantt - Ajmer Vande Bharat Express", 1, "North Western Railway", 1),
            ("IR_22895", "22895", "Howrah - Puri Vande Bharat Express", 1, "South Eastern Railway", 1),
            ("IR_22896", "22896", "Puri - Howrah Vande Bharat Express", 1, "East Coast Railway", 1),
            ("IR_20901", "20901", "Mumbai Central - Gandhinagar Vande Bharat Express", 1, "Western Railway", 1),
            ("IR_20902", "20902", "Gandhinagar - Mumbai Central Vande Bharat Express", 1, "Western Railway", 1),
            ("IR_22545", "22545", "Lucknow - Varanasi Vande Bharat Express", 1, "Northern Railway", 1),
            ("IR_22546", "22546", "Varanasi - Lucknow Vande Bharat Express", 1, "Northern Railway", 1),
            ("IR_12797", "12797", "Venkatadri Superfast Express (Kacheguda - Tirupati)", 1, "South Central Railway", 1),
            ("IR_12798", "12798", "Venkatadri Superfast Express (Tirupati - Kacheguda)", 1, "South Central Railway", 1),
            ("IR_17406", "17406", "Krishna Express (Secunderabad - Tirupati)", 1, "South Central Railway", 1),
            ("IR_17405", "17405", "Krishna Express (Tirupati - Secunderabad)", 1, "South Central Railway", 1),
            ("IR_20671", "20671", "Madurai - Bengaluru Vande Bharat Express", 1, "Southern Railway", 1),
            ("IR_20672", "20672", "Bengaluru - Madurai Vande Bharat Express", 1, "South Western Railway", 1),
            ("IR_17229", "17229", "Sabari Express (Kochi - Coimbatore - Hyderabad)", 1, "Southern Railway", 1),
            ("IR_17230", "17230", "Sabari Express (Hyderabad - Coimbatore - Kochi)", 1, "South Central Railway", 1),
            ("IR_11020", "11020", "Konark Express (Bhubaneswar - Vijayawada - Secunderabad - Pune - Mumbai)", 1, "Central Railway", 1),
            ("IR_11019", "11019", "Konark Express (Mumbai - Pune - Secunderabad - Vijayawada - Bhubaneswar)", 1, "Central Railway", 1),
            ("IR_12625", "12625", "Kerala Express (New Delhi - Vijayawada - Coimbatore - Kochi - Trivandrum)", 1, "Southern Railway", 1),
            ("IR_12626", "12626", "Kerala Express (Trivandrum - Kochi - Coimbatore - Vijayawada - New Delhi)", 1, "Northern Railway", 1),
            ("IR_20979", "20979", "Jaipur - Ahmedabad Vande Bharat Express", 1, "North Western Railway", 1),
            ("IR_20980", "20980", "Ahmedabad - Jaipur Vande Bharat Express", 1, "Western Railway", 1),
            ("IR_11036", "11036", "Sharavati Express (Mysuru - Bengaluru - Hubballi - Pune - Mumbai)", 1, "Central Railway", 1),
            ("IR_11035", "11035", "Sharavati Express (Mumbai - Pune - Hubballi - Bengaluru - Mysuru)", 1, "Central Railway", 1),

            # Buses
            ("BUS_SETC_MDU", "SETC AC", "SETC AC Sleeper (Chennai - Madurai)", 2, "SETC Tamil Nadu", 2),
            ("BUS_SETC_CBE", "SETC Ultra", "SETC Ultra Deluxe (Chennai - Coimbatore)", 2, "SETC Tamil Nadu", 2),
            ("BUS_TNSTC_TPJ", "TNSTC Deluxe", "TNSTC Deluxe Express (Madurai - Trichy)", 2, "TNSTC", 2),
            ("BUS_TNSTC_SA", "TNSTC Classic", "TNSTC Classic Express (Coimbatore - Salem)", 2, "TNSTC", 2),
            ("BUS_SETC_PDKT", "SETC Deluxe", "SETC Deluxe (Chennai - Pudukkottai)", 2, "SETC Tamil Nadu", 2),
            ("BUS_KSRTC_MYS", "KSRTC Airavat", "KSRTC Airavat Club Class (Bengaluru - Mysuru)", 2, "KSRTC Karnataka", 2),
            ("BUS_KSRTC_UBL", "KSRTC Diamond", "KSRTC Diamond Class Multi-Axle (Bengaluru - Hubballi)", 2, "KSRTC Karnataka", 2),
            ("BUS_KSRTC_MAQ", "KSRTC Club", "KSRTC Airavat Club Class (Bengaluru - Mangaluru)", 2, "KSRTC Karnataka", 2),
            ("BUS_TSRTC_WL", "TSRTC Garuda", "TSRTC Garuda Plus (Hyderabad - Warangal)", 2, "TSRTC Telangana", 2),
            ("BUS_TSRTC_KRMR", "TSRTC Rajdhani", "TSRTC Rajdhani Non-Stop (Hyderabad - Karimnagar)", 2, "TSRTC Telangana", 2),
            ("BUS_APSRTC_BZA", "APSRTC Amaravati", "APSRTC Amaravati Multi-Axle (Hyderabad - Vijayawada)", 2, "APSRTC", 2),
            ("BUS_APSRTC_VSKP", "APSRTC Garuda", "APSRTC Garuda Plus (Vijayawada - Visakhapatnam)", 2, "APSRTC", 2),
            ("BUS_APSRTC_TPTY", "APSRTC Express", "APSRTC Super Luxury (Chennai - Tirupati)", 2, "APSRTC", 2),
            ("BUS_TSRTC_TPTY", "TSRTC Garuda", "TSRTC Garuda Plus AC Sleeper (Hyderabad - Tirupati)", 2, "TSRTC Telangana", 2),
            ("BUS_KSRTC_MDU", "KSRTC Airavat", "KSRTC Airavat Club Class (Bengaluru - Madurai)", 2, "KSRTC Karnataka", 2),
            ("BUS_KSRTC_HYD", "KSRTC FlyBus", "KSRTC FlyBus Multi-Axle (Bengaluru - Hyderabad)", 2, "KSRTC Karnataka", 2),
            ("BUS_RSRTC_ADI", "RSRTC Goldline", "RSRTC Goldline AC Express (Jaipur - Ahmedabad)", 2, "RSRTC Rajasthan", 2),
            ("BUS_MSRTC_UBL", "MSRTC Shivneri", "MSRTC Shivneri AC Sleeper (Pune - Hubballi - Bengaluru)", 2, "MSRTC Maharashtra", 2),
            ("BUS_KERALA_TVC", "Kerala RTC SWIFT", "Kerala RTC SWIFT Super Air Deluxe (Kochi - Thiruvananthapuram)", 2, "Kerala RTC", 2),
            ("BUS_KERALA_CLT", "Kerala RTC AC", "Kerala RTC SWIFT AC Seater (Kochi - Kozhikode)", 2, "Kerala RTC", 2),
            ("BUS_MSRTC_PUNE", "MSRTC Shivneri", "MSRTC Shivneri AC Volvo (Mumbai - Pune)", 2, "MSRTC Maharashtra", 2),
            ("BUS_RSRTC_JP", "RSRTC Goldline", "RSRTC Goldline AC Super Deluxe (Delhi - Jaipur)", 2, "RSRTC Rajasthan", 2),
            ("BUS_OSRTC_BBS", "OSRTC Volvo", "OSRTC Volvo AC Sleeper (Kolkata - Bhubaneswar)", 2, "OSRTC Odisha", 2),
            ("BUS_GSRTC_ST", "GSRTC Gurjanagari", "GSRTC Gurjanagari AC Express (Ahmedabad - Surat)", 2, "GSRTC Gujarat", 2),
            ("BUS_UPSRTC_BSB", "UPSRTC Janrath", "UPSRTC Janrath AC Express (Lucknow - Varanasi)", 2, "UPSRTC Uttar Pradesh", 2),
            ("BUS_TSRTC_CBE_HYD", "TSRTC Garuda", "TSRTC Garuda Plus AC Sleeper (Coimbatore - Hyderabad)", 2, "TSRTC Telangana", 2),
            ("BUS_APSRTC_BZA_MUM", "APSRTC Amaravati", "APSRTC Amaravati Multi-Axle Sleeper (Vijayawada - Mumbai)", 2, "APSRTC", 2),
            ("BUS_MSRTC_MYS_PUNE", "MSRTC Shivneri", "MSRTC Shivneri AC Sleeper (Mysuru - Pune)", 2, "MSRTC Maharashtra", 2),

            # Metros
            ("METRO_CMRL_BLUE", "CMRL Blue", "Chennai Metro Blue Line (Central - Airport)", 3, "Chennai Metro Rail Limited", 3),
            ("METRO_BMRCL_PURPLE", "BMRCL Purple", "Namma Metro Purple Line (Majestic - Whitefield)", 3, "Bangalore Metro Rail Corporation", 3),
            ("METRO_HMR_RED", "HMR Red", "Hyderabad Metro Red Line (MGBS - Ameerpet)", 3, "Hyderabad Metro Rail", 3),
        ]

        for rid, sname, lname, mid, op, ds_id in routes_data:
            rt = Route(
                id=rid,
                route_short_name=sname,
                route_long_name=lname,
                transport_mode_id=mid,
                operator_name=op,
                data_source_id=ds_id,
                is_active=True
            )
            db.merge(rt)
        db.commit()

        # 5. Trips & Stop Times for All Corridors
        trips_and_stops = [
            # 1. Chennai <-> Madurai
            {"trip_id": "TRIP_VB_20605", "route_id": "IR_20605", "headsign": "Madurai Junction", "dep": "05:45", "arr": "12:15", "stops": [("MS", 1, "05:45", "05:45", 0.0), ("TPJ", 2, "09:40", "09:45", 337.0), ("DG", 3, "10:58", "11:00", 431.0), ("MDU", 4, "12:15", "12:15", 493.0)]},
            {"trip_id": "TRIP_VB_20606", "route_id": "IR_20606", "headsign": "Chennai Egmore", "dep": "14:40", "arr": "21:10", "stops": [("MDU", 1, "14:40", "14:40", 0.0), ("DG", 2, "15:43", "15:45", 62.0), ("TPJ", 3, "16:55", "17:00", 156.0), ("MS", 4, "21:10", "21:10", 493.0)]},
            {"trip_id": "TRIP_PANDIAN_12637", "route_id": "IR_12637", "headsign": "Madurai Junction", "dep": "21:40", "arr": "05:35", "stops": [("MS", 1, "21:40", "21:40", 0.0), ("TPJ", 2, "02:25", "02:30", 337.0), ("DG", 3, "03:48", "03:50", 431.0), ("MDU", 4, "05:35", "05:35", 493.0)]},
            {"trip_id": "TRIP_PANDIAN_12638", "route_id": "IR_12638", "headsign": "Chennai Egmore", "dep": "21:35", "arr": "05:15", "stops": [("MDU", 1, "21:35", "21:35", 0.0), ("DG", 2, "22:33", "22:35", 62.0), ("TPJ", 3, "23:45", "23:50", 156.0), ("MS", 4, "05:15", "05:15", 493.0)]},
            {"trip_id": "TRIP_SETC_MDU_01", "route_id": "BUS_SETC_MDU", "headsign": "Madurai Mattuthavani", "dep": "07:30", "arr": "15:45", "stops": [("CMBT_BUS", 1, "07:30", "07:30", 0.0), ("MDU_BUS", 2, "15:45", "15:45", 465.0)]},
            {"trip_id": "TRIP_SETC_MDU_RET", "route_id": "BUS_SETC_MDU", "headsign": "Chennai CMBT", "dep": "08:00", "arr": "16:15", "stops": [("MDU_BUS", 1, "08:00", "08:00", 0.0), ("CMBT_BUS", 2, "16:15", "16:15", 465.0)]},

            # 2. Madurai <-> Tiruchirappalli (Trichy)
            {"trip_id": "TRIP_TNSTC_TPJ_MORN", "route_id": "BUS_TNSTC_TPJ", "headsign": "Trichy Central Bus Stand", "dep": "06:30", "arr": "09:00", "stops": [("MDU_BUS", 1, "06:30", "06:30", 0.0), ("TPJ_BUS", 2, "09:00", "09:00", 135.0)]},
            {"trip_id": "TRIP_TNSTC_TPJ_RET", "route_id": "BUS_TNSTC_TPJ", "headsign": "Madurai Mattuthavani", "dep": "10:30", "arr": "13:00", "stops": [("TPJ_BUS", 1, "10:30", "10:30", 0.0), ("MDU_BUS", 2, "13:00", "13:00", 135.0)]},

            # 3. Chennai <-> Coimbatore
            {"trip_id": "TRIP_VB_20643", "route_id": "IR_20643", "headsign": "Coimbatore Junction", "dep": "06:10", "arr": "11:50", "stops": [("MAS", 1, "06:10", "06:10", 0.0), ("SA", 2, "09:48", "09:50", 335.0), ("ED", 3, "10:38", "10:40", 396.0), ("TUP", 4, "11:13", "11:15", 446.0), ("CBE", 5, "11:50", "11:50", 497.0)]},
            {"trip_id": "TRIP_VB_20644", "route_id": "IR_20644", "headsign": "Chennai Central", "dep": "15:05", "arr": "20:45", "stops": [("CBE", 1, "15:05", "15:05", 0.0), ("TUP", 2, "15:38", "15:40", 51.0), ("ED", 3, "16:15", "16:20", 101.0), ("SA", 4, "17:08", "17:10", 162.0), ("MAS", 5, "20:45", "20:45", 497.0)]},
            {"trip_id": "TRIP_CHERAN_12673", "route_id": "IR_12673", "headsign": "Coimbatore Junction", "dep": "22:00", "arr": "06:00", "stops": [("MAS", 1, "22:00", "22:00", 0.0), ("SA", 2, "02:47", "02:50", 335.0), ("ED", 3, "03:50", "03:55", 396.0), ("TUP", 4, "04:43", "04:45", 446.0), ("CBE", 5, "06:00", "06:00", 497.0)]},
            {"trip_id": "TRIP_CHERAN_12674", "route_id": "IR_12674", "headsign": "Chennai Central", "dep": "22:50", "arr": "07:00", "stops": [("CBE", 1, "22:50", "22:50", 0.0), ("TUP", 2, "23:33", "23:35", 51.0), ("ED", 3, "00:25", "00:30", 101.0), ("SA", 4, "01:22", "01:25", 162.0), ("MAS", 5, "07:00", "07:00", 497.0)]},
            {"trip_id": "TRIP_SETC_CBE_01", "route_id": "BUS_SETC_CBE", "headsign": "Coimbatore Gandhipuram", "dep": "07:00", "arr": "16:30", "stops": [("CMBT_BUS", 1, "07:00", "07:00", 0.0), ("CBE_BUS", 2, "16:30", "16:30", 505.0)]},
            {"trip_id": "TRIP_SETC_CBE_RET", "route_id": "BUS_SETC_CBE", "headsign": "Chennai CMBT", "dep": "08:30", "arr": "18:00", "stops": [("CBE_BUS", 1, "08:30", "08:30", 0.0), ("CMBT_BUS", 2, "18:00", "18:00", 505.0)]},

            # 4. Coimbatore <-> Salem
            {"trip_id": "TRIP_TNSTC_SA_MORN", "route_id": "BUS_TNSTC_SA", "headsign": "Salem Central Bus Stand", "dep": "07:15", "arr": "10:45", "stops": [("CBE_BUS", 1, "07:15", "07:15", 0.0), ("SA_BUS", 2, "10:45", "10:45", 165.0)]},
            {"trip_id": "TRIP_TNSTC_SA_RET", "route_id": "BUS_TNSTC_SA", "headsign": "Coimbatore Gandhipuram", "dep": "11:30", "arr": "15:00", "stops": [("SA_BUS", 1, "11:30", "11:30", 0.0), ("CBE_BUS", 2, "15:00", "15:00", 165.0)]},

            # 5. Chennai <-> Pudukkottai
            {"trip_id": "TRIP_SILAMBU_16181", "route_id": "IR_16181", "headsign": "Pudukkottai / Sengottai", "dep": "20:25", "arr": "03:43", "stops": [("MS", 1, "20:25", "20:25", 0.0), ("TPJ", 2, "02:50", "02:55", 337.0), ("PDKT", 3, "03:43", "03:45", 389.0)]},
            {"trip_id": "TRIP_SILAMBU_16182", "route_id": "IR_16182", "headsign": "Chennai Egmore", "dep": "22:58", "arr": "05:45", "stops": [("PDKT", 1, "22:58", "23:00", 0.0), ("TPJ", 2, "23:55", "00:05", 52.0), ("MS", 3, "05:45", "05:45", 389.0)]},
            {"trip_id": "TRIP_PALLAVAN_PDKT", "route_id": "IR_16181", "headsign": "Karaikkudi via Pudukkottai", "dep": "15:45", "arr": "21:40", "stops": [("MS", 1, "15:45", "15:45", 0.0), ("TPJ", 2, "20:40", "20:45", 337.0), ("PDKT", 3, "21:40", "21:40", 389.0)]},
            {"trip_id": "TRIP_PALLAVAN_RET", "route_id": "IR_16182", "headsign": "Chennai Egmore", "dep": "06:00", "arr": "12:15", "stops": [("PDKT", 1, "06:00", "06:00", 0.0), ("TPJ", 2, "06:50", "06:55", 52.0), ("MS", 3, "12:15", "12:15", 389.0)]},
            {"trip_id": "TRIP_SETC_PDKT_01", "route_id": "BUS_SETC_PDKT", "headsign": "Pudukkottai New Bus Stand", "dep": "08:15", "arr": "14:45", "stops": [("KCBT_BUS", 1, "08:15", "08:15", 0.0), ("PDKT_BUS", 2, "14:45", "14:45", 370.0)]},
            {"trip_id": "TRIP_SETC_PDKT_RET", "route_id": "BUS_SETC_PDKT", "headsign": "Chennai Kilambakkam KCBT", "dep": "10:00", "arr": "16:30", "stops": [("PDKT_BUS", 1, "10:00", "10:00", 0.0), ("KCBT_BUS", 2, "16:30", "16:30", 370.0)]},
            {"trip_id": "TRIP_SETC_PDKT_CMBT", "route_id": "BUS_SETC_PDKT", "headsign": "Pudukkottai New Bus Stand via CMBT", "dep": "07:30", "arr": "14:30", "stops": [("CMBT_BUS", 1, "07:30", "07:30", 0.0), ("KCBT_BUS", 2, "08:20", "08:25", 28.0), ("PDKT_BUS", 3, "14:30", "14:30", 380.0)]},

            # 6. Chennai <-> Bengaluru
            {"trip_id": "TRIP_VB_20607", "route_id": "IR_20607", "headsign": "Mysuru Junction via KSR Bengaluru", "dep": "05:50", "arr": "10:10", "stops": [("MAS", 1, "05:50", "05:50", 0.0), ("KPD", 2, "07:13", "07:15", 130.0), ("SBC", 3, "10:10", "10:15", 359.0), ("MANDYA", 4, "11:18", "11:20", 452.0), ("MYS", 5, "12:20", "12:20", 497.0)]},
            {"trip_id": "TRIP_VB_20608", "route_id": "IR_20608", "headsign": "Chennai Central via KSR Bengaluru", "dep": "13:05", "arr": "19:20", "stops": [("MYS", 1, "13:05", "13:05", 0.0), ("MANDYA", 2, "13:48", "13:50", 45.0), ("SBC", 3, "14:45", "14:50", 138.0), ("KPD", 4, "17:33", "17:35", 367.0), ("MAS", 5, "19:20", "19:20", 497.0)]},

            # 7. Bengaluru <-> Mysuru
            {"trip_id": "TRIP_TIPPU_12613", "route_id": "IR_12613", "headsign": "Mysuru Junction", "dep": "15:00", "arr": "17:30", "stops": [("SBC", 1, "15:00", "15:00", 0.0), ("MANDYA", 2, "16:18", "16:20", 93.0), ("MYS", 3, "17:30", "17:30", 139.0)]},
            {"trip_id": "TRIP_TIPPU_12614", "route_id": "IR_12614", "headsign": "KSR Bengaluru", "dep": "11:15", "arr": "13:45", "stops": [("MYS", 1, "11:15", "11:15", 0.0), ("MANDYA", 2, "12:08", "12:10", 46.0), ("SBC", 3, "13:45", "13:45", 139.0)]},
            {"trip_id": "TRIP_KSRTC_MYS_01", "route_id": "BUS_KSRTC_MYS", "headsign": "Mysuru Suburban Bus Stand", "dep": "07:00", "arr": "09:15", "stops": [("KBS_BUS", 1, "07:00", "07:00", 0.0), ("MYS_BUS", 2, "09:15", "09:15", 145.0)]},
            {"trip_id": "TRIP_KSRTC_MYS_RET", "route_id": "BUS_KSRTC_MYS", "headsign": "Bengaluru Majestic KBS", "dep": "08:30", "arr": "10:45", "stops": [("MYS_BUS", 1, "08:30", "08:30", 0.0), ("KBS_BUS", 2, "10:45", "10:45", 145.0)]},

            # 8. Bengaluru <-> Hubballi
            {"trip_id": "TRIP_VB_20661", "route_id": "IR_20661", "headsign": "SSS Hubballi Junction", "dep": "05:45", "arr": "10:45", "stops": [("SBC", 1, "05:45", "05:45", 0.0), ("YPR", 2, "05:55", "05:57", 6.0), ("UBL", 3, "10:45", "10:45", 469.0)]},
            {"trip_id": "TRIP_VB_20662", "route_id": "IR_20662", "headsign": "KSR Bengaluru", "dep": "15:15", "arr": "20:15", "stops": [("UBL", 1, "15:15", "15:15", 0.0), ("YPR", 2, "20:00", "20:02", 463.0), ("SBC", 3, "20:15", "20:15", 469.0)]},
            {"trip_id": "TRIP_SIDDHAGANGA_12725", "route_id": "IR_12725", "headsign": "SSS Hubballi Junction", "dep": "12:45", "arr": "20:30", "stops": [("SBC", 1, "12:45", "12:45", 0.0), ("YPR", 2, "12:55", "12:57", 6.0), ("UBL", 3, "20:30", "20:30", 469.0)]},
            {"trip_id": "TRIP_KSRTC_UBL_01", "route_id": "BUS_KSRTC_UBL", "headsign": "Hubballi Hosur Bus Stand", "dep": "06:30", "arr": "13:30", "stops": [("KBS_BUS", 1, "06:30", "06:30", 0.0), ("UBL_BUS", 2, "13:30", "13:30", 410.0)]},
            {"trip_id": "TRIP_KSRTC_UBL_RET", "route_id": "BUS_KSRTC_UBL", "headsign": "Bengaluru Majestic KBS", "dep": "14:00", "arr": "21:00", "stops": [("UBL_BUS", 1, "14:00", "14:00", 0.0), ("KBS_BUS", 2, "21:00", "21:00", 410.0)]},

            # 9. Bengaluru <-> Mangaluru
            {"trip_id": "TRIP_GOMTESH_16575", "route_id": "IR_16575", "headsign": "Mangaluru Central", "dep": "07:00", "arr": "16:30", "stops": [("YPR", 1, "07:00", "07:00", 0.0), ("MAQ", 2, "16:30", "16:30", 353.0)]},
            {"trip_id": "TRIP_GOMTESH_16576", "route_id": "IR_16576", "headsign": "Yesvantpur Junction", "dep": "11:30", "arr": "20:45", "stops": [("MAQ", 1, "11:30", "11:30", 0.0), ("YPR", 2, "20:45", "20:45", 353.0)]},
            {"trip_id": "TRIP_KSRTC_MAQ_01", "route_id": "BUS_KSRTC_MAQ", "headsign": "Mangaluru KSRTC Stand", "dep": "07:30", "arr": "15:00", "stops": [("KBS_BUS", 1, "07:30", "07:30", 0.0), ("MAQ_BUS", 2, "15:00", "15:00", 350.0)]},
            {"trip_id": "TRIP_KSRTC_MAQ_RET", "route_id": "BUS_KSRTC_MAQ", "headsign": "Bengaluru Majestic KBS", "dep": "09:00", "arr": "16:30", "stops": [("MAQ_BUS", 1, "09:00", "09:00", 0.0), ("KBS_BUS", 2, "16:30", "16:30", 350.0)]},

            # 10. Hyderabad <-> Warangal
            {"trip_id": "TRIP_SATAVAHANA_12713", "route_id": "IR_12713", "headsign": "Vijayawada via Warangal", "dep": "06:15", "arr": "11:55", "stops": [("SC", 1, "06:15", "06:15", 0.0), ("KZJ", 2, "08:18", "08:20", 132.0), ("WL", 3, "08:33", "08:35", 142.0), ("KMT", 4, "09:58", "10:00", 249.0), ("BZA", 5, "11:55", "11:55", 350.0)]},
            {"trip_id": "TRIP_SATAVAHANA_12714", "route_id": "IR_12714", "headsign": "Secunderabad via Warangal", "dep": "16:25", "arr": "22:15", "stops": [("BZA", 1, "16:25", "16:25", 0.0), ("KMT", 2, "17:38", "17:40", 101.0), ("WL", 3, "19:08", "19:10", 208.0), ("KZJ", 4, "19:28", "19:30", 218.0), ("SC", 5, "22:15", "22:15", 350.0)]},
            {"trip_id": "TRIP_TSRTC_WL_01", "route_id": "BUS_TSRTC_WL", "headsign": "Hanamkonda Warangal", "dep": "07:00", "arr": "09:45", "stops": [("MGBS_BUS", 1, "07:00", "07:00", 0.0), ("WL_BUS", 2, "09:45", "09:45", 148.0)]},
            {"trip_id": "TRIP_TSRTC_WL_RET", "route_id": "BUS_TSRTC_WL", "headsign": "Hyderabad MGBS", "dep": "10:30", "arr": "13:15", "stops": [("WL_BUS", 1, "10:30", "10:30", 0.0), ("MGBS_BUS", 2, "13:15", "13:15", 148.0)]},

            # 11. Hyderabad <-> Karimnagar
            {"trip_id": "TRIP_KRMR_12761", "route_id": "IR_12761", "headsign": "Karimnagar Railway Station", "dep": "04:30", "arr": "08:40", "stops": [("SC", 1, "04:30", "04:30", 0.0), ("KZJ", 2, "06:33", "06:35", 132.0), ("KRMR", 3, "08:40", "08:40", 212.0)]},
            {"trip_id": "TRIP_KRMR_EXP_17007", "route_id": "IR_12761", "headsign": "Karimnagar Express", "dep": "08:15", "arr": "12:30", "stops": [("SC", 1, "08:15", "08:15", 0.0), ("KZJ", 2, "10:18", "10:20", 132.0), ("KRMR", 3, "12:30", "12:30", 212.0)]},
            {"trip_id": "TRIP_KRMR_12762", "route_id": "IR_12762", "headsign": "Secunderabad Junction", "dep": "19:15", "arr": "23:20", "stops": [("KRMR", 1, "19:15", "19:15", 0.0), ("KZJ", 2, "20:53", "20:55", 80.0), ("SC", 3, "23:20", "23:20", 212.0)]},
            {"trip_id": "TRIP_TSRTC_KRMR_01", "route_id": "BUS_TSRTC_KRMR", "headsign": "Karimnagar Central Bus Stand", "dep": "06:30", "arr": "09:45", "stops": [("JBS_BUS", 1, "06:30", "06:30", 0.0), ("KRMR_BUS", 2, "09:45", "09:45", 162.0)]},
            {"trip_id": "TRIP_TSRTC_KRMR_RET", "route_id": "BUS_TSRTC_KRMR", "headsign": "Hyderabad JBS", "dep": "11:00", "arr": "14:15", "stops": [("KRMR_BUS", 1, "11:00", "11:00", 0.0), ("JBS_BUS", 2, "14:15", "14:15", 162.0)]},
            {"trip_id": "TRIP_TSRTC_KRMR_MGBS", "route_id": "BUS_TSRTC_KRMR", "headsign": "Karimnagar Central via JBS", "dep": "07:15", "arr": "10:50", "stops": [("MGBS_BUS", 1, "07:15", "07:15", 0.0), ("JBS_BUS", 2, "07:55", "08:00", 12.0), ("KRMR_BUS", 3, "10:50", "10:50", 174.0)]},

            # 12. Hyderabad <-> Vijayawada & Visakhapatnam
            {"trip_id": "TRIP_VB_20834", "route_id": "IR_20834", "headsign": "Visakhapatnam Junction via Vijayawada", "dep": "15:00", "arr": "23:30", "stops": [("SC", 1, "15:00", "15:00", 0.0), ("WL", 2, "16:33", "16:35", 142.0), ("KMT", 3, "17:43", "17:45", 249.0), ("BZA", 4, "19:00", "19:05", 350.0), ("VSKP", 5, "23:30", "23:30", 699.0)]},
            {"trip_id": "TRIP_VB_20833", "route_id": "IR_20833", "headsign": "Secunderabad via Vijayawada", "dep": "05:45", "arr": "14:15", "stops": [("VSKP", 1, "05:45", "05:45", 0.0), ("BZA", 2, "10:00", "10:05", 349.0), ("KMT", 3, "11:18", "11:20", 450.0), ("WL", 4, "12:28", "12:30", 557.0), ("SC", 5, "14:15", "14:15", 699.0)]},
            {"trip_id": "TRIP_RATNACHAL_12717", "route_id": "IR_12717", "headsign": "Visakhapatnam Junction", "dep": "06:15", "arr": "12:45", "stops": [("BZA", 1, "06:15", "06:15", 0.0), ("VSKP", 2, "12:45", "12:45", 349.0)]},
            {"trip_id": "TRIP_RATNACHAL_12718", "route_id": "IR_12718", "headsign": "Vijayawada Junction", "dep": "13:05", "arr": "19:40", "stops": [("VSKP", 1, "13:05", "13:05", 0.0), ("BZA", 2, "19:40", "19:40", 349.0)]},
            {"trip_id": "TRIP_APSRTC_BZA_01", "route_id": "BUS_APSRTC_BZA", "headsign": "Vijayawada PNBS", "dep": "07:30", "arr": "13:00", "stops": [("MGBS_BUS", 1, "07:30", "07:30", 0.0), ("PNBS_BUS", 2, "13:00", "13:00", 275.0)]},
            {"trip_id": "TRIP_APSRTC_BZA_RET", "route_id": "BUS_APSRTC_BZA", "headsign": "Hyderabad MGBS", "dep": "14:30", "arr": "20:00", "stops": [("PNBS_BUS", 1, "14:30", "14:30", 0.0), ("MGBS_BUS", 2, "20:00", "20:00", 275.0)]},
            {"trip_id": "TRIP_APSRTC_VSKP_01", "route_id": "BUS_APSRTC_VSKP", "headsign": "Visakhapatnam RTC Complex", "dep": "07:00", "arr": "14:30", "stops": [("PNBS_BUS", 1, "07:00", "07:00", 0.0), ("VSKP_BUS", 2, "14:30", "14:30", 360.0)]},
            {"trip_id": "TRIP_APSRTC_VSKP_RET", "route_id": "BUS_APSRTC_VSKP", "headsign": "Vijayawada PNBS", "dep": "15:00", "arr": "22:30", "stops": [("VSKP_BUS", 1, "15:00", "15:00", 0.0), ("PNBS_BUS", 2, "22:30", "22:30", 360.0)]},

            # 13. Tirupati <-> Chennai
            {"trip_id": "TRIP_SAPTHAGIRI_16057", "route_id": "IR_16057", "headsign": "Tirupati Main", "dep": "06:25", "arr": "09:40", "stops": [("MAS", 1, "06:25", "06:25", 0.0), ("AJJ", 2, "07:33", "07:35", 69.0), ("TPTY", 3, "09:40", "09:40", 147.0)]},
            {"trip_id": "TRIP_SAPTHAGIRI_16058", "route_id": "IR_16058", "headsign": "Chennai Central", "dep": "18:05", "arr": "21:35", "stops": [("TPTY", 1, "18:05", "18:05", 0.0), ("AJJ", 2, "20:03", "20:05", 78.0), ("MAS", 3, "21:35", "21:35", 147.0)]},
            {"trip_id": "TRIP_APSRTC_TPTY_01", "route_id": "BUS_APSRTC_TPTY", "headsign": "Tirupati Central Bus Station", "dep": "06:00", "arr": "09:30", "stops": [("CMBT_BUS", 1, "06:00", "06:00", 0.0), ("TPTY_BUS", 2, "09:30", "09:30", 135.0)]},
            {"trip_id": "TRIP_APSRTC_TPTY_RET", "route_id": "BUS_APSRTC_TPTY", "headsign": "Chennai CMBT", "dep": "11:00", "arr": "14:30", "stops": [("TPTY_BUS", 1, "11:00", "11:00", 0.0), ("CMBT_BUS", 2, "14:30", "14:30", 135.0)]},

            # 14. Kerala: Kochi <-> Thiruvananthapuram & Kozhikode
            {"trip_id": "TRIP_VB_20633", "route_id": "IR_20633", "headsign": "Thiruvananthapuram Central via Kochi", "dep": "17:28", "arr": "22:35", "stops": [("CLT", 1, "17:28", "17:30", 0.0), ("ERS", 2, "19:40", "19:45", 193.0), ("TVC", 3, "22:35", "22:35", 400.0)]},
            {"trip_id": "TRIP_VB_20634", "route_id": "IR_20634", "headsign": "Kozhikode via Kochi", "dep": "05:20", "arr": "10:28", "stops": [("TVC", 1, "05:20", "05:20", 0.0), ("ERS", 2, "08:15", "08:20", 207.0), ("CLT", 3, "10:28", "10:28", 400.0)]},
            {"trip_id": "TRIP_JAN_12075", "route_id": "IR_12075", "headsign": "Thiruvananthapuram Central via Kochi", "dep": "13:45", "arr": "21:25", "stops": [("CLT", 1, "13:45", "13:45", 0.0), ("ERS", 2, "17:20", "17:25", 193.0), ("TVC", 3, "21:25", "21:25", 400.0)]},
            {"trip_id": "TRIP_JAN_12076", "route_id": "IR_12076", "headsign": "Kozhikode via Kochi", "dep": "06:00", "arr": "13:00", "stops": [("TVC", 1, "06:00", "06:00", 0.0), ("ERS", 2, "09:12", "09:17", 207.0), ("CLT", 3, "13:00", "13:00", 400.0)]},
            {"trip_id": "TRIP_KERALA_TVC_01", "route_id": "BUS_KERALA_TVC", "headsign": "Thiruvananthapuram Thampanoor", "dep": "07:00", "arr": "12:15", "stops": [("ERS_BUS", 1, "07:00", "07:00", 0.0), ("TVC_BUS", 2, "12:15", "12:15", 215.0)]},
            {"trip_id": "TRIP_KERALA_TVC_RET", "route_id": "BUS_KERALA_TVC", "headsign": "Ernakulam KSRTC Stand", "dep": "14:00", "arr": "19:15", "stops": [("TVC_BUS", 1, "14:00", "14:00", 0.0), ("ERS_BUS", 2, "19:15", "19:15", 215.0)]},
            {"trip_id": "TRIP_KERALA_CLT_01", "route_id": "BUS_KERALA_CLT", "headsign": "Kozhikode KSRTC Terminal", "dep": "06:30", "arr": "11:45", "stops": [("ERS_BUS", 1, "06:30", "06:30", 0.0), ("CLT_BUS", 2, "11:45", "11:45", 190.0)]},
            {"trip_id": "TRIP_KERALA_CLT_RET", "route_id": "BUS_KERALA_CLT", "headsign": "Ernakulam KSRTC Stand", "dep": "13:00", "arr": "18:15", "stops": [("CLT_BUS", 1, "13:00", "13:00", 0.0), ("ERS_BUS", 2, "18:15", "18:15", 190.0)]},

            # 15. Mumbai <-> Pune
            {"trip_id": "TRIP_DECCAN_12123", "route_id": "IR_12123", "headsign": "Pune Junction", "dep": "17:10", "arr": "20:25", "stops": [("CSMT", 1, "17:10", "17:10", 0.0), ("DR", 2, "17:23", "17:25", 9.0), ("TNA", 3, "17:53", "17:55", 34.0), ("LNL", 4, "19:28", "19:30", 128.0), ("PUNE", 5, "20:25", "20:25", 192.0)]},
            {"trip_id": "TRIP_DECCAN_12124", "route_id": "IR_12124", "headsign": "Mumbai CSMT", "dep": "07:15", "arr": "10:25", "stops": [("PUNE", 1, "07:15", "07:15", 0.0), ("LNL", 2, "08:08", "08:10", 64.0), ("TNA", 3, "09:38", "09:40", 158.0), ("DR", 4, "10:03", "10:05", 183.0), ("CSMT", 5, "10:25", "10:25", 192.0)]},
            {"trip_id": "TRIP_MSRTC_PUNE_01", "route_id": "BUS_MSRTC_PUNE", "headsign": "Pune Shivajinagar", "dep": "06:30", "arr": "10:00", "stops": [("DADAR_ASIAD_BUS", 1, "06:30", "06:30", 0.0), ("SHIVAJINAGAR_BUS", 2, "10:00", "10:00", 160.0)]},
            {"trip_id": "TRIP_MSRTC_PUNE_RET", "route_id": "BUS_MSRTC_PUNE", "headsign": "Mumbai Dadar Asiad", "dep": "11:00", "arr": "14:30", "stops": [("SHIVAJINAGAR_BUS", 1, "11:00", "11:00", 0.0), ("DADAR_ASIAD_BUS", 2, "14:30", "14:30", 160.0)]},

            # 16. Delhi <-> Jaipur
            {"trip_id": "TRIP_VB_20977", "route_id": "IR_20977", "headsign": "Delhi Cantt", "dep": "07:55", "arr": "11:35", "stops": [("JP", 1, "07:55", "07:55", 0.0), ("AWR", 2, "09:28", "09:30", 151.0), ("GGN", 3, "10:58", "11:00", 274.0), ("DEC", 4, "11:35", "11:35", 290.0)]},
            {"trip_id": "TRIP_VB_20978", "route_id": "IR_20978", "headsign": "Jaipur Junction", "dep": "15:40", "arr": "19:25", "stops": [("DEC", 1, "15:40", "15:40", 0.0), ("GGN", 2, "15:58", "16:00", 16.0), ("AWR", 3, "17:35", "17:37", 139.0), ("JP", 4, "19:25", "19:25", 290.0)]},
            {"trip_id": "TRIP_RSRTC_JP_01", "route_id": "BUS_RSRTC_JP", "headsign": "Jaipur Sindhi Camp", "dep": "06:00", "arr": "11:30", "stops": [("KASHMERE_GATE_BUS", 1, "06:00", "06:00", 0.0), ("SINDHI_CAMP_BUS", 2, "11:30", "11:30", 270.0)]},
            {"trip_id": "TRIP_RSRTC_JP_RET", "route_id": "BUS_RSRTC_JP", "headsign": "Delhi ISBT Kashmere Gate", "dep": "13:00", "arr": "18:30", "stops": [("SINDHI_CAMP_BUS", 1, "13:00", "13:00", 0.0), ("KASHMERE_GATE_BUS", 2, "18:30", "18:30", 270.0)]},

            # 17. Kolkata <-> Bhubaneswar
            {"trip_id": "TRIP_VB_22895", "route_id": "IR_22895", "headsign": "Bhubaneswar / Puri", "dep": "06:10", "arr": "11:45", "stops": [("HWH", 1, "06:10", "06:10", 0.0), ("BBS", 2, "11:45", "11:45", 437.0)]},
            {"trip_id": "TRIP_VB_22896", "route_id": "IR_22896", "headsign": "Howrah Junction", "dep": "14:50", "arr": "20:30", "stops": [("BBS", 1, "14:50", "14:50", 0.0), ("HWH", 2, "20:30", "20:30", 437.0)]},
            {"trip_id": "TRIP_OSRTC_BBS_01", "route_id": "BUS_OSRTC_BBS", "headsign": "Bhubaneswar Baramunda ISBT", "dep": "06:30", "arr": "15:00", "stops": [("BABUGHAT_BUS", 1, "06:30", "06:30", 0.0), ("BARAMUNDA_BUS", 2, "15:00", "15:00", 445.0)]},
            {"trip_id": "TRIP_OSRTC_BBS_RET", "route_id": "BUS_OSRTC_BBS", "headsign": "Kolkata Babughat Stand", "dep": "07:30", "arr": "16:00", "stops": [("BARAMUNDA_BUS", 1, "07:30", "07:30", 0.0), ("BABUGHAT_BUS", 2, "16:00", "16:00", 445.0)]},

            # 18. Ahmedabad <-> Surat
            {"trip_id": "TRIP_VB_20901", "route_id": "IR_20901", "headsign": "Ahmedabad Junction", "dep": "08:55", "arr": "11:25", "stops": [("ST", 1, "08:55", "08:58", 0.0), ("ADI", 2, "11:25", "11:25", 229.0)]},
            {"trip_id": "TRIP_VB_20902", "route_id": "IR_20902", "headsign": "Surat / Mumbai", "dep": "15:00", "arr": "17:30", "stops": [("ADI", 1, "15:00", "15:00", 0.0), ("ST", 2, "17:30", "17:33", 229.0)]},
            {"trip_id": "TRIP_GSRTC_ST_01", "route_id": "BUS_GSRTC_ST", "headsign": "Surat Central Bus Station", "dep": "07:00", "arr": "11:30", "stops": [("GEETA_MANDIR_BUS", 1, "07:00", "07:00", 0.0), ("SURAT_BUS", 2, "11:30", "11:30", 265.0)]},
            {"trip_id": "TRIP_GSRTC_ST_RET", "route_id": "BUS_GSRTC_ST", "headsign": "Ahmedabad Geeta Mandir", "dep": "12:30", "arr": "17:00", "stops": [("SURAT_BUS", 1, "12:30", "12:30", 0.0), ("GEETA_MANDIR_BUS", 2, "17:00", "17:00", 265.0)]},

            # 19. Lucknow <-> Varanasi
            {"trip_id": "TRIP_VB_22545", "route_id": "IR_22545", "headsign": "Varanasi Junction", "dep": "07:15", "arr": "11:30", "stops": [("LKO", 1, "07:15", "07:15", 0.0), ("BSB", 2, "11:30", "11:30", 301.0)]},
            {"trip_id": "TRIP_VB_22546", "route_id": "IR_22546", "headsign": "Lucknow Charbagh", "dep": "15:15", "arr": "19:30", "stops": [("BSB", 1, "15:15", "15:15", 0.0), ("LKO", 2, "19:30", "19:30", 301.0)]},
            {"trip_id": "TRIP_UPSRTC_BSB_01", "route_id": "BUS_UPSRTC_BSB", "headsign": "Varanasi Cantt UPSRTC", "dep": "06:30", "arr": "13:00", "stops": [("KAISARBAGH_BUS", 1, "06:30", "06:30", 0.0), ("CANTT_BUS_BSB", 2, "13:00", "13:00", 310.0)]},
            {"trip_id": "TRIP_UPSRTC_BSB_RET", "route_id": "BUS_UPSRTC_BSB", "headsign": "Lucknow Kaisarbagh", "dep": "14:00", "arr": "20:30", "stops": [("CANTT_BUS_BSB", 1, "14:00", "14:00", 0.0), ("KAISARBAGH_BUS", 2, "20:30", "20:30", 310.0)]},

            # 20. National Trunk Connections
            # Hyderabad <-> Tirupati
            {"trip_id": "TRIP_VENKATADRI_12797", "route_id": "IR_12797", "headsign": "Tirupati Main via Renigunta", "dep": "20:05", "arr": "06:55", "stops": [("KCG", 1, "20:05", "20:05", 0.0), ("SC", 2, "20:40", "20:45", 8.0), ("WL", 3, "22:50", "22:52", 150.0), ("KMT", 4, "00:05", "00:07", 257.0), ("BZA", 5, "01:45", "01:55", 358.0), ("RU", 6, "06:20", "06:22", 720.0), ("TPTY", 7, "06:55", "06:55", 730.0)]},
            {"trip_id": "TRIP_VENKATADRI_12798", "route_id": "IR_12798", "headsign": "Kacheguda / Secunderabad", "dep": "21:55", "arr": "08:15", "stops": [("TPTY", 1, "21:55", "21:55", 0.0), ("RU", 2, "22:15", "22:17", 10.0), ("BZA", 3, "02:40", "02:50", 372.0), ("KMT", 4, "04:15", "04:17", 473.0), ("WL", 5, "05:40", "05:42", 580.0), ("SC", 6, "07:45", "07:50", 722.0), ("KCG", 7, "08:15", "08:15", 730.0)]},
            {"trip_id": "TRIP_TSRTC_TPTY_01", "route_id": "BUS_TSRTC_TPTY", "headsign": "Tirupati Central Bus Station", "dep": "21:00", "arr": "06:30", "stops": [("MGBS_BUS", 1, "21:00", "21:00", 0.0), ("TPTY_BUS", 2, "06:30", "06:30", 550.0)]},
            {"trip_id": "TRIP_TSRTC_TPTY_RET", "route_id": "BUS_TSRTC_TPTY", "headsign": "Hyderabad MGBS Imlibun", "dep": "20:30", "arr": "06:00", "stops": [("TPTY_BUS", 1, "20:30", "20:30", 0.0), ("MGBS_BUS", 2, "06:00", "06:00", 550.0)]},
            {"trip_id": "TRIP_TSRTC_TPTY_DAY", "route_id": "BUS_TSRTC_TPTY", "headsign": "Tirupati Central Bus Station", "dep": "06:30", "arr": "16:00", "stops": [("MGBS_BUS", 1, "06:30", "06:30", 0.0), ("TPTY_BUS", 2, "16:00", "16:00", 550.0)]},
            {"trip_id": "TRIP_TSRTC_TPTY_DAY_RET", "route_id": "BUS_TSRTC_TPTY", "headsign": "Hyderabad MGBS Imlibun", "dep": "07:30", "arr": "17:00", "stops": [("TPTY_BUS", 1, "07:30", "07:30", 0.0), ("MGBS_BUS", 2, "17:00", "17:00", 550.0)]},

            # Madurai <-> Bengaluru
            {"trip_id": "TRIP_VB_20671", "route_id": "IR_20671", "headsign": "KSR Bengaluru via Salem", "dep": "05:15", "arr": "12:30", "stops": [("MDU", 1, "05:15", "05:15", 0.0), ("DG", 2, "06:05", "06:07", 62.0), ("TPJ", 3, "07:00", "07:05", 156.0), ("SA", 4, "08:30", "08:35", 300.0), ("BWT", 5, "10:55", "10:57", 440.0), ("KJM", 6, "11:50", "11:52", 500.0), ("SBC", 7, "12:30", "12:30", 515.0)]},
            {"trip_id": "TRIP_VB_20672", "route_id": "IR_20672", "headsign": "Madurai Junction via Salem", "dep": "13:30", "arr": "20:45", "stops": [("SBC", 1, "13:30", "13:30", 0.0), ("KJM", 2, "13:50", "13:52", 15.0), ("BWT", 3, "14:45", "14:47", 75.0), ("SA", 4, "17:15", "17:20", 215.0), ("TPJ", 5, "18:45", "18:50", 359.0), ("DG", 6, "19:40", "19:42", 453.0), ("MDU", 7, "20:45", "20:45", 515.0)]},
            {"trip_id": "TRIP_KSRTC_MDU_01", "route_id": "BUS_KSRTC_MDU", "headsign": "Madurai Mattuthavani", "dep": "22:00", "arr": "06:15", "stops": [("KBS_BUS", 1, "22:00", "22:00", 0.0), ("SA_BUS", 2, "02:30", "02:35", 210.0), ("MDU_BUS", 3, "06:15", "06:15", 435.0)]},
            {"trip_id": "TRIP_KSRTC_MDU_RET", "route_id": "BUS_KSRTC_MDU", "headsign": "Bengaluru Majestic KBS", "dep": "21:30", "arr": "05:45", "stops": [("MDU_BUS", 1, "21:30", "21:30", 0.0), ("SA_BUS", 2, "01:30", "01:35", 225.0), ("KBS_BUS", 3, "05:45", "05:45", 435.0)]},

            # Coimbatore <-> Hyderabad & Bengaluru <-> Hyderabad Bus
            {"trip_id": "TRIP_SABARI_17229", "route_id": "IR_17229", "headsign": "Secunderabad via Tirupati", "dep": "04:40", "arr": "04:55", "stops": [("ERS", 1, "04:40", "04:45", 0.0), ("CBE", 2, "08:00", "08:05", 205.0), ("TUP", 3, "08:48", "08:50", 256.0), ("ED", 4, "09:40", "09:45", 306.0), ("SA", 5, "10:35", "10:40", 366.0), ("JTJ", 6, "12:20", "12:22", 486.0), ("KPD", 7, "13:45", "13:50", 570.0), ("TPTY", 8, "16:35", "16:40", 675.0), ("BZA", 9, "21:40", "21:50", 1055.0), ("KMT", 10, "23:10", "23:12", 1156.0), ("WL", 11, "00:35", "00:37", 1263.0), ("SC", 12, "04:55", "04:55", 1405.0)]},
            {"trip_id": "TRIP_SABARI_17230", "route_id": "IR_17230", "headsign": "Coimbatore / Ernakulam via Tirupati", "dep": "12:20", "arr": "11:15", "stops": [("SC", 1, "12:20", "12:20", 0.0), ("WL", 2, "14:35", "14:37", 142.0), ("KMT", 3, "16:00", "16:02", 249.0), ("BZA", 4, "17:40", "17:50", 350.0), ("TPTY", 5, "22:45", "22:50", 730.0), ("KPD", 6, "01:10", "01:15", 835.0), ("JTJ", 7, "02:25", "02:27", 919.0), ("SA", 8, "04:00", "04:05", 1039.0), ("ED", 9, "05:00", "05:05", 1099.0), ("TUP", 10, "05:50", "05:52", 1149.0), ("CBE", 11, "06:45", "06:50", 1200.0), ("ERS", 12, "11:15", "11:15", 1405.0)]},
            {"trip_id": "TRIP_KSRTC_HYD_01", "route_id": "BUS_KSRTC_HYD", "headsign": "Hyderabad MGBS", "dep": "06:30", "arr": "15:00", "stops": [("KBS_BUS", 1, "06:30", "06:30", 0.0), ("MGBS_BUS", 2, "15:00", "15:00", 570.0)]},
            {"trip_id": "TRIP_KSRTC_HYD_RET", "route_id": "BUS_KSRTC_HYD", "headsign": "Bengaluru Majestic KBS", "dep": "07:30", "arr": "16:00", "stops": [("MGBS_BUS", 1, "07:30", "07:30", 0.0), ("KBS_BUS", 2, "16:00", "16:00", 570.0)]},
            {"trip_id": "TRIP_KSRTC_HYD_NIGHT", "route_id": "BUS_KSRTC_HYD", "headsign": "Hyderabad MGBS", "dep": "21:30", "arr": "06:00", "stops": [("KBS_BUS", 1, "21:30", "21:30", 0.0), ("MGBS_BUS", 2, "06:00", "06:00", 570.0)]},
            {"trip_id": "TRIP_KSRTC_HYD_NIGHT_RET", "route_id": "BUS_KSRTC_HYD", "headsign": "Bengaluru Majestic KBS", "dep": "22:00", "arr": "06:30", "stops": [("MGBS_BUS", 1, "22:00", "22:00", 0.0), ("KBS_BUS", 2, "06:30", "06:30", 570.0)]},

            # Vijayawada <-> Secunderabad <-> Pune <-> Mumbai
            {"trip_id": "TRIP_KONARK_11020", "route_id": "IR_11020", "headsign": "Mumbai Dadar / CSMT via Pune", "dep": "15:20", "arr": "22:45", "stops": [("BBS", 1, "15:20", "15:20", 0.0), ("VSKP", 2, "22:20", "22:40", 443.0), ("BZA", 3, "04:35", "04:50", 792.0), ("KMT", 4, "06:05", "06:07", 893.0), ("WL", 5, "07:25", "07:27", 1000.0), ("KZJ", 6, "07:45", "07:47", 1010.0), ("SC", 7, "10:50", "11:05", 1142.0), ("PUNE", 8, "19:40", "19:45", 1740.0), ("LNL", 9, "20:48", "20:50", 1804.0), ("DR", 10, "22:45", "22:45", 1920.0)]},
            {"trip_id": "TRIP_KONARK_11019", "route_id": "IR_11019", "headsign": "Bhubaneswar via Pune & Secunderabad", "dep": "14:15", "arr": "23:15", "stops": [("DR", 1, "14:15", "14:15", 0.0), ("LNL", 2, "16:20", "16:22", 116.0), ("PUNE", 3, "17:55", "18:00", 180.0), ("SC", 4, "03:15", "03:30", 778.0), ("KZJ", 5, "05:18", "05:20", 910.0), ("WL", 6, "05:43", "05:45", 920.0), ("KMT", 7, "07:08", "07:10", 1027.0), ("BZA", 8, "08:45", "09:00", 1128.0), ("VSKP", 9, "15:30", "15:50", 1477.0), ("BBS", 10, "23:15", "23:15", 1920.0)]},

            # Delhi <-> Kochi via National Spine
            {"trip_id": "TRIP_KERALA_12625", "route_id": "IR_12625", "headsign": "Thiruvananthapuram via Kochi", "dep": "20:10", "arr": "12:30", "stops": [("NDLS", 1, "20:10", "20:10", 0.0), ("WL", 2, "14:15", "14:17", 1435.0), ("BZA", 3, "16:45", "16:55", 1543.0), ("KPD", 4, "22:50", "22:55", 1978.0), ("SA", 5, "01:45", "01:50", 2183.0), ("ED", 6, "02:40", "02:45", 2243.0), ("CBE", 7, "04:15", "04:20", 2294.0), ("ERS", 8, "08:40", "08:45", 2499.0), ("TVC", 9, "12:30", "12:30", 2705.0)]},
            {"trip_id": "TRIP_KERALA_12626", "route_id": "IR_12626", "headsign": "New Delhi via Coimbatore", "dep": "12:30", "arr": "04:35", "stops": [("TVC", 1, "12:30", "12:30", 0.0), ("ERS", 2, "15:55", "16:00", 206.0), ("CBE", 3, "20:20", "20:25", 411.0), ("ED", 4, "21:40", "21:45", 462.0), ("SA", 5, "22:45", "22:50", 522.0), ("KPD", 6, "01:50", "01:55", 727.0), ("BZA", 7, "07:45", "07:55", 1162.0), ("WL", 8, "10:15", "10:17", 1270.0), ("NDLS", 9, "04:35", "04:35", 2705.0)]},

            # Jaipur <-> Ahmedabad
            {"trip_id": "TRIP_VB_20979", "route_id": "IR_20979", "headsign": "Ahmedabad Junction", "dep": "06:10", "arr": "12:55", "stops": [("JP", 1, "06:10", "06:10", 0.0), ("AWR", 2, "07:20", "07:22", 151.0), ("ADI", 3, "12:55", "12:55", 648.0)]},
            {"trip_id": "TRIP_VB_20980", "route_id": "IR_20980", "headsign": "Jaipur Junction", "dep": "15:45", "arr": "22:30", "stops": [("ADI", 1, "15:45", "15:45", 0.0), ("AWR", 2, "21:18", "21:20", 497.0), ("JP", 3, "22:30", "22:30", 648.0)]},
            {"trip_id": "TRIP_RSRTC_ADI_01", "route_id": "BUS_RSRTC_ADI", "headsign": "Ahmedabad Geeta Mandir", "dep": "20:00", "arr": "07:30", "stops": [("SINDHI_CAMP_BUS", 1, "20:00", "20:00", 0.0), ("GEETA_MANDIR_BUS", 2, "07:30", "07:30", 655.0)]},
            {"trip_id": "TRIP_RSRTC_ADI_RET", "route_id": "BUS_RSRTC_ADI", "headsign": "Jaipur Sindhi Camp", "dep": "20:30", "arr": "08:00", "stops": [("GEETA_MANDIR_BUS", 1, "20:30", "20:30", 0.0), ("SINDHI_CAMP_BUS", 2, "08:00", "08:00", 655.0)]},

            # Mysuru <-> Hubballi <-> Pune
            {"trip_id": "TRIP_SHARAVATI_11036", "route_id": "IR_11036", "headsign": "Mumbai Dadar via Pune", "dep": "06:15", "arr": "02:30", "stops": [("MYS", 1, "06:15", "06:15", 0.0), ("MANDYA", 2, "07:00", "07:02", 45.0), ("SBC", 3, "08:35", "08:50", 138.0), ("YPR", 4, "09:05", "09:07", 144.0), ("UBL", 5, "14:40", "14:50", 613.0), ("PUNE", 6, "22:45", "22:50", 1027.0), ("LNL", 7, "23:45", "23:47", 1091.0), ("DR", 8, "02:30", "02:30", 1205.0)]},
            {"trip_id": "TRIP_SHARAVATI_11035", "route_id": "IR_11035", "headsign": "Mysuru Junction via Pune", "dep": "21:30", "arr": "18:15", "stops": [("DR", 1, "21:30", "21:30", 0.0), ("LNL", 2, "23:55", "23:57", 114.0), ("PUNE", 3, "01:00", "01:05", 178.0), ("UBL", 4, "09:15", "09:25", 592.0), ("YPR", 5, "15:15", "15:17", 1061.0), ("SBC", 6, "15:40", "15:45", 1067.0), ("MANDYA", 7, "17:15", "17:17", 1160.0), ("MYS", 8, "18:15", "18:15", 1205.0)]},
            {"trip_id": "TRIP_MSRTC_UBL_01", "route_id": "BUS_MSRTC_UBL", "headsign": "Bengaluru KBS via Hubballi", "dep": "21:00", "arr": "11:30", "stops": [("SHIVAJINAGAR_BUS", 1, "21:00", "21:00", 0.0), ("UBL_BUS", 2, "05:00", "05:15", 414.0), ("KBS_BUS", 3, "11:30", "11:30", 824.0)]},
            {"trip_id": "TRIP_MSRTC_UBL_RET", "route_id": "BUS_MSRTC_UBL", "headsign": "Pune Shivajinagar via Hubballi", "dep": "19:00", "arr": "09:30", "stops": [("KBS_BUS", 1, "19:00", "19:00", 0.0), ("UBL_BUS", 2, "01:30", "01:45", 410.0), ("SHIVAJINAGAR_BUS", 3, "09:30", "09:30", 824.0)]},
            {"trip_id": "TRIP_MSRTC_MYS_PUNE_01", "route_id": "BUS_MSRTC_MYS_PUNE", "headsign": "Pune Swargate Bus Stand", "dep": "18:00", "arr": "08:30", "stops": [("MYS_BUS", 1, "18:00", "18:00", 0.0), ("SWARGATE_BUS", 2, "08:30", "08:30", 870.0)]},
            {"trip_id": "TRIP_MSRTC_MYS_PUNE_RET", "route_id": "BUS_MSRTC_MYS_PUNE", "headsign": "Mysuru Central Bus Stand", "dep": "19:00", "arr": "09:30", "stops": [("SWARGATE_BUS", 1, "19:00", "19:00", 0.0), ("MYS_BUS", 2, "09:30", "09:30", 870.0)]},

            # Interstate Express Buses (Coimbatore <-> Hyderabad, Vijayawada <-> Mumbai)
            {"trip_id": "TRIP_TSRTC_CBE_HYD_01", "route_id": "BUS_TSRTC_CBE_HYD", "headsign": "Hyderabad MGBS via Salem & Bengaluru", "dep": "17:30", "arr": "08:30", "stops": [("CBE_BUS", 1, "17:30", "17:30", 0.0), ("MGBS_BUS", 2, "08:30", "08:30", 920.0)]},
            {"trip_id": "TRIP_TSRTC_CBE_HYD_RET", "route_id": "BUS_TSRTC_CBE_HYD", "headsign": "Coimbatore Gandhipuram", "dep": "18:00", "arr": "09:00", "stops": [("MGBS_BUS", 1, "18:00", "18:00", 0.0), ("CBE_BUS", 2, "09:00", "09:00", 920.0)]},
            {"trip_id": "TRIP_APSRTC_BZA_MUM_01", "route_id": "BUS_APSRTC_BZA_MUM", "headsign": "Mumbai Dadar Asiad Stand via Pune", "dep": "15:30", "arr": "09:00", "stops": [("PNBS_BUS", 1, "15:30", "15:30", 0.0), ("DADAR_ASIAD_BUS", 2, "09:00", "09:00", 985.0)]},
            {"trip_id": "TRIP_APSRTC_BZA_MUM_RET", "route_id": "BUS_APSRTC_BZA_MUM", "headsign": "Vijayawada Pandit Nehru Bus Station", "dep": "16:00", "arr": "09:30", "stops": [("DADAR_ASIAD_BUS", 1, "16:00", "16:00", 0.0), ("PNBS_BUS", 2, "09:30", "09:30", 985.0)]},

            # 21. Urban Metros
            {"trip_id": "TRIP_CMRL_BL_01", "route_id": "METRO_CMRL_BLUE", "headsign": "Airport Metro", "dep": "06:00", "arr": "06:40", "stops": [("CMRL_CENTRAL", 1, "06:00", "06:00", 0.0), ("CMRL_AIRPORT", 2, "06:40", "06:40", 25.0)]},
            {"trip_id": "TRIP_BMRCL_P_01", "route_id": "METRO_BMRCL_PURPLE", "headsign": "Whitefield Kadugodi", "dep": "06:00", "arr": "06:45", "stops": [("BMRCL_MAJESTIC", 1, "06:00", "06:00", 0.0), ("BMRCL_MAJESTIC", 2, "06:45", "06:45", 24.0)]},
            {"trip_id": "TRIP_HMR_R_01", "route_id": "METRO_HMR_RED", "headsign": "Ameerpet Metro", "dep": "06:00", "arr": "06:22", "stops": [("HYD_METRO_MGBS", 1, "06:00", "06:00", 0.0), ("HYD_METRO_AMEERPET", 2, "06:22", "06:22", 11.0)]},
        ]

        # Insert Trips and StopTimes
        trip_ids = [td["trip_id"] for td in trips_and_stops]
        db.query(StopTime).filter(StopTime.trip_id.in_(trip_ids)).delete(synchronize_session=False)
        db.commit()

        for td in trips_and_stops:
            tr = Trip(
                id=td["trip_id"],
                route_id=td["route_id"],
                trip_headsign=td["headsign"],
                scheduled_departure=td["dep"],
                scheduled_arrival=td["arr"],
                operating_days="DAILY,Mon,Tue,Wed,Thu,Fri,Sat,Sun"
            )
            db.merge(tr)

            for st_id, seq, arr, dep, dist in td["stops"]:
                st_time = StopTime(
                    trip_id=td["trip_id"],
                    station_id=st_id,
                    stop_sequence=seq,
                    arrival_time=arr,
                    departure_time=dep,
                    distance_from_start_km=dist
                )
                db.add(st_time)
        db.commit()

        # 6. Intermodal Walk Transfers
        db.query(Transfer).delete(synchronize_session=False)
        db.commit()
        transfers_data = [
            ("MAS", "CMRL_CENTRAL", "walk", 4, 0.25, "Walkway subway linking Chennai Central & CMRL"),
            ("CMRL_CENTRAL", "MAS", "walk", 4, 0.25, "Subway linking CMRL & Chennai Central"),
            ("MAS", "MS", "walk", 10, 1.80, "Suburban rail / walking concourse between Chennai Central and Chennai Egmore"),
            ("MS", "MAS", "walk", 10, 1.80, "Suburban rail / walking concourse between Chennai Egmore and Chennai Central"),
            ("MS", "CMRL_CENTRAL", "walk", 8, 1.20, "Pedestrian link between Chennai Egmore and Central"),
            ("CMRL_CENTRAL", "MS", "walk", 8, 1.20, "Pedestrian link between Chennai Central and Egmore"),
            ("CMBT_BUS", "KCBT_BUS", "bus", 40, 28.00, "MTC 70V feeder bus between CMBT and Kilambakkam KCBT"),
            ("KCBT_BUS", "CMBT_BUS", "bus", 40, 28.00, "MTC 70V feeder bus between Kilambakkam KCBT and CMBT"),
            ("MAS", "CMBT_BUS", "metro", 20, 10.50, "CMRL Green Line direct from Chennai Central to CMBT"),
            ("CMBT_BUS", "MAS", "metro", 20, 10.50, "CMRL Green Line direct from CMBT to Chennai Central"),
            ("SC", "JBS_BUS", "walk", 8, 0.85, "Covered foot overbridge linking Secunderabad Station & Jubilee Bus Station"),
            ("JBS_BUS", "SC", "walk", 8, 0.85, "Covered foot overbridge linking Jubilee Bus Station & Secunderabad Station"),
            ("MGBS_BUS", "JBS_BUS", "bus", 25, 11.50, "TSRTC City bus link between MGBS and JBS"),
            ("JBS_BUS", "MGBS_BUS", "bus", 25, 11.50, "TSRTC City bus link between JBS and MGBS"),
            ("SC", "MGBS_BUS", "metro", 18, 9.20, "Hyderabad Metro Green Line connecting Secunderabad and MGBS"),
            ("MGBS_BUS", "SC", "metro", 18, 9.20, "Hyderabad Metro Green Line connecting MGBS and Secunderabad"),
            ("KCG", "MGBS_BUS", "walk", 12, 1.90, "Feeder / auto link connecting Kacheguda Railway & MGBS"),
            ("MGBS_BUS", "KCG", "walk", 12, 1.90, "Feeder / auto link connecting MGBS & Kacheguda Railway"),
            ("HYB", "MGBS_BUS", "walk", 10, 1.60, "City bus link connecting Hyderabad Nampally & MGBS"),
            ("MGBS_BUS", "HYB", "walk", 10, 1.60, "City bus link connecting MGBS & Hyderabad Nampally"),
            ("SC", "KCG", "train", 15, 7.50, "MMTS suburban rail between Secunderabad and Kacheguda"),
            ("KCG", "SC", "train", 15, 7.50, "MMTS suburban rail between Kacheguda and Secunderabad"),
            ("SC", "HYB", "train", 12, 9.00, "MMTS suburban rail between Secunderabad and Hyderabad Deccan"),
            ("HYB", "SC", "train", 12, 9.00, "MMTS suburban rail between Hyderabad Deccan and Secunderabad"),
            ("TPTY", "RU", "train", 12, 9.80, "Suburban rail shuttle linking Tirupati Main & Renigunta Junction"),
            ("RU", "TPTY", "train", 12, 9.80, "Suburban rail shuttle linking Renigunta Junction & Tirupati Main"),
            ("SBC", "KBS_BUS", "walk", 5, 0.35, "Skywalk connecting KSR Bengaluru & Majestic Bus Station"),
            ("KBS_BUS", "SBC", "walk", 5, 0.35, "Skywalk connecting Majestic Bus Station & KSR Bengaluru"),
            ("SBC", "BMRCL_MAJESTIC", "walk", 4, 0.30, "Underground skywalk from KSR Bengaluru to Namma Metro"),
            ("BMRCL_MAJESTIC", "SBC", "walk", 4, 0.30, "Underground skywalk from Namma Metro to KSR Bengaluru"),
            ("KBS_BUS", "BMRCL_MAJESTIC", "walk", 3, 0.20, "Direct pedestrian concourse from KBS to Metro"),
            ("BMRCL_MAJESTIC", "KBS_BUS", "walk", 3, 0.20, "Direct pedestrian concourse from Metro to KBS"),
            ("MGBS_BUS", "HYD_METRO_MGBS", "walk", 3, 0.20, "Covered foot overbridge linking MGBS Bus & Metro"),
            ("HYD_METRO_MGBS", "MGBS_BUS", "walk", 3, 0.20, "Covered foot overbridge linking Metro & MGBS Bus"),
            ("MDU", "MDU_BUS", "walk", 20, 4.50, "Auto-rickshaw / feeder transfer to Mattuthavani Bus Stand"),
            ("MDU_BUS", "MDU", "walk", 20, 4.50, "Feeder transfer to Madurai Junction"),
            ("CBE", "CBE_BUS", "walk", 15, 2.50, "City bus / feeder transfer to Gandhipuram Stand"),
            ("CBE_BUS", "CBE", "walk", 15, 2.50, "City bus / feeder transfer to Coimbatore Junction"),
            ("TPJ", "TPJ_BUS", "walk", 10, 1.20, "Walk / auto transfer to Trichy Central Bus Stand"),
            ("TPJ_BUS", "TPJ", "walk", 10, 1.20, "Walk / auto transfer to Trichy Junction"),
            ("PDKT", "PDKT_BUS", "walk", 10, 1.00, "Walkway to Pudukkottai New Bus Stand"),
            ("PDKT_BUS", "PDKT", "walk", 10, 1.00, "Walkway to Pudukkottai Railway Station"),
            ("MYS", "MYS_BUS", "walk", 12, 1.50, "Feeder link to Mysuru Suburban Bus Stand"),
            ("MYS_BUS", "MYS", "walk", 12, 1.50, "Feeder link to Mysuru Railway Station"),
            ("UBL", "UBL_BUS", "walk", 12, 1.80, "Feeder link to Hubballi Hosur Bus Stand"),
            ("UBL_BUS", "UBL", "walk", 12, 1.80, "Feeder link to SSS Hubballi Junction"),
            ("MAQ", "MAQ_BUS", "walk", 12, 1.50, "Feeder link to Mangaluru KSRTC Bus Stand"),
            ("MAQ_BUS", "MAQ", "walk", 12, 1.50, "Feeder link to Mangaluru Central"),
            ("WL", "WL_BUS", "walk", 15, 2.20, "Feeder link to Hanamkonda Bus Stand"),
            ("WL_BUS", "WL", "walk", 15, 2.20, "Feeder link to Warangal Railway Station"),
            ("KRMR", "KRMR_BUS", "walk", 12, 1.50, "Feeder link to Karimnagar TSRTC Bus Stand"),
            ("KRMR_BUS", "KRMR", "walk", 12, 1.50, "Feeder link to Karimnagar Railway Station"),
            ("BZA", "PNBS_BUS", "walk", 10, 1.20, "Feeder link between Vijayawada Jn & PNBS Bus Stand"),
            ("PNBS_BUS", "BZA", "walk", 10, 1.20, "Feeder link between PNBS Bus Stand & Vijayawada Jn"),
            ("VSKP", "VSKP_BUS", "walk", 12, 1.80, "Feeder link to Dwaraka RTC Complex"),
            ("VSKP_BUS", "VSKP", "walk", 12, 1.80, "Feeder link to Visakhapatnam Junction"),
            ("TPTY", "TPTY_BUS", "walk", 8, 0.80, "Walkway from Tirupati Railway to Bus Station"),
            ("TPTY_BUS", "TPTY", "walk", 8, 0.80, "Walkway from Bus Station to Tirupati Railway"),
            ("ERS", "ERS_BUS", "walk", 10, 1.00, "Walkway between Ernakulam Junction & KSRTC Stand"),
            ("ERS_BUS", "ERS", "walk", 10, 1.00, "Walkway between KSRTC Stand & Ernakulam Junction"),
            ("TVC", "TVC_BUS", "walk", 5, 0.30, "Pedestrian subway connecting TVC Central & Thampanoor Bus Station"),
            ("TVC_BUS", "TVC", "walk", 5, 0.30, "Pedestrian subway connecting Thampanoor Bus Station & TVC Central"),
            ("CLT", "CLT_BUS", "walk", 10, 1.00, "Walkway between Kozhikode Station & KSRTC Terminal"),
            ("CLT_BUS", "CLT", "walk", 10, 1.00, "Walkway between KSRTC Terminal & Kozhikode Station"),
            ("DR", "DADAR_ASIAD_BUS", "walk", 5, 0.30, "Pedestrian skywalk connecting Dadar Station & Asiad Stand"),
            ("DADAR_ASIAD_BUS", "DR", "walk", 5, 0.30, "Pedestrian skywalk connecting Asiad Stand & Dadar Station"),
            ("PUNE", "SHIVAJINAGAR_BUS", "walk", 15, 2.50, "Local bus/auto link between Pune Jn & Shivajinagar"),
            ("SHIVAJINAGAR_BUS", "PUNE", "walk", 15, 2.50, "Local bus/auto link between Shivajinagar & Pune Jn"),
            ("NDLS", "KASHMERE_GATE_BUS", "walk", 15, 3.50, "Delhi Metro Yellow Line transfer link"),
            ("KASHMERE_GATE_BUS", "NDLS", "walk", 15, 3.50, "Delhi Metro Yellow Line transfer link"),
            ("JP", "SINDHI_CAMP_BUS", "walk", 10, 1.20, "Walkway between Sindhi Camp & Jaipur Junction"),
            ("SINDHI_CAMP_BUS", "JP", "walk", 10, 1.20, "Walkway between Jaipur Junction & Sindhi Camp"),
            ("HWH", "BABUGHAT_BUS", "walk", 15, 2.00, "Ferry/walk link between Howrah & Babughat"),
            ("BABUGHAT_BUS", "HWH", "walk", 15, 2.00, "Ferry/walk link between Babughat & Howrah"),
            ("BBS", "BARAMUNDA_BUS", "walk", 20, 5.00, "City bus link between Bhubaneswar Station & Baramunda"),
            ("BARAMUNDA_BUS", "BBS", "walk", 20, 5.00, "City bus link between Baramunda & Bhubaneswar Station"),
            ("ADI", "GEETA_MANDIR_BUS", "walk", 12, 1.80, "BRTS link between Ahmedabad Station & Geeta Mandir"),
            ("GEETA_MANDIR_BUS", "ADI", "walk", 12, 1.80, "BRTS link between Geeta Mandir & Ahmedabad Station"),
            ("ST", "SURAT_BUS", "walk", 5, 0.40, "Direct pedestrian walkway from Surat Station to GSRTC Bus Station"),
            ("SURAT_BUS", "ST", "walk", 5, 0.40, "Direct pedestrian walkway from GSRTC Bus Station to Surat Station"),
            ("LKO", "KAISARBAGH_BUS", "walk", 15, 2.50, "City bus link between Charbagh and Kaisarbagh"),
            ("KAISARBAGH_BUS", "LKO", "walk", 15, 2.50, "City bus link between Kaisarbagh and Charbagh"),
            ("BSB", "CANTT_BUS_BSB", "walk", 5, 0.35, "Pedestrian link between Varanasi Cantt Station & Bus Stand"),
            ("CANTT_BUS_BSB", "BSB", "walk", 5, 0.35, "Pedestrian link between Varanasi Cantt Bus Stand & Station"),
        ]

        for u, v, mode, dur, dist, notes in transfers_data:
            tr = Transfer(
                from_station_id=u,
                to_station_id=v,
                transfer_type=mode.upper(),
                min_transfer_time_min=dur,
                distance_meters=int(dist * 1000),
                walking_route_notes=notes
            )
            db.add(tr)
        db.commit()

        # 7. Generate Graph Connections and update Gazetteer flags
        from app.services.transport_data_service import TransportDataService
        svc = TransportDataService(db=db)
        svc.rebuild_connections_from_stop_times()

        gaz = GazetteerService(db=db)
        gaz.refresh_transit_coverage_flags()

        logger.info("India-wide transit datasets, buses, and multimodal graphs seeded successfully!")

    except Exception as e:
        logger.error(f"Error seeding India-wide transit data: {e}", exc_info=True)
        if db:
            db.rollback()
    finally:
        if close_db and db:
            db.close()
