from event_api.db.postgres import SessionLocal
from event_api.db.models import User
from event_api.security import (
    hash_password,
    verify_password,
    create_access_token
)


def create_user(user_data):
    """
    Create new customer account
    """

    db = SessionLocal()

    existing = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing:
        db.close()
        return None

    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        city=user_data.city,
        area=user_data.area
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    token = create_access_token({
        "user_id": user.user_id,
        "email": user.email
    })

    return {
        "user": user,
        "token": token
    }


def login_user(login_data):
    """
    Validate customer login
    """

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user:
        db.close()
        return None

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        db.close()
        return None

    token = create_access_token({
        "user_id": user.user_id,
        "email": user.email
    })

    db.close()

    return {
        "user": user,
        "token": token
    }