import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueryExtraction(BaseModel):
    origin: Optional[str] = Field(None, description="Origin city or station name")
    destination: Optional[str] = Field(None, description="Destination city or station name")
    travel_date: Optional[str] = Field(None, description="Resolved date in YYYY-MM-DD")
    departure_after: Optional[str] = Field(None, description="Time in HH:MM after which journey should start")
    arrival_before: Optional[str] = Field(None, description="Time in HH:MM before which user needs to arrive")
    preferred_modes: List[str] = Field(default_factory=lambda: ["train", "bus", "metro"], description="List of preferred modes")
    optimisation: str = Field(default="fastest", description="One of: fastest, cheapest, fewest_transfers, delay_aware")
    max_transfers: Optional[int] = Field(None, description="Maximum number of transfers allowed")
    max_budget: Optional[float] = Field(None, description="Budget in INR")
    clarification_question: Optional[str] = Field(None, description="Question to ask if origin or destination is missing")
    explanation_summary: str = Field(default="", description="Brief friendly conversational summary")

STATION_SYNONYMS = {
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
    "bengaluru": "SBC",
    "bangalore": "SBC",
    "ksr bengaluru": "SBC",
    "majestic": "BMRCL_MAJESTIC",
    "majestic bus": "KBS_BUS",
    "whitefield": "BMRCL_WHITEFIELD",
    "krishnarajapuram": "KJM",
    "kr puram": "KJM",
    "yesvantpur": "YPR",
    "smvt": "SMVB",
    "cantt": "BNC",
    "bangalore cantt": "BNC",
    "electronic city": "ECITY_BUS",
    "silk board": "SILKBOARD_BUS",
    "shantinagar": "SHANTINAGAR_BUS",
    "katpadi": "KPD",
    "vellore": "KPD",
    "arakkonam": "AJJ",
    "jolarpettai": "JTJ",
    "bangarapet": "BWT"
}

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.client = None

        if self.api_key and self.api_key.strip():
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google Gemini client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize google.genai Client: {e}")
                self.client = None

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    def parse_natural_language_query(self, user_prompt: str) -> Dict[str, Any]:
        """Convert natural language travel request into validated search parameters."""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        # If Gemini API key is configured, use structured prompt
        if self.is_configured:
            try:
                system_instruction = (
                    "You are an expert Indian Public Transport assistant. "
                    "Extract structured travel parameters from the user's natural language request. "
                    f"Today's date is {today.strftime('%Y-%m-%d')} ({today.strftime('%A')}). "
                    f"Tomorrow's date is {tomorrow.strftime('%Y-%m-%d')} ({tomorrow.strftime('%A')}). "
                    "Resolve relative dates (e.g., 'tomorrow', 'this Friday', 'next Monday') to YYYY-MM-DD. "
                    "Map optimization preferences to: 'fastest', 'cheapest', 'fewest_transfers', or 'delay_aware'. "
                    "Return strictly valid JSON adhering to the QueryExtraction schema. "
                    "Do NOT invent fictional schedules or fares."
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": QueryExtraction,
                        "system_instruction": system_instruction
                    }
                )

                extracted_data = json.loads(response.text)
                return self._resolve_and_validate(extracted_data, user_prompt)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to deterministic NLP parser.")

        # Graceful Deterministic Fallback Parser (offline rule-based)
        return self._offline_nlp_parse(user_prompt)

    def _offline_nlp_parse(self, prompt: str) -> Dict[str, Any]:
        """Deterministic offline rule-based parser when Gemini API key is unavailable."""
        p_lower = prompt.lower()
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        origin_found = None
        dest_found = None

        # Detect 'from X to Y' pattern
        from_to_match = re.search(r'from\s+([a-z\s\.\_]+?)\s+to\s+([a-z\s\.\_]+?)(?:\s+tomorrow|\s+today|\s+before|\s+after|\s+with|\s+under|\.|$)', p_lower)
        if from_to_match:
            cand_from = from_to_match.group(1).strip()
            cand_to = from_to_match.group(2).strip()
            origin_found = cand_from
            dest_found = cand_to
        else:
            # Match known cities/stations
            matches = []
            for name, code in STATION_SYNONYMS.items():
                if name in p_lower:
                    matches.append((name, code))
            if len(matches) >= 2:
                origin_found = matches[0][0]
                dest_found = matches[1][0]
            elif len(matches) == 1:
                origin_found = matches[0][0]

        # Date detection
        travel_date = today.strftime("%Y-%m-%d")
        if "tomorrow" in p_lower:
            travel_date = tomorrow.strftime("%Y-%m-%d")

        # Time detection
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

        # Optimization
        optimisation = "fastest"
        if "cheap" in p_lower or "budget" in p_lower or "low cost" in p_lower:
            optimisation = "cheapest"
        elif "fewest transfer" in p_lower or "direct" in p_lower or "less transfer" in p_lower:
            optimisation = "fewest_transfers"
        elif "delay" in p_lower or "punctual" in p_lower or "reliable" in p_lower:
            optimisation = "delay_aware"

        # Preferred Modes
        modes = []
        if "train" in p_lower:
            modes.append("train")
        if "bus" in p_lower:
            modes.append("bus")
        if "metro" in p_lower:
            modes.append("metro")
        if not modes:
            modes = ["train", "bus", "metro"]

        # Clarification question if missing origin or destination
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

        # Fuzzy partial matching if exact synonym not matched
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

        # Check default corridor if city names were used
        if not origin_station_id and "chennai" in raw_prompt.lower():
            origin_station_id = "MAS"
        if not dest_station_id and ("bengaluru" in raw_prompt.lower() or "bangalore" in raw_prompt.lower()):
            dest_station_id = "SBC"

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
            "is_gemini_backed": self.is_configured and not fallback,
            "fallback_used": fallback or not self.is_configured
        }

    def explain_route(self, journey: Dict[str, Any], user_preference: str = "fastest") -> Dict[str, Any]:
        """Generate reasoned explanation of a calculated route, its ML delay risk, and trade-offs."""
        legs_summary = []
        for i, leg in enumerate(journey.get("legs", [])):
            legs_summary.append(
                f"Leg {i+1}: {leg['from_station_name']} -> {leg['to_station_name']} via {leg['mode'].upper()} "
                f"({leg['route_name']}), Dep: {leg['scheduled_departure']}, Arr: {leg['scheduled_arrival']}, Fare: ₹{leg['fare_inr']}"
                + (f", Predicted Delay: {leg['predicted_delay_min']} min" if leg.get('predicted_delay_min', 0) > 0 else "")
            )

        journey_text = "\n".join(legs_summary)
        stats = (
            f"Total Duration: {journey.get('scheduled_duration_formatted')} (Estimated: {journey.get('estimated_duration_formatted')}), "
            f"Total Fare: ₹{journey.get('total_fare_inr')}, Transfers: {journey.get('transfer_count')}, "
            f"Delay Risk: {journey.get('delay_risk_level')}, Total Predicted Delay: {journey.get('predicted_delay_min')} min."
        )

        if self.is_configured:
            try:
                prompt = (
                    f"Explain why this public transit journey is recommended for a user prioritizing '{user_preference}'.\n\n"
                    f"Journey Details:\n{journey_text}\n\nKey Metrics:\n{stats}\n\n"
                    "Requirements:\n"
                    "- Highlight speed, cost, and transfer trade-offs.\n"
                    "- Explain the machine learning train delay prediction and whether transfer buffers are safe.\n"
                    "- Remind the user that delays are data-driven estimates and not guarantees.\n"
                    "- Keep response concise (under 120 words), professional, and grounded in the data provided."
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return {
                    "explanation": response.text.strip(),
                    "is_gemini_backed": True
                }
            except Exception as e:
                logger.warning(f"Gemini explanation generation failed: {e}")

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
            "is_gemini_backed": False,
            "notice": "Generated via deterministic rules (Configure GEMINI_API_KEY in .env for custom conversational LLM explanations)."
        }

