from fastapi import APIRouter, HTTPException
from event_api.schemas.auth_schema import (
    SignupRequest,
    LoginRequest
)
from event_api.services.auth_service import (
    create_user,
    login_user
)
from uuid import uuid4
from datetime import datetime, UTC
from kafka_engine.producers.producer import publish_event


router = APIRouter(prefix="/auth", tags=["Authentication"])


def build_event(event_type, payload):
    """
    Standard event builder
    """

    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "event_ts": datetime.now(UTC).isoformat(),
        "source_system": "customer-ui",
        "payload": payload
    }


@router.post("/signup")
def signup(payload: SignupRequest):
    """
    Customer signup
    """

    result = create_user(payload)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    event = build_event(
        "USER_REGISTERED",
        {
            "user_id": result["user"].user_id,
            "name": result["user"].name,
            "phone": result["user"].phone,
            "email": result["user"].email,
            "city": result["user"].city,
            "area": result["user"].area
        }
    )

    publish_event(
        "user_activity_events",
        event
    )

    return {
        "message": "Signup successful",
        "access_token": result["token"]
    }


@router.post("/login")
def login(payload: LoginRequest):
    """
    Customer login
    """

    result = login_user(payload)

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    event = build_event(
        "USER_LOGGED_IN",
        {
            "user_id": result["user"].user_id,
            "email": result["user"].email
        }
    )

    publish_event(
        "user_activity_events",
        event
    )

    return {
        "message": "Login successful",
        "access_token": result["token"]
    }