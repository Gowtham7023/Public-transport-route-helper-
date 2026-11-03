from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import (
    AIQueryRequest, AIQueryResponse, AIExplainRequest, AIExplainResponse
)
from app.services.mistral_service import MistralService
from app.services.route_engine import GraphRouteEngine
from app.api.routes import get_route_engine, resolve_station_candidates, resolve_station_id

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])

_ai_service_instance = None

def get_ai_service() -> MistralService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = MistralService()
    return _ai_service_instance

@router.post("/query", response_model=AIQueryResponse)
def natural_language_query(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    ai_svc: MistralService = Depends(get_ai_service),
    engine: GraphRouteEngine = Depends(get_route_engine)
):
    """
    Process natural language travel queries using Mistral AI NLU,
    extract validated search parameters, and query the Graph Route Engine.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Query prompt cannot be empty.")

    # 1. Extract travel parameters using Mistral Service
    parsed = ai_svc.parse_natural_language_query(request.prompt)

    # 2. Check if clarification is needed (e.g., missing destination)
    if parsed.get("clarification_question") and not (parsed.get("origin_station_id") and parsed.get("destination_station_id")):
        return AIQueryResponse(
            prompt=request.prompt,
            parsed_parameters=parsed,
            clarification_question=parsed["clarification_question"],
            assistant_reply=parsed["clarification_question"],
            routes_found=0,
            recommended_journeys=[],
            is_ai_backed=parsed.get("is_ai_backed", False),
            is_gemini_backed=parsed.get("is_ai_backed", False),
            model_name=parsed.get("model_name"),
            notice="Please provide departure and arrival points to calculate route options."
        )

    orig_input = parsed.get("origin_station_id") or parsed.get("origin")
    dest_input = parsed.get("destination_station_id") or parsed.get("destination")

    orig_ids, orig_disp = resolve_station_candidates(orig_input, db, parsed.get("preferred_modes"))
    dest_ids, dest_disp = resolve_station_candidates(dest_input, db, parsed.get("preferred_modes"))

    if not orig_ids or not dest_ids:
        return AIQueryResponse(
            prompt=request.prompt,
            parsed_parameters=parsed,
            clarification_question=f"Could not resolve active transit stations for {parsed.get('origin', 'origin')} to {parsed.get('destination', 'destination')}.",
            assistant_reply="Transit stations for this corridor could not be found in the active transit graph.",
            routes_found=0,
            recommended_journeys=[],
            is_ai_backed=parsed.get("is_ai_backed", False),
            is_gemini_backed=parsed.get("is_ai_backed", False),
            model_name=parsed.get("model_name"),
            notice="Please search between supported cities in the verified transit network."
        )

    # 3. Query Graph Route Engine with extracted parameters across all candidate stations
    res = engine.search_multimodal_journeys(
        origin_stations=orig_ids,
        dest_stations=dest_ids,
        travel_date=parsed.get("travel_date", "2026-11-04"),
        dep_after=parsed.get("departure_after", "00:00"),
        arrival_before=parsed.get("arrival_before"),
        preferred_modes=parsed.get("preferred_modes"),
        optimisation=parsed.get("optimisation", "fastest"),
        max_transfers=parsed.get("max_transfers"),
        max_budget=parsed.get("max_budget"),
        limit=10
    )
    journeys = res["journeys"]

    reply = parsed.get("assistant_reply") or f"Found {len(journeys)} verified journeys between {orig_disp or orig_input} and {dest_disp or dest_input}."

    notice = None
    if not ai_svc.is_configured:
        notice = "Conversational parser operating in offline deterministic mode. Configure MISTRAL_API_KEY in .env."

    return AIQueryResponse(
        prompt=request.prompt,
        parsed_parameters=parsed,
        clarification_question=None,
        assistant_reply=reply,
        routes_found=len(journeys),
        recommended_journeys=journeys,
        is_ai_backed=parsed.get("is_ai_backed", False),
        is_gemini_backed=parsed.get("is_ai_backed", False),
        model_name=parsed.get("model_name"),
        notice=notice
    )

@router.post("/explain-route", response_model=AIExplainResponse)
def explain_route(
    request: AIExplainRequest,
    ai_svc: MistralService = Depends(get_ai_service)
):
    """Generate structured route explanation explaining speed, fares, and ML delay trade-offs using Mistral AI."""
    if not request.journey:
        raise HTTPException(status_code=400, detail="Journey object required for explanation.")

    result = ai_svc.explain_route(
        journey=request.journey,
        user_preference=request.user_preference or "fastest"
    )

    return AIExplainResponse(
        explanation=result["explanation"],
        is_ai_backed=result.get("is_ai_backed", False),
        is_gemini_backed=result.get("is_ai_backed", False),
        model_name=result.get("model_name"),
        notice=result.get("notice")
    )
