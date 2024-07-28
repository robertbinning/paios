from fastapi import HTTPException, Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from webauthn import (
    verify_registration_response,
    verify_authentication_response
)
import webauthn
from backend.models import User
from backend.db import SessionLocal, engine  # Ensure correct import

class RegistrationOptions(BaseModel):
    email: str

class VerifyRegistration(BaseModel):
    email: str
    att_resp: dict

class AuthenticationOptions(BaseModel):
    email: str

class VerifyAuthentication(BaseModel):
    email: str
    auth_resp: dict

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/webauthn/generate-registration-options")
async def generate_registration_options(registration_options: RegistrationOptions, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == registration_options.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    options = webauthn.generate_registration_options(
        rp_name="pAI-OS",
        user_id=str(user.id),
        user_name=user.email,
        attestation="direct",
        authenticator_selection={"userVerification": "preferred"},
    )

    user.current_challenge = options["challenge"]
    db.commit()

    return options

@router.post("/webauthn/verify-registration")
async def verify_registration(verify_registration: VerifyRegistration, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == verify_registration.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verification = verify_registration_response(
        response=verify_registration.att_resp,
        expected_challenge=user.current_challenge,
        expected_origin="https://localhost:3080",
        expected_rp_id="localhost",
    )

    if verification.verified:
        user.current_challenge = None
        user.credential_id = verification.registration_info.credential_id
        db.commit()

    return {"verified": verification.verified}

@router.post("/webauthn/generate-authentication-options")
async def generate_authentication_options(authentication_options: AuthenticationOptions, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == authentication_options.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    options = webauthn.generate_authentication_options(
        allow_credentials=[
            {"id": user.credential_id, "type": "public-key", "transports": ["usb", "ble", "nfc"]}
        ],
        user_verification="preferred",
    )

    user.current_challenge = options["challenge"]
    db.commit()

    return options

@router.post("/webauthn/verify-authentication")
async def verify_authentication(verify_authentication: VerifyAuthentication, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == verify_authentication.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verification = verify_authentication_response(
        response=verify_authentication.auth_resp,
        expected_challenge=user.current_challenge,
        expected_origin="https://localhost:3080",
        expected_rp_id="localhost",
    )

    if verification.verified:
        user.current_challenge = None
        db.commit()

    return {"verified": verification.verified}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=3080, ssl_certfile="./localhost+2.pem", ssl_keyfile="./localhost+2-key.pem")
