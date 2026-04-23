from fastapi import Header, HTTPException
from jose import jwt
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.split(" ")[1]

        # Fetch JWKS
        jwks = requests.get(JWKS_URL).json()

        # Extract header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        # Find correct key
        key = next(
            (k for k in jwks["keys"] if k["kid"] == kid),
            None
        )

        if not key:
            raise HTTPException(status_code=401, detail="Public key not found")

        # Decode token
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            options={"verify_aud": False}
        )

        return payload["sub"]

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")