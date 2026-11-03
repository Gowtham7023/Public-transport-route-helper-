import os
import re
import json
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

STATION_SYNONYMS = {
    # Chennai Hubs
    "chennai": "MAS",
    "chennai central": "MAS",
    "mgr central": "MAS",
    "central": "MAS",
    "egmore": "MS",
    "chennai egmore": "MS",
    "tambaram": "TBM",
    "chennai airport": "CMRL_AIRPORT",
    "airport": "CMRL_AIRPORT",
    "koyambedu": "CMBT_BUS",
    "cmbt": "CMBT_BUS",
    "kilambakkam": "KCBT_BUS",
    "kcbt": "KCBT_BUS",

    # Bengaluru Hubs
    "bengaluru": "SBC",
    "bangalore": "SBC",
    "ksr bengaluru": "SBC",
    "majestic": "BMRCL_MAJESTIC",
    "majestic bus": "KBS_BUS",
    "kbs": "KBS_BUS",
    "kempegowda": "KBS_BUS",
    "whitefield": "BMRCL_WHITEFIELD",
    "krishnarajapuram": "KJM",
    "kr puram": "KJM",
    "yesvantpur": "YPR",
    "cantt": "BNC",
    "bangalore cantt": "BNC",
    "electronic city": "ECITY_BUS",
    "silk board": "SILKBOARD_BUS",
    "shantinagar": "SHANTINAGAR_BUS",

    # Mysuru Hubs
    "mysuru": "MYS",
    "mysore": "MYS",
    "mysuru bus": "MYS_BUS",
    "mysore bus": "MYS_BUS",
    "mandya": "MANDYA",

    # Madurai Hubs
    "madurai": "MDU",
    "madurai junction": "MDU",
    "madurai bus": "MDU_BUS",
    "mattuthavani": "MDU_BUS",
    "dindigul": "DG",
    "tiruchirappalli": "TPJ",
    "trichy": "TPJ",

    # Coimbatore Corridor
    "coimbatore": "CBE",
    "coimbatore junction": "CBE",
    "coimbatore bus": "CBE_BUS",
    "gandhipuram": "CBE_BUS",
    "salem": "SA",
    "erode": "ED",
    "tiruppur": "TUP",

    # Hyderabad Hubs
    "hyderabad": "SC",
    "secunderabad": "SC",
    "nampally": "HYB",
    "hyderabad deccan": "HYB",
    "kacheguda": "KCG",
    "mahatma gandhi bus station": "MGBS_BUS",
    "mgbs": "MGBS_BUS",
    "imlibun": "MGBS_BUS",
    "warangal": "WL",
    "khammam": "KMT",

    # Vijayawada Hubs
    "vijayawada": "BZA",
    "vijayawada junction": "BZA",
    "pandit nehru bus station": "PNBS_BUS",
    "pnbs": "PNBS_BUS",

    # Mumbai Hubs
    "mumbai": "CSMT",
    "bombay": "CSMT",
    "cst": "CSMT",
    "csmt": "CSMT",
    "dadar": "DR",
    "dadar bus": "DADAR_ASIAD_BUS",
    "lokmanya tilak": "LTT",
    "ltt": "LTT",
    "kurla": "LTT",
    "thane": "TNA",
    "lonavala": "LNL",

    # Pune Hubs
    "pune": "PUNE",
    "pune junction": "PUNE",
    "shivajinagar": "SHIVAJINAGAR_BUS",
    "shivaji nagar": "SHIVAJINAGAR_BUS",
    "swargate": "SWARGATE_BUS",

    # Delhi NCR Hubs
    "delhi": "NDLS",
    "new delhi": "NDLS",
    "old delhi": "DLI",
    "hazrat nizamuddin": "NZM",
    "nizamuddin": "NZM",
    "anand vihar": "ANVT",
    "kashmere gate": "KASHMERE_GATE_BUS",
    "isbt": "KASHMERE_GATE_BUS",
    "gurgaon": "GGN",
    "rewari": "RE",

    # Jaipur Hubs
    "jaipur": "JP",
    "jaipur junction": "JP",
    "sindhi camp": "SINDHI_CAMP_BUS",
    "sindhi camp bus": "SINDHI_CAMP_BUS",
    "alwar": "AWR",
    "bandikui": "BKI",
    "dausa": "DO",
    "gandhi nagar jaipur": "GADJ",

    # Corridor Towns
    "katpadi": "KPD",
    "vellore": "KPD",
    "arakkonam": "AJJ",
    "jolarpettai": "JTJ",
    "bangarapet": "BWT",

    # Tirupati Hubs
    "tirupati": "TPTY",
    "renigunta": "RU",
    "tirupati bus": "TPTY_BUS",

    # Pudukkottai Hubs
    "pudukkottai": "PDKT",
    "pudukottai": "PDKT",
    "pdkt": "PDKT",
    "pudukkottai bus": "PDKT_BUS",

    # Kochi / Ernakulam Hubs
    "kochi": "ERS",
    "cochin": "ERS",
    "ernakulam": "ERS",
    "ernakulam junction": "ERS",

    # Ahmedabad & Gujarat
    "ahmedabad": "ADI",
    "amdavad": "ADI",
    "geeta mandir": "GEETA_MANDIR_BUS",
    "surat": "ST",

    # Uttar Pradesh Hubs
    "lucknow": "LKO",
    "charbagh": "LKO",
    "kaisarbagh": "KAISARBAGH_BUS",
    "varanasi": "BSB",
    "banaras": "BSB",
    "kashi": "BSB",

    # Other Regional Hubs
    "bhubaneswar": "BBS",
    "visakhapatnam": "VSKP",
    "vizag": "VSKP",
    "hubballi": "UBL",
    "hubli": "UBL",
    "thiruvananthapuram": "TVC",
    "trivandrum": "TVC"
}

class MistralService:
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.model_name = settings.MISTRAL_MODEL
        self.base_url = "https://api.mistral.ai/v1/chat/completions"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def parse_natural_language_query(self, user_prompt: str) -> Dict[str, Any]:
        """Convert natural language travel request into validated search parameters using Mistral AI."""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        if self.is_configured:
            try:
                system_prompt = (
                    "You are an expert Indian Public Transport assistant. "
                    "Extract structured travel parameters from the user's natural language request. "
                    f"Today's date is {today.strftime('%Y-%m-%d')} ({today.strftime('%A')}). "
                    f"Tomorrow's date is {tomorrow.strftime('%Y-%m-%d')} ({tomorrow.strftime('%A')}). "
                    "Resolve relative dates (e.g., 'tomorrow', 'this Friday', 'next Monday') to YYYY-MM-DD. "
                    "Map optimization preferences strictly to one of: 'fastest', 'cheapest', 'fewest_transfers', or 'delay_aware'. "
                    "Respond with a valid JSON object strictly matching this format:\n"
                    "{\n"
                    '  "origin": "Origin city or station name",\n'
                    '  "destination": "Destination city or station name",\n'
                    '  "travel_date": "YYYY-MM-DD",\n'
                    '  "departure_after": "HH:MM",\n'
                    '  "arrival_before": "HH:MM or null",\n'
                    '  "preferred_modes": ["train", "bus", "metro"],\n'
                    '  "optimisation": "fastest | cheapest | fewest_transfers | delay_aware",\n'
                    '  "max_transfers": null,\n'
                    '  "max_budget": null,\n'
                    '  "clarification_question": "Question if origin or destination is missing, otherwise null",\n'
                    '  "explanation_summary": "Friendly 1-sentence reply confirming parameters"\n'
                    "}"
                )

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }

                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(self.base_url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        content_str = resp.json()["choices"][0]["message"]["content"]
                        extracted_data = json.loads(content_str)
                        return self._resolve_and_validate(extracted_data, user_prompt, fallback=False)
                    else:
                        logger.warning(f"Mistral API error {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Mistral API call failed: {e}. Falling back to deterministic NLP parser.")

        # Graceful Deterministic Fallback Parser (offline rule-based)
        return self._offline_nlp_parse(user_prompt)

    def _offline_nlp_parse(self, prompt: str) -> Dict[str, Any]:
        """Deterministic offline rule-based parser when API key is unavailable or error occurs."""
        p_lower = prompt.lower()
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        origin_found = None
        dest_found = None

        from_to_match = re.search(r'from\s+([a-z\s\.\_]+?)\s+to\s+([a-z\s\.\_]+?)(?:\s+tomorrow|\s+today|\s+before|\s+after|\s+with|\s+under|\.|$)', p_lower)
        if from_to_match:
            cand_from = from_to_match.group(1).strip()
            cand_to = from_to_match.group(2).strip()
            origin_found = cand_from
            dest_found = cand_to
        else:
            matches = []
            for name, code in STATION_SYNONYMS.items():
                if name in p_lower:
                    matches.append((name, code))
            if len(matches) >= 2:
                origin_found = matches[0][0]
                dest_found = matches[1][0]
            elif len(matches) == 1:
                origin_found = matches[0][0]

        travel_date = today.strftime("%Y-%m-%d")
        if "tomorrow" in p_lower:
            travel_date = tomorrow.strftime("%Y-%m-%d")

        arr_before = None
        dep_after = "05:00"
        before_match = re.search(r'before\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', p_lower)
        if before_match:
            hr = int(before_match.group(1))
            mn = int(before_match.group(2) or 0)
            ampm = before_match.group(3)
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0
            arr_before = f"{hr:02d}:{mn:02d}"

        after_match = re.search(r'after\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', p_lower)
        if after_match:
            hr = int(after_match.group(1))
            mn = int(after_match.group(2) or 0)
            ampm = after_match.group(3)
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0
            dep_after = f"{hr:02d}:{mn:02d}"

        optimisation = "fastest"
        if "cheap" in p_lower or "budget" in p_lower or "low cost" in p_lower:
            optimisation = "cheapest"
        elif "fewest transfer" in p_lower or "direct" in p_lower or "less transfer" in p_lower:
            optimisation = "fewest_transfers"
        elif "delay" in p_lower or "punctual" in p_lower or "reliable" in p_lower:
            optimisation = "delay_aware"

        modes = []
        if "train" in p_lower:
            modes.append("train")
        if "bus" in p_lower:
            modes.append("bus")
        if "metro" in p_lower:
            modes.append("metro")
        if not modes:
            modes = ["train", "bus", "metro"]

        clarification = None
        if not origin_found and not dest_found:
            clarification = "Please specify both your origin and destination (e.g., 'From Chennai to Bengaluru')."
        elif not origin_found:
            clarification = "Where are you departing from?"
        elif not dest_found:
            clarification = f"Where would you like to travel to from {origin_found.title()}?"

        data = {
            "origin": origin_found,
            "destination": dest_found,
            "travel_date": travel_date,
            "departure_after": dep_after,
            "arrival_before": arr_before,
            "preferred_modes": modes,
            "optimisation": optimisation,
            "max_transfers": 1 if "direct" in p_lower else None,
            "max_budget": None,
            "clarification_question": clarification,
            "explanation_summary": f"Searching {optimisation} journeys from {origin_found or '...'} to {dest_found or '...'}"
        }
        return self._resolve_and_validate(data, prompt, fallback=True)

    def _resolve_and_validate(self, data: Dict[str, Any], raw_prompt: str, fallback: bool = False) -> Dict[str, Any]:
        """Resolve station names to station IDs and check validity."""
        orig_raw = str(data.get("origin") or "").strip().lower()
        dest_raw = str(data.get("destination") or "").strip().lower()

        origin_station_id = STATION_SYNONYMS.get(orig_raw, None)
        dest_station_id = STATION_SYNONYMS.get(dest_raw, None)

        if not origin_station_id and orig_raw:
            for syn, code in STATION_SYNONYMS.items():
                if syn in orig_raw:
                    origin_station_id = code
                    break

        if not dest_station_id and dest_raw:
            for syn, code in STATION_SYNONYMS.items():
                if syn in dest_raw:
                    dest_station_id = code
                    break

        if not origin_station_id:
            for syn, code in STATION_SYNONYMS.items():
                if syn in raw_prompt.lower():
                    origin_station_id = code
                    break

        if not dest_station_id:
            for syn, code in reversed(list(STATION_SYNONYMS.items())):
                if syn in raw_prompt.lower() and code != origin_station_id:
                    dest_station_id = code
                    break

        return {
            "origin_station_id": origin_station_id,
            "destination_station_id": dest_station_id,
            "origin_name": data.get("origin"),
            "destination_name": data.get("destination"),
            "travel_date": data.get("travel_date") or datetime.now().strftime("%Y-%m-%d"),
            "departure_after": data.get("departure_after") or "05:00",
            "arrival_before": data.get("arrival_before"),
            "preferred_modes": data.get("preferred_modes") or ["train", "bus", "metro"],
            "optimisation": data.get("optimisation") or "fastest",
            "max_transfers": data.get("max_transfers"),
            "max_budget": data.get("max_budget"),
            "clarification_question": data.get("clarification_question"),
            "assistant_reply": data.get("explanation_summary") or f"Here are the verified routes from {data.get('origin', 'your origin')} to {data.get('destination', 'your destination')}.",
            "is_ai_backed": self.is_configured and not fallback,
            "model_name": self.model_name if (self.is_configured and not fallback) else "offline_rule_engine",
            "fallback_used": fallback or not self.is_configured
        }

    def explain_route(self, journey: Dict[str, Any], user_preference: str = "fastest") -> Dict[str, Any]:
        """Generate reasoned explanation of a calculated route, its ML delay risk, and trade-offs using Mistral AI."""
        legs_summary = []
        for i, leg in enumerate(journey.get("legs", [])):
            dep_info = f"{leg.get('departure_date_formatted', '')} {leg.get('scheduled_departure', '')}".strip()
            arr_info = f"{leg.get('arrival_date_formatted', '')} {leg.get('scheduled_arrival', '')}".strip()
            legs_summary.append(
                f"Leg {i+1}: {leg['from_station_name']} -> {leg['to_station_name']} via {leg['mode'].upper()} "
                f"({leg.get('route_name', '')}), Boarding: {dep_info}, Arrival: {arr_info}, Fare: ₹{leg.get('fare_inr', 0)}"
                + (f", Predicted Delay: {leg['predicted_delay_min']} min ({leg.get('delay_risk_level', 'LOW')} Risk)" if leg.get('predicted_delay_min', 0) > 0 else "")
                + (f", Transfer Wait: {leg['transfer_wait_min']} min" if leg.get('transfer_wait_min', 0) > 0 else "")
            )

        journey_text = "\n".join(legs_summary)
        dep_str = f"{journey.get('departure_date_formatted', '')} {journey.get('scheduled_departure', '')}".strip()
        arr_str = f"{journey.get('arrival_date_formatted', '')} {journey.get('scheduled_arrival', '')}".strip()
        stats = (
            f"Departure: {dep_str}, Arrival: {arr_str}, "
            f"Total Duration: {journey.get('scheduled_duration_formatted')} (Estimated with ML: {journey.get('estimated_duration_formatted')}), "
            f"Total Fare: ₹{journey.get('total_fare_inr')} ({'Verified' if journey.get('is_fare_verified') else 'Unverified'}), "
            f"Transfers: {journey.get('transfer_count')}, Delay Risk: {journey.get('delay_risk_level')}, Total Predicted Delay: {journey.get('predicted_delay_min')} min."
        )

        if self.is_configured:
            try:
                system_prompt = (
                    "You are a public transit journey planner assistant for India. "
                    "Analyze the provided transit route and explain why it is recommended based on the user's optimization priority. "
                    "Highlight trade-offs between speed, cost, and machine learning delay risk. "
                    "Do NOT invent fictional schedules or fares; use strictly the provided data. "
                    "Keep the response professional, helpful, and concise (under 120 words)."
                )
                user_msg = (
                    f"User Optimization Preference: '{user_preference}'\n\n"
                    f"Journey Legs:\n{journey_text}\n\n"
                    f"Summary Metrics:\n{stats}\n\n"
                    "Provide a clear, helpful route explanation."
                )

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.2
                }

                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(self.base_url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        text_resp = resp.json()["choices"][0]["message"]["content"].strip()
                        return {
                            "explanation": text_resp,
                            "is_ai_backed": True,
                            "model_name": self.model_name
                        }
                    else:
                        logger.warning(f"Mistral explain API error {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Mistral explanation generation failed: {e}")

        # Grounded Deterministic Explainer
        dur = journey.get("scheduled_duration_formatted", "")
        fare = journey.get("total_fare_inr", 0)
        trans = journey.get("transfer_count", 0)
        delay = journey.get("predicted_delay_min", 0.0)
        risk = journey.get("delay_risk_level", "LOW")
        mode_str = ", ".join(journey.get("modes", []))

        exp = (
            f"This {mode_str} journey covers {journey.get('total_distance_km')} km in {dur} with a verified fare of ₹{fare:.0f}. "
            f"With {trans} transfer(s), our machine learning model estimates an arrival delay of approximately {delay:.1f} minutes "
            f"(Delay Risk: {risk}). "
            f"{'Direct connection eliminates transfer risks.' if trans == 0 else 'Adequate transfer buffer windows have been scheduled between connections.'} "
            f"Estimates are model-backed from historical railway operations and subject to real-time track conditions."
        )
        return {
            "explanation": exp,
            "is_ai_backed": False,
            "model_name": "offline_rule_engine"
        }

